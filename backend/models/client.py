from sqlalchemy import Column, Integer, String
from sqlalchemy.types import Numeric
from database import Base

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nom = Column(String(100), nullable=False, index=True)
    prenom = Column(String(100), nullable=False, index=True)
    distance = Column(Numeric(10, 2), nullable=False)  # Distance en km
    telephone = Column(String(20), nullable=False)
    tarif_km = Column(Numeric(10, 2), nullable=False, default=3.00)  # Tarif kilométrique (DA/km)
    
    def __repr__(self):
        return f"<Client {self.id}: {self.prenom} {self.nom} - {self.distance}km @ {self.tarif_km}DA/km>"
