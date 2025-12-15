from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from decimal import Decimal
from io import BytesIO

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
from middleware.auth import require_gestionnaire, require_admin  # ⭐ v3.6.0: Permissions

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

from services.mission_service import MissionService

@router.post("/", response_model=MissionResponse, status_code=201)
def create_mission(mission: MissionCreate, db: Session = Depends(get_db), _: None = Depends(require_gestionnaire)):
    """Créer une nouvelle mission"""
    service = MissionService(db)
    db_mission = service.create_mission(mission)
    
    # Log action
    chauffeur = db.query(Employe).filter(Employe.id == db_mission.chauffeur_id).first()
    client = db.query(Client).filter(Client.id == db_mission.client_id).first()
    
    log_action(
        db=db,
        module_name="missions",
        action_type=ActionType.CREATE,
        description=f"Création mission #{db_mission.id} pour {chauffeur.prenom} {chauffeur.nom} - Client: {client.nom}",
        new_data=clean_data_for_logging(db_mission)
    )
    
    return db_mission

@router.put("/{mission_id}", response_model=MissionResponse)
def update_mission(
    mission_id: int,
    mission: MissionCreate,
    _: None = Depends(require_gestionnaire),
    db: Session = Depends(get_db)
):
    """Modifier une mission existante"""
    service = MissionService(db)
    db_mission = service.update_mission(mission_id, mission)
    
    # Log action
    log_action(
        db=db,
        module_name="missions",
        action_type=ActionType.UPDATE,
        description=f"Modification mission #{mission_id}",
        new_data=clean_data_for_logging(db_mission)
    )
    
    return db_mission

@router.delete("/{mission_id}", status_code=204)
def delete_mission(
    mission_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_gestionnaire)
):
    """Supprimer une mission"""
    
    db_mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not db_mission:
        raise HTTPException(status_code=404, detail="Mission non trouvée")
    
    # Log action before delete
    log_action(
        db=db,
        module_name="missions",
        action_type=ActionType.DELETE,
        description=f"Suppression mission #{mission_id}",
        old_data=clean_data_for_logging(db_mission)
    )
    
    db.delete(db_mission)
    db.commit()
    
    return None

@router.get("/{mission_id}/client/{client_detail_id}/ordre-mission/pdf")
def generate_client_ordre_mission_pdf(
    mission_id: int,
    client_detail_id: int,
    db: Session = Depends(get_db)
):
    """Générer un ordre de mission PDF pour un client spécifique"""
    from models import MissionClientDetail, LogisticsType
    
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission non trouvée")
    
    client_detail = db.query(MissionClientDetail).filter(
        MissionClientDetail.id == client_detail_id,
        MissionClientDetail.mission_id == mission_id
    ).first()
    
    if not client_detail:
        raise HTTPException(status_code=404, detail="Détail client non trouvé")
    
    chauffeur = db.query(Employe).filter(Employe.id == mission.chauffeur_id).first()
    client = db.query(Client).filter(Client.id == client_detail.client_id).first()
    
    if not chauffeur or not client:
        raise HTTPException(status_code=404, detail="Données manquantes")
    
    # ⭐ v3.6.0: Récupérer le camion si assigné
    camion = None
    if mission.camion_id:
        from models.camion import Camion
        camion = db.query(Camion).filter(Camion.id == mission.camion_id).first()
    
    # Prepare logistics data
    logistics_data = []
    for movement in client_detail.logistics_movements:
        logistics_type = db.query(LogisticsType).filter(
            LogisticsType.id == movement.logistics_type_id
        ).first()
        
        logistics_data.append({
            'type_name': logistics_type.name if logistics_type else 'Inconnu',
            'quantity_out': movement.quantity_out,
            'quantity_in': movement.quantity_in
        })
    
    mission_data = {
        'id': mission.id,
        'date_mission': str(mission.date_mission),
        'chauffeur_nom': chauffeur.nom,
        'chauffeur_prenom': chauffeur.prenom,
        'client_nom': client.nom,
        'client_prenom': client.prenom,
        'distance': float(mission.distance),
        'prime_calculee': float(mission.prime_calculee),
        'montant_encaisse': float(client_detail.montant_encaisse),
        'observations': client_detail.observations or '',
        'logistics': logistics_data,
        # ⭐ v3.6.0: Camion
        'camion_marque': camion.marque if camion else None,
        'camion_modele': camion.modele if camion else None,
        'camion_immatriculation': camion.immatriculation if camion else None
    }
    
    pdf_buffer = pdf_generator.generate_ordre_mission_enhanced(mission_data)
    
    return StreamingResponse(
        pdf_buffer,
        media_type='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename="ordre_mission_{mission_id}_client_{client_detail.client_id}.pdf"'
        }
    )

@router.get("/{mission_id}/ordres-mission/pdf-multi")
def generate_all_ordres_mission_pdf(
    mission_id: int,
    db: Session = Depends(get_db)
):
    """
    ⭐ v3.6.0: Générer un seul fichier PDF contenant un ordre de mission par client (multi-pages)
    """
    from models import MissionClientDetail, LogisticsType
    from models.camion import Camion
    
    # Récupérer la mission
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission non trouvée")
    
    # Récupérer le chauffeur
    chauffeur = db.query(Employe).filter(Employe.id == mission.chauffeur_id).first()
    if not chauffeur:
        raise HTTPException(status_code=404, detail="Chauffeur non trouvé")
    
    # Récupérer le camion si assigné
    camion = None
    if mission.camion_id:
        camion = db.query(Camion).filter(Camion.id == mission.camion_id).first()
        print(f"DEBUG: Camion trouvé: {camion.marque} {camion.modele} - {camion.immatriculation}")
    else:
        print(f"DEBUG: Pas de camion_id pour cette mission (camion_id={mission.camion_id})")
    
    # Récupérer tous les détails clients pour cette mission
    client_details = db.query(MissionClientDetail).filter(
        MissionClientDetail.mission_id == mission_id
    ).all()
    
    if not client_details:
        raise HTTPException(status_code=404, detail="Aucun client trouvé pour cette mission")
    
    # Préparer les données de tous les clients
    all_clients_data = []
    
    for client_detail in client_details:
        # Récupérer le client
        client = db.query(Client).filter(Client.id == client_detail.client_id).first()
        if not client:
            continue
        
        # Préparer les données logistiques pour ce client
        logistics_data = []
        for movement in client_detail.logistics_movements:
            logistics_type = db.query(LogisticsType).filter(
                LogisticsType.id == movement.logistics_type_id
            ).first()
            
            logistics_data.append({
                'type_name': logistics_type.name if logistics_type else 'Inconnu',
                'quantity_out': movement.quantity_out,
                'quantity_in': movement.quantity_in
            })
        
        # Préparer les données pour le PDF de ce client
        mission_data = {
            'id': mission.id,
            'date_mission': str(mission.date_mission),
            'chauffeur_nom': chauffeur.nom,
            'chauffeur_prenom': chauffeur.prenom,
            'client_nom': client.nom,
            'client_prenom': client.prenom,
            'distance': float(client_detail.distance_km) if client_detail.distance_km else float(mission.distance),
            'prime_calculee': float(mission.prime_calculee),
            'montant_encaisse': float(client_detail.montant_encaisse) if client_detail.montant_encaisse else 0,
            'observations': client_detail.observations or '',
            'logistics': logistics_data,
            # Camion
            'camion_marque': camion.marque if camion else None,
            'camion_modele': camion.modele if camion else None,
            'camion_immatriculation': camion.immatriculation if camion else None
        }
        
        print(f"DEBUG: Client {client.nom} - camion_immat: {mission_data['camion_immatriculation']}")
        all_clients_data.append(mission_data)
    
    # Générer le PDF multi-pages (un ordre par client)
    pdf_buffer = pdf_generator.generate_ordres_mission_multi_clients(all_clients_data)
    
    return StreamingResponse(
        pdf_buffer,
        media_type='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename="ordres_mission_{mission_id:05d}.pdf"'
        }
    )

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
def delete_mission(mission_id: int, db: Session = Depends(get_db), _: None = Depends(require_gestionnaire)):
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
    db: Session = Depends(get_db),
    _: None = Depends(require_admin)  # ⭐ v3.6.0: Admin only
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
    
    try:
        print(f"DEBUG: Generating PDF for mission {mission_id}")
        
        # 1. Récupérer la mission simple
        mission = db.query(Mission).filter(Mission.id == mission_id).first()
        
        if not mission:
            print("DEBUG: Mission not found")
            raise HTTPException(status_code=404, detail="Mission non trouvée")
        
        print(f"DEBUG: Mission found: {mission.id}")
        
        # 2. Récupérer chauffeur, client et camion (v3.6.0)
        chauffeur = db.query(Employe).filter(Employe.id == mission.chauffeur_id).first()
        client = db.query(Client).filter(Client.id == mission.client_id).first()
        
        if not chauffeur or not client:
            print("DEBUG: Chauffeur or Client not found")
            raise HTTPException(status_code=404, detail="Données manquantes")
        
        print(f"DEBUG: Chauffeur: {chauffeur.nom}, Client: {client.nom}")
        
        # ⭐ v3.6.0: Récupérer le camion si assigné
        camion = None
        if mission.camion_id:
            from models.camion import Camion
            camion = db.query(Camion).filter(Camion.id == mission.camion_id).first()
            if camion:
                print(f"DEBUG: Camion: {camion.marque} {camion.modele} - {camion.immatriculation}")
        
        # 3. Récupérer les données logistiques via requêtes directes
        from models.mission_client_detail import MissionClientDetail, MissionLogisticsMovement
        from models.logistics_type import LogisticsType
        
        logistics = []
        montant_encaisse_total = 0.0
        observations_list = []
        
        print("DEBUG: Querying client details")
        
        # Récupérer tous les détails clients pour cette mission
        client_details = db.query(MissionClientDetail).filter(
            MissionClientDetail.mission_id == mission_id
        ).all()
        
        print(f"DEBUG: Found {len(client_details)} client details")
        
        for detail in client_details:
            # Montant encaissé
            if detail.montant_encaisse:
                montant_encaisse_total += float(detail.montant_encaisse)
            
            # Observations
            if detail.observations:
                observations_list.append(detail.observations)
            
            # Récupérer les mouvements logistiques pour ce détail
            movements = db.query(MissionLogisticsMovement).filter(
                MissionLogisticsMovement.mission_client_detail_id == detail.id
            ).all()
            
            print(f"DEBUG: Found {len(movements)} movements for detail {detail.id}")
            
            for movement in movements:
                # Récupérer le type logistique
                log_type = db.query(LogisticsType).filter(
                    LogisticsType.id == movement.logistics_type_id
                ).first()
                
                if log_type:
                    logistics.append({
                        'type_name': log_type.name,
                        'quantity_out': movement.quantity_out,
                        'quantity_in': movement.quantity_in
                    })
        
        print(f"DEBUG: Total logistics: {len(logistics)}, Total amount: {montant_encaisse_total}")
        
        observations_str = "\n".join(observations_list)
        
        
        # 5. Préparer les données pour le PDF (⭐ v3.6.0: ajout camion)
        mission_data = {
            'id': mission.id,
            'date_mission': str(mission.date_mission),
            'chauffeur_nom': chauffeur.nom,
            'chauffeur_prenom': chauffeur.prenom,
            'client_nom': client.nom,
            'client_prenom': client.prenom,
            'distance': float(mission.distance),
            'prime_calculee': float(mission.prime_calculee),
            'montant_encaisse': montant_encaisse_total,
            'observations': observations_str,
            'logistics': logistics,
            # ⭐ v3.6.0: Camion
            'camion_marque': camion.marque if camion else None,
            'camion_modele': camion.modele if camion else None,
            'camion_immatriculation': camion.immatriculation if camion else None
        }
        
        print(f"DEBUG: Mission data camion - marque: {mission_data['camion_marque']}, modele: {mission_data['camion_modele']}, immat: {mission_data['camion_immatriculation']}")
        print("DEBUG: Calling PDF generator")
        
        # 6. Générer le PDF
        pdf_buffer = pdf_generator.generate_ordre_mission_enhanced(mission_data)
        
        print("DEBUG: PDF generated successfully")
        
        return StreamingResponse(
            pdf_buffer,
            media_type='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename="ordre_mission_{mission_id:05d}.pdf"'
            }
        )
        
    except HTTPException as e:
        # Re-lever les exceptions HTTP
        raise e
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"ERROR generating PDF: {error_msg}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur lors de la génération du PDF: {error_msg}"
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
