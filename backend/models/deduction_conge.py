from sqlalchemy import Column, Integer, Numeric, ForeignKey, DateTime, Date, String, func
from sqlalchemy.orm import relationship
from database import Base

class DeductionConge(Base):
    """
    Table pour enregistrer les déductions de congés
    
    ARCHITECTURE v3.7.0:
    - Table conges: Enregistre uniquement les jours ACQUIS par période
    - Table deductions_conges: Enregistre chaque PRISE de congé
    - Solde = SUM(conges.jours_conges_acquis) - SUM(deductions_conges.jours_deduits)
    
    AVANTAGES:
    - Historique complet de chaque prise de congé
    - Pas de modification des périodes d'acquisition
    - Facilite les annulations/corrections
    - Séparation claire: acquisition vs consommation
    """
    __tablename__ = "deductions_conges"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employe_id = Column(Integer, ForeignKey("employes.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Quantité déduite
    jours_deduits = Column(Numeric(5, 2), nullable=False, comment="Nombre de jours de congé pris")
    
    # Période de déduction sur bulletin de paie
    mois_deduction = Column(Integer, nullable=False, comment="Mois de déduction sur bulletin (1-12)", index=True)
    annee_deduction = Column(Integer, nullable=False, comment="Année de déduction sur bulletin", index=True)
    
    # Informations complémentaires
    date_debut = Column(Date, nullable=True, comment="Date de début du congé")
    date_fin = Column(Date, nullable=True, comment="Date de fin du congé")
    type_conge = Column(String(50), default="ANNUEL", comment="Type: ANNUEL, MALADIE, EXCEPTIONNEL, etc.")
    motif = Column(String(255), nullable=True, comment="Motif ou description")
    
    # Métadonnées
    created_at = Column(DateTime, server_default=func.now(), comment="Date de création")
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="Utilisateur créateur")
    
    # Relations
    employe = relationship("Employe", back_populates="deductions_conges")
    createur = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<DeductionConge employe#{self.employe_id} {self.jours_deduits}j déduit {self.mois_deduction}/{self.annee_deduction}>"
