from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from decimal import Decimal

from database import get_db
from models import Avance, Employe
from schemas import (
    AvanceCreate,
    AvanceUpdate,
    AvanceResponse,
    AvanceListResponse,
    AvanceTotalMensuel,
)

router = APIRouter(prefix="/avances", tags=["Avances"])

@router.post("/", response_model=AvanceResponse, status_code=201)
def create_avance(avance: AvanceCreate, db: Session = Depends(get_db)):
    """Créer une nouvelle avance"""
    
    # Vérifier que l'employé existe
    employe = db.query(Employe).filter(Employe.id == avance.employe_id).first()
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    db_avance = Avance(**avance.model_dump())
    db.add(db_avance)
    db.commit()
    db.refresh(db_avance)
    
    return db_avance

@router.get("/", response_model=AvanceListResponse)
def list_avances(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    employe_id: Optional[int] = None,
    annee: Optional[int] = None,
    mois: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Lister toutes les avances avec filtres"""
    
    query = db.query(Avance)
    
    if employe_id:
        query = query.filter(Avance.employe_id == employe_id)
    
    if annee:
        query = query.filter(Avance.annee_deduction == annee)
    
    if mois:
        query = query.filter(Avance.mois_deduction == mois)
    
    total = query.count()
    avances = query.offset(skip).limit(limit).all()
    
    return AvanceListResponse(total=total, avances=avances)

@router.get("/total-mensuel")
def get_total_mensuel(
    annee: int = Query(..., ge=2000, le=2100),
    mois: int = Query(..., ge=1, le=12),
    employe_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Obtenir le total des avances par employé pour un mois"""
    
    query = db.query(
        Avance.employe_id,
        func.sum(Avance.montant).label("total_avances"),
        func.count(Avance.id).label("nombre_avances")
    ).filter(
        Avance.annee_deduction == annee,
        Avance.mois_deduction == mois
    )
    
    if employe_id:
        query = query.filter(Avance.employe_id == employe_id)
    
    results = query.group_by(Avance.employe_id).all()
    
    # Enrichir avec les informations de l'employé
    totaux = []
    for result in results:
        employe = db.query(Employe).filter(Employe.id == result.employe_id).first()
        if employe:
            totaux.append(AvanceTotalMensuel(
                employe_id=employe.id,
                employe_nom=employe.nom,
                employe_prenom=employe.prenom,
                mois=mois,
                annee=annee,
                total_avances=result.total_avances or Decimal(0),
                nombre_avances=result.nombre_avances
            ))
    
    return {
        "annee": annee,
        "mois": mois,
        "totaux": totaux
    }

@router.get("/{avance_id}", response_model=AvanceResponse)
def get_avance(avance_id: int, db: Session = Depends(get_db)):
    """Obtenir une avance par son ID"""
    
    avance = db.query(Avance).filter(Avance.id == avance_id).first()
    
    if not avance:
        raise HTTPException(status_code=404, detail="Avance non trouvée")
    
    return avance

@router.put("/{avance_id}", response_model=AvanceResponse)
def update_avance(
    avance_id: int,
    avance_update: AvanceUpdate,
    db: Session = Depends(get_db)
):
    """Mettre à jour une avance"""
    
    avance = db.query(Avance).filter(Avance.id == avance_id).first()
    
    if not avance:
        raise HTTPException(status_code=404, detail="Avance non trouvée")
    
    update_data = avance_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(avance, field, value)
    
    db.commit()
    db.refresh(avance)
    
    return avance

@router.delete("/{avance_id}", status_code=204)
def delete_avance(avance_id: int, db: Session = Depends(get_db)):
    """Supprimer une avance"""
    
    avance = db.query(Avance).filter(Avance.id == avance_id).first()
    
    if not avance:
        raise HTTPException(status_code=404, detail="Avance non trouvée")
    
    db.delete(avance)
    db.commit()
    
    return None
