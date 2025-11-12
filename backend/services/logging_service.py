"""
Service de logging pour enregistrer toutes les opérations CRUD
"""
from sqlalchemy.orm import Session
from models import Logging, ActionType, User
from typing import Optional, Dict, Any
from fastapi import Request
import json


def log_action(
    db: Session,
    module_name: str,
    action_type: ActionType,
    record_id: Optional[int] = None,
    old_data: Optional[Dict[str, Any]] = None,
    new_data: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None,
    user: Optional[User] = None,
    request: Optional[Request] = None
) -> Logging:
    """
    Enregistre une action dans les logs
    
    Args:
        db: Session de base de données
        module_name: Nom du module (employes, pointages, clients, etc.)
        action_type: Type d'action (CREATE, UPDATE, DELETE)
        record_id: ID de l'enregistrement affecté
        old_data: Données avant modification (pour UPDATE/DELETE)
        new_data: Nouvelles données (pour CREATE/UPDATE)
        description: Description de l'action
        user: Utilisateur qui a effectué l'action
        request: Requête HTTP pour extraire l'IP
    
    Returns:
        L'enregistrement de log créé
    """
    # Extraire l'IP si la requête est fournie
    ip_address = None
    if request:
        ip_address = request.client.host if request.client else None
    
    # Créer le log
    log_entry = Logging(
        user_id=user.id if user else None,
        user_email=user.email if user else None,
        module_name=module_name,
        action_type=action_type,
        record_id=record_id,
        old_data=old_data,
        new_data=new_data,
        description=description,
        ip_address=ip_address
    )
    
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    
    return log_entry


def clean_data_for_logging(data: Any) -> Optional[Dict[str, Any]]:
    """
    Nettoie les données pour le logging (enlève les champs sensibles)
    """
    if data is None:
        return None
    
    if hasattr(data, 'to_dict'):
        data_dict = data.to_dict()
    elif hasattr(data, '__dict__'):
        data_dict = {k: v for k, v in data.__dict__.items() if not k.startswith('_')}
    elif isinstance(data, dict):
        data_dict = data.copy()
    else:
        return None
    
    # Masquer les champs sensibles
    sensitive_fields = ['password', 'password_hash', 'token']
    for field in sensitive_fields:
        if field in data_dict:
            data_dict[field] = '***HIDDEN***'
    
    # Convertir les objets datetime en string
    for key, value in data_dict.items():
        if hasattr(value, 'isoformat'):
            data_dict[key] = value.isoformat()
        elif hasattr(value, '__name__'):  # Pour les enums
            data_dict[key] = str(value)
    
    return data_dict
