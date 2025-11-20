"""Modèle pour les salaires mensuels"""

from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Salaire(Base):
    """Modèle pour les salaires mensuels des employés"""
    __tablename__ = "salaires"

    id = Column(Integer, primary_key=True, index=True)
    employe_id = Column(Integer, ForeignKey("employes.id", ondelete="CASCADE"), nullable=False)
    annee = Column(Integer, nullable=False)
    mois = Column(Integer, nullable=False)
    
    # Données de base
    jours_travailles = Column(Integer, default=0)
    jours_ouvrables = Column(Integer, default=26)
    
    # Salaire et heures
    salaire_base_proratis = Column(Numeric(10, 2), default=0)
    heures_supplementaires = Column(Numeric(10, 2), default=0)
    
    # Primes cotisables
    indemnite_nuisance = Column(Numeric(10, 2), default=0)
    ifsp = Column(Numeric(10, 2), default=0)
    iep = Column(Numeric(10, 2), default=0)
    prime_encouragement = Column(Numeric(10, 2), default=0)
    prime_chauffeur = Column(Numeric(10, 2), default=0)
    prime_nuit_agent_securite = Column(Numeric(10, 2), default=0)
    prime_deplacement = Column(Numeric(10, 2), default=0)
    prime_objectif = Column(Numeric(10, 2), default=0)
    prime_variable = Column(Numeric(10, 2), default=0)
    
    # Salaire cotisable
    salaire_cotisable = Column(Numeric(10, 2), default=0)
    
    # Déduction SS
    retenue_securite_sociale = Column(Numeric(10, 2), default=0)
    
    # Primes non cotisables mais imposables
    panier = Column(Numeric(10, 2), default=0)
    prime_transport = Column(Numeric(10, 2), default=0)
    
    # Salaire imposable
    salaire_imposable = Column(Numeric(10, 2), default=0)
    
    # IRG
    irg = Column(Numeric(10, 2), default=0)
    
    # Autres déductions
    total_avances = Column(Numeric(10, 2), default=0)
    retenue_credit = Column(Numeric(10, 2), default=0)
    
    # Prime femme foyer
    prime_femme_foyer = Column(Numeric(10, 2), default=0)
    
    # Salaire net
    salaire_net = Column(Numeric(10, 2), default=0)
    
    # Métadonnées
    date_paiement = Column(Date)
    statut = Column(String(20), default='brouillon')
    notes = Column(String(500))
    created_at = Column(Date, default=datetime.now)
    updated_at = Column(Date, default=datetime.now, onupdate=datetime.now)
    
    # Relation
    employe = relationship("Employe", back_populates="salaires")
    
    # Index pour performance
    __table_args__ = (
        Index('idx_employe_annee_mois', 'employe_id', 'annee', 'mois', unique=True),
        Index('idx_annee', 'annee'),
        Index('idx_mois', 'mois'),
        Index('idx_statut', 'statut'),
    )
