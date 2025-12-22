from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.types import Numeric
from sqlalchemy.orm import relationship
from database import Base
import enum

class StatutCredit(str, enum.Enum):
    EN_COURS = "En cours"
    SOLDE = "Soldé"

class Credit(Base):
    __tablename__ = "credits"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employe_id = Column(Integer, ForeignKey("employes.id", ondelete="CASCADE"), nullable=False)
    date_octroi = Column(Date, nullable=False, index=True)
    montant_total = Column(Numeric(12, 2), nullable=False)
    nombre_mensualites = Column(Integer, nullable=False)
    montant_mensualite = Column(Numeric(12, 2), nullable=False)  # Calculé automatiquement
    montant_retenu = Column(Numeric(12, 2), default=0, nullable=False)  # Cumul des retenues
    statut = Column(SQLEnum(StatutCredit), default=StatutCredit.EN_COURS, nullable=False)
    
    # Dates de début et fin prévisionnelles
    mois_debut = Column(Integer, nullable=True, comment="Mois de début des retenues (1-12)")
    annee_debut = Column(Integer, nullable=True, comment="Année de début des retenues")
    mois_fin_prevu = Column(Integer, nullable=True, comment="Mois de fin prévu des retenues (1-12)")
    annee_fin_prevu = Column(Integer, nullable=True, comment="Année de fin prévue des retenues")
    
    # Relations
    employe = relationship("Employe", back_populates="credits")
    retenues = relationship("RetenueCredit", back_populates="credit", cascade="all, delete-orphan")
    prorogations = relationship("ProrogationCredit", back_populates="credit", cascade="all, delete-orphan")
    
    @property
    def montant_restant(self):
        """Calcul du montant restant"""
        return self.montant_total - self.montant_retenu
    
    def __repr__(self):
        return f"<Credit {self.id}: {self.montant_total} DA - {self.employe_id}>"

class RetenueCredit(Base):
    __tablename__ = "retenues_credit"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    credit_id = Column(Integer, ForeignKey("credits.id", ondelete="CASCADE"), nullable=False)
    mois = Column(Integer, nullable=False, index=True)
    annee = Column(Integer, nullable=False, index=True)
    montant = Column(Numeric(12, 2), nullable=False)
    date_retenue = Column(Date, nullable=False)
    
    # Relation
    credit = relationship("Credit", back_populates="retenues")
    
    def __repr__(self):
        return f"<RetenueCredit {self.id}: {self.montant} DA - {self.mois}/{self.annee}>"

class ProrogationCredit(Base):
    __tablename__ = "prorogations_credit"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    credit_id = Column(Integer, ForeignKey("credits.id", ondelete="CASCADE"), nullable=False)
    date_prorogation = Column(Date, nullable=False, index=True)
    mois_initial = Column(Integer, nullable=False)
    annee_initiale = Column(Integer, nullable=False)
    mois_reporte = Column(Integer, nullable=False)
    annee_reportee = Column(Integer, nullable=False)
    motif = Column(String(500), nullable=False)
    
    # Relation
    credit = relationship("Credit", back_populates="prorogations")
    
    def __repr__(self):
        return f"<ProrogationCredit {self.id}: {self.mois_initial}/{self.annee_initiale} -> {self.mois_reporte}/{self.annee_reportee}>"
