from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from decimal import Decimal

class MissionBase(BaseModel):
    date_mission: date
    chauffeur_id: int
    client_id: int

class MissionLogisticsMovementBase(BaseModel):
    logistics_type_id: int
    quantity_out: int = 0
    quantity_in: int = 0

class MissionLogisticsMovementCreate(MissionLogisticsMovementBase):
    pass

class MissionLogisticsMovementResponse(MissionLogisticsMovementBase):
    id: int
    logistics_type_name: Optional[str] = None

    class Config:
        from_attributes = True

class MissionClientDetailBase(BaseModel):
    client_id: int
    distance_km: Optional[Decimal] = None  # ⭐ v3.6.0: Distance pour calcul multi-clients
    montant_encaisse: Decimal = Decimal('0.00')
    statut_versement: str = "EN_ATTENTE"
    observations: Optional[str] = None

class MissionClientDetailCreate(MissionClientDetailBase):
    logistics: list[MissionLogisticsMovementCreate] = []

class MissionClientDetailResponse(MissionClientDetailBase):
    id: int
    distance_km: Optional[Decimal] = None  # ⭐ v3.6.0: Distance pour calcul multi-clients
    client_name: Optional[str] = None
    logistics_movements: list[MissionLogisticsMovementResponse] = []

    class Config:
        from_attributes = True

class MissionCreate(BaseModel):
    date_mission: date
    chauffeur_id: int
    camion_id: Optional[int] = None  # ⭐ v3.6.0: Camion assigné à la mission
    # Legacy field for backward compatibility, optional if clients list is provided
    client_id: Optional[int] = None 
    clients: list[MissionClientDetailCreate] = []

class MissionResponse(MissionBase):
    id: int
    camion_id: Optional[int] = None  # ⭐ v3.6.0: Camion assigné
    distance: Decimal
    tarif_km: Decimal
    prime_calculee: Decimal
    client_details: list[MissionClientDetailResponse] = []
    
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
