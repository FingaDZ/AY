from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class ParametresSalaire(Base):
    """Paramètres configurables pour le calcul des salaires"""
    __tablename__ = 'parametres_salaire'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Indemnités (montants fixes en DA)
    indemnite_nuisance = Column(Numeric(10, 2), default=1000.00, nullable=False, comment="Indemnité Nuisance (DA)")
    ifsp = Column(Numeric(10, 2), default=500.00, nullable=False, comment="IFSP (DA)")
    iep = Column(Numeric(10, 2), default=300.00, nullable=False, comment="IEP (DA)")
    prime_encouragement = Column(Numeric(10, 2), default=500.00, nullable=False, comment="Prime Encouragement (DA)")
    
    # Primes fixes (DA)
    prime_chauffeur = Column(Numeric(10, 2), default=800.00, nullable=False, comment="Prime chauffeur (DA)")
    prime_nuit_agent_securite = Column(Numeric(10, 2), default=600.00, nullable=False, comment="Prime nuit sécurité (DA)")
    prime_deplacement = Column(Numeric(10, 2), default=400.00, nullable=False, comment="Prime déplacement (DA)")
    prime_femme_foyer = Column(Numeric(10, 2), default=1000.00, nullable=False, comment="Prime femme au foyer (DA)")
    panier = Column(Numeric(10, 2), default=300.00, nullable=False, comment="Panier (DA)")
    prime_transport = Column(Numeric(10, 2), default=500.00, nullable=False, comment="Transport (DA)")
    
    # Retenues (%)
    taux_securite_sociale = Column(Numeric(5, 2), default=9.00, nullable=False, comment="Retenue Sécurité Sociale (%)")
    
    # Options de calcul
    activer_heures_supp = Column(Boolean, default=True, nullable=False, comment="Activer calcul heures supplémentaires")
    activer_irg_proratise = Column(Boolean, default=True, nullable=False, comment="Proratiser IRG selon jours travaillés")
    mode_calcul_conges = Column(String(20), default='proratise', nullable=False, comment="Mode calcul congés: complet|proratise|hybride")
    
    # Métadonnées
    date_modification = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'indemnite_nuisance': float(self.indemnite_nuisance),
            'ifsp': float(self.ifsp),
            'iep': float(self.iep),
            'prime_encouragement': float(self.prime_encouragement),
            'prime_chauffeur': float(self.prime_chauffeur),
            'prime_nuit_agent_securite': float(self.prime_nuit_agent_securite),
            'prime_deplacement': float(self.prime_deplacement),
            'prime_femme_foyer': float(self.prime_femme_foyer),
            'panier': float(self.panier),
            'prime_transport': float(self.prime_transport),
            'taux_securite_sociale': float(self.taux_securite_sociale),
            'activer_heures_supp': self.activer_heures_supp,
            'activer_irg_proratise': self.activer_irg_proratise,
            'mode_calcul_conges': self.mode_calcul_conges,
        }
