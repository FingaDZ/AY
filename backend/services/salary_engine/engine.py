from decimal import Decimal
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
import logging

from .tax_provider import TaxProvider
from models import Employe, Salaire, ParametresSalaire

logger = logging.getLogger(__name__)

class SalaryEngine:
    """
    Nouveau moteur de calcul de paie (V3).
    Conçu pour être modulaire, testable et basé sur la BDD.
    """
    def __init__(self, db: Session):
        self.db = db
        self.tax_provider = TaxProvider(db)
        self.params = self._load_params()

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
        Retourne un dictionnaire complet des valeurs calculées.
        """
        employee = self.db.query(Employe).filter(Employe.id == employee_id).first()
        if not employee:
            raise ValueError(f"Employé {employee_id} introuvable")

        # 1. Base (Salaire Base, Jours travaillés/Absences)
        # TODO: Intégrer AttendanceProvider
        worked_days = 30 # Placeholder
        base_salary = employee.salaire_base # Placeholder logic

        # 2. Primes (Nuisance, IEP, etc.)
        # TODO: Intégrer BonusProvider
        allowances = Decimal(0)

        # 3. Brut Cotisable
        cotisable_salary = base_salary + allowances # Simplification

        # 4. Déductions Sociales (SS)
        ss_deduction = cotisable_salary * (self.params.taux_securite_sociale / Decimal(100))

        # 5. Imposable
        taxable_salary = cotisable_salary - ss_deduction

        # 6. IRG (Via TaxProvider)
        irg = self.tax_provider.calculate_irg(taxable_salary)

        # 7. Net
        net_salary = taxable_salary - irg

        return {
            "employee_id": employee.id,
            "year": year,
            "month": month,
            "base_salary": base_salary,
            "cotisable_salary": cotisable_salary,
            "ss_deduction": ss_deduction,
            "taxable_salary": taxable_salary,
            "irg": irg,
            "net_salary": net_salary
        }
