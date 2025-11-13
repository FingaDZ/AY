from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.poste_travail import PosteTravail
from models.employe import Employe
from models.user import User
from schemas.poste_travail import (
    PosteTravailCreate,
    PosteTravailUpdate,
    PosteTravailResponse,
    PosteTravailListResponse
)
from middleware.auth import require_auth, require_admin
from services.logging_service import log_action, clean_data_for_logging, ActionType

router = APIRouter(prefix="/postes", tags=["postes_travail"])

@router.post("/", response_model=PosteTravailResponse, status_code=201)
def create_poste(
    poste: PosteTravailCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Créer un nouveau poste de travail (Admin uniquement)"""
    
    # Vérifier si le libellé existe déjà
    existing = db.query(PosteTravail).filter(
        PosteTravail.libelle == poste.libelle
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Un poste avec le libellé '{poste.libelle}' existe déjà"
        )
    
    # Créer le poste
    db_poste = PosteTravail(**poste.model_dump())
    db.add(db_poste)
    db.commit()
    db.refresh(db_poste)
    
    # Log
    try:
        log_action(
            db=db,
            module_name="postes_travail",
            action_type=ActionType.CREATE,
            record_id=db_poste.id,
            new_data=clean_data_for_logging(db_poste),
            description=f"Création poste: {db_poste.libelle}",
            user=current_user,
            request=request
        )
    except Exception as e:
        print(f"Erreur logging: {e}")
    
    return db_poste

@router.get("/", response_model=PosteTravailListResponse)
def list_postes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    actif_seulement: bool = Query(True, description="Afficher uniquement les postes actifs"),
    chauffeurs_seulement: bool = Query(False, description="Afficher uniquement les chauffeurs"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth)
):
    """Lister tous les postes de travail"""
    
    query = db.query(PosteTravail)
    
    if actif_seulement:
        query = query.filter(PosteTravail.actif == True)
    
    if chauffeurs_seulement:
        query = query.filter(PosteTravail.est_chauffeur == True)
    
    total = query.count()
    postes = query.order_by(PosteTravail.libelle).offset(skip).limit(limit).all()
    
    return {"total": total, "postes": postes}

@router.get("/{poste_id}", response_model=PosteTravailResponse)
def get_poste(
    poste_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth)
):
    """Récupérer un poste par son ID"""
    
    poste = db.query(PosteTravail).filter(PosteTravail.id == poste_id).first()
    
    if not poste:
        raise HTTPException(status_code=404, detail="Poste non trouvé")
    
    return poste

@router.put("/{poste_id}", response_model=PosteTravailResponse)
def update_poste(
    poste_id: int,
    poste_update: PosteTravailUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Modifier un poste de travail (Admin uniquement)"""
    
    poste = db.query(PosteTravail).filter(PosteTravail.id == poste_id).first()
    
    if not poste:
        raise HTTPException(status_code=404, detail="Poste non trouvé")
    
    # Vérifier si le poste est modifiable
    if not poste.modifiable:
        raise HTTPException(
            status_code=403,
            detail=f"Le poste '{poste.libelle}' ne peut pas être modifié (poste système)"
        )
    
    # Sauvegarder l'ancien état
    old_data = clean_data_for_logging(poste)
    
    # Vérifier l'unicité du libellé si modifié
    update_data = poste_update.model_dump(exclude_unset=True)
    if 'libelle' in update_data:
        existing = db.query(PosteTravail).filter(
            PosteTravail.libelle == update_data['libelle'],
            PosteTravail.id != poste_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Un autre poste avec le libellé '{update_data['libelle']}' existe déjà"
            )
    
    # Mettre à jour
    for field, value in update_data.items():
        setattr(poste, field, value)
    
    db.commit()
    db.refresh(poste)
    
    # Log
    try:
        log_action(
            db=db,
            module_name="postes_travail",
            action_type=ActionType.UPDATE,
            record_id=poste.id,
            old_data=old_data,
            new_data=clean_data_for_logging(poste),
            description=f"Modification poste: {poste.libelle}",
            user=current_user,
            request=request
        )
    except Exception as e:
        print(f"Erreur logging: {e}")
    
    return poste

@router.delete("/{poste_id}", status_code=200)
def delete_poste(
    poste_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Désactiver un poste (soft delete) - Admin uniquement"""
    
    poste = db.query(PosteTravail).filter(PosteTravail.id == poste_id).first()
    
    if not poste:
        raise HTTPException(status_code=404, detail="Poste non trouvé")
    
    # Vérifier si le poste est modifiable
    if not poste.modifiable:
        raise HTTPException(
            status_code=403,
            detail=f"Le poste '{poste.libelle}' ne peut pas être supprimé (poste système)"
        )
    
    # Vérifier si des employés utilisent ce poste
    employes_count = db.query(Employe).filter(
        Employe.poste_travail == poste.libelle,
        Employe.actif == True
    ).count()
    
    if employes_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Impossible de supprimer ce poste : {employes_count} employé(s) actif(s) l'utilisent encore"
        )
    
    # Soft delete
    poste_data = clean_data_for_logging(poste)
    poste.actif = False
    db.commit()
    
    # Log
    try:
        log_action(
            db=db,
            module_name="postes_travail",
            action_type=ActionType.DELETE,
            record_id=poste.id,
            old_data=poste_data,
            description=f"Suppression poste: {poste.libelle}",
            user=current_user,
            request=request
        )
    except Exception as e:
        print(f"Erreur logging: {e}")
    
    return {"message": f"Poste '{poste.libelle}' désactivé avec succès"}
