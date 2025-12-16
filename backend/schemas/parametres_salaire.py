"""Schémas Pydantic pour les paramètres de salaire"""

from pydantic import BaseModel, Field
from typing import Optional


class ParametresSalaireBase(BaseModel):
    """Schéma de base pour les paramètres de salaire"""
    
    # Indemnités (%)
    taux_in: float = Field(default=5.00, ge=0, le=100, description="Indemnité Nuisance (%)")
    taux_ifsp: float = Field(default=5.00, ge=0, le=100, description="IFSP (%)")
    taux_iep_par_an: float = Field(default=1.00, ge=0, le=100, description="IEP par année (%)")
    taux_prime_encouragement: float = Field(default=10.00, ge=0, le=100, description="Prime Encouragement (%)")
    anciennete_min_encouragement: int = Field(default=1, ge=0, description="Ancienneté min (années)")
    
    # Primes fixes (DA)
    prime_chauffeur_jour: float = Field(default=100.00, ge=0, description="Prime chauffeur/jour (DA)")
    prime_nuit_securite: float = Field(default=750.00, ge=0, description="Prime nuit/mois (DA)")
    panier_jour: float = Field(default=100.00, ge=0, description="Panier/jour (DA)")
    transport_jour: float = Field(default=100.00, ge=0, description="Transport/jour (DA)")
    prime_femme_foyer: float = Field(default=1000.00, ge=0, description="Prime femme foyer (DA)")
    
    # Retenues (%)
    taux_securite_sociale: float = Field(default=9.00, ge=0, le=100, description="Retenue SS (%)")
    
    # Options
    calculer_heures_supp: bool = Field(default=True, description="Calculer heures supplémentaires")
    mode_calcul_conges: str = Field(default="complet", description="Mode congés: complet|proratise|hybride")
    jours_ouvrables_base: int = Field(default=30, ge=1, le=31, description="Jours ouvrables/mois")  # v3.5.3: 30 jours au lieu de 26
    irg_proratise: bool = Field(default=True, description="Proratiser IRG")
    
    # v3.6.0: Kilomètres multi-clients
    km_supplementaire_par_client: int = Field(default=10, ge=0, description="Km supplémentaires par client additionnel")


class ParametresSalaireCreate(ParametresSalaireBase):
    """Schéma pour créer des paramètres"""
    pass


class ParametresSalaireUpdate(ParametresSalaireBase):
    """Schéma pour mettre à jour des paramètres"""
    pass


class ParametresSalaireResponse(ParametresSalaireBase):
    """Schéma de réponse avec ID"""
    id: int
    
    class Config:
        from_attributes = True


class IRGBaremeBase(BaseModel):
    """Schéma de base pour une tranche IRG"""
    salaire_min: float = Field(description="Salaire minimum (DA)")
    salaire_max: Optional[float] = Field(default=None, description="Salaire maximum (DA)")
    irg: float = Field(description="Montant IRG (DA)")
    actif: bool = Field(default=True)
    

class IRGBaremeCreate(IRGBaremeBase):
    """Schéma pour créer une tranche IRG"""
    pass


class IRGBaremeResponse(IRGBaremeBase):
    """Schéma de réponse IRG"""
    id: int
    
    class Config:
        from_attributes = True


class ReportAvanceCreditBase(BaseModel):
    """Schéma de base pour un report"""
    employe_id: int
    type: str = Field(description="'avance' ou 'credit'")
    montant_reporte: float
    mois_destination: int = Field(ge=1, le=12)
    annee_destination: int
    motif: Optional[str] = None
    

class ReportAvanceCreditCreate(ReportAvanceCreditBase):
    """Schéma pour créer un report manuel"""
    avance_id: Optional[int] = None
    credit_id: Optional[int] = None


class ReportAvanceCreditResponse(ReportAvanceCreditBase):
    """Schéma de réponse report"""
    id: int
    avance_id: Optional[int]
    credit_id: Optional[int]
    mois_origine: int
    annee_origine: int
    automatique: bool
    traite: bool
    
    class Config:
        from_attributes = True
