from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class ParametresSalaire(Base):
    """Paramètres configurables pour le calcul des salaires"""
    __tablename__ = 'parametres_salaire'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Indemnités (%)
    taux_in = Column(Numeric(5, 2), default=5.00, nullable=False, comment="Indemnité Nuisance (%)")
    taux_ifsp = Column(Numeric(5, 2), default=5.00, nullable=False, comment="IFSP (%)")
    taux_iep_par_an = Column(Numeric(5, 2), default=1.00, nullable=False, comment="IEP par année d'ancienneté (%)")
    taux_prime_encouragement = Column(Numeric(5, 2), default=10.00, nullable=False, comment="Prime Encouragement (%)")
    anciennete_min_encouragement = Column(Integer, default=1, nullable=False, comment="Ancienneté min pour prime encouragement (années)")
    
    # Primes fixes (DA)
    prime_chauffeur_jour = Column(Numeric(10, 2), default=100.00, nullable=False, comment="Prime chauffeur par jour (DA)")
    prime_nuit_securite = Column(Numeric(10, 2), default=750.00, nullable=False, comment="Prime nuit sécurité mensuelle (DA)")
    panier_jour = Column(Numeric(10, 2), default=100.00, nullable=False, comment="Panier par jour (DA)")
    transport_jour = Column(Numeric(10, 2), default=100.00, nullable=False, comment="Transport par jour (DA)")
    prime_femme_foyer = Column(Numeric(10, 2), default=1000.00, nullable=False, comment="Prime femme au foyer (DA)")
    
    # Retenues (%)
    taux_securite_sociale = Column(Numeric(5, 2), default=9.00, nullable=False, comment="Retenue Sécurité Sociale (%)")
    
    # Options de calcul
    calculer_heures_supp = Column(Boolean, default=True, nullable=False, comment="Activer calcul heures supplémentaires")
    mode_calcul_conges = Column(String(20), default='complet', nullable=False, comment="Mode calcul congés: complet|proratise|hybride")
    jours_ouvrables_base = Column(Integer, default=26, nullable=False, comment="Nombre de jours ouvrables par mois")
    
    # IRG
    irg_proratise = Column(Boolean, default=True, nullable=False, comment="Proratiser IRG selon jours travaillés")
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
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
