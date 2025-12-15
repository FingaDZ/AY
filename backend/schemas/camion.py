"""
Schémas Pydantic pour les Camions
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date
import re


class CamionBase(BaseModel):
    """Schéma de base pour un camion"""
    marque: str = Field(..., min_length=1, max_length=50, description="Marque du véhicule")
    modele: str = Field(..., min_length=1, max_length=50, description="Modèle du véhicule")
    immatriculation: str = Field(..., min_length=1, max_length=20, description="Immatriculation unique")
    annee_fabrication: Optional[int] = Field(None, ge=1900, le=2100, description="Année de fabrication")
    capacite_charge: Optional[int] = Field(None, ge=0, description="Capacité de charge en kg")
    actif: bool = Field(True, description="Véhicule actif")
    date_acquisition: Optional[date] = Field(None, description="Date d'acquisition")
    date_revision: Optional[date] = Field(None, description="Date prochaine révision")
    notes: Optional[str] = Field(None, description="Notes diverses")

    @field_validator('immatriculation')
    @classmethod
    def validate_immatriculation(cls, v: str) -> str:
        """Valider le format de l'immatriculation"""
        # Nettoyer les espaces
        v = v.strip().upper()
        
        # Vérifier format algérien standard: XXXXXX-XXX-XX
        # Accepter aussi d'autres formats (flexible)
        if not re.match(r'^[A-Z0-9\-]+$', v):
            raise ValueError("L'immatriculation ne doit contenir que des lettres, chiffres et tirets")
        
        return v


class CamionCreate(CamionBase):
    """Schéma pour créer un camion"""
    pass


class CamionUpdate(BaseModel):
    """Schéma pour mettre à jour un camion (tous les champs optionnels)"""
    marque: Optional[str] = Field(None, min_length=1, max_length=50)
    modele: Optional[str] = Field(None, min_length=1, max_length=50)
    immatriculation: Optional[str] = Field(None, min_length=1, max_length=20)
    annee_fabrication: Optional[int] = Field(None, ge=1900, le=2100)
    capacite_charge: Optional[int] = Field(None, ge=0)
    actif: Optional[bool] = None
    date_acquisition: Optional[date] = None
    date_revision: Optional[date] = None
    notes: Optional[str] = None

    @field_validator('immatriculation')
    @classmethod
    def validate_immatriculation(cls, v: Optional[str]) -> Optional[str]:
        """Valider le format de l'immatriculation si fourni"""
        if v is None:
            return v
        
        v = v.strip().upper()
        if not re.match(r'^[A-Z0-9\-]+$', v):
            raise ValueError("L'immatriculation ne doit contenir que des lettres, chiffres et tirets")
        
        return v


class CamionResponse(CamionBase):
    """Schéma de réponse pour un camion"""
    id: int
    nombre_missions: int = Field(0, description="Nombre de missions effectuées avec ce camion")
    
    class Config:
        from_attributes = True


class CamionList(BaseModel):
    """Liste de camions avec pagination"""
    total: int
    camions: list[CamionResponse]
    actifs: int = Field(description="Nombre de camions actifs")
    inactifs: int = Field(description="Nombre de camions inactifs")
