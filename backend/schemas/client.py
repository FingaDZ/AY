from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

class ClientBase(BaseModel):
    nom: str = Field(..., min_length=1, max_length=100)
    prenom: str = Field(..., min_length=1, max_length=100)
    distance: Decimal = Field(..., gt=0, description="Distance en kilomètres")
    telephone: str = Field(..., min_length=1, max_length=20)

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    nom: Optional[str] = Field(None, min_length=1, max_length=100)
    prenom: Optional[str] = Field(None, min_length=1, max_length=100)
    distance: Optional[Decimal] = Field(None, gt=0)
    telephone: Optional[str] = Field(None, min_length=1, max_length=20)

class ClientResponse(ClientBase):
    id: int
    
    class Config:
        from_attributes = True

class ClientListResponse(BaseModel):
    total: int
    clients: list[ClientResponse]
