import openpyxl
import csv
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
            # Utiliser le fichier irg.xlsx à la racine du projet
            fichier_irg = Path(__file__).parent.parent.parent / "irg.xlsx"
        
        self.fichier_irg = Path(fichier_irg)
        self.bareme = self._charger_bareme()
    
    def _charger_bareme(self) -> List[Tuple[Decimal, Decimal]]:
        """
        Charger le barème IRG directement depuis F:\Code\AY HR\irg.xlsx
        Retourne une liste de tuples (salaire, irg)
        """
        if not self.fichier_irg.exists():
            print(f"❌ ERREUR: Fichier IRG non trouvé: {self.fichier_irg}")
            raise FileNotFoundError(f"Fichier IRG requis non trouvé: {self.fichier_irg}")
        
        try:
            wb = openpyxl.load_workbook(self.fichier_irg, data_only=True)
            sheet = wb.active
            
            bareme = []
            # Ignorer la première ligne (en-têtes: MONTANT, IRG)
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if row[0] is not None and row[1] is not None:
                    salaire = Decimal(str(row[0]))
                    irg = Decimal(str(row[1]))
                    bareme.append((salaire, irg))
            
            wb.close()
            
            print(f"✅ Barème IRG chargé depuis {self.fichier_irg.name}: {len(bareme)} lignes")
            return bareme
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement du barème IRG: {e}")
            raise
        
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
            raise
    
    def calculer_irg(self, salaire_imposable: Decimal) -> Decimal:
        """
        Calculer l'IRG pour un salaire imposable donné
        Lookup direct dans le fichier Excel sans calcul
        
        Args:
            salaire_imposable: Salaire imposable en DA
            
        Returns:
            Montant de l'IRG en DA (valeur exacte du fichier Excel)
        """
        if not self.bareme:
            return Decimal("0")
        
        # Si le salaire est inférieur au premier seuil
        if salaire_imposable < self.bareme[0][0]:
            return Decimal("0")
        
        # Si le salaire est supérieur au dernier seuil
        if salaire_imposable >= self.bareme[-1][0]:
            return self.bareme[-1][1]
        
        # Recherche du salaire exact ou immédiatement inférieur
        irg_retenu = Decimal("0")
        
        for salaire_bareme, irg_bareme in self.bareme:
            if salaire_imposable >= salaire_bareme:
                irg_retenu = irg_bareme
            else:
                # On a dépassé, on retourne l'IRG précédent
                break
        
        return irg_retenu
    
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
