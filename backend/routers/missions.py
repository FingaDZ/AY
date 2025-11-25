from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
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
from services.pdf_generator import PDFGenerator
from services.logging_service import log_action, clean_data_for_logging, ActionType

router = APIRouter(prefix="/missions", tags=["Missions"])
pdf_generator = PDFGenerator()

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
    
    # Utiliser le tarif kilométrique du client
    tarif_km = client.tarif_km
    
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
    
    # Log action
    log_action(
        db=db,
        module="missions",
        action=ActionType.CREATE,
        description=f"Création mission #{db_mission.id} pour {chauffeur.prenom} {chauffeur.nom} - Client: {client.nom}",
        new_data=clean_data_for_logging(db_mission)
    )
    
    return db_mission

@router.put("/{mission_id}", response_model=MissionResponse)
def update_mission(
    mission_id: int,
    mission: MissionCreate,
    db: Session = Depends(get_db)
):
    """Modifier une mission existante"""
    
    # Vérifier que la mission existe
    db_mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not db_mission:
        raise HTTPException(status_code=404, detail="Mission non trouvée")
    
    # Vérifier que le chauffeur existe
    chauffeur = db.query(Employe).filter(Employe.id == mission.chauffeur_id).first()
    if not chauffeur:
        raise HTTPException(status_code=404, detail="Chauffeur non trouvé")
    
    # Vérifier que le client existe
    client = db.query(Client).filter(Client.id == mission.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    # Recalculer la prime avec le tarif du client
    distance = client.distance
    tarif_km = client.tarif_km
    prime_calculee = distance * tarif_km
    
    # Mettre à jour les champs
    db_mission.date_mission = mission.date_mission
    db_mission.chauffeur_id = mission.chauffeur_id
    db_mission.client_id = mission.client_id
    db_mission.distance = distance
    db_mission.prime_calculee = prime_calculee
    
    # Log action
    log_action(
        db=db,
        module="missions",
        action=ActionType.UPDATE,
        description=f"Modification mission #{mission_id}",
        new_data=clean_data_for_logging(db_mission)
    )
    
    db.commit()
    db.refresh(db_mission)
    
    return db_mission

@router.delete("/{mission_id}", status_code=204)
def delete_mission(
    mission_id: int,
    db: Session = Depends(get_db)
):
    """Supprimer une mission"""
    
    db_mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not db_mission:
        raise HTTPException(status_code=404, detail="Mission non trouvée")
    
    # Log action before delete
    log_action(
        db=db,
        module="missions",
        action=ActionType.DELETE,
        description=f"Suppression mission #{mission_id}",
        old_data=clean_data_for_logging(db_mission)
    )
    
    db.delete(db_mission)
    db.commit()
    
    return None

@router.get("/", response_model=MissionListResponse)
def list_missions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    chauffeur_id: Optional[int] = None,
    client_id: Optional[int] = None,
    date_debut: Optional[str] = None,
    date_fin: Optional[str] = None,
    annee: Optional[int] = None,
    mois: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Lister toutes les missions avec filtres"""
    
    query = db.query(Mission)
    
    if chauffeur_id:
        query = query.filter(Mission.chauffeur_id == chauffeur_id)
    
    if client_id:
        query = query.filter(Mission.client_id == client_id)
    
    if date_debut:
        query = query.filter(Mission.date_mission >= date_debut)
    
    if date_fin:
        query = query.filter(Mission.date_mission <= date_fin)
    
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

@router.get("/totaux-chauffeur")
def get_totaux_chauffeur(
    chauffeur_id: Optional[int] = None,
    date_debut: Optional[str] = None,
    date_fin: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Obtenir les totaux par chauffeur (nombre de missions, distance totale, primes totales)"""
    
    query = db.query(
        Mission.chauffeur_id,
        Employe.prenom,
        Employe.nom,
        func.count(Mission.id).label('nombre_missions'),
        func.sum(Mission.distance).label('total_distance'),
        func.sum(Mission.prime_calculee).label('total_primes')
    ).join(Employe, Mission.chauffeur_id == Employe.id)
    
    if chauffeur_id:
        query = query.filter(Mission.chauffeur_id == chauffeur_id)
    
    if date_debut:
        query = query.filter(Mission.date_mission >= date_debut)
    
    if date_fin:
        query = query.filter(Mission.date_mission <= date_fin)
    
    query = query.group_by(Mission.chauffeur_id, Employe.prenom, Employe.nom)
    
    results = query.all()
    
    totaux = [
        {
            "chauffeur_id": r.chauffeur_id,
            "nom_complet": f"{r.prenom} {r.nom}",
            "nombre_missions": r.nombre_missions,
            "total_distance": float(r.total_distance or 0),
            "total_primes": float(r.total_primes or 0)
        }
        for r in results
    ]
    
    return {"totaux": totaux}

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

@router.get("/{mission_id}/ordre-mission/pdf")
def generate_ordre_mission_pdf(
    mission_id: int,
    db: Session = Depends(get_db)
):
    """Générer un ordre de mission PDF pour un chauffeur"""
    
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission non trouvée")
    
    chauffeur = db.query(Employe).filter(Employe.id == mission.chauffeur_id).first()
    client = db.query(Client).filter(Client.id == mission.client_id).first()
    
    if not chauffeur or not client:
        raise HTTPException(status_code=404, detail="Données manquantes")
    
    mission_data = {
        'id': mission.id,
        'date_mission': str(mission.date_mission),
        'chauffeur_nom': chauffeur.nom,
        'chauffeur_prenom': chauffeur.prenom,
        'client_nom': client.nom,
        'client_prenom': client.prenom,
        'distance': float(mission.distance),
        'prime_calculee': float(mission.prime_calculee)
    }
    
    pdf_buffer = pdf_generator.generate_ordre_mission(mission_data)
    
    return StreamingResponse(
        pdf_buffer,
        media_type='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename="ordre_mission_{mission_id:05d}.pdf"'
        }
    )

@router.post("/rapport/pdf")
def generate_rapport_missions_pdf(
    chauffeur_id: Optional[int] = None,
    client_id: Optional[int] = None,
    date_debut: Optional[str] = None,
    date_fin: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Générer un rapport PDF des missions filtrées"""
    
    query = db.query(Mission)
    
    if chauffeur_id:
        query = query.filter(Mission.chauffeur_id == chauffeur_id)
    
    if client_id:
        query = query.filter(Mission.client_id == client_id)
    
    if date_debut:
        query = query.filter(Mission.date_mission >= date_debut)
    
    if date_fin:
        query = query.filter(Mission.date_mission <= date_fin)
    
    missions = query.all()
    
    if not missions:
        raise HTTPException(status_code=404, detail="Aucune mission trouvée avec ces filtres")
    
    # Préparer les données pour le PDF
    missions_data = []
    for mission in missions:
        chauffeur = db.query(Employe).filter(Employe.id == mission.chauffeur_id).first()
        client = db.query(Client).filter(Client.id == mission.client_id).first()
        
        missions_data.append({
            'date_mission': str(mission.date_mission),
            'chauffeur_prenom': chauffeur.prenom,
            'chauffeur_nom': chauffeur.nom,
            'client_prenom': client.prenom,
            'client_nom': client.nom,
            'distance': float(mission.distance),
            'prime_calculee': float(mission.prime_calculee)
        })
    
    filters = {}
    if date_debut:
        filters['date_debut'] = date_debut
    if date_fin:
        filters['date_fin'] = date_fin
    
    pdf_buffer = pdf_generator.generate_rapport_missions(missions_data, filters)
    
    return StreamingResponse(
        pdf_buffer,
        media_type='application/pdf',
        headers={
            'Content-Disposition': 'attachment; filename="rapport_missions.pdf"'
        }
    )
