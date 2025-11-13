from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date
from decimal import Decimal

class EmployeBase(BaseModel):
    nom: str = Field(..., min_length=1, max_length=100)
    prenom: str = Field(..., min_length=1, max_length=100)
    date_naissance: date
    lieu_naissance: str = Field(..., min_length=1, max_length=200)
    adresse: str = Field(..., min_length=1, max_length=500)
    mobile: str = Field(..., min_length=1, max_length=20)
    numero_secu_sociale: str = Field(..., min_length=1, max_length=50)
    numero_compte_bancaire: str = Field(..., min_length=1, max_length=50)
    numero_anem: Optional[str] = Field(None, max_length=50)
    situation_familiale: str  # "Célibataire" ou "Marié"
    femme_au_foyer: bool = False
    date_recrutement: date
    date_fin_contrat: Optional[date] = None
    poste_travail: str = Field(..., min_length=1, max_length=100)
    salaire_base: Decimal = Field(..., gt=0)
    prime_nuit_agent_securite: bool = False
    statut_contrat: str = "Actif"  # "Actif" ou "Inactif"
    actif: bool = True  # Soft delete - True par défaut

class EmployeCreate(EmployeBase):
    pass

class EmployeUpdate(BaseModel):
    nom: Optional[str] = Field(None, min_length=1, max_length=100)
    prenom: Optional[str] = Field(None, min_length=1, max_length=100)
    date_naissance: Optional[date] = None
    lieu_naissance: Optional[str] = Field(None, min_length=1, max_length=200)
    adresse: Optional[str] = Field(None, min_length=1, max_length=500)
    mobile: Optional[str] = Field(None, min_length=1, max_length=20)
    numero_secu_sociale: Optional[str] = Field(None, min_length=1, max_length=50)
    numero_compte_bancaire: Optional[str] = Field(None, min_length=1, max_length=50)
    numero_anem: Optional[str] = Field(None, max_length=50)
    situation_familiale: Optional[str] = None
    femme_au_foyer: Optional[bool] = None
    date_recrutement: Optional[date] = None
    date_fin_contrat: Optional[date] = None
    poste_travail: Optional[str] = Field(None, min_length=1, max_length=100)
    salaire_base: Optional[Decimal] = Field(None, gt=0)
    prime_nuit_agent_securite: Optional[bool] = None
    statut_contrat: Optional[str] = None
    actif: Optional[bool] = None  # Permet de réactiver un employé

class EmployeResponse(EmployeBase):
    id: int
    
    class Config:
        from_attributes = True

class EmployeListResponse(BaseModel):
    total: int
    employes: list[EmployeResponse]
