from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import Optional
from datetime import datetime

from database import get_db
from models import Logging, User, ActionType
from middleware import require_admin


router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get("/", response_model=dict)
async def get_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000),
    module_name: Optional[str] = None,
    action_type: Optional[str] = None,
    user_id: Optional[int] = None,
    date_debut: Optional[str] = None,
    date_fin: Optional[str] = None,
    search: Optional[str] = None
):
    """
    Récupérer les logs avec filtres
    Les logs sont en lecture seule (pas de modification/suppression possible)
    """
    query = db.query(Logging)
    
    # Filtres
    filters = []
    
    if module_name:
        filters.append(Logging.module_name == module_name)
    
    if action_type:
        try:
            action_enum = ActionType[action_type.upper()]
            filters.append(Logging.action_type == action_enum)
        except KeyError:
            pass
    
    if user_id:
        filters.append(Logging.user_id == user_id)
    
    if date_debut:
        try:
            date_debut_obj = datetime.fromisoformat(date_debut)
            filters.append(Logging.timestamp >= date_debut_obj)
        except ValueError:
            pass
    
    if date_fin:
        try:
            date_fin_obj = datetime.fromisoformat(date_fin)
            filters.append(Logging.timestamp <= date_fin_obj)
        except ValueError:
            pass
    
    if search:
        filters.append(
            or_(
                Logging.user_email.contains(search),
                Logging.description.contains(search)
            )
        )
    
    if filters:
        query = query.filter(and_(*filters))
    
    # Tri par date décroissante (plus récent en premier)
    query = query.order_by(desc(Logging.timestamp))
    
    # Pagination
    total = query.count()
    offset = (page - 1) * limit
    logs = query.offset(offset).limit(limit).all()
    
    return {
        'total': total,
        'page': page,
        'limit': limit,
        'logs': [log.to_dict() for log in logs]
    }


@router.get("/modules", response_model=list)
async def get_modules(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Récupérer la liste des modules disponibles dans les logs
    """
    modules = db.query(Logging.module_name).distinct().all()
    return [module[0] for module in modules]


@router.get("/users", response_model=list)
async def get_log_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Récupérer la liste des utilisateurs qui ont effectué des actions
    """
    users = db.query(Logging.user_id, Logging.user_email)\
        .filter(Logging.user_id.isnot(None))\
        .distinct()\
        .all()
    
    return [
        {'id': user[0], 'email': user[1]}
        for user in users
    ]


@router.get("/{log_id}", response_model=dict)
async def get_log_detail(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Récupérer le détail d'un log spécifique
    """
    log = db.query(Logging).filter(Logging.id == log_id).first()
    if not log:
        return {'error': 'Log non trouvé'}
    
    return log.to_dict()
