"""
Router API pour la gestion des camions
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from database import get_db
from models import Camion, Mission, ActionType, User
from schemas import (
    CamionCreate, CamionUpdate, CamionResponse, CamionList
)
from services.logging_service import log_action
from middleware import require_auth, require_admin

router = APIRouter(prefix="/camions", tags=["Camions"])


@router.get("", response_model=CamionList)
def get_camions(
    actif: Optional[bool] = Query(None, description="Filtrer par statut actif/inactif"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Récupérer la liste des camions avec filtres optionnels"""
    
    query = db.query(Camion)
    
    # Filtre par statut
    if actif is not None:
        query = query.filter(Camion.actif == actif)
    
    # Ordre alphabétique
    query = query.order_by(Camion.marque, Camion.modele)
    
    # Total avant pagination
    total = query.count()
    
    # Pagination
    camions = query.offset(skip).limit(limit).all()
    
    # Statistiques
    actifs_count = db.query(Camion).filter(Camion.actif == True).count()
    inactifs_count = db.query(Camion).filter(Camion.actif == False).count()
    
    # Convertir en réponses avec nombre de missions
    camions_response = []
    for camion in camions:
        camion_dict = camion.to_dict()
        # Compter missions
        nb_missions = db.query(Mission).filter(Mission.camion_id == camion.id).count()
        camion_dict['nombre_missions'] = nb_missions
        camions_response.append(CamionResponse(**camion_dict))
    
    return CamionList(
        total=total,
        camions=camions_response,
        actifs=actifs_count,
        inactifs=inactifs_count
    )


@router.get("/{camion_id}", response_model=CamionResponse)
def get_camion(
    camion_id: int,
    db: Session = Depends(get_db)
):
    """Récupérer un camion par son ID"""
    
    camion = db.query(Camion).filter(Camion.id == camion_id).first()
    
    if not camion:
        raise HTTPException(status_code=404, detail="Camion non trouvé")
    
    # Ajouter nombre de missions
    camion_dict = camion.to_dict()
    nb_missions = db.query(Mission).filter(Mission.camion_id == camion.id).count()
    camion_dict['nombre_missions'] = nb_missions
    
    return CamionResponse(**camion_dict)


@router.post("", response_model=CamionResponse, status_code=201)
def create_camion(
    camion: CamionCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Créer un nouveau camion"""
    
    # Vérifier unicité immatriculation
    existing = db.query(Camion).filter(
        Camion.immatriculation == camion.immatriculation.upper()
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Un camion avec l'immatriculation {camion.immatriculation} existe déjà"
        )
    
    # Créer camion
    db_camion = Camion(
        marque=camion.marque,
        modele=camion.modele,
        immatriculation=camion.immatriculation.upper(),
        annee_fabrication=camion.annee_fabrication,
        capacite_charge=camion.capacite_charge,
        actif=camion.actif,
        date_acquisition=camion.date_acquisition,
        date_revision=camion.date_revision,
        notes=camion.notes
    )
    
    db.add(db_camion)
    db.commit()
    db.refresh(db_camion)
    
    # Log action
    log_action(
        db=db,
        module_name="camions",
        action_type=ActionType.CREATE,
        description=f"Création camion {db_camion.marque} {db_camion.modele} - {db_camion.immatriculation}",
        user=current_user,
        record_id=db_camion.id,
        request=request
    )
    
    camion_dict = db_camion.to_dict()
    camion_dict['nombre_missions'] = 0
    
    return CamionResponse(**camion_dict)


@router.put("/{camion_id}", response_model=CamionResponse)
def update_camion(
    camion_id: int,
    camion_update: CamionUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Mettre à jour un camion"""
    
    db_camion = db.query(Camion).filter(Camion.id == camion_id).first()
    
    if not db_camion:
        raise HTTPException(status_code=404, detail="Camion non trouvé")
    
    # Vérifier unicité immatriculation si modifiée
    if camion_update.immatriculation:
        immat_upper = camion_update.immatriculation.upper()
        existing = db.query(Camion).filter(
            Camion.immatriculation == immat_upper,
            Camion.id != camion_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Un autre camion avec l'immatriculation {immat_upper} existe déjà"
            )
    
    # Mettre à jour champs fournis
    update_data = camion_update.model_dump(exclude_unset=True)
    
    if 'immatriculation' in update_data:
        update_data['immatriculation'] = update_data['immatriculation'].upper()
    
    for key, value in update_data.items():
        setattr(db_camion, key, value)
    
    db.commit()
    db.refresh(db_camion)
    
    # Log action
    log_action(
        db=db,
        module_name="camions",
        action_type=ActionType.UPDATE,
        description=f"Modification camion {db_camion.marque} {db_camion.modele} - {db_camion.immatriculation}",
        user=current_user,
        record_id=db_camion.id,
        request=request
    )
    
    camion_dict = db_camion.to_dict()
    nb_missions = db.query(Mission).filter(Mission.camion_id == camion_id).count()
    camion_dict['nombre_missions'] = nb_missions
    
    return CamionResponse(**camion_dict)


@router.delete("/{camion_id}", status_code=204)
def delete_camion(
    camion_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Supprimer un camion (ou le désactiver si des missions existent)"""
    
    db_camion = db.query(Camion).filter(Camion.id == camion_id).first()
    
    if not db_camion:
        raise HTTPException(status_code=404, detail="Camion non trouvé")
    
    # Vérifier si des missions existent
    missions_count = db.query(Mission).filter(Mission.camion_id == camion_id).count()
    
    if missions_count > 0:
        # Ne pas supprimer, juste désactiver
        db_camion.actif = False
        db.commit()
        
        log_action(
            db=db,
            module_name="camions",
            action_type=ActionType.UPDATE,
            description=f"Désactivation camion {db_camion.marque} {db_camion.modele} ({missions_count} missions liées)",
            user=current_user,
            record_id=db_camion.id,
            request=request
        )
        
        raise HTTPException(
            status_code=400,
            detail=f"Impossible de supprimer: {missions_count} mission(s) liée(s). Le camion a été désactivé."
        )
    
    # Aucune mission, suppression OK
    immat = db_camion.immatriculation
    marque_modele = f"{db_camion.marque} {db_camion.modele}"
    
    db.delete(db_camion)
    db.commit()
    
    # Log action
    log_action(
        db=db,
        module_name="camions",
        action_type=ActionType.DELETE,
        description=f"Suppression camion {marque_modele} - {immat}",
        user=current_user,
        record_id=camion_id,
        request=request
    )
    
    return None


@router.get("/{camion_id}/missions")
def get_camion_missions(
    camion_id: int,
    annee: Optional[int] = Query(None, ge=2000, le=2100),
    mois: Optional[int] = Query(None, ge=1, le=12),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Récupérer les missions d'un camion avec filtres optionnels"""
    
    # Vérifier camion existe
    camion = db.query(Camion).filter(Camion.id == camion_id).first()
    if not camion:
        raise HTTPException(status_code=404, detail="Camion non trouvé")
    
    # Query missions
    query = db.query(Mission).filter(Mission.camion_id == camion_id)
    
    # Filtres
    if annee and mois:
        from datetime import date as dt_date
        from calendar import monthrange
        start_date = dt_date(annee, mois, 1)
        _, last_day = monthrange(annee, mois)
        end_date = dt_date(annee, mois, last_day)
        query = query.filter(
            Mission.date_mission >= start_date,
            Mission.date_mission <= end_date
        )
    
    # Ordre chronologique inversé
    query = query.order_by(Mission.date_mission.desc())
    
    total = query.count()
    missions = query.offset(skip).limit(limit).all()
    
    return {
        "camion": camion.to_dict(),
        "total_missions": total,
        "missions": [
            {
                "id": m.id,
                "date_mission": str(m.date_mission),
                "chauffeur_id": m.chauffeur_id,
                "chauffeur_nom": f"{m.chauffeur.nom} {m.chauffeur.prenom}" if m.chauffeur else "N/A",
                "client_id": m.client_id,
                "client_nom": m.client.nom if m.client else "N/A",
                "distance": float(m.distance),
                "prime_calculee": float(m.prime_calculee)
            }
            for m in missions
        ]
    }
