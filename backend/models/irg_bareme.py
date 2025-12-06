from sqlalchemy import Column, Integer, Numeric, Boolean, DateTime
from datetime import datetime
from database import Base

class IRGBareme(Base):
    """Modèle pour le barème IRG (Impôt sur le Revenu Global)
    
    Structure simple : 2 colonnes seulement
    - tranche_min : Salaire (colonne MONTANT du fichier Excel)
    - taux : Montant IRG (colonne IRG du fichier Excel)
    """
    __tablename__ = 'irg_bareme'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Colonne 1 : Salaire (MONTANT dans Excel)
    tranche_min = Column('tranche_min', Numeric(15, 2), nullable=False, comment="Salaire (MONTANT)")
    
    # Colonne 2 : Montant IRG (IRG dans Excel)
    taux = Column('taux', Numeric(5, 2), nullable=False, comment="Montant IRG")
    
    # Colonnes supplémentaires de la DB (non utilisées pour l'import)
    tranche_max = Column('tranche_max', Numeric(15, 2), nullable=True)
    montant_deduit = Column('montant_deduit', Numeric(15, 2), nullable=True, default=0)
    actif = Column(Boolean, default=True, nullable=True)
    date_creation = Column('date_creation', DateTime, default=datetime.now, nullable=True)
    
    # Propriétés pour compatibilité avec le code existant
    @property
    def salaire_min(self):
        """Alias : salaire = tranche_min"""
        return self.tranche_min
    
    @salaire_min.setter
    def salaire_min(self, value):
        self.tranche_min = value
    
    @property
    def irg(self):
        """Alias : montant IRG = taux"""
        return self.taux
    
    @irg.setter
    def irg(self, value):
        self.taux = value
    
    def __repr__(self):
        return f"<IRGBareme(salaire={self.tranche_min}, irg={self.taux})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "salaire_min": float(self.tranche_min) if self.tranche_min else None,
            "irg": float(self.taux) if self.taux else None,
            "actif": self.actif
        }
