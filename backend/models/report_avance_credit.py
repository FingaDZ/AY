from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class ReportAvanceCredit(Base):
    """Gestion des reports d'avances et crédits (automatique ou manuel)"""
    __tablename__ = 'reports_avance_credit'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Identification
    employe_id = Column(Integer, ForeignKey('employes.id'), nullable=False, index=True)
    type = Column(String(20), nullable=False, comment="Type: 'avance' ou 'credit'")
    
    # Références aux entités d'origine
    avance_id = Column(Integer, ForeignKey('avances.id'), nullable=True)
    credit_id = Column(Integer, ForeignKey('credits.id'), nullable=True)
    
    # Montants
    montant_reporte = Column(Numeric(10, 2), nullable=False, comment="Montant reporté (DA)")
    
    # Périodes
    mois_origine = Column(Integer, nullable=False, comment="Mois où le report a été créé")
    annee_origine = Column(Integer, nullable=False, comment="Année où le report a été créé")
    mois_destination = Column(Integer, nullable=False, index=True, comment="Mois où appliquer le report")
    annee_destination = Column(Integer, nullable=False, index=True, comment="Année où appliquer le report")
    
    # Contexte
    motif = Column(Text, nullable=True, comment="Raison du report (obligatoire si manuel)")
    automatique = Column(Boolean, default=False, nullable=False, comment="Report automatique (salaire insuffisant) ou manuel")
    
    # Suivi
    traite = Column(Boolean, default=False, nullable=False, index=True, comment="Report déjà appliqué dans un calcul de salaire")
    date_traitement = Column(DateTime, nullable=True, comment="Quand le report a été appliqué")
    salaire_id = Column(Integer, ForeignKey('salaires.id'), nullable=True, comment="Salaire où le report a été appliqué")
    
    # Audit
    cree_par = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    
    # Relations
    employe = relationship("Employe", foreign_keys=[employe_id])
    avance = relationship("Avance", foreign_keys=[avance_id])
    credit = relationship("Credit", foreign_keys=[credit_id])
    createur = relationship("User", foreign_keys=[cree_par])
    
    def __repr__(self):
        return f"<ReportAvanceCredit(employe_id={self.employe_id}, type={self.type}, montant={self.montant_reporte}, traite={self.traite})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'employe_id': self.employe_id,
            'type': self.type,
            'avance_id': self.avance_id,
            'credit_id': self.credit_id,
            'montant_reporte': float(self.montant_reporte),
            'mois_origine': self.mois_origine,
            'annee_origine': self.annee_origine,
            'mois_destination': self.mois_destination,
            'annee_destination': self.annee_destination,
            'motif': self.motif,
            'automatique': self.automatique,
            'traite': self.traite,
            'date_traitement': self.date_traitement.isoformat() if self.date_traitement else None,
            'cree_par': self.cree_par,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
