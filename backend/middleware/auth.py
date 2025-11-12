"""
Middleware d'authentification et d'autorisation
"""
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import User, UserRole


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Récupère l'utilisateur actuel depuis le token d'autorisation.
    Pour l'instant, on utilise un système simple basé sur l'ID utilisateur.
    TODO: Implémenter JWT pour production
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié"
        )
    
    try:
        # Format attendu: "Bearer <user_id>"
        scheme, user_id = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Schéma invalide")
        
        user_id = int(user_id)
        user = db.query(User).filter(User.id == user_id, User.actif == True).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non trouvé ou inactif"
            )
        
        return user
        
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide"
        )


async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Vérifie que l'utilisateur actuel est un administrateur
    """
    if current_user.role != UserRole.Admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé. Droits administrateur requis."
        )
    return current_user


async def require_auth(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Vérifie simplement que l'utilisateur est authentifié (admin ou utilisateur)
    """
    return current_user
