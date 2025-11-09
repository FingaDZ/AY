from pydantic import BaseModel, Field
from typing import Optional, Dict

class PointageBase(BaseModel):
    employe_id: int
    annee: int = Field(..., ge=2000, le=2100)
    mois: int = Field(..., ge=1, le=12)
    
class PointageCreate(PointageBase):
    pass

class PointageJourUpdate(BaseModel):
    numero_jour: int = Field(..., ge=1, le=31)
    valeur: Optional[str] = None  # "Tr", "Ab", "Co", "Ma", "Fe", "Ar" ou None

class PointageUpdate(BaseModel):
    jours: Dict[int, Optional[str]]  # {1: "Tr", 2: "Ab", ...}

class PointageVerrouillage(BaseModel):
    verrouille: bool

class PointageTotaux(BaseModel):
    travailles: int
    absents: int
    conges: int
    maladies: int
    feries: int
    arrets: int
    total_travailles: int  # Tr + Fe

class PointageResponse(PointageBase):
    id: int
    verrouille: bool
    jours: Dict[int, Optional[str]]  # {1: "Tr", 2: "Ab", ...}
    totaux: PointageTotaux
    
    class Config:
        from_attributes = True

class PointageListResponse(BaseModel):
    total: int
    pointages: list[PointageResponse]
