from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from decimal import Decimal

class AvanceBase(BaseModel):
    employe_id: int
    date_avance: date
    montant: Decimal = Field(..., gt=0)
    mois_deduction: int = Field(..., ge=1, le=12)
    annee_deduction: int = Field(..., ge=2000)
    motif: Optional[str] = None

class AvanceCreate(AvanceBase):
    pass

class AvanceUpdate(BaseModel):
    date_avance: Optional[date] = None
    montant: Optional[Decimal] = Field(None, gt=0)
    mois_deduction: Optional[int] = Field(None, ge=1, le=12)
    annee_deduction: Optional[int] = Field(None, ge=2000)
    motif: Optional[str] = None

class AvanceResponse(AvanceBase):
    id: int
    
    class Config:
        from_attributes = True

class AvanceListResponse(BaseModel):
    total: int
    avances: list[AvanceResponse]

class AvanceTotalMensuel(BaseModel):
    employe_id: int
    employe_nom: str
    employe_prenom: str
    mois: int
    annee: int
    total_avances: Decimal
    nombre_avances: int
