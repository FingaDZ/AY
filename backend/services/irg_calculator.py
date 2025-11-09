import openpyxl
from decimal import Decimal
from typing import Dict, List, Tuple
from pathlib import Path


class IRGCalculator:
    """Service de calcul de l'IRG à partir du fichier Excel"""
    
    def __init__(self, fichier_irg: str = None):
        """
        Initialiser le calculateur IRG
        
        Args:
            fichier_irg: Chemin vers le fichier irg.xlsx
        """
        if fichier_irg is None:
            # Chemin par défaut
            fichier_irg = Path(__file__).parent.parent / "data" / "irg.xlsx"
        
        self.fichier_irg = Path(fichier_irg)
        self.bareme = self._charger_bareme()
    
    def _charger_bareme(self) -> List[Tuple[Decimal, Decimal]]:
        """
        Charger le barème IRG depuis le fichier Excel
        Retourne une liste de tuples (salaire, irg)
        """
        if not self.fichier_irg.exists():
            print(f"⚠️  Fichier IRG non trouvé: {self.fichier_irg}")
            print("Utilisation du barème par défaut")
            return self._bareme_par_defaut()
        
        try:
            wb = openpyxl.load_workbook(self.fichier_irg, data_only=True)
            ws = wb.active
            
            bareme = []
            for row in ws.iter_rows(min_row=2, values_only=True):  # Skip header
                if row[0] is not None and row[1] is not None:
                    salaire = Decimal(str(row[0]))
                    irg = Decimal(str(row[1]))
                    bareme.append((salaire, irg))
            
            # Trier par salaire
            bareme.sort(key=lambda x: x[0])
            
            print(f"✅ Barème IRG chargé: {len(bareme)} tranches")
            return bareme
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement du barème IRG: {e}")
            print("Utilisation du barème par défaut")
            return self._bareme_par_defaut()
    
    def _bareme_par_defaut(self) -> List[Tuple[Decimal, Decimal]]:
        """Barème IRG par défaut (Algérie 2024 - à vérifier)"""
        return [
            (Decimal("0"), Decimal("0")),
            (Decimal("30000"), Decimal("0")),
            (Decimal("35000"), Decimal("500")),
            (Decimal("40000"), Decimal("1000")),
            (Decimal("45000"), Decimal("1750")),
            (Decimal("50000"), Decimal("2500")),
            (Decimal("55000"), Decimal("3500")),
            (Decimal("60000"), Decimal("4500")),
            (Decimal("70000"), Decimal("7000")),
            (Decimal("80000"), Decimal("9500")),
            (Decimal("90000"), Decimal("12500")),
            (Decimal("100000"), Decimal("15500")),
            (Decimal("120000"), Decimal("22500")),
            (Decimal("150000"), Decimal("33000")),
        ]
    
    def calculer_irg(self, salaire_imposable: Decimal) -> Decimal:
        """
        Calculer l'IRG pour un salaire imposable donné
        
        Args:
            salaire_imposable: Salaire imposable en DA
            
        Returns:
            Montant de l'IRG en DA
        """
        if not self.bareme:
            return Decimal("0")
        
        # Si le salaire est inférieur au premier seuil, pas d'IRG
        if salaire_imposable <= self.bareme[0][0]:
            return Decimal("0")
        
        # Si le salaire est supérieur au dernier seuil, extrapoler
        if salaire_imposable >= self.bareme[-1][0]:
            # Interpolation linéaire sur les deux derniers points
            if len(self.bareme) >= 2:
                s1, irg1 = self.bareme[-2]
                s2, irg2 = self.bareme[-1]
                taux = (irg2 - irg1) / (s2 - s1)
                return irg2 + (salaire_imposable - s2) * taux
            else:
                return self.bareme[-1][1]
        
        # Interpolation linéaire entre deux tranches
        for i in range(len(self.bareme) - 1):
            s1, irg1 = self.bareme[i]
            s2, irg2 = self.bareme[i + 1]
            
            if s1 <= salaire_imposable <= s2:
                # Interpolation linéaire
                if s2 == s1:
                    return irg1
                
                ratio = (salaire_imposable - s1) / (s2 - s1)
                irg = irg1 + (irg2 - irg1) * ratio
                return irg.quantize(Decimal("0.01"))
        
        return Decimal("0")
    
    def recharger_bareme(self):
        """Recharger le barème depuis le fichier"""
        self.bareme = self._charger_bareme()


# Instance globale
_irg_calculator = None

def get_irg_calculator() -> IRGCalculator:
    """Obtenir l'instance du calculateur IRG"""
    global _irg_calculator
    if _irg_calculator is None:
        _irg_calculator = IRGCalculator()
    return _irg_calculator
