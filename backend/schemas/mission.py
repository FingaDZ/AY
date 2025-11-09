from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from decimal import Decimal

class MissionBase(BaseModel):
    date_mission: date
    chauffeur_id: int
    client_id: int

class MissionCreate(MissionBase):
    pass

class MissionResponse(MissionBase):
    id: int
    distance: Decimal
    tarif_km: Decimal
    prime_calculee: Decimal
    
    class Config:
        from_attributes = True

class MissionListResponse(BaseModel):
    total: int
    missions: list[MissionResponse]

class MissionPrimeMensuelle(BaseModel):
    chauffeur_id: int
    chauffeur_nom: str
    chauffeur_prenom: str
    total_prime: Decimal
    nombre_missions: int

class ParametreBase(BaseModel):
    cle: str
    valeur: str
    description: Optional[str] = None

class ParametreCreate(ParametreBase):
    pass

class ParametreUpdate(BaseModel):
    valeur: str
    description: Optional[str] = None

class ParametreResponse(ParametreBase):
    id: int
    
    class Config:
        from_attributes = True
