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

def repartir_conges_intelligemment(
    db: Session,
    employe_id: int,
    jours_a_prendre: float,
    mois_deduction: int,
    annee_deduction: int
) -> List[dict]:
    """
    Répartir intelligemment les jours de congé à prendre sur les périodes disponibles.
    
    Logique:
    1. Récupère toutes les périodes avec solde disponible (acquis > pris)
    2. Trie par ancienneté (année, mois croissant)
    3. Déduit d'abord des mois les plus anciens
    4. Ne dépasse jamais les jours acquis de chaque période
    
    Args:
        db: Session SQLAlchemy
        employe_id: ID de l'employé
        jours_a_prendre: Nombre total de jours à prendre
        mois_deduction: Mois de déduction sur bulletin
        annee_deduction: Année de déduction sur bulletin
        
    Returns:
        Liste de dicts: [{'conge_id': int, 'jours_a_deduire': float, 'periode': str}, ...]
        
    Raises:
        HTTPException: Si solde insuffisant
    """
    # Récupérer toutes les périodes avec leurs soldes disponibles
    periodes = db.query(Conge).filter(
        Conge.employe_id == employe_id
    ).order_by(Conge.annee.asc(), Conge.mois.asc()).all()
    
    repartition = []
    reste_a_prendre = jours_a_prendre
    
    for periode in periodes:
        if reste_a_prendre <= 0:
            break
            
        # Calcul du disponible pour cette période
        acquis = float(periode.jours_conges_acquis or 0)
        pris = float(periode.jours_conges_pris or 0)
        disponible = acquis - pris
        
        if disponible <= 0:
            continue  # Période déjà consommée
        
        # Prendre le minimum entre ce qui reste à prendre et ce qui est disponible
        a_deduire = min(reste_a_prendre, disponible)
        
        repartition.append({
            'conge_id': periode.id,
            'periode': f"{periode.mois}/{periode.annee}",
            'acquis': acquis,
            'pris_avant': pris,
            'jours_a_deduire': a_deduire,
            'nouveau_pris': pris + a_deduire,
            'mois_deduction': mois_deduction,
            'annee_deduction': annee_deduction
        })
        
        reste_a_prendre -= a_deduire
    
    # Vérifier si on a pu tout répartir
    if reste_a_prendre > 0.01:  # Tolérance 0.01j pour erreurs d'arrondi
        total_disponible = sum(r['jours_a_deduire'] for r in repartition)
        raise HTTPException(
            status_code=400,
            detail=f"Solde insuffisant! Demande: {jours_a_prendre:.2f}j, Disponible: {total_disponible:.2f}j, Manque: {reste_a_prendre:.2f}j"
        )
    
    return repartition

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
    """
    Mettre à jour la consommation de congés avec répartition intelligente TOTALE
    
    LOGIQUE v3.6.1 CORRIGÉE:
    - jours_pris = TOTAL GLOBAL que l'employé doit prendre (pas un ajout!)
    - Le système réinitialise toutes les périodes puis répartit ce total
    - Répartition automatique: du plus ancien au plus récent
    - Validation: ne jamais dépasser l'acquis de chaque période
    
    ATTENTION: Cette saisie REMPLACE toutes les saisies précédentes!
    """
    conge = db.query(Conge).filter(Conge.id == conge_id).first()
    if not conge:
        raise HTTPException(status_code=404, detail="Enregistrement congé non trouvé")
    
    # Sauvegarder l'ancienne valeur (convertir Decimal en float pour JSON)
    old_jours_pris = float(conge.jours_conges_pris or 0)
    
    # v3.5.3: VALIDATION STRICTE avec support décimales
    jours_pris = float(update.jours_pris)
    
    # Mois et année de déduction (par défaut: mois d'acquisition)
    mois_deduction = update.mois_deduction or conge.mois
    annee_deduction = update.annee_deduction or conge.annee
    
    # Validation mois/année
    if not (1 <= mois_deduction <= 12):
        raise HTTPException(status_code=400, detail="Mois de déduction invalide (doit être entre 1 et 12)")
    if annee_deduction < 2000 or annee_deduction > 2100:
        raise HTTPException(status_code=400, detail="Année de déduction invalide")
    
    # ⭐ CORRECTION v3.6.1 hotfix7: Répartition intelligente TOTALE
    # jours_pris = TOTAL global voulu (pas un ajout!)
    # Sauvegarder le total actuel pour information
    periodes_employe = db.query(Conge).filter(
        Conge.employe_id == conge.employe_id
    ).all()
    
    total_actuel = sum(float(p.jours_conges_pris or 0) for p in periodes_employe)
    
    # Réinitialiser toutes les périodes à 0 (nouvelle répartition complète)
    for p in periodes_employe:
        p.jours_conges_pris = 0.0
    
    # Appliquer la répartition intelligente
    try:
        repartition = repartir_conges_intelligemment(
            db=db,
            employe_id=conge.employe_id,
            jours_a_prendre=jours_pris,
            mois_deduction=mois_deduction,
            annee_deduction=annee_deduction
        )
    except HTTPException as e:
        # Restaurer les anciennes valeurs en cas d'erreur
        for p in periodes_employe:
            db.refresh(p)
        raise e
    
    # Appliquer la répartition calculée
    messages_repartition = []
    for item in repartition:
        periode_conge = db.query(Conge).filter(Conge.id == item['conge_id']).first()
        if periode_conge:
            periode_conge.jours_conges_pris = item['nouveau_pris']
            periode_conge.mois_deduction = item['mois_deduction']
            periode_conge.annee_deduction = item['annee_deduction']
            messages_repartition.append(
                f"  • {item['periode']}: {item['jours_a_deduire']:.2f}j (acquis {item['acquis']:.2f}j)"
            )
    
    # Recalculer les soldes cumulés pour toutes les périodes
    periodes_triees = sorted(periodes_employe, key=lambda p: (p.annee, p.mois))
    for periode in periodes_triees:
        stats_cumul = db.query(
            func.sum(Conge.jours_conges_acquis).label("total_acquis"),
            func.sum(Conge.jours_conges_pris).label("total_pris")
        ).filter(
            Conge.employe_id == conge.employe_id,
            (Conge.annee < periode.annee) | ((Conge.annee == periode.annee) & (Conge.mois <= periode.mois))
        ).first()
        
        total_acquis_cumul = float(stats_cumul.total_acquis or 0)
        total_pris_cumul = float(stats_cumul.total_pris or 0)
        periode.jours_conges_restants = total_acquis_cumul - total_pris_cumul
    
    db.commit()
    db.refresh(conge)
    
    # Log l'action avec détails de répartition
    description = f"Modification consommation congés - Employé #{conge.employe_id}\n" \
                  f"Total saisi: {jours_pris:.2f}j\n" \
                  f"Déduction sur bulletin: {mois_deduction}/{annee_deduction}\n" \
                  f"Répartition automatique:\n" + "\n".join(messages_repartition)
    
    log_action(
        db=db,
        module_name="conges",
        action_type=ActionType.UPDATE,
        record_id=conge_id,
        old_data={"jours_pris": old_jours_pris},
        new_data={"jours_pris": jours_pris, "repartition": repartition},
        description=description,
        user=current_user,
        request=request
    )
    
    return {
        "message": "Consommation mise à jour avec répartition intelligente",
        "conge_id": conge.id,
        "ancien_total": total_actuel,
        "nouveau_total": jours_pris,
        "difference": jours_pris - total_actuel,
        "repartition": repartition,
        "details": messages_repartition
    }

@router.get("/synthese/{employe_id}")
def get_synthese_conges(employe_id: int, db: Session = Depends(get_db)):
    """
    Obtenir la synthèse des congés pour un employé v3.7.0
    
    NOUVELLE ARCHITECTURE:
    - Total Acquis: SUM(conges.jours_conges_acquis)
    - Total Déduit: SUM(deductions_conges.jours_deduits)
    - Solde: Total Acquis - Total Déduit
    - Périodes: Liste détaillée avec solde cumulé
    """
    from models import DeductionConge
    from sqlalchemy import or_, and_
    
    employe = db.query(Employe).filter(Employe.id == employe_id).first()
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    # Total acquis (somme des congés acquis)
    total_acquis = db.query(func.sum(Conge.jours_conges_acquis)).filter(
        Conge.employe_id == employe_id
    ).scalar() or 0
    
    # Total déduit (nouvelle table deductions_conges)
    total_deduit = db.query(func.sum(DeductionConge.jours_deduits)).filter(
        DeductionConge.employe_id == employe_id
    ).scalar() or 0
    
    solde = float(total_acquis) - float(total_deduit)
    
    # Récupérer le détail des périodes avec solde cumulé
    periodes = db.query(Conge).filter(
        Conge.employe_id == employe_id
    ).order_by(Conge.annee.asc(), Conge.mois.asc()).all()
    
    periodes_detail = []
    solde_cumule = 0
    
    for periode in periodes:
        # Acquis jusqu'à cette période
        acquis_jusque = db.query(func.sum(Conge.jours_conges_acquis)).filter(
            Conge.employe_id == employe_id,
            or_(
                Conge.annee < periode.annee,
                and_(Conge.annee == periode.annee, Conge.mois <= periode.mois)
            )
        ).scalar() or 0
        
        # Déduit jusqu'à cette période (TOTAL global, pas par période)
        deduit_jusque = db.query(func.sum(DeductionConge.jours_deduits)).filter(
            DeductionConge.employe_id == employe_id
        ).scalar() or 0
        
        solde_cumule = float(acquis_jusque) - float(deduit_jusque)
        
        # Déductions liées à cette période d'acquisition
        deductions = db.query(DeductionConge).filter(
            DeductionConge.employe_id == employe_id
        ).all()
        
        periodes_detail.append({
            "mois": periode.mois,
            "annee": periode.annee,
            "jours_travailles": periode.jours_travailles,
            "jours_acquis": float(periode.jours_conges_acquis or 0),
            "solde_cumule": round(solde_cumule, 2),
            "nb_deductions": len(deductions)
        })
    
    return {
        "employe": f"{employe.prenom} {employe.nom}",
        "total_acquis": round(float(total_acquis), 2),
        "total_deduit": round(float(total_deduit), 2),
        "solde": round(solde, 2),
        "periodes": periodes_detail
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
