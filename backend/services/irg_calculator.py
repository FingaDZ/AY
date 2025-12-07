from decimal import Decimal
import openpyxl
import os
import logging
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session

# Configuration du logging
logger = logging.getLogger(__name__)

class IRGCalculator:
    """
    Calculateur IRG basé sur un fichier Excel (Legacy Mode v2.4.2)
    Bypasse la base de données pour une stabilité maximale.
    """
    _instance = None
    _bareme_cache = []
    _last_load_time = None

    def __new__(cls, db: Optional[Session] = None):
        if cls._instance is None:
            cls._instance = super(IRGCalculator, cls).__new__(cls)
            cls._instance._charger_bareme()
        return cls._instance

    def __init__(self, db: Optional[Session] = None):
        # On ignore la DB ici, on utilise uniquement le fichier Excel
        if not self._bareme_cache:
            self._charger_bareme()

    def _charger_bareme(self):
        """Charge le barème depuis le fichier Excel"""
        try:
            file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'irg.xlsx')
            
            if not os.path.exists(file_path):
                logger.error(f"Fichier IRG introuvable: {file_path}")
                # Fallback sur un barème vide (évite le crash)
                self._bareme_cache = []
                return

            wb = openpyxl.load_workbook(file_path, data_only=True)
            sheet = wb.active
            
            nouveau_bareme = []
            # Supposons que le fichier a: Col A = Salaire Min, Col B = Montant IRG
            # On saute l'en-tête
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if row[0] is not None and row[1] is not None:
                    try:
                        salaire = Decimal(str(row[0]))
                        montant = Decimal(str(row[1]))
                        nouveau_bareme.append((salaire, montant))
                    except Exception:
                        continue

            self._bareme_cache = sorted(nouveau_bareme, key=lambda x: x[0])
            logger.info(f"Barème IRG chargé: {len(self._bareme_cache)} entrées")
        except Exception as e:
            logger.error(f"Erreur chargement IRG: {e}")
            self._bareme_cache = []

    def calculer_irg(self, salaire_imposable):
        if not self._bareme_cache:
            return Decimal(0)

        salaire = Decimal(salaire_imposable)
        
        # Le barème est une liste de tuples (seuil_salaire, montant_irg)
        # Ex: (30000, 0), (30010, 10), ..., (40000, 2500)
        # On cherche la ligne où notre salaire est >= seuil
        # En général dans le fichier irg.xlsx algérien "simplifié" (2 colonnes):
        # Col A = Salaire, Col B = Retenue
        # C'est une correspondance directe ou par palier.
        # Si c'est un barème par tranche (barème 2020+), le fichier contient souvent le MONTANT EXACT de la retenue pour chaque salaire (par pas de 10 DA).
        
        # Recherche dichotomique ou linéaire optimisée
        # Puisque le fichier contient des milliers de lignes (pas de 10 DA), on cherche la valeur la plus proche inférieure ou égale.
        
        # Optimisation: parcourir
        # Si le fichier est un barème "complet" (tous les salaires listés), on prend la correspondance exacte ou la plus proche inférieure.
        
        tranche_trouvee = (Decimal(0), Decimal(0))
        
        # On parcourt pour trouver le palier immediately infra ou égal
        # Comme c'est trié, on peut s'arrêter quand on dépasse
        for seuil, montant in self._bareme_cache:
            if seuil <= salaire:
                tranche_trouvee = (seuil, montant)
            else:
                break
                
        return tranche_trouvee[1]

    def recharger_bareme(self):
        self._charger_bareme()

def get_irg_calculator(db: Session = None) -> IRGCalculator:
    return IRGCalculator(db)
