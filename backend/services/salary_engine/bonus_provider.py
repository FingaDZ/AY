from decimal import Decimal
from typing import Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from models import Employe, ParametresSalaire, Mission

class BonusProvider:
    """
    Gère le calcul des primes et indemnités (IEP, nuisances, transport, etc.).
    """
    def __init__(self, db: Session, params: ParametresSalaire):
        self.db = db
        self.params = params

    def calculate_bonuses(self, employee: Employe, year: int, month: int, 
                         base_salary: Decimal, worked_days: int) -> Dict:
        """
        Calcule toutes les primes.
        """
        # 1. Primes liées au salaire de base (Pourcentage)
        nuisance = base_salary * (self.params.taux_in / Decimal(100))
        ifsp = base_salary * (self.params.taux_ifsp / Decimal(100))
        
        # 2. IEP (Ancienneté)
        seniority_years = self._calculate_seniority(employee.date_recrutement, year, month)
        iep = base_salary * Decimal(seniority_years) * (self.params.taux_iep_par_an / Decimal(100))
        
        # 3. Prime Encouragement
        encouragement = Decimal(0)
        if seniority_years >= self.params.anciennete_min_encouragement:
            encouragement = base_salary * (self.params.taux_prime_encouragement / Decimal(100))
            
        # 4. Primes journalières
        chauffeur = Decimal(0)
        if "chauffeur" in (employee.poste_travail or "").lower():
            chauffeur = self.params.prime_chauffeur_jour * Decimal(worked_days)
            
        panier = self.params.panier_jour * Decimal(worked_days)
        transport = self.params.transport_jour * Decimal(worked_days)
        
        # 5. Primes Spéciales
        night_shift = self.params.prime_nuit_securite if employee.prime_nuit_agent_securite else Decimal(0)
        home_maker = self.params.prime_femme_foyer if employee.femme_au_foyer else Decimal(0) # Non imposable/Non cotisable souvent, à vérifier
        
        # 6. Prime Déplacement (Missions)
        travel_bonus = self._calculate_travel_bonus(employee.id, year, month)

        return {
            "indemnite_nuisance": nuisance,
            "ifsp": ifsp,
            "iep": iep,
            "prime_encouragement": encouragement,
            "prime_chauffeur": chauffeur,
            "prime_nuit_agent_securite": night_shift,
            "prime_deplacement": travel_bonus,
            "panier": panier,
            "prime_transport": transport,
            "prime_femme_foyer": home_maker
        }

    def _calculate_seniority(self, recruitment_date: date, year: int, month: int) -> int:
        """Calcul ancienneté en années au 1er du mois"""
        calc_date = date(year, month, 1)
        if recruitment_date > calc_date:
            return 0
        delta = calc_date - recruitment_date
        return max(0, delta.days // 365)

    def _calculate_travel_bonus(self, employee_id: int, year: int, month: int) -> Decimal:
        """Somme des primes de mission du mois"""
        total = self.db.query(func.sum(Mission.prime_calculee)).filter(
            Mission.chauffeur_id == employee_id,
            func.year(Mission.date_mission) == year,
            func.month(Mission.date_mission) == month
        ).scalar()
        return total or Decimal(0)
