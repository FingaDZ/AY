from sqlalchemy import Column, Integer, Numeric, Boolean, DateTime
from datetime import datetime
from database import Base

class IRGBareme(Base):
    """Modèle pour le barème IRG (Impôt sur le Revenu Global)"""
    __tablename__ = 'irg_bareme'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Tranches de salaire - NOMS ALIGNÉS AVEC LA DB
    tranche_min = Column('tranche_min', Numeric(15, 2), nullable=False, comment="Salaire minimum de la tranche")
    tranche_max = Column('tranche_max', Numeric(15, 2), nullable=True, comment="Salaire maximum de la tranche (NULL pour dernière tranche)")
    
    # Taux et montant - NOMS ALIGNÉS AVEC LA DB
    taux = Column('taux', Numeric(5, 2), nullable=False, comment="Taux IRG")
    montant_deduit = Column('montant_deduit', Numeric(15, 2), nullable=True, default=0, comment="Montant déduit")
    
    # Gestion des versions du barème
    actif = Column(Boolean, default=True, nullable=True, comment="Barème actif ou archivé")
    date_creation = Column('date_creation', DateTime, default=datetime.now, nullable=True)
    
    # Propriétés pour compatibilité avec le code existant
    @property
    def salaire_min(self):
        """Alias pour compatibilité"""
        return self.tranche_min
    
    @salaire_min.setter
    def salaire_min(self, value):
        self.tranche_min = value
    
    @property
    def salaire_max(self):
        """Alias pour compatibilité"""
        return self.tranche_max
    
    @salaire_max.setter
    def salaire_max(self, value):
        self.tranche_max = value
    
    @property
    def irg(self):
        """Alias pour compatibilité - retourne le taux"""
        return self.taux
    
    @irg.setter
    def irg(self, value):
        self.taux = value
    
    def __repr__(self):
        return f"<IRGBareme(id={self.id}, tranche_min={self.tranche_min}, taux={self.taux}, actif={self.actif})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "salaire_min": float(self.tranche_min) if self.tranche_min else None,
            "salaire_max": float(self.tranche_max) if self.tranche_max else None,
            "irg": float(self.taux) if self.taux else None,
            "actif": self.actif,
            "date_debut": None,  # Pas dans la DB actuelle
            "date_fin": None,    # Pas dans la DB actuelle
            "created_at": self.date_creation.isoformat() if self.date_creation else None
        }
