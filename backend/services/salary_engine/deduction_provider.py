from decimal import Decimal
from typing import Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from models import Avance, Credit, RetenueCredit, ProrogationCredit, StatutCredit, ParametresSalaire

class DeductionProvider:
    """
    Gère le calcul des déductions (Avances, Crédits).
    Mode lecture seule pour le calcul (pas d'écriture en DB ici).
    """
    def __init__(self, db: Session, params: ParametresSalaire):
        self.db = db
        self.params = params

    def calculate_deductions(self, employee_id: int, year: int, month: int) -> Dict:
        """
        Calcule les déductions prévues pour le mois.
        """
        # 1. Total Avances
        total_avances = self._calculate_advances(employee_id, year, month)
        
        # 2. Retenue Crédit (Simulation)
        credit_retention = self._calculate_credit_retention(employee_id, year, month)

        return {
            "total_avances": total_avances,
            "retenue_credit": credit_retention
        }

    def _calculate_advances(self, employee_id: int, year: int, month: int) -> Decimal:
        """Somme des avances du mois"""
        result = self.db.query(func.sum(Avance.montant)).filter(
            Avance.employe_id == employee_id,
            Avance.annee_deduction == year,
            Avance.mois_deduction == month
        ).scalar()
        return result or Decimal(0)

    def _calculate_credit_retention(self, employee_id: int, year: int, month: int) -> Decimal:
        """
        Calcule la retenue de crédit sans modifier la base de données.
        """
        # Crédits en cours
        credits = self.db.query(Credit).filter(
            Credit.employe_id == employee_id,
            Credit.statut == StatutCredit.EN_COURS
        ).all()
        
        total_retention = Decimal(0)
        
        for credit in credits:
            # Vérifier prorogation
            prorogation = self.db.query(ProrogationCredit).filter(
                ProrogationCredit.credit_id == credit.id,
                ProrogationCredit.mois_initial == month,
                ProrogationCredit.annee_initiale == year
            ).first()
            
            if prorogation:
                continue
            
            # Vérifier si retenue déjà payée/enregistrée (cas d'édition multiple)
            existing_retention = self.db.query(RetenueCredit).filter(
                RetenueCredit.credit_id == credit.id,
                RetenueCredit.mois == month,
                RetenueCredit.annee == year
            ).first()
            
            if existing_retention:
                total_retention += existing_retention.montant
            else:
                # Simulation du calcul
                remaining = credit.montant_restant
                if remaining > 0:
                    amount = min(credit.montant_mensualite, remaining)
                    total_retention += amount
                    
        return total_retention
