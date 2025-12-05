import openpyxl
import csv
from decimal import Decimal
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models import IRGBareme

class IRGCalculator:
    """Service de calcul de l'IRG (Source: BDD prio, avec fallback Excel)"""
    
    def __init__(self, db: Session = None, fichier_irg: str = None):
        """
        Initialiser le calculateur IRG
        Args:
            db: Session SQLAlchemy (optionnel)
            fichier_irg: Chemin vers fichier Excel (fallback)
        """
        self.db = db
        if fichier_irg is None:
            self.fichier_irg = Path(__file__).parent.parent.parent / "irg.xlsx"
        else:
            self.fichier_irg = Path(fichier_irg)
            
        self.bareme = self._charger_bareme()
    
    def _charger_bareme(self) -> List[Tuple[Decimal, Decimal]]:
        """Charger le barème (BDD ou Excel)"""
        # 1. Essayer depuis la BDD
        if self.db:
            try:
                bareme_db = self._charger_bareme_db()
                if bareme_db:
                    # print(f"✅ Barème IRG chargé depuis BDD: {len(bareme_db)} tranches")
                    return bareme_db
            except Exception as e:
                print(f"⚠️ Erreur chargement BDD, fallback Excel: {e}")
        
        # 2. Fallback Excel
        return self._charger_bareme_excel()

    def _charger_bareme_db(self) -> List[Tuple[Decimal, Decimal]]:
        """Lire depuis la table irg_bareme"""
        items = self.db.query(IRGBareme).filter(
            IRGBareme.actif == True
        ).order_by(IRGBareme.salaire_min).all()
        
        if not items:
            return []
            
        return [(item.salaire_min, item.irg) for item in items]

    def _charger_bareme_excel(self) -> List[Tuple[Decimal, Decimal]]:
        """Lire depuis le fichier Excel"""
        if not self.fichier_irg.exists():
            print(f"⚠️ Fichier IRG non trouvé: {self.fichier_irg} (IRG = 0)")
            return []
        
        try:
            wb = openpyxl.load_workbook(self.fichier_irg, data_only=True)
            sheet = wb.active
            
            bareme = []
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if row[0] is not None and row[1] is not None:
                    try:
                        salaire = Decimal(str(row[0]))
                        irg = Decimal(str(row[1]))
                        bareme.append((salaire, irg))
                    except:
                        continue
            
            # Trier par salaire croissant
            bareme.sort(key=lambda x: x[0])
            
            # print(f"✅ Barème IRG chargé depuis Excel: {len(bareme)} tranches")
            return bareme
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement du barème Excel: {e}")
            return []
    
    def calculer_irg(self, salaire_imposable: Decimal) -> Decimal:
        """
        Calculer l'IRG pour un salaire imposable donné
        """
        if not self.bareme:
            return Decimal("0")
        
        # Si le salaire est inférieur au premier seuil
        if salaire_imposable < self.bareme[0][0]:
            return Decimal("0")
        
        # Si le salaire est supérieur au dernier seuil, prendre le max
        if salaire_imposable >= self.bareme[-1][0]:
            return self.bareme[-1][1]
        
        # Recherche du salaire exact ou immédiatement inférieur
        irg_retenu = Decimal("0")
        
        for salaire_bareme, irg_bareme in self.bareme:
            if salaire_imposable >= salaire_bareme:
                irg_retenu = irg_bareme
            else:
                break
        
        return irg_retenu
    
    def recharger_bareme(self):
        """Forcer le rechargement du barème (après update BDD)"""
        self.bareme = self._charger_bareme()


# Singleton pattern (optionnel, mais utile pour cache)
_irg_calculator = None

def get_irg_calculator(db: Session = None) -> IRGCalculator:
    """Obtenir l'instance du calculateur IRG (avec mise à jour DB si fournie)"""
    global _irg_calculator
    
    if _irg_calculator is None:
        _irg_calculator = IRGCalculator(db)
    elif db is not None and _irg_calculator.db != db:
        # Mettre à jour la session DB si elle change
        _irg_calculator.db = db
        # Et recharger potentiellement si on passait d'un mode sans DB à avec DB
        _irg_calculator.recharger_bareme()
        
    return _irg_calculator
