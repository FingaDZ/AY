from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from decimal import Decimal

from database import get_db
from models import Mission, Employe, Client, Parametre
from schemas import (
    MissionCreate,
    MissionResponse,
    MissionListResponse,
    MissionPrimeMensuelle,
    ParametreCreate,
    ParametreUpdate,
    ParametreResponse,
)

router = APIRouter(prefix="/missions", tags=["Missions"])

def get_tarif_km(db: Session) -> Decimal:
    """Obtenir le tarif kilométrique depuis les paramètres"""
    param = db.query(Parametre).filter(Parametre.cle == "tarif_km").first()
    if not param:
        # Créer le paramètre avec valeur par défaut si non existant
        param = Parametre(
            cle="tarif_km",
            valeur="3.00",
            description="Tarif kilométrique pour les missions (DA/km)"
        )
        db.add(param)
        db.commit()
    return Decimal(param.valeur)

@router.post("/", response_model=MissionResponse, status_code=201)
def create_mission(mission: MissionCreate, db: Session = Depends(get_db)):
    """Créer une nouvelle mission"""
    
    # Vérifier que le chauffeur existe et a le poste "Chauffeur"
    chauffeur = db.query(Employe).filter(Employe.id == mission.chauffeur_id).first()
    if not chauffeur:
        raise HTTPException(status_code=404, detail="Chauffeur non trouvé")
    
    if "chauffeur" not in chauffeur.poste_travail.lower():
        raise HTTPException(
            status_code=400,
            detail="L'employé sélectionné n'est pas un chauffeur"
        )
    
    # Vérifier que le client existe
    client = db.query(Client).filter(Client.id == mission.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    # Récupérer le tarif kilométrique
    tarif_km = get_tarif_km(db)
    
    # Calculer la prime
    prime_calculee = client.distance * tarif_km
    
    # Créer la mission
    db_mission = Mission(
        date_mission=mission.date_mission,
        chauffeur_id=mission.chauffeur_id,
        client_id=mission.client_id,
        distance=client.distance,
        tarif_km=tarif_km,
        prime_calculee=prime_calculee
    )
    
    db.add(db_mission)
    db.commit()
    db.refresh(db_mission)
    
    return db_mission

@router.get("/", response_model=MissionListResponse)
def list_missions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    chauffeur_id: Optional[int] = None,
    annee: Optional[int] = None,
    mois: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Lister toutes les missions avec filtres"""
    
    query = db.query(Mission)
    
    if chauffeur_id:
        query = query.filter(Mission.chauffeur_id == chauffeur_id)
    
    if annee and mois:
        query = query.filter(
            func.year(Mission.date_mission) == annee,
            func.month(Mission.date_mission) == mois
        )
    elif annee:
        query = query.filter(func.year(Mission.date_mission) == annee)
    
    total = query.count()
    missions = query.offset(skip).limit(limit).all()
    
    return MissionListResponse(total=total, missions=missions)

@router.get("/primes-mensuelles")
def get_primes_mensuelles(
    annee: int = Query(..., ge=2000, le=2100),
    mois: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db)
):
    """Obtenir le total des primes de déplacement par chauffeur pour un mois"""
    
    # Grouper les missions par chauffeur
    results = db.query(
        Mission.chauffeur_id,
        func.sum(Mission.prime_calculee).label("total_prime"),
        func.count(Mission.id).label("nombre_missions")
    ).filter(
        func.year(Mission.date_mission) == annee,
        func.month(Mission.date_mission) == mois
    ).group_by(Mission.chauffeur_id).all()
    
    # Enrichir avec les informations du chauffeur
    primes = []
    for result in results:
        chauffeur = db.query(Employe).filter(Employe.id == result.chauffeur_id).first()
        if chauffeur:
            primes.append(MissionPrimeMensuelle(
                chauffeur_id=chauffeur.id,
                chauffeur_nom=chauffeur.nom,
                chauffeur_prenom=chauffeur.prenom,
                total_prime=result.total_prime or Decimal(0),
                nombre_missions=result.nombre_missions
            ))
    
    return {
        "annee": annee,
        "mois": mois,
        "primes": primes
    }

@router.get("/{mission_id}", response_model=MissionResponse)
def get_mission(mission_id: int, db: Session = Depends(get_db)):
    """Obtenir une mission par son ID"""
    
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    
    if not mission:
        raise HTTPException(status_code=404, detail="Mission non trouvée")
    
    return mission

@router.delete("/{mission_id}", status_code=204)
def delete_mission(mission_id: int, db: Session = Depends(get_db)):
    """Supprimer une mission"""
    
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    
    if not mission:
        raise HTTPException(status_code=404, detail="Mission non trouvée")
    
    db.delete(mission)
    db.commit()
    
    return None

# Routes pour les paramètres
@router.get("/parametres/tarif-km", response_model=ParametreResponse)
def get_tarif_km_param(db: Session = Depends(get_db)):
    """Obtenir le paramètre du tarif kilométrique"""
    
    param = db.query(Parametre).filter(Parametre.cle == "tarif_km").first()
    
    if not param:
        param = Parametre(
            cle="tarif_km",
            valeur="3.00",
            description="Tarif kilométrique pour les missions (DA/km)"
        )
        db.add(param)
        db.commit()
        db.refresh(param)
    
    return param

@router.put("/parametres/tarif-km", response_model=ParametreResponse)
def update_tarif_km(
    param_update: ParametreUpdate,
    db: Session = Depends(get_db)
):
    """Mettre à jour le tarif kilométrique"""
    
    param = db.query(Parametre).filter(Parametre.cle == "tarif_km").first()
    
    if not param:
        param = Parametre(
            cle="tarif_km",
            valeur=param_update.valeur,
            description=param_update.description or "Tarif kilométrique pour les missions (DA/km)"
        )
        db.add(param)
    else:
        param.valeur = param_update.valeur
        if param_update.description:
            param.description = param_update.description
    
    db.commit()
    db.refresh(param)
    
    return param
