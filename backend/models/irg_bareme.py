from sqlalchemy import Column, Integer, Numeric, Boolean, Date, DateTime
from database import Base
from datetime import datetime


class IRGBareme(Base):
    """Barème IRG pour le calcul de l'impôt sur le revenu"""
    __tablename__ = 'irg_bareme'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Tranches de salaire
    salaire_min = Column(Numeric(10, 2), nullable=False, index=True, comment="Salaire minimum de la tranche (DA)")
    salaire_max = Column(Numeric(10, 2), nullable=True, comment="Salaire maximum de la tranche (DA), NULL pour dernière tranche")
    
    # IRG correspondant
    irg = Column(Numeric(10, 2), nullable=False, comment="Montant IRG pour cette tranche (DA)")
    
    # Gestion des versions du barème
    actif = Column(Boolean, default=True, nullable=False, index=True, comment="Barème actuellement utilisé")
    date_debut = Column(Date, nullable=True, comment="Date de début de validité")
    date_fin = Column(Date, nullable=True, comment="Date de fin de validité")
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    
    def __repr__(self):
        return f"<IRGBareme(salaire_min={self.salaire_min}, irg={self.irg}, actif={self.actif})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'salaire_min': float(self.salaire_min),
            'salaire_max': float(self.salaire_max) if self.salaire_max else None,
            'irg': float(self.irg),
            'actif': self.actif,
            'date_debut': self.date_debut.isoformat() if self.date_debut else None,
            'date_fin': self.date_fin.isoformat() if self.date_fin else None,
        }
