from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from database import Base
from datetime import datetime
import enum


class UserRole(str, enum.Enum):
    Admin = "Admin"
    Utilisateur = "Utilisateur"


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.Utilisateur)
    actif = Column(Boolean, default=True)
    date_creation = Column(DateTime, default=datetime.now)
    derniere_connexion = Column(DateTime, nullable=True)

    def to_dict(self):
        """Convertir en dict sans password_hash"""
        return {
            'id': self.id,
            'email': self.email,
            'nom': self.nom,
            'prenom': self.prenom,
            'role': self.role.value if isinstance(self.role, UserRole) else self.role,
            'actif': self.actif,
            'date_creation': self.date_creation.isoformat() if self.date_creation else None,
            'derniere_connexion': self.derniere_connexion.isoformat() if self.derniere_connexion else None,
        }
