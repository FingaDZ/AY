"""
Middleware pour le logging automatique des opérations CRUD
"""
from fastapi import Request
from sqlalchemy.orm import Session
from models import Logging, ActionType, User
from services.logging_service import clean_data_for_logging
from typing import Callable
import json


# Mapping des routes vers les modules
ROUTE_TO_MODULE = {
    '/api/employes': 'employes',
    '/api/pointages': 'pointages',
    '/api/clients': 'clients',
    '/api/missions': 'missions',
    '/api/avances': 'avances',
    '/api/credits': 'credits',
    '/api/salaires': 'salaires',
    '/api/parametres': 'parametres',
    '/api/database-config': 'database_config',
}

# Mapping des méthodes HTTP vers les actions
METHOD_TO_ACTION = {
    'POST': ActionType.CREATE,
    'PUT': ActionType.UPDATE,
    'PATCH': ActionType.UPDATE,
    'DELETE': ActionType.DELETE,
}


async def log_request_middleware(request: Request, call_next: Callable):
    """
    Middleware pour logger automatiquement les requêtes CRUD
    """
    # Laisser passer la requête
    response = await call_next(request)
    
    # Vérifier si c'est une route à logger
    should_log = False
    module_name = None
    
    for route_prefix, module in ROUTE_TO_MODULE.items():
        if request.url.path.startswith(route_prefix):
            should_log = True
            module_name = module
            break
    
    # Vérifier si c'est une méthode à logger
    if should_log and request.method in METHOD_TO_ACTION:
        action_type = METHOD_TO_ACTION[request.method]
        
        # On ne peut pas logger ici car la réponse est déjà envoyée
        # Le logging doit être fait dans chaque endpoint
        # Ce middleware sert juste de base pour une future implémentation
        pass
    
    return response
