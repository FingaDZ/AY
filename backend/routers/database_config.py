from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from typing import Optional
from pydantic import BaseModel
from urllib.parse import quote_plus

from database import get_db
from models import DatabaseConfig, User
from middleware import require_admin


router = APIRouter(prefix="/database-config", tags=["Configuration Base de Données"])


class DatabaseConfigCreate(BaseModel):
    host: str
    port: int = 3306
    database_name: str
    username: str
    password: str
    charset: str = "utf8mb4"


class DatabaseConfigUpdate(BaseModel):
    host: Optional[str] = None
    port: Optional[int] = None
    database_name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    charset: Optional[str] = None


class DatabaseConfigResponse(BaseModel):
    id: int
    host: str
    port: int
    database_name: str
    username: str
    password: str  # Sera masqué dans la réponse
    charset: str
    is_active: bool
    date_creation: Optional[str]
    derniere_modification: Optional[str]

    class Config:
        from_attributes = True


@router.get("/", response_model=dict)
async def get_database_config(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Récupérer la configuration de la base de données active"""
    config = db.query(DatabaseConfig).filter(DatabaseConfig.is_active == True).first()
    if not config:
        # Retourner une configuration par défaut si aucune n'existe
        return {
            'id': None,
            'host': 'localhost',
            'port': 3306,
            'database_name': 'ay_hr',
            'username': 'root',
            'password': '',
            'charset': 'utf8mb4',
            'is_active': False,
            'date_creation': None,
            'derniere_modification': None,
            'source': 'default'
        }
    return config.to_dict()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_or_update_database_config(
    config_data: DatabaseConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Créer ou mettre à jour la configuration de la base de données"""
    
    # Vérifier la connexion avant de sauvegarder
    try:
        # Encoder le mot de passe pour gérer les caractères spéciaux
        encoded_password = quote_plus(config_data.password)
        test_connection_string = f"mysql+pymysql://{config_data.username}:{encoded_password}@{config_data.host}:{config_data.port}/{config_data.database_name}?charset={config_data.charset}"
        test_engine = create_engine(test_connection_string)
        test_connection = test_engine.connect()
        test_connection.close()
        test_engine.dispose()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Impossible de se connecter à la base de données: {str(e)}"
        )
    
    # Désactiver toutes les configurations existantes
    db.query(DatabaseConfig).update({'is_active': False})
    
    # Créer la nouvelle configuration
    config = DatabaseConfig(
        host=config_data.host,
        port=config_data.port,
        database_name=config_data.database_name,
        username=config_data.username,
        password=config_data.password,
        charset=config_data.charset,
        is_active=True
    )
    
    db.add(config)
    db.commit()
    db.refresh(config)
    
    return {
        **config.to_dict(),
        'message': 'Configuration sauvegardée. Redémarrez le serveur pour appliquer les changements.'
    }


@router.put("/{config_id}", response_model=dict)
async def update_database_config(
    config_id: int,
    config_data: DatabaseConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Mettre à jour une configuration existante"""
    config = db.query(DatabaseConfig).filter(DatabaseConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration non trouvée")
    
    # Mettre à jour les champs fournis
    update_data = config_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)
    
    # Tester la connexion si les paramètres ont changé
    if any(k in update_data for k in ['host', 'port', 'database_name', 'username', 'password']):
        try:
            test_connection_string = config.connection_string()
            test_engine = create_engine(test_connection_string)
            test_connection = test_engine.connect()
            test_connection.close()
            test_engine.dispose()
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Impossible de se connecter avec ces paramètres: {str(e)}"
            )
    
    # Désactiver les autres et activer celle-ci
    db.query(DatabaseConfig).filter(DatabaseConfig.id != config_id).update({'is_active': False})
    config.is_active = True
    
    db.commit()
    db.refresh(config)
    
    return {
        **config.to_dict(),
        'message': 'Configuration mise à jour. Redémarrez le serveur pour appliquer les changements.'
    }


@router.post("/test", response_model=dict)
async def test_database_connection(
    config_data: DatabaseConfigCreate,
    current_user: User = Depends(require_admin)
):
    """Tester une connexion sans sauvegarder"""
    try:
        # Encoder le mot de passe pour gérer les caractères spéciaux (!@#$%^&*)
        encoded_password = quote_plus(config_data.password)
        test_connection_string = f"mysql+pymysql://{config_data.username}:{encoded_password}@{config_data.host}:{config_data.port}/{config_data.database_name}?charset={config_data.charset}"
        test_engine = create_engine(test_connection_string)
        test_connection = test_engine.connect()
        
        # Tester une requête simple
        from sqlalchemy import text
        result = test_connection.execute(text("SELECT VERSION()"))
        version = result.fetchone()[0]
        
        test_connection.close()
        test_engine.dispose()
        
        return {
            'success': True,
            'message': 'Connexion réussie',
            'mysql_version': version
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Échec de la connexion: {str(e)}'
        }


@router.get("/history", response_model=list)
async def get_configuration_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Récupérer l'historique des configurations"""
    configs = db.query(DatabaseConfig).order_by(DatabaseConfig.date_creation.desc()).all()
    return [config.to_dict() for config in configs]
