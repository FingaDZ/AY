import sys
import os
from decimal import Decimal
import unittest
from unittest.mock import MagicMock
from datetime import date

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.salaire_calculator import SalaireCalculator
from models import Employe, Pointage, ParametresSalaire

class TestSalaireCalculatorV3(unittest.TestCase):
    def setUp(self):
        self.db = MagicMock()
        self.calc = SalaireCalculator(self.db)
        
        # Mock Params
        self.params = ParametresSalaire(
            taux_in=Decimal(5),
            taux_ifsp=Decimal(5),
            taux_iep_par_an=Decimal(1),
            taux_prime_encouragement=Decimal(10),
            taux_securite_sociale=Decimal(9),
            calculer_heures_supp=True,
            mode_calcul_conges="complet",
            jours_ouvrables_base=26,
            irg_proratise=True,
            prime_chauffeur_jour=Decimal(100),
            panier_jour=Decimal(100),
            transport_jour=Decimal(100),
            prime_femme_foyer=Decimal(1000)
        )
        self.calc.params = self.params
        
        # Mock Employe
        self.employe = Employe(
            id=1,
            nom="Test",
            prenom="User",
            salaire_base=Decimal(30000),
            date_recrutement=date(2020, 1, 1), # > 1 an
            poste_travail="Ingenieur",
            prime_nuit_agent_securite=False,
            femme_au_foyer=False
        )
        self.db.query.return_value.filter.return_value.first.return_value = self.employe
        
        # Mock Pointage
        self.pointage = MagicMock()
        self.pointage.calculer_totaux.return_value = {
            "total_travailles": 22,
            "jours_travailles": 22,
            "jours_absences": 0
        }
        # SalaireCalculator queries Pointage
        # The mock setup for query chaining is complex, simplifying:
        # We need to mock the query sequence in logic
        # But validating internal methods is easier
        
    def test_irg_proratise(self):
        """Test IRG Prorated Calculation"""
        # Case 1: Full month (30 days equivalent)
        # Salaire imposable 35000 approx
        salaire_imposable = Decimal(35000)
        jours = 30
        
        # Normal IRG
        irg_normal = self.calc._calculer_irg(salaire_imposable)
        irg_prorated = self.calc._calculer_irg_proratise(salaire_imposable, jours)
        
        self.assertEqual(irg_normal, irg_prorated)
        
        # Case 2: Partial month (15 days)
        # Salaire imposable = 17500 (half of 35000)
        salaire_imposable = Decimal(17500)
        jours = 15
        
        # Logic:
        # 1. Extrapolate 30j: 17500 / 15 * 30 = 35000
        # 2. IRG on 35000 = irg_normal (say 3000)
        # 3. Prorate: 3000 / 30 * 15 = 1500
        
        irg_expected = (irg_normal / Decimal(30)) * Decimal(15)
        irg_calculated = self.calc._calculer_irg_proratise(salaire_imposable, jours)
        
        # Allow small rounding diffs
        self.assertAlmostEqual(irg_calculated, Decimal(int(irg_expected)), delta=1)

    def test_conges_complet(self):
        """Test Mode Complet"""
        self.calc.params.mode_calcul_conges = "complet"
        self.employe.salaire_base = Decimal(30000)
        
        # 15 days worked + 15 days leave = 30 days paid
        val = self.calc._calculer_salaire_avec_conges(self.employe, 15, 15)
        self.assertEqual(val, Decimal(30000))
        
        # 20 days worked + 0 days leave = 20/30 paid
        val = self.calc._calculer_salaire_avec_conges(self.employe, 20, 0)
        self.assertEqual(val, Decimal(20000))

    def test_conges_proratise(self):
        """Test Mode Proratise"""
        self.calc.params.mode_calcul_conges = "proratise"
        
        # 15 days worked + 15 days leave
        # Part Work: 30000 * 15/30 = 15000
        # Part Leave: 30000 * 15/30 = 15000
        # Total: 30000
        val = self.calc._calculer_salaire_avec_conges(self.employe, 15, 15)
        self.assertEqual(val, Decimal(30000))

if __name__ == '__main__':
    unittest.main()
