"""
Nouveau router pour les déductions de congés (v3.7.0)
Architecture: Séparation acquisition (table conges) et consommation (table deductions_conges)
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from decimal import Decimal
from datetime import date

from database import get_db
from models import Conge, DeductionConge, Employe, User, ActionType
from pydantic import BaseModel
from services.logging_service import log_action
from middleware.auth import get_current_user, require_gestionnaire

router = APIRouter(prefix="/deductions-conges", tags=["Déductions Congés"])

# Schemas
class DeductionCreate(BaseModel):
    employe_id: int
    jours_deduits: float
    mois_deduction: int
    annee_deduction: int
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    type_conge: str = "ANNUEL"
    motif: Optional[str] = None

class DeductionResponse(BaseModel):
    id: int
    employe_id: int
    jours_deduits: float
    mois_deduction: int
    annee_deduction: int
    date_debut: Optional[date]
    date_fin: Optional[date]
    type_conge: str
    motif: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True

class SoldeCongeResponse(BaseModel):
    employe_id: int
    total_acquis: float
    total_deduit: float
    solde_disponible: float
    periodes: List[dict]  # Détail par période

@router.post("/", dependencies=[Depends(require_gestionnaire)])
def creer_deduction(
    deduction: DeductionCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Créer une nouvelle déduction de congé
    
    LOGIQUE v3.7.0:
    1. Vérifier que l'employé a assez de solde
    2. Créer l'enregistrement dans deductions_conges
    3. Recalculer tous les soldes cumulés de l'employé
    4. Logger l'action
    """
    # Validation
    if not (1 <= deduction.mois_deduction <= 12):
        raise HTTPException(status_code=400, detail="Mois invalide (1-12)")
    if deduction.annee_deduction < 2000 or deduction.annee_deduction > 2100:
        raise HTTPException(status_code=400, detail="Année invalide")
    if deduction.jours_deduits <= 0:
        raise HTTPException(status_code=400, detail="Jours déduits doit être > 0")
    
    # Vérifier l'employé existe
    employe = db.query(Employe).filter(Employe.id == deduction.employe_id).first()
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    # Calculer le solde disponible
    total_acquis = db.query(func.sum(Conge.jours_conges_acquis)).filter(
        Conge.employe_id == deduction.employe_id
    ).scalar() or 0
    
    total_deduit = db.query(func.sum(DeductionConge.jours_deduits)).filter(
        DeductionConge.employe_id == deduction.employe_id
    ).scalar() or 0
    
    solde_disponible = float(total_acquis) - float(total_deduit)
    
    # Vérifier le solde
    if deduction.jours_deduits > solde_disponible:
        raise HTTPException(
            status_code=400,
            detail=f"Solde insuffisant! Disponible: {solde_disponible:.2f}j, Demandé: {deduction.jours_deduits:.2f}j"
        )
    
    # Créer la déduction
    nouvelle_deduction = DeductionConge(
        employe_id=deduction.employe_id,
        jours_deduits=deduction.jours_deduits,
        mois_deduction=deduction.mois_deduction,
        annee_deduction=deduction.annee_deduction,
        date_debut=deduction.date_debut,
        date_fin=deduction.date_fin,
        type_conge=deduction.type_conge,
        motif=deduction.motif,
        created_by=current_user.id
    )
    
    db.add(nouvelle_deduction)
    db.commit()
    db.refresh(nouvelle_deduction)
    
    # Recalculer les soldes de toutes les périodes de cet employé
    recalculer_soldes_employe(db, deduction.employe_id)
    
    # Logger
    log_action(
        db=db,
        module_name="deductions_conges",
        action_type=ActionType.CREATE,
        record_id=nouvelle_deduction.id,
        old_data=None,
        new_data={
            "jours_deduits": deduction.jours_deduits,
            "mois_deduction": deduction.mois_deduction,
            "annee_deduction": deduction.annee_deduction
        },
        description=f"Nouvelle déduction: {deduction.jours_deduits}j pour {employe.prenom} {employe.nom} - Bulletin {deduction.mois_deduction}/{deduction.annee_deduction}",
        user=current_user,
        request=request
    )
    
    nouveau_solde = solde_disponible - deduction.jours_deduits
    
    return {
        "message": "Déduction créée avec succès",
        "deduction_id": nouvelle_deduction.id,
        "ancien_solde": solde_disponible,
        "nouveau_solde": nouveau_solde,
        "jours_deduits": deduction.jours_deduits
    }

@router.get("/employe/{employe_id}")
def liste_deductions_employe(
    employe_id: int,
    annee: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Lister toutes les déductions d'un employé"""
    query = db.query(DeductionConge).filter(DeductionConge.employe_id == employe_id)
    
    if annee:
        query = query.filter(DeductionConge.annee_deduction == annee)
    
    deductions = query.order_by(
        DeductionConge.annee_deduction.desc(),
        DeductionConge.mois_deduction.desc()
    ).all()
    
    return [
        {
            "id": d.id,
            "jours_deduits": float(d.jours_deduits),
            "mois_deduction": d.mois_deduction,
            "annee_deduction": d.annee_deduction,
            "type_conge": d.type_conge,
            "motif": d.motif,
            "date_debut": str(d.date_debut) if d.date_debut else None,
            "date_fin": str(d.date_fin) if d.date_fin else None,
            "created_at": str(d.created_at)
        }
        for d in deductions
    ]

@router.get("/solde/{employe_id}")
def calculer_solde_conges(employe_id: int, db: Session = Depends(get_db)):
    """
    Calculer le solde de congés d'un employé avec détail par période
    
    RETOURNE:
    - total_acquis: Somme de tous les jours acquis
    - total_deduit: Somme de toutes les déductions
    - solde_disponible: Différence
    - periodes: Liste avec détail de chaque période
    """
    # Vérifier l'employé
    employe = db.query(Employe).filter(Employe.id == employe_id).first()
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    # Total acquis
    total_acquis = db.query(func.sum(Conge.jours_conges_acquis)).filter(
        Conge.employe_id == employe_id
    ).scalar() or 0
    
    # Total déduit
    total_deduit = db.query(func.sum(DeductionConge.jours_deduits)).filter(
        DeductionConge.employe_id == employe_id
    ).scalar() or 0
    
    solde_disponible = float(total_acquis) - float(total_deduit)
    
    # Détail par période d'acquisition
    periodes_query = db.query(Conge).filter(
        Conge.employe_id == employe_id
    ).order_by(Conge.annee, Conge.mois).all()
    
    periodes = []
    solde_cumule = 0
    
    for periode in periodes_query:
        # Calculer solde cumulé jusqu'à cette période
        acquis_jusque = db.query(func.sum(Conge.jours_conges_acquis)).filter(
            Conge.employe_id == employe_id,
            or_(
                Conge.annee < periode.annee,
                and_(Conge.annee == periode.annee, Conge.mois <= periode.mois)
            )
        ).scalar() or 0
        
        deduit_jusque = db.query(func.sum(DeductionConge.jours_deduits)).filter(
            DeductionConge.employe_id == employe_id
        ).scalar() or 0
        
        solde_cumule = float(acquis_jusque) - float(deduit_jusque)
        
        periodes.append({
            "mois": periode.mois,
            "annee": periode.annee,
            "jours_travailles": periode.jours_travailles,
            "jours_acquis": float(periode.jours_conges_acquis or 0),
            "solde_cumule": solde_cumule
        })
    
    return {
        "employe_id": employe_id,
        "employe_nom": f"{employe.prenom} {employe.nom}",
        "total_acquis": float(total_acquis),
        "total_deduit": float(total_deduit),
        "solde_disponible": solde_disponible,
        "periodes": periodes
    }

@router.delete("/{deduction_id}", dependencies=[Depends(require_gestionnaire)])
def supprimer_deduction(
    deduction_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprimer une déduction de congé"""
    deduction = db.query(DeductionConge).filter(DeductionConge.id == deduction_id).first()
    if not deduction:
        raise HTTPException(status_code=404, detail="Déduction non trouvée")
    
    employe_id = deduction.employe_id
    old_data = {
        "jours_deduits": float(deduction.jours_deduits),
        "mois_deduction": deduction.mois_deduction,
        "annee_deduction": deduction.annee_deduction
    }
    
    db.delete(deduction)
    db.commit()
    
    # Recalculer les soldes
    recalculer_soldes_employe(db, employe_id)
    
    # Logger
    log_action(
        db=db,
        module_name="deductions_conges",
        action_type=ActionType.DELETE,
        record_id=deduction_id,
        old_data=old_data,
        new_data=None,
        description=f"Suppression déduction #{deduction_id}",
        user=current_user,
        request=request
    )
    
    return {"message": "Déduction supprimée", "deduction_id": deduction_id}

def recalculer_soldes_employe(db: Session, employe_id: int):
    """
    Recalculer les soldes cumulés de toutes les périodes d'un employé
    
    Cette fonction met à jour jours_conges_restants dans la table conges
    pour affichage cohérent (même si on utilise les déductions)
    """
    periodes = db.query(Conge).filter(
        Conge.employe_id == employe_id
    ).order_by(Conge.annee, Conge.mois).all()
    
    # Total déduit global
    total_deduit = db.query(func.sum(DeductionConge.jours_deduits)).filter(
        DeductionConge.employe_id == employe_id
    ).scalar() or 0
    
    for periode in periodes:
        # Acquis jusqu'à cette période
        acquis_jusque = db.query(func.sum(Conge.jours_conges_acquis)).filter(
            Conge.employe_id == employe_id,
            or_(
                Conge.annee < periode.annee,
                and_(Conge.annee == periode.annee, Conge.mois <= periode.mois)
            )
        ).scalar() or 0
        
        # Solde cumulé
        periode.jours_conges_restants = float(acquis_jusque) - float(total_deduit)
    
    db.commit()
