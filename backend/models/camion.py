"""
Modèle Camion - Gestion du parc de véhicules
"""
from sqlalchemy import Column, Integer, String, Boolean, Date, Text
from sqlalchemy.orm import relationship
from database import Base


class Camion(Base):
    """Modèle pour la gestion des camions/véhicules"""
    __tablename__ = "camions"
    
    id = Column(Integer, primary_key=True, index=True)
    marque = Column(String(50), nullable=False, comment="Marque du véhicule (ex: HYUNDAI)")
    modele = Column(String(50), nullable=False, comment="Modèle du véhicule (ex: HD35)")
    immatriculation = Column(String(20), unique=True, nullable=False, index=True, 
                            comment="Numéro d'immatriculation unique (ex: 152455-109-43)")
    annee_fabrication = Column(Integer, comment="Année de fabrication du véhicule")
    capacite_charge = Column(Integer, comment="Capacité de charge en kilogrammes")
    actif = Column(Boolean, default=True, nullable=False, comment="Véhicule actif dans le parc")
    date_acquisition = Column(Date, comment="Date d'acquisition du véhicule")
    date_revision = Column(Date, comment="Date de la prochaine révision/contrôle technique")
    notes = Column(Text, comment="Notes diverses (historique, incidents, etc.)")
    
    # Relations
    missions = relationship("Mission", back_populates="camion")
    
    def __repr__(self):
        return f"<Camion(id={self.id}, marque={self.marque}, modele={self.modele}, " \
               f"immatriculation={self.immatriculation})>"
    
    def to_dict(self):
        """Convertir en dictionnaire pour API"""
        return {
            "id": self.id,
            "marque": self.marque,
            "modele": self.modele,
            "immatriculation": self.immatriculation,
            "annee_fabrication": self.annee_fabrication,
            "capacite_charge": self.capacite_charge,
            "actif": self.actif,
            "date_acquisition": str(self.date_acquisition) if self.date_acquisition else None,
            "date_revision": str(self.date_revision) if self.date_revision else None,
            "notes": self.notes,
            "nombre_missions": len(self.missions) if self.missions else 0
        }
