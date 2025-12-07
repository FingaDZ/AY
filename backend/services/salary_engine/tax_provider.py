from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.irg_bareme import IRGBareme
import logging

logger = logging.getLogger(__name__)

class TaxProvider:
    """
    Fournisseur de calculs fiscaux (IRG) basé sur la base de données.
    Remplace l'ancien système Excel.
    """
    def __init__(self, db: Session):
        self.db = db

    def calculate_irg(self, taxable_salary: Decimal) -> Decimal:
        """
        Calcule l'IRG pour un salaire imposable donné en interrogeant la DB.
        Logique: Trouve le palier inférieur ou égal le plus proche.
        """
        if taxable_salary <= 0:
            return Decimal(0)

        # Requête optimisée: 
        # SELECT montant_irg FROM irg_bareme 
        # WHERE salaire <= :salaire 
        # ORDER BY salaire DESC 
        # LIMIT 1
        entry = (
            self.db.query(IRGBareme)
            .filter(IRGBareme.salaire <= taxable_salary)
            .order_by(desc(IRGBareme.salaire))
            .first()
        )

        if not entry:
            logger.warning(f"Aucun barème IRG trouvé pour salaire: {taxable_salary}")
            return Decimal(0)

        return entry.montant_irg
