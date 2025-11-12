from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, EmailStr
import bcrypt

from database import get_db
from models import User, UserRole
from middleware import require_admin


router = APIRouter(prefix="/utilisateurs", tags=["Utilisateurs"])


class UserCreate(BaseModel):
    email: EmailStr
    nom: str
    prenom: str
    password: str
    role: str = "Utilisateur"


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    nom: str | None = None
    prenom: str | None = None
    password: str | None = None
    role: str | None = None
    actif: bool | None = None


class UserResponse(BaseModel):
    id: int
    email: str
    nom: str
    prenom: str
    role: str
    actif: bool
    date_creation: str | None
    derniere_connexion: str | None

    class Config:
        from_attributes = True


def hash_password(password: str) -> str:
    """Hash un mot de passe avec bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie un mot de passe"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


@router.get("/", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Lister tous les utilisateurs"""
    users = db.query(User).all()
    return [user.to_dict() for user in users]


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Créer un nouvel utilisateur"""
    
    # Vérifier si l'email existe déjà
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Un utilisateur avec l'email {user_data.email} existe déjà"
        )
    
    # Valider le rôle
    if user_data.role not in [UserRole.Admin.value, UserRole.Utilisateur.value]:
        raise HTTPException(status_code=400, detail="Rôle invalide")
    
    # Créer l'utilisateur
    user = User(
        email=user_data.email,
        nom=user_data.nom,
        prenom=user_data.prenom,
        password_hash=hash_password(user_data.password),
        role=UserRole(user_data.role),
        actif=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user.to_dict()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Obtenir un utilisateur par ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user.to_dict()


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Mettre à jour un utilisateur"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Mettre à jour les champs
    if user_data.email:
        # Vérifier doublon email
        existing = db.query(User).filter(
            User.email == user_data.email,
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
        user.email = user_data.email
    
    if user_data.nom:
        user.nom = user_data.nom
    if user_data.prenom:
        user.prenom = user_data.prenom
    if user_data.password:
        user.password_hash = hash_password(user_data.password)
    if user_data.role:
        if user_data.role not in [UserRole.Admin.value, UserRole.Utilisateur.value]:
            raise HTTPException(status_code=400, detail="Rôle invalide")
        user.role = UserRole(user_data.role)
    if user_data.actif is not None:
        user.actif = user_data.actif
    
    db.commit()
    db.refresh(user)
    return user.to_dict()


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Supprimer un utilisateur"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Empêcher la suppression du dernier admin
    if user.role == UserRole.Admin:
        admin_count = db.query(User).filter(User.role == UserRole.Admin).count()
        if admin_count <= 1:
            raise HTTPException(
                status_code=400,
                detail="Impossible de supprimer le dernier administrateur"
            )
    
    db.delete(user)
    db.commit()
    return None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    user: UserResponse
    message: str


@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Connexion simple (authentification basique)"""
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Email ou mot de passe incorrect"
        )
    
    if not user.actif:
        raise HTTPException(
            status_code=403,
            detail="Compte désactivé"
        )
    
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Email ou mot de passe incorrect"
        )
    
    # Mettre à jour la date de dernière connexion
    from datetime import datetime
    user.derniere_connexion = datetime.now()
    db.commit()
    
    return {
        "user": user.to_dict(),
        "message": "Connexion réussie"
    }
