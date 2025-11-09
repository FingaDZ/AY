from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from decimal import Decimal

class CreditBase(BaseModel):
    employe_id: int
    date_octroi: date
    montant_total: Decimal = Field(..., gt=0)
    nombre_mensualites: int = Field(..., gt=0)

class CreditCreate(CreditBase):
    pass

class CreditUpdate(BaseModel):
    nombre_mensualites: Optional[int] = Field(None, gt=0)

class CreditResponse(CreditBase):
    id: int
    montant_mensualite: Decimal
    montant_retenu: Decimal
    montant_restant: Decimal
    statut: str
    
    class Config:
        from_attributes = True

class CreditListResponse(BaseModel):
    total: int
    credits: list[CreditResponse]

class RetenueCreditBase(BaseModel):
    credit_id: int
    mois: int = Field(..., ge=1, le=12)
    annee: int = Field(..., ge=2000)
    montant: Decimal = Field(..., gt=0)
    date_retenue: date

class RetenueCreditResponse(RetenueCreditBase):
    id: int
    
    class Config:
        from_attributes = True

class ProrogationCreditBase(BaseModel):
    credit_id: int
    date_prorogation: date
    mois_initial: int = Field(..., ge=1, le=12)
    annee_initiale: int = Field(..., ge=2000)
    mois_reporte: int = Field(..., ge=1, le=12)
    annee_reportee: int = Field(..., ge=2000)
    motif: str

class ProrogationCreditCreate(ProrogationCreditBase):
    pass

class ProrogationCreditResponse(ProrogationCreditBase):
    id: int
    
    class Config:
        from_attributes = True
