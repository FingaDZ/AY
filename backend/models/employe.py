from sqlalchemy import Column, Integer, String, Date, Boolean, Enum as SQLEnum
from sqlalchemy.types import Numeric
from sqlalchemy.orm import relationship
from database import Base
import enum

class SituationFamiliale(str, enum.Enum):
    CELIBATAIRE = "Célibataire"
    MARIE = "Marié"

class StatutContrat(str, enum.Enum):
    ACTIF = "Actif"
    INACTIF = "Inactif"

class Employe(Base):
    __tablename__ = "employes"
    
    # Identifiant unique (généré automatiquement)
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Informations personnelles
    nom = Column(String(100), nullable=False, index=True)
    prenom = Column(String(100), nullable=False, index=True)
    date_naissance = Column(Date, nullable=False)
    lieu_naissance = Column(String(200), nullable=False)
    
    # Coordonnées
    adresse = Column(String(500), nullable=False)
    mobile = Column(String(20), nullable=False)
    
    # Informations administratives
    numero_secu_sociale = Column(String(50), unique=True, nullable=False)
    numero_compte_bancaire = Column(String(50), nullable=False)
    numero_anem = Column(String(50), nullable=True, index=True)  # N° ANEM (alphanumérique)
    
    # Situation
    situation_familiale = Column(SQLEnum(SituationFamiliale), nullable=False)
    femme_au_foyer = Column(Boolean, default=False, nullable=False)
    
    # Emploi
    date_recrutement = Column(Date, nullable=False)
    date_fin_contrat = Column(Date, nullable=True)
    poste_travail = Column(String(100), nullable=False, index=True)
    
    # Salaire
    salaire_base = Column(Numeric(12, 2), nullable=False)
    
    # Primes spécifiques
    prime_nuit_agent_securite = Column(Boolean, default=False, nullable=False)  # Prime de nuit 750 DA/mois pour agents de sécurité
    
    # Statut
    statut_contrat = Column(SQLEnum(StatutContrat), default=StatutContrat.ACTIF, nullable=False, index=True)
    actif = Column(Boolean, default=True, nullable=False, index=True)  # Soft delete
    
    # Relations
    pointages = relationship("Pointage", back_populates="employe", cascade="all, delete-orphan")
    avances = relationship("Avance", back_populates="employe", cascade="all, delete-orphan")
    credits = relationship("Credit", back_populates="employe", cascade="all, delete-orphan")
    missions = relationship("Mission", back_populates="chauffeur", cascade="all, delete-orphan")
    conges = relationship("Conge", back_populates="employe", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Employe {self.id}: {self.prenom} {self.nom}>"
