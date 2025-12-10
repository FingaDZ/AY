from sqlalchemy import Column, Integer, Numeric, ForeignKey, DateTime, Date, String, func
from sqlalchemy.orm import relationship
from database import Base

class Conge(Base):
    __tablename__ = "conges"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employe_id = Column(Integer, ForeignKey("employes.id", ondelete="CASCADE"), nullable=False)
    annee = Column(Integer, nullable=False, index=True)
    mois = Column(Integer, nullable=False, index=True)
    jours_travailles = Column(Integer, default=0)
    jours_conges_acquis = Column(Numeric(5, 2), default=0.00)
    jours_conges_pris = Column(Numeric(5, 2), default=0.00)
    jours_conges_restants = Column(Numeric(5, 2), default=0.00)
    
    # Nouvelles colonnes pour la saisie de congé
    date_debut = Column(Date, nullable=True, comment="Date de début du congé pris")
    date_fin = Column(Date, nullable=True, comment="Date de fin du congé pris")
    type_conge = Column(String(50), nullable=True, default="ANNUEL", comment="Type: ANNUEL, MALADIE, AUTRE")
    commentaire = Column(String(500), nullable=True, comment="Commentaire ou raison")
    
    date_calcul = Column(DateTime, server_default=func.now())
    derniere_mise_a_jour = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relation
    employe = relationship("Employe", back_populates="conges")
    
    @staticmethod
    def calculer_jours_conges(jours_travailles: int, est_nouveau_recrue: bool = False) -> float:
        """
        Calculer les jours de congés acquis selon les règles:
        - 30 jours travaillés = 2.5 jours de congé
        - Minimum 8 jours travaillés pour avoir 1 jour de congé
        - Nouveaux recrutements: minimum 15 jours travaillés pour calculer 2.5 jours
        """
        if jours_travailles < 8:
            return 0.0
        
        if est_nouveau_recrue and jours_travailles < 15:
            return 0.0
        
        # Calcul proportionnel: (jours_travailles / 30) * 2.5
        jours_conges = (jours_travailles / 30) * 2.5
        
        # Plafonner à 2.5 jours maximum (30-31 jours = 2.5 jours)
        jours_conges = min(jours_conges, 2.5)
        
        # Arrondir à 1 décimale
        return round(jours_conges, 1)
    
    def __repr__(self):
        return f"<Conge {self.employe_id} - {self.mois}/{self.annee}: {self.jours_conges_acquis}j>"
