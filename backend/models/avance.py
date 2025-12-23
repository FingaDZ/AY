from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.types import Numeric
from sqlalchemy.orm import relationship
from database import Base

class Avance(Base):
    __tablename__ = "avances"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employe_id = Column(Integer, ForeignKey("employes.id", ondelete="CASCADE"), nullable=False)
    date_avance = Column(Date, nullable=False, index=True)
    montant = Column(Numeric(12, 2), nullable=False)
    mois_deduction = Column(Integer, nullable=False, index=True)  # Mois de déduction (1-12)
    annee_deduction = Column(Integer, nullable=False, index=True)  # Année de déduction
    motif = Column(String(500), nullable=True)
    
    # ⭐ v3.6.1: Suivi des déductions
    deduit = Column(Boolean, default=False, nullable=False, index=True)  # Avance déduite du salaire
    date_deduction = Column(Date, nullable=True, index=True)  # Date de la déduction
    
    # Relation
    employe = relationship("Employe", back_populates="avances")
    
    def __repr__(self):
        return f"<Avance {self.id}: {self.montant} DA - {self.employe_id}>"
