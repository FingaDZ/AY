from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from decimal import Decimal

from database import get_db
from models import Conge, Employe, Pointage, ActionType, User
from pydantic import BaseModel
from datetime import date, datetime, timedelta
from services.logging_service import log_action
from middleware.auth import get_current_user

router = APIRouter(prefix="/conges", tags=["Congés"])

# Schemas locaux pour éviter les dépendances circulaires ou complexes
class CongeUpdate(BaseModel):
    jours_pris: float  # v3.5.3: Décimales supportées
    mois_deduction: Optional[int] = None  # Mois où déduire du bulletin de paie (1-12)
    annee_deduction: Optional[int] = None  # Année où déduire du bulletin de paie

class CongeCreateFromDates(BaseModel):
    employe_id: int
    date_debut: date
    date_fin: date
    type_conge: str = "ANNUEL"
    commentaire: Optional[str] = None

class CongeResponse(BaseModel):
    id: int
    employe_id: int
    employe_nom: str
    employe_prenom: str
    annee: int
    mois: int
    jours_travailles: int
    jours_conges_acquis: float  # v3.5.3: Décimales
    jours_conges_pris: float    # v3.5.3: Décimales
    jours_conges_restants: float  # v3.5.3: Décimales
    mois_deduction: Optional[int] = None  # Mois de déduction bulletin
    annee_deduction: Optional[int] = None  # Année de déduction bulletin

    class Config:
        from_attributes = True

@router.get("/", response_model=List[CongeResponse])
def list_conges(
    employe_id: Optional[int] = None,
    annee: Optional[int] = None,
    mois: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Lister les congés avec filtres"""
    query = db.query(Conge).join(Employe)
    
    if employe_id:
        query = query.filter(Conge.employe_id == employe_id)
    
    if annee:
        query = query.filter(Conge.annee == annee)
    
    if mois:
        query = query.filter(Conge.mois == mois)
        
    # Tri par année/mois décroissant
    query = query.order_by(Conge.annee.desc(), Conge.mois.desc(), Employe.nom)
    
    conges = query.all()
    
    # Transformation pour la réponse
    results = []
    for c in conges:
        results.append(CongeResponse(
            id=c.id,
            employe_id=c.employe_id,
            employe_nom=c.employe.nom,
            employe_prenom=c.employe.prenom,
            annee=c.annee,
            mois=c.mois,
            jours_travailles=c.jours_travailles,
            jours_conges_acquis=float(c.jours_conges_acquis or 0),  # ⭐ v3.6.0 Phase 5: Décimal
            jours_conges_pris=float(c.jours_conges_pris or 0),  # ⭐ v3.6.0
            jours_conges_restants=float(c.jours_conges_restants or 0),  # ⭐ v3.6.0
            mois_deduction=c.mois_deduction,
            annee_deduction=c.annee_deduction
        ))
        
    return results

@router.put("/{conge_id}/consommation")
def update_consommation(
    conge_id: int,
    update: CongeUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mettre à jour la consommation de congés pour un mois donné"""
    conge = db.query(Conge).filter(Conge.id == conge_id).first()
    if not conge:
        raise HTTPException(status_code=404, detail="Enregistrement congé non trouvé")
    
    # Sauvegarder l'ancienne valeur (convertir Decimal en float pour JSON)
    old_jours_pris = float(conge.jours_conges_pris or 0)
    
    # v3.5.3: VALIDATION STRICTE avec support décimales
    jours_pris = float(update.jours_pris)
    
    # Calculer le total acquis pour cet employé
    stats = db.query(
        func.sum(Conge.jours_conges_acquis).label("total_acquis")
    ).filter(Conge.employe_id == conge.employe_id).first()
    
    total_acquis = float(stats.total_acquis or 0)
    
    # Calculer total pris (sans compter ce mois)
    total_pris_autres = db.query(
        func.sum(Conge.jours_conges_pris)
    ).filter(
        Conge.employe_id == conge.employe_id,
        Conge.id != conge_id
    ).scalar() or 0
    
    total_pris_prevu = float(total_pris_autres) + jours_pris
    
    # BLOCAGE: Interdire de prendre plus que l'acquis
    if total_pris_prevu > total_acquis:
        raise HTTPException(
            status_code=400,
            detail=f"INTERDIT: Congés pris ({total_pris_prevu:.2f}j) > Congés acquis ({total_acquis:.2f}j). Solde insuffisant!"
        )
    
    # Mise à jour (v3.5.3: avec décimales)
    conge.jours_conges_pris = jours_pris
    
    # Mise à jour du mois/année de déduction si fournis
    if update.mois_deduction is not None:
        if not (1 <= update.mois_deduction <= 12):
            raise HTTPException(status_code=400, detail="Mois de déduction invalide (doit être entre 1 et 12)")
        conge.mois_deduction = update.mois_deduction
        
    if update.annee_deduction is not None:
        if update.annee_deduction < 2000 or update.annee_deduction > 2100:
            raise HTTPException(status_code=400, detail="Année de déduction invalide")
        conge.annee_deduction = update.annee_deduction
    
    # ⭐ CORRECTION v3.6.1: Recalcul du SOLDE CUMULÉ (pas juste cette période)
    # Solde = (Total acquis depuis début) - (Total pris depuis début)
    stats_cumul = db.query(
        func.sum(Conge.jours_conges_acquis).label("total_acquis"),
        func.sum(Conge.jours_conges_pris).label("total_pris")
    ).filter(
        Conge.employe_id == conge.employe_id,
        (Conge.annee < conge.annee) | ((Conge.annee == conge.annee) & (Conge.mois <= conge.mois))
    ).first()
    
    total_acquis_cumul = float(stats_cumul.total_acquis or 0)
    total_pris_cumul = float(stats_cumul.total_pris or 0)
    conge.jours_conges_restants = total_acquis_cumul - total_pris_cumul
    
    db.commit()
    db.refresh(conge)
    
    # Log l'action
    log_action(
        db=db,
        module_name="conges",
        action_type=ActionType.UPDATE,
        record_id=conge_id,
        old_data={"jours_pris": old_jours_pris},
        new_data={"jours_pris": jours_pris},
        description=f"Modification consommation congés {conge.mois}/{conge.annee} - Employé #{conge.employe_id}",
        user=current_user,
        request=request
    )
    
    return {"message": "Consommation mise à jour", "conge_id": conge.id}

@router.get("/synthese/{employe_id}")
def get_synthese_conges(employe_id: int, db: Session = Depends(get_db)):
    """Obtenir la synthèse des congés pour un employé (Total Acquis, Total Pris, Solde)"""
    
    employe = db.query(Employe).filter(Employe.id == employe_id).first()
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
        
    stats = db.query(
        func.sum(Conge.jours_conges_acquis).label("total_acquis"),
        func.sum(Conge.jours_conges_pris).label("total_pris")
    ).filter(Conge.employe_id == employe_id).first()
    
    total_acquis = float(stats.total_acquis or 0)
    total_pris = float(stats.total_pris or 0)
    solde = total_acquis - total_pris
    
    return {
        "employe": f"{employe.prenom} {employe.nom}",
        "total_acquis": round(total_acquis, 2),
        "total_pris": round(total_pris, 2),
        "solde": round(solde, 2)
    }

@router.get("/verifier-saisie/{annee}/{mois}")
def verifier_saisie_conges(annee: int, mois: int, db: Session = Depends(get_db)):
    """Vérifier si des congés ont été pris mais non saisis pour une période"""
    
    # Récupérer tous les enregistrements de congés pour cette période
    conges = db.query(Conge).join(Employe).filter(
        Conge.annee == annee,
        Conge.mois == mois,
        Employe.statut == "Actif"
    ).all()
    
    conges_non_saisis = []
    
    for conge in conges:
        # Si jours_conges_acquis > 0 mais jours_conges_pris est NULL/0
        # ET qu'il y a des jours marqués comme "Congé" dans les pointages
        pointage = db.query(Pointage).filter(
            Pointage.employe_id == conge.employe_id,
            Pointage.annee == annee,
            Pointage.mois == mois
        ).first()
        
        if pointage:
            # Compter les jours de congé dans les pointages (valeur = 1)
            jours_conge_pointage = 0
            for i in range(1, 32):
                jour_col = f"jour_{str(i).zfill(2)}"
                if hasattr(pointage, jour_col):
                    val = getattr(pointage, jour_col)
                    # Si congé (valeur 1) et pas travail normal
                    # On suppose que les congés sont marqués d'une certaine façon
                    # Pour simplifier: on vérifie si jours_conges_pris est à 0 ou None
                    pass
            
            # Vérifier si congé_pris non saisi mais acquis existe
            if conge.jours_conges_acquis > 0 and (conge.jours_conges_pris is None or conge.jours_conges_pris == 0):
                conges_non_saisis.append({
                    "employe_id": conge.employe_id,
                    "employe_nom": f"{conge.employe.prenom} {conge.employe.nom}",
                    "jours_acquis": conge.jours_conges_acquis,
                    "conge_id": conge.id
                })
    
    return {
        "annee": annee,
        "mois": mois,
        "conges_non_saisis": conges_non_saisis,
        "count": len(conges_non_saisis),
        "a_verifier": len(conges_non_saisis) > 0
    }

@router.post("/creer-depuis-dates")
def creer_conge_depuis_dates(
    conge_data: CongeCreateFromDates,
    db: Session = Depends(get_db)
):
    """
    Créer un enregistrement de congé depuis des dates et marquer les jours dans les pointages
    Les jours de congé sont considérés comme travaillés (valeur=1) pour la paie
    """
    employe = db.query(Employe).filter(Employe.id == conge_data.employe_id).first()
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    # Calculer le nombre de jours ouvrables (exclure vendredi et samedi)
    current_date = conge_data.date_debut
    jours_pris = 0
    jours_par_mois = {}  # {(annee, mois): [jours]}
    
    while current_date <= conge_data.date_fin:
        # Exclure vendredi (4) et samedi (5)
        if current_date.weekday() not in [4, 5]:
            jours_pris += 1
            key = (current_date.year, current_date.month)
            if key not in jours_par_mois:
                jours_par_mois[key] = []
            jours_par_mois[key].append(current_date.day)
        current_date += timedelta(days=1)
    
    # Mettre à jour les pointages (marquer comme Congé = 1 pour être payé)
    for (annee, mois), jours in jours_par_mois.items():
        pointage = db.query(Pointage).filter(
            Pointage.employe_id == conge_data.employe_id,
            Pointage.annee == annee,
            Pointage.mois == mois
        ).first()
        
        if not pointage:
            # Créer le pointage s'il n'existe pas
            pointage = Pointage(
                employe_id=conge_data.employe_id,
                annee=annee,
                mois=mois,
                verrouille=0
            )
            db.add(pointage)
            db.flush()
        
        # Marquer les jours de congé comme travaillés (1) pour la paie
        for jour in jours:
            pointage.set_jour(jour, 1)
        
        # Mettre à jour ou créer l'enregistrement de congé mensuel
        conge = db.query(Conge).filter(
            Conge.employe_id == conge_data.employe_id,
            Conge.annee == annee,
            Conge.mois == mois
        ).first()
        
        if not conge:
            conge = Conge(
                employe_id=conge_data.employe_id,
                annee=annee,
                mois=mois,
                jours_travailles=0,
                jours_conges_acquis=0,
                jours_conges_pris=0,
                jours_conges_restants=0
            )
            db.add(conge)
        
        # Ajouter les jours pris dans ce mois (v3.5.3: avec décimales)
        jours_mois = float(len(jours))
        conge.jours_conges_pris = float(conge.jours_conges_pris or 0) + jours_mois
        conge.date_debut = conge_data.date_debut
        conge.date_fin = conge_data.date_fin
        conge.type_conge = conge_data.type_conge
        conge.commentaire = conge_data.commentaire
        conge.jours_conges_restants = float(conge.jours_conges_acquis or 0) - float(conge.jours_conges_pris or 0)
    
    db.commit()
    
    return {
        "message": "Congé enregistré avec succès",
        "jours_pris": jours_pris,
        "mois_impactes": len(jours_par_mois)
    }

@router.post("/recalculer-periode")
def recalculer_conges_periode(
    annee: int,
    mois: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recalculer tous les congés pour une période donnée
    
    Utile après:
    - Vidage de la base de données
    - Corrections massives de pointages
    - Migration de version
    """
    from services.conges_calculator import recalculer_conges_periode
    
    results = recalculer_conges_periode(db, annee, mois)
    
    # Log l'action
    log_action(
        db=db,
        module_name="conges",
        action_type=ActionType.UPDATE,
        record_id=0,
        new_data=results,
        description=f"Recalcul batch congés {mois}/{annee} - {results['recalcules']} recalculés",
        user=current_user,
        request=request
    )
    
    return {
        "message": f"Recalcul terminé pour {mois}/{annee}",
        "recalcules": results["recalcules"],
        "erreurs": results["erreurs"],
        "details": results["details"]
    }

@router.get("/{conge_id}/titre-conge")
def generer_titre_conge(conge_id: int, db: Session = Depends(get_db)):
    """Générer un titre de congé (PDF) pour un employé"""
    conge = db.query(Conge).filter(Conge.id == conge_id).first()
    if not conge:
        raise HTTPException(status_code=404, detail="Congé non trouvé")
    
    employe = conge.employe
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    # Générer le PDF
    from services.pdf_generator import PDFGenerator
    pdf_gen = PDFGenerator()
    
    # Créer les données pour le titre de congé
    titre_data = {
        "employe": employe,
        "conge": conge,
        "date_debut": conge.date_debut or date.today(),
        "date_fin": conge.date_fin or date.today(),
        "type_conge": conge.type_conge or "ANNUEL",
        "jours_pris": float(conge.jours_conges_pris or 0),
        "commentaire": conge.commentaire or ""
    }
    
    pdf_bytes = pdf_gen.generate_titre_conge(titre_data)
    
    return StreamingResponse(
        pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=titre_conge_{employe.nom}_{employe.prenom}_{conge.annee}_{conge.mois}.pdf"
        }
    )
