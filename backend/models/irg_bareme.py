from sqlalchemy import Column, Integer, Numeric, Boolean, DateTime
from datetime import datetime
from database import Base

class IRGBareme(Base):
    """Modèle pour le barème IRG (Impôt sur le Revenu Global)
    
    Structure alignée avec le fichier Excel (2 colonnes):
    - salaire : Montant du salaire (colonne MONTANT)
    - montant_irg : Montant IRG à retenir (colonne IRG)
    """
    __tablename__ = 'irg_bareme'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Colonne 1 : Salaire (MONTANT dans Excel)
    salaire = Column('salaire', Numeric(15, 2), nullable=False, index=True, comment="Salaire (MONTANT)")
    
    # Colonne 2 : Montant IRG (IRG dans Excel)
    montant_irg = Column('montant_irg', Numeric(15, 2), nullable=False, comment="Montant IRG")
    
    # Métadonnées
    actif = Column(Boolean, default=True, nullable=True, index=True, comment="Barème actif")
    date_creation = Column('date_creation', DateTime, default=datetime.now, nullable=True)
    
    # Propriétés pour compatibilité avec le code existant
    @property
    def salaire_min(self):
        """Alias pour compatibilité : salaire_min = salaire"""
        return self.salaire
    
    @salaire_min.setter
    def salaire_min(self, value):
        self.salaire = value
    
    @property
    def irg(self):
        """Alias pour compatibilité : irg = montant_irg"""
        return self.montant_irg
    
    @irg.setter
    def irg(self, value):
        self.montant_irg = value
    
    # Alias pour ancienne structure (si utilisé ailleurs)
    @property
    def tranche_min(self):
        return self.salaire
    
    @property
    def taux(self):
        return self.montant_irg
    
    def __repr__(self):
        return f"<IRGBareme(salaire={self.salaire}, montant_irg={self.montant_irg})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "salaire": float(self.salaire) if self.salaire else None,
            "montant_irg": float(self.montant_irg) if self.montant_irg else None,
            "salaire_min": float(self.salaire) if self.salaire else None,  # Compatibilité
            "irg": float(self.montant_irg) if self.montant_irg else None,  # Compatibilité
            "actif": self.actif
        }
