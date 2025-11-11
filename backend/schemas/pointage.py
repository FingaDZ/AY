from pydantic import BaseModel, Field
from typing import Optional, Dict

class PointageBase(BaseModel):
    employe_id: int
    annee: int = Field(..., ge=2000, le=2100)
    mois: int = Field(..., ge=1, le=12)
    
class PointageCreate(PointageBase):
    jour_01: Optional[int] = None
    jour_02: Optional[int] = None
    jour_03: Optional[int] = None
    jour_04: Optional[int] = None
    jour_05: Optional[int] = None
    jour_06: Optional[int] = None
    jour_07: Optional[int] = None
    jour_08: Optional[int] = None
    jour_09: Optional[int] = None
    jour_10: Optional[int] = None
    jour_11: Optional[int] = None
    jour_12: Optional[int] = None
    jour_13: Optional[int] = None
    jour_14: Optional[int] = None
    jour_15: Optional[int] = None
    jour_16: Optional[int] = None
    jour_17: Optional[int] = None
    jour_18: Optional[int] = None
    jour_19: Optional[int] = None
    jour_20: Optional[int] = None
    jour_21: Optional[int] = None
    jour_22: Optional[int] = None
    jour_23: Optional[int] = None
    jour_24: Optional[int] = None
    jour_25: Optional[int] = None
    jour_26: Optional[int] = None
    jour_27: Optional[int] = None
    jour_28: Optional[int] = None
    jour_29: Optional[int] = None
    jour_30: Optional[int] = None
    jour_31: Optional[int] = None

class PointageJourUpdate(BaseModel):
    numero_jour: int = Field(..., ge=1, le=31)
    valeur: Optional[int] = None  # 0 ou 1

class PointageUpdate(BaseModel):
    jours: Dict[int, Optional[int]]  # {1: 1, 2: 0, ...}

class PointageVerrouillage(BaseModel):
    verrouille: bool

class PointageTotaux(BaseModel):
    total_travailles: int  # Total des jours où valeur = 1 (Travaillé + Férié)

class PointageResponse(PointageBase):
    id: int
    verrouille: bool
    jours: Dict[int, Optional[int]]  # {1: 1, 2: 0, ...}
    totaux: PointageTotaux
    
    class Config:
        from_attributes = True

class PointageListResponse(BaseModel):
    total: int
    pointages: list[PointageResponse]
