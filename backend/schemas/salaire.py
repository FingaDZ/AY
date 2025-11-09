from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import date
from decimal import Decimal

class SalaireCalculBase(BaseModel):
    employe_id: int
    annee: int = Field(..., ge=2000)
    mois: int = Field(..., ge=1, le=12)
    
    # Jours
    jours_travailles: int
    jours_ouvrables: int
    
    # Éléments du salaire cotisable
    salaire_base_proratis: Decimal
    heures_supplementaires: Decimal = Decimal(0)
    indemnite_nuisance: Decimal = Decimal(0)  # 5%
    ifsp: Decimal = Decimal(0)  # 5%
    iep: Decimal = Decimal(0)  # Selon ancienneté
    prime_encouragement: Decimal = Decimal(0)  # 10% si > 1 an
    prime_chauffeur: Decimal = Decimal(0)  # 100 DA × jours travaillés
    prime_deplacement: Decimal = Decimal(0)  # Missions
    prime_objectif: Decimal = Decimal(0)
    prime_variable: Decimal = Decimal(0)
    
    # Salaire cotisable
    salaire_cotisable: Decimal
    
    # Retenues sur salaire cotisable
    retenue_securite_sociale: Decimal  # 9%
    
    # Éléments supplémentaires
    panier: Decimal = Decimal(0)  # 100 DA × jours
    prime_transport: Decimal = Decimal(0)  # 100 DA × jours
    
    # IRG
    irg: Decimal
    
    # Salaire imposable
    salaire_imposable: Decimal
    
    # Déductions finales
    total_avances: Decimal = Decimal(0)
    retenue_credit: Decimal = Decimal(0)
    
    # Prime finale
    prime_femme_foyer: Decimal = Decimal(0)  # 1000 DA si applicable
    
    # Salaire net
    salaire_net: Decimal

class SalaireCalculCreate(BaseModel):
    employe_id: int
    annee: int = Field(..., ge=2000)
    mois: int = Field(..., ge=1, le=12)
    jours_supplementaires: int = Field(default=0, ge=0)
    prime_objectif: Decimal = Field(default=Decimal(0), ge=0)
    prime_variable: Decimal = Field(default=Decimal(0), ge=0)

class SalaireCalculResponse(SalaireCalculBase):
    id: int
    employe_nom: str
    employe_prenom: str
    employe_poste: str
    
    class Config:
        from_attributes = True

class SalaireCalculListResponse(BaseModel):
    total: int
    salaires: list[SalaireCalculResponse]
    totaux: Dict[str, Decimal]  # Totaux globaux

class SalaireDetailResponse(BaseModel):
    """Détail complet d'un salaire pour affichage/rapport"""
    # Informations employé
    employe_id: int
    nom: str
    prenom: str
    numero_compte: str
    date_naissance: date
    lieu_naissance: str
    situation_familiale: str
    telephone: str
    date_recrutement: date
    date_fin_contrat: Optional[date]
    numero_secu_sociale: str
    poste_travail: str
    
    # Période
    mois: int
    annee: int
    
    # Détails calcul
    details: SalaireCalculResponse
