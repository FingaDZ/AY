from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.types import Numeric
from sqlalchemy.orm import relationship
from database import Base

class Mission(Base):
    __tablename__ = "missions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date_mission = Column(Date, nullable=False, index=True)
    chauffeur_id = Column(Integer, ForeignKey("employes.id", ondelete="CASCADE"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="RESTRICT"), nullable=False)
    camion_id = Column(Integer, ForeignKey("camions.id", ondelete="RESTRICT"), nullable=True)  # ⭐ v3.6.0: Camion utilisé
    distance = Column(Numeric(10, 2), nullable=False)  # Distance récupérée du client
    tarif_km = Column(Numeric(10, 2), nullable=False)  # Tarif kilométrique au moment de la mission
    prime_calculee = Column(Numeric(12, 2), nullable=False)  # Distance × Tarif/km
    
    # Relations
    chauffeur = relationship("Employe", back_populates="missions")
    client = relationship("Client")
    camion = relationship("Camion", back_populates="missions")  # ⭐ v3.6.0: Relation camion
    client_details = relationship("MissionClientDetail", back_populates="mission", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Mission {self.id}: Chauffeur {self.chauffeur_id} - {self.date_mission}>"

class Parametre(Base):
    __tablename__ = "parametres"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cle = Column(String(50), unique=True, nullable=False, index=True)
    valeur = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    
    def __repr__(self):
        return f"<Parametre {self.cle}: {self.valeur}>"
