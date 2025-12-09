from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging

from database import get_db
from models import Employe
from services.salary_engine import SalaryEngine

router = APIRouter(prefix="/edition-salaires", tags=["Edition Salaires"])
logger = logging.getLogger(__name__)

@router.get("/preview", response_model=List[Dict[str, Any]])
def get_salary_preview(
    annee: int = Query(..., description="Année de calcul"),
    mois: int = Query(..., description="Mois de calcul"),
    db: Session = Depends(get_db)
):
    """
    Simule le calcul des salaires pour tous les employés actifs sur la période.
    Ne sauvegarde rien en base (Mode Lecture Seule).
    """
    engine = SalaryEngine(db)
    results = []
    
    # 1. Récupérer employés actifs
    # TODO: Filtrer par date de sortie eventuellement
    employees = db.query(Employe).filter(Employe.actif == True).all()
    
    for employee in employees:
        try:
            # Tenter le calcul
            result = engine.calculate_for_employee(employee.id, annee, mois)
            # Ajouter statut succès
            result["status"] = "OK"
            result["error"] = None
            results.append(result)
        except ValueError as e:
            # Erreur métier (ex: pas de pointage)
            logger.warning(f"Calcul impossible pour {employee.nom}: {e}")
            results.append({
                "employe_id": employee.id,
                "employe_nom": employee.nom,
                "employe_prenom": employee.prenom,
                "employe_matricule": employee.matricule,
                "status": "ERROR",
                "error": str(e),
                "salaire_net": 0
            })
        except Exception as e:
            logger.error(f"Erreur technique pour {employee.nom}: {e}", exc_info=True)
            results.append({
                "employe_id": employee.id,
                "employe_nom": employee.nom,
                "employe_prenom": employee.prenom,
                "employe_matricule": employee.matricule,
                "status": "CRITICAL_ERROR",
                "error": "Erreur technique",
                "salaire_net": 0
            })
            
    return results
