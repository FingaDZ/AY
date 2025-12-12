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
    jours_conges_acquis = Column(Integer, default=0)  # v3.5.1: Plus de décimales
    jours_conges_pris = Column(Integer, default=0)     # v3.5.1: Plus de décimales
    jours_conges_restants = Column(Integer, default=0)  # v3.5.1: Plus de décimales
    
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
    def calculer_jours_conges(jours_travailles: int, est_nouveau_recrue: bool = False) -> int:
        """
        Calculer les jours de congés acquis selon les NOUVELLES règles v3.5.1:
        
        RÈGLE 1: 8 jours travaillés = 1 jour de congé (pas de décimal)
        RÈGLE 2: Nouveau recruté: minimum 15 jours travaillés pour avoir 1 jour
        RÈGLE 3: Pas de décimales, arrondi intelligent:
                 - 8-15 jours → 1 jour
                 - 16-23 jours → 2 jours  
                 - 24-30 jours → 3 jours
        RÈGLE 4: IMPORTANT - jours_travailles doit EXCLURE les jours de congé pris
                 (comptage basé uniquement sur jours réellement travaillés)
        
        Retour: int (nombre entier de jours, pas de décimal)
        """
        # RÈGLE 1 & 2: Seuil minimum
        if est_nouveau_recrue:
            # Nouveau recruté: minimum 15 jours pour avoir 1 jour
            if jours_travailles < 15:
                return 0
            # Entre 15-22 jours → 1 jour
            elif jours_travailles < 23:
                return 1
            # 23-30 jours → 2 jours
            elif jours_travailles <= 30:
                return 2
            else:
                return 2  # Plafond pour nouveau
        else:
            # Employé standard: 8 jours = 1 jour de congé
            if jours_travailles < 8:
                return 0
            
            # RÈGLE 3: Arrondi intelligent par tranches
            # 8-15 jours → 1 jour
            if jours_travailles < 16:
                return 1
            # 16-23 jours → 2 jours
            elif jours_travailles < 24:
                return 2
            # 24-30+ jours → 3 jours
            else:
                return 3
    
    def __repr__(self):
        return f"<Conge {self.employe_id} - {self.mois}/{self.annee}: {self.jours_conges_acquis}j>"
