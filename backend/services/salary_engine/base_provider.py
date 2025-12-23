from decimal import Decimal
from typing import Dict, Tuple
from sqlalchemy.orm import Session
import calendar
from datetime import date

from models import Employe, ParametresSalaire, Pointage

class BaseSalaryProvider:
    """
    Gère le calcul du salaire de base, des heures travaillées et des heures supplémentaires.
    """
    def __init__(self, db: Session, params: ParametresSalaire):
        self.db = db
        self.params = params

    def calculate_base_details(self, employee: Employe, year: int, month: int, 
                             worked_days: int, leave_days: int) -> Dict:
        """
        Calcule les détails du salaire de base.
        """
        # 1. Jours Ouvrables Travaillés (estimé pour Heures Supp)
        business_days_worked = self._calculate_business_days_worked(year, month, worked_days)
        
        # 2. Salaire de Base Proratisé (selon mode congés)
        prorated_base = self._calculate_prorated_base(employee.salaire_base, worked_days, leave_days)

        # 3. Heures Supplémentaires
        overtime_amount = self._calculate_overtime(employee.salaire_base, business_days_worked)

        return {
            "salaire_base": employee.salaire_base,
            "salaire_base_proratis": prorated_base,
            "jours_travailles": worked_days,
            "jours_conges": leave_days,
            "jours_ouvrables_travailles": business_days_worked,
            "heures_supplementaires": overtime_amount
        }

    def _calculate_business_days_worked(self, year: int, month: int, total_worked_days: int) -> int:
        """
        Calcule les jours ouvrables travaillés (excluant vendredis/fériés grosso modo).
        Logique reprise de l'ancien calculator: Total - Vendredis.
        """
        _, days_in_month = calendar.monthrange(year, month)
        fridays_count = sum(1 for day in range(1, days_in_month + 1) 
                          if calendar.weekday(year, month, day) == 4) # 4 = Vendredi
        
        return max(0, total_worked_days - fridays_count)

    def _calculate_prorated_base(self, base_salary: Decimal, worked_days: int, leave_days: int) -> Decimal:
        """
        Calcule le salaire de base selon le mode de gestion des congés.
        """
        mode = self.params.mode_calcul_conges or "complet"
        
        if mode == "complet":
            # Salaire complet basé sur 30 jours (jours_travailles + jours_conges)
            total_days = worked_days + leave_days
            payable_days = min(30, total_days) if total_days > 30 else total_days
            return base_salary * Decimal(payable_days) / Decimal(30)
            
        elif mode == "proratise":
            # Deux parts séparées: Travail / 30 + Congés / 30
            part_work = base_salary * Decimal(worked_days) / Decimal(30)
            part_leave = base_salary * Decimal(leave_days) / Decimal(30)
            return part_work + part_leave
            
        elif mode == "hybride":
            # Salaire sur jours ouvrables base (ex: 26)
            base_days = getattr(self.params, 'jours_ouvrables_base', 26) or 26
            part_work = base_salary * Decimal(worked_days) / Decimal(base_days)
            part_leave = base_salary * Decimal(leave_days) / Decimal(base_days)
            return part_work + part_leave
        
        return Decimal(0)

    def _calculate_overtime(self, base_salary: Decimal, business_days_worked: int) -> Decimal:
        """
        Calcule le montant des heures supplémentaires.
        """
        if not self.params.activer_heures_supp:
            return Decimal(0)
            
        # Taux horaire = salaire_base / 30 jours / 8 heures
        hourly_rate = base_salary / Decimal(30) / Decimal(8)
        
        # 34.67h pour 26j => 1.33346h/jour
        overtime_hours_per_day = Decimal("1.33346")
        
        return (
            Decimal(business_days_worked) * 
            overtime_hours_per_day * 
            hourly_rate * 
            Decimal("1.5")  # Majoration 50%
        )
