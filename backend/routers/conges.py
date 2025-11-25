from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from decimal import Decimal

from database import get_db
from models import Conge, Employe
from pydantic import BaseModel
from datetime import date

router = APIRouter(prefix="/conges", tags=["Congés"])

# Schemas locaux pour éviter les dépendances circulaires ou complexes
class CongeUpdate(BaseModel):
    jours_pris: float

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
