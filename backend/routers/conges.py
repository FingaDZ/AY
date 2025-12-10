from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from decimal import Decimal

from database import get_db
from models import Conge, Employe, Pointage
from pydantic import BaseModel
from datetime import date, datetime, timedelta

router = APIRouter(prefix="/conges", tags=["Congés"])

# Schemas locaux pour éviter les dépendances circulaires ou complexes
class CongeUpdate(BaseModel):
    jours_pris: float

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
    jours_conges_acquis: float
    jours_conges_pris: float
    jours_conges_restants: float

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
            jours_conges_acquis=float(c.jours_conges_acquis or 0),
            jours_conges_pris=float(c.jours_conges_pris or 0),
            jours_conges_restants=float(c.jours_conges_restants or 0)
        ))
        
    return results

@router.put("/{conge_id}/consommation")
def update_consommation(
    conge_id: int,
    update: CongeUpdate,
    db: Session = Depends(get_db)
):
    """Mettre à jour la consommation de congés pour un mois donné"""
    conge = db.query(Conge).filter(Conge.id == conge_id).first()
    if not conge:
        raise HTTPException(status_code=404, detail="Enregistrement congé non trouvé")
    
    # Mise à jour
    conge.jours_conges_pris = Decimal(update.jours_pris)
    
    # Recalcul du reste
    # Note: Le reste est calculé par rapport à l'acquis de ce mois spécifique
    # Dans une gestion plus complexe, on pourrait avoir un compteur global, 
    # mais ici on suit le modèle mensuel existant.
    conge.jours_conges_restants = conge.jours_conges_acquis - conge.jours_conges_pris
    
    db.commit()
    db.refresh(conge)
    
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
        "total_acquis": total_acquis,
        "total_pris": total_pris,
        "solde": solde
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
        
        # Ajouter les jours pris dans ce mois
        jours_mois = len(jours)
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
