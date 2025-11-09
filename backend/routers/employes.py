from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from database import get_db
from models import Employe, StatutContrat
from schemas import (
    EmployeCreate,
    EmployeUpdate,
    EmployeResponse,
    EmployeListResponse,
)

router = APIRouter(prefix="/employes", tags=["Employés"])

@router.post("/", response_model=EmployeResponse, status_code=201)
def create_employe(employe: EmployeCreate, db: Session = Depends(get_db)):
    """Créer un nouvel employé"""
    
    # Vérifier si le numéro de sécurité sociale existe déjà
    existing = db.query(Employe).filter(
        Employe.numero_secu_sociale == employe.numero_secu_sociale
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Un employé avec ce numéro de sécurité sociale existe déjà"
        )
    
    db_employe = Employe(**employe.model_dump())
    db.add(db_employe)
    db.commit()
    db.refresh(db_employe)
    
    return db_employe

@router.get("/", response_model=EmployeListResponse)
def list_employes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    statut: Optional[str] = Query(None, description="Filtrer par statut (Actif/Inactif)"),
    search: Optional[str] = Query(None, description="Rechercher par nom ou prénom"),
    poste: Optional[str] = Query(None, description="Filtrer par poste"),
    db: Session = Depends(get_db)
):
    """Lister tous les employés avec filtres"""
    
    query = db.query(Employe)
    
    # Filtrer par statut
    if statut:
        if statut not in ["Actif", "Inactif"]:
            raise HTTPException(status_code=400, detail="Statut invalide")
        query = query.filter(Employe.statut_contrat == statut)
    
    # Recherche par nom ou prénom
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Employe.nom.like(search_pattern)) | 
            (Employe.prenom.like(search_pattern))
        )
    
    # Filtrer par poste
    if poste:
        query = query.filter(Employe.poste_travail.like(f"%{poste}%"))
    
    total = query.count()
    employes = query.offset(skip).limit(limit).all()
    
    return EmployeListResponse(total=total, employes=employes)

@router.get("/{employe_id}", response_model=EmployeResponse)
def get_employe(employe_id: int, db: Session = Depends(get_db)):
    """Obtenir un employé par son ID"""
    
    employe = db.query(Employe).filter(Employe.id == employe_id).first()
    
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    return employe

@router.put("/{employe_id}", response_model=EmployeResponse)
def update_employe(
    employe_id: int,
    employe_update: EmployeUpdate,
    db: Session = Depends(get_db)
):
    """Mettre à jour un employé"""
    
    employe = db.query(Employe).filter(Employe.id == employe_id).first()
    
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    # Vérifier le numéro de sécurité sociale si modifié
    if employe_update.numero_secu_sociale:
        existing = db.query(Employe).filter(
            Employe.numero_secu_sociale == employe_update.numero_secu_sociale,
            Employe.id != employe_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Un autre employé avec ce numéro de sécurité sociale existe déjà"
            )
    
    # Mettre à jour les champs
    update_data = employe_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(employe, field, value)
    
    db.commit()
    db.refresh(employe)
    
    return employe

@router.delete("/{employe_id}", status_code=204)
def delete_employe(employe_id: int, db: Session = Depends(get_db)):
    """Supprimer un employé"""
    
    employe = db.query(Employe).filter(Employe.id == employe_id).first()
    
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    db.delete(employe)
    db.commit()
    
    return None

@router.post("/{employe_id}/valider-contrat")
def valider_contrat(employe_id: int, db: Session = Depends(get_db)):
    """Valider automatiquement le statut du contrat selon les dates"""
    
    employe = db.query(Employe).filter(Employe.id == employe_id).first()
    
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    today = date.today()
    
    # Si la date de fin de contrat est passée, marquer comme inactif
    if employe.date_fin_contrat and employe.date_fin_contrat < today:
        employe.statut_contrat = StatutContrat.INACTIF
    # Si la date de recrutement n'est pas encore arrivée, marquer comme inactif
    elif employe.date_recrutement > today:
        employe.statut_contrat = StatutContrat.INACTIF
    else:
        employe.statut_contrat = StatutContrat.ACTIF
    
    db.commit()
    db.refresh(employe)
    
    return {
        "employe_id": employe.id,
        "statut": employe.statut_contrat.value,
        "message": "Statut du contrat validé"
    }

@router.post("/valider-tous-contrats")
def valider_tous_contrats(db: Session = Depends(get_db)):
    """Valider tous les contrats automatiquement"""
    
    employes = db.query(Employe).all()
    today = date.today()
    updated_count = 0
    
    for employe in employes:
        old_statut = employe.statut_contrat
        
        if employe.date_fin_contrat and employe.date_fin_contrat < today:
            employe.statut_contrat = StatutContrat.INACTIF
        elif employe.date_recrutement > today:
            employe.statut_contrat = StatutContrat.INACTIF
        else:
            employe.statut_contrat = StatutContrat.ACTIF
        
        if old_statut != employe.statut_contrat:
            updated_count += 1
    
    db.commit()
    
    return {
        "total_employes": len(employes),
        "employes_mis_a_jour": updated_count,
        "message": "Validation des contrats terminée"
    }
