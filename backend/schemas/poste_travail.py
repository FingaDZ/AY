from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PosteTravailBase(BaseModel):
    libelle: str = Field(..., min_length=1, max_length=100, description="Nom du poste")
    est_chauffeur: bool = Field(False, description="Indique si le poste est chauffeur")
    modifiable: bool = Field(True, description="Indique si le poste peut être modifié/supprimé")
    actif: bool = Field(True, description="Statut actif/inactif (soft delete)")

class PosteTravailCreate(PosteTravailBase):
    pass

class PosteTravailUpdate(BaseModel):
    libelle: Optional[str] = Field(None, min_length=1, max_length=100)
    est_chauffeur: Optional[bool] = None
    modifiable: Optional[bool] = None
    actif: Optional[bool] = None

class PosteTravailResponse(PosteTravailBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PosteTravailListResponse(BaseModel):
    total: int
    postes: list[PosteTravailResponse]
