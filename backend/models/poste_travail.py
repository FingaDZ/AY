from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy.sql import func
from database import Base

class PosteTravail(Base):
    __tablename__ = "postes_travail"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    libelle = Column(String(100), unique=True, nullable=False, index=True)
    est_chauffeur = Column(Boolean, default=False, nullable=False, index=True)
    modifiable = Column(Boolean, default=True, nullable=False)
    actif = Column(Boolean, default=True, nullable=False, index=True)
    
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    def __repr__(self):
        return f"<PosteTravail {self.id}: {self.libelle}>"
