"""
Service de calcul des primes kilométriques pour missions multi-clients
"""
from decimal import Decimal
from typing import List, Dict
from sqlalchemy.orm import Session

from models import Mission, MissionClientDetail, ParametresSalaire


def calculer_km_mission_multi_clients(
    clients_km: List[Dict[str, any]],
    tarif_km: Decimal,
    db: Session
) -> Dict[str, any]:
    """
    Calcule la prime kilométrique pour une mission multi-clients.
    
    Logique v3.6.0:
    - Prendre le km le plus élevé parmi tous les clients
    - Ajouter km_supplementaire_par_client × (nb_clients - 1)
    - Prime = distance_totale × tarif_km
    
    Args:
        clients_km: Liste de dicts avec {client_id, distance_km}
        tarif_km: Tarif kilométrique en DA/km
        db: Session SQLAlchemy
    
    Returns:
        Dict avec {
            distance_calculee: float,
            km_max: float,
            nb_clients: int,
            km_supplementaire: int,
            prime_calculee: float,
            details_calcul: str
        }
    
    Example:
        >>> clients = [
        ...     {"client_id": 1, "distance_km": 25},
        ...     {"client_id": 2, "distance_km": 40},
        ...     {"client_id": 3, "distance_km": 15}
        ... ]
        >>> calculer_km_mission_multi_clients(clients, Decimal("35.00"), db)
        {
            "distance_calculee": 60.0,  # 40 (max) + 2 × 10
            "km_max": 40.0,
            "nb_clients": 3,
            "km_supplementaire": 10,
            "prime_calculee": 2100.0,  # 60 × 35
            "details_calcul": "Client max: 40 km + 2 clients × 10 km/client = 60 km"
        }
    """
    
    # Récupérer km_supplementaire depuis parametres_salaire
    params = db.query(ParametresSalaire).first()
    if not params:
        # Valeur par défaut si pas de paramètres
        km_supplementaire = 10
    else:
        km_supplementaire = params.km_supplementaire_par_client
    
    # Validation
    if not clients_km or len(clients_km) == 0:
        raise ValueError("La liste de clients ne peut pas être vide")
    
    # Extraire toutes les distances et trouver le max
    distances = [float(client.get("distance_km", 0)) for client in clients_km]
    km_max = max(distances)
    nb_clients = len(clients_km)
    
    # Calcul: km_max + (nb_clients - 1) × km_supplementaire
    km_additionnels = (nb_clients - 1) * km_supplementaire
    distance_totale = km_max + km_additionnels
    
    # Prime = distance × tarif
    prime = Decimal(str(distance_totale)) * tarif_km
    
    # Construction du détail explicatif
    if nb_clients == 1:
        details_calcul = f"1 client: {km_max} km"
    else:
        details_calcul = (
            f"Client max: {km_max} km + "
            f"{nb_clients - 1} client(s) × {km_supplementaire} km/client = "
            f"{distance_totale} km"
        )
    
    return {
        "distance_calculee": float(distance_totale),
        "km_max": float(km_max),
        "nb_clients": nb_clients,
        "km_supplementaire": km_supplementaire,
        "km_additionnels": km_additionnels,
        "prime_calculee": float(prime),
        "details_calcul": details_calcul
    }


def recalculer_prime_mission(mission_id: int, db: Session) -> Mission:
    """
    Recalcule la prime d'une mission existante en fonction de ses client_details.
    
    Utilisé après modification des clients d'une mission.
    
    Args:
        mission_id: ID de la mission
        db: Session SQLAlchemy
    
    Returns:
        Mission mise à jour
    """
    
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise ValueError(f"Mission {mission_id} introuvable")
    
    # Récupérer les détails clients avec distances
    client_details = db.query(MissionClientDetail).filter(
        MissionClientDetail.mission_id == mission_id
    ).all()
    
    if not client_details:
        # Aucun client_detail: utiliser l'ancien système (client_id + distance de la mission)
        mission.prime_calculee = mission.distance * mission.tarif_km
        db.commit()
        return mission
    
    # Construire liste clients_km
    clients_km = [
        {
            "client_id": detail.client_id,
            "distance_km": float(detail.distance_km or 0)
        }
        for detail in client_details
        if detail.distance_km  # Ignorer les entrées sans distance
    ]
    
    if not clients_km:
        # Tous les détails sont sans distance: fallback ancien système
        mission.prime_calculee = mission.distance * mission.tarif_km
    else:
        # Calcul multi-clients
        resultat = calculer_km_mission_multi_clients(
            clients_km=clients_km,
            tarif_km=mission.tarif_km,
            db=db
        )
        
        # Mettre à jour mission
        mission.distance = Decimal(str(resultat["distance_calculee"]))
        mission.prime_calculee = Decimal(str(resultat["prime_calculee"]))
    
    db.commit()
    db.refresh(mission)
    
    return mission
