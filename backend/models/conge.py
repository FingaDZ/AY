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
    jours_conges_acquis = Column(Numeric(5, 2), default=0.00)  # v3.5.3: Décimales max 2.5j/mois
    jours_conges_pris = Column(Numeric(5, 2), default=0.00)     # v3.5.3: Décimales
    jours_conges_restants = Column(Numeric(5, 2), default=0.00)  # v3.5.3: Décimales
    
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
        Calculer les jours de congés acquis selon les règles v3.5.3:
        
        RÈGLE 1: Maximum 2.5 jours par mois (30 jours travaillés)
        RÈGLE 2: Formule proportionnelle: (jours_travaillés / 30) * 2.5
        RÈGLE 3: Avec décimales (0.5j, 1.2j, 2.5j...)
        RÈGLE 4: IMPORTANT - jours_travailles doit EXCLURE les jours de congé pris
                 (comptage basé uniquement sur jours réellement travaillés)
        
        Retour: float (avec décimales, max 2.5)
        """
        from decimal import Decimal, ROUND_HALF_UP
        
        if jours_travailles <= 0:
            return 0.0
        
        # Formule: (jours_travaillés / 30) * 2.5
        # Utiliser Decimal pour précision
        jours_decimal = Decimal(str(jours_travailles))
        conges_calcules = (jours_decimal / Decimal('30')) * Decimal('2.5')
        
        # Arrondir à 2 décimales
        conges_arrondis = float(conges_calcules.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        
        # Plafonner à 2.5 jours maximum
        return min(conges_arrondis, 2.5)
    
    def __repr__(self):
        return f"<Conge {self.employe_id} - {self.mois}/{self.annee}: {self.jours_conges_acquis}j>"
