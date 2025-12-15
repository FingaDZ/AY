from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from database import Base

class MissionClientDetail(Base):
    __tablename__ = "mission_client_details"

    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id", ondelete="CASCADE"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    
    # v3.6.0: Distance kilométrique pour calcul multi-clients
    distance_km = Column(Numeric(10, 2), nullable=True, comment="Distance en km pour ce client")
    
    montant_encaisse = Column(Numeric(10, 2), default=0.0)
    statut_versement = Column(String(20), default="EN_ATTENTE") # EN_ATTENTE, VERSE, VALIDE
    observations = Column(Text, nullable=True)

    # Relationships
    mission = relationship("Mission", back_populates="client_details")
    client = relationship("Client")
    logistics_movements = relationship("MissionLogisticsMovement", back_populates="client_detail", cascade="all, delete-orphan")

class MissionLogisticsMovement(Base):
    __tablename__ = "mission_logistics_movements"

    id = Column(Integer, primary_key=True, index=True)
    mission_client_detail_id = Column(Integer, ForeignKey("mission_client_details.id", ondelete="CASCADE"), nullable=False)
    logistics_type_id = Column(Integer, ForeignKey("logistics_types.id"), nullable=False)
    
    quantity_out = Column(Integer, default=0) # Livré
    quantity_in = Column(Integer, default=0)  # Récupéré

    # Relationships
    client_detail = relationship("MissionClientDetail", back_populates="logistics_movements")
    logistics_type = relationship("LogisticsType")
