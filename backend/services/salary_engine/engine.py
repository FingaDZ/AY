from decimal import Decimal
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
import logging

from .base_provider import BaseSalaryProvider
from .bonus_provider import BonusProvider
from .deduction_provider import DeductionProvider
from .tax_provider import TaxProvider
from models import Employe, Salaire, ParametresSalaire, Pointage # Added Pointage

logger = logging.getLogger(__name__)

class SalaryEngine:
    """
    Nouveau moteur de calcul de paie (V3).
    Conçu pour être modulaire, testable et basé sur la BDD.
    """
    def __init__(self, db: Session):
        self.db = db
        self.params = self._load_params()
        
        # Initialize Providers
        self.base_provider = BaseSalaryProvider(db, self.params)
        self.bonus_provider = BonusProvider(db, self.params)
        self.deduction_provider = DeductionProvider(db, self.params)
        self.tax_provider = TaxProvider(db)

    def _load_params(self) -> ParametresSalaire:
        params = self.db.query(ParametresSalaire).first()
        if not params:
            params = ParametresSalaire()
            self.db.add(params)
            self.db.commit()
        return params

    def calculate_for_employee(self, employee_id: int, year: int, month: int) -> Dict:
        """
        Orchestre le calcul pour un employé spécifique.
        """
        employee = self.db.query(Employe).filter(Employe.id == employee_id).first()
        if not employee:
            raise ValueError(f"Employé {employee_id} introuvable")

        # 0. Récupérer Pointage (Données variables)
        pointage = self.db.query(Pointage).filter(
            Pointage.employe_id == employee_id,
            Pointage.annee == year,
            Pointage.mois == month
        ).first()
        
        if not pointage:
             # Fallback ou erreur? Pour l'instant erreur comme avant
             raise ValueError(f"Absence de pointage pour {employee.nom} {employee.prenom}")
             
        pointage_totals = pointage.calculer_totaux()
        worked_days = pointage_totals.get("total_travailles", 0)
        # TODO: Gestion des congés via un module dédié ou input manuel dans le futur.
        # Pour l'instant on suppose 0 congés sauf si transmis
        leave_days = 0 

        # 1. Base Salary & Hours
        base_data = self.base_provider.calculate_base_details(
            employee, year, month, worked_days, leave_days
        )
        
        # 2. Bonuses (Primes)
        bonus_data = self.bonus_provider.calculate_bonuses(
            employee, year, month, 
            base_data["salaire_base"], 
            base_data["jours_travailles"]
        )
        
        # 3. Calcul Cotisable (Base proratisée + HS + Primes Cotisables)
        # Quelles primes sont cotisables ? 
        # En général: Nuisance, IFSP, IEP, Encouragement, Chauffeur, Nuit, Déplacement, Variable, Objectif 
        # Panier/Transport/FemmeFoyer NON cotisables
        
        # On définit explicitement les clées cotisables
        cotisable_keys = [
            "indemnite_nuisance", "ifsp", "iep", "prime_encouragement", 
            "prime_chauffeur", "prime_nuit_agent_securite", "prime_deplacement"
        ]
        total_primes_cotisables = sum(bonus_data.get(k, Decimal(0)) for k in cotisable_keys)
        
        # Ajouter primes manuelles (Si passées en args? Pour l'instant 0)
        prime_objectif = Decimal(0)
        prime_variable = Decimal(0)
        
        salaire_cotisable = (
            base_data["salaire_base_proratis"] + 
            base_data["heures_supplementaires"] + 
            total_primes_cotisables + 
            prime_objectif + 
            prime_variable
        )

        # 4. SS Deduction
        ss_deduction = salaire_cotisable * (self.params.taux_securite_sociale / Decimal(100))

        # 5. Imposable
        # Imposable = Cotisable - SS + Primes Non Cotisables Imposables (Panier + Transport) - Non Imposables
        # Panier/Transport sont imposables
        salaire_imposable = (
            salaire_cotisable - 
            ss_deduction + 
            bonus_data.get("panier", Decimal(0)) + 
            bonus_data.get("prime_transport", Decimal(0))
        )
        
        # 6. IRG
        # Attention: Prorata IRG logic (Si nécessaire, voir old calculator. Pour l'instant basic)
        irg = self.tax_provider.calculate_irg(salaire_imposable)
        
        # 7. Deductions (Avances/Credits)
        deduction_data = self.deduction_provider.calculate_deductions(employee_id, year, month)
        
        # 8. Net
        # Net = Imposable - IRG - Avances - Credits + Non Imposable (Femme Foyer)
        salaire_net = (
            salaire_imposable - 
            irg - 
            deduction_data["total_avances"] - 
            deduction_data["retenue_credit"] + 
            bonus_data.get("prime_femme_foyer", Decimal(0))
        )

        # Assembly Result
        return {
            "employe_id": employee.id,
            "annee": year,
            "mois": month,
            **base_data,
            **bonus_data,
            "prime_objectif": prime_objectif,
            "prime_variable": prime_variable,
            "salaire_cotisable": salaire_cotisable,
            "retenue_securite_sociale": ss_deduction,
            "salaire_imposable": salaire_imposable,
            "irg": irg,
            **deduction_data,
            "salaire_net": salaire_net,
            
            # Metadata util
            "employe_nom": employee.nom,
            "employe_prenom": employee.prenom,
            "employe_id": employee.id
        }
