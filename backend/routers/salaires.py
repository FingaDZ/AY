from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from decimal import Decimal

from database import get_db
from models import Employe, StatutContrat
from schemas import SalaireCalculCreate, SalaireDetailResponse
from services import SalaireCalculator

router = APIRouter(prefix="/salaires", tags=["Salaires"])

@router.post("/calculer")
def calculer_salaire(
    calcul: SalaireCalculCreate,
    db: Session = Depends(get_db)
):
    """Calculer le salaire d'un employé pour un mois"""
    
    calculator = SalaireCalculator(db)
    
    try:
        resultat = calculator.calculer_salaire(
            employe_id=calcul.employe_id,
            annee=calcul.annee,
            mois=calcul.mois,
            jours_supplementaires=calcul.jours_supplementaires,
            prime_objectif=calcul.prime_objectif,
            prime_variable=calcul.prime_variable
        )
        return resultat
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/calculer-tous")
def calculer_tous_salaires(
    annee: int = Query(..., ge=2000, le=2100),
    mois: int = Query(..., ge=1, le=12),
    jours_supplementaires: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Calculer les salaires de tous les employés actifs pour un mois"""
    
    # Récupérer tous les employés actifs
    employes = db.query(Employe).filter(
        Employe.statut_contrat == StatutContrat.ACTIF
    ).all()
    
    calculator = SalaireCalculator(db)
    resultats = []
    erreurs = []
    
    # Totaux globaux
    totaux = {
        "salaire_cotisable": Decimal(0),
        "retenue_securite_sociale": Decimal(0),
        "irg": Decimal(0),
        "total_avances": Decimal(0),
        "retenue_credit": Decimal(0),
        "salaire_imposable": Decimal(0),
        "salaire_net": Decimal(0),
    }
    
    for employe in employes:
        try:
            resultat = calculator.calculer_salaire(
                employe_id=employe.id,
                annee=annee,
                mois=mois,
                jours_supplementaires=jours_supplementaires,
                prime_objectif=Decimal(0),
                prime_variable=Decimal(0)
            )
            resultats.append(resultat)
            
            # Ajouter aux totaux
            totaux["salaire_cotisable"] += resultat["salaire_cotisable"]
            totaux["retenue_securite_sociale"] += resultat["retenue_securite_sociale"]
            totaux["irg"] += resultat["irg"]
            totaux["total_avances"] += resultat["total_avances"]
            totaux["retenue_credit"] += resultat["retenue_credit"]
            totaux["salaire_imposable"] += resultat["salaire_imposable"]
            totaux["salaire_net"] += resultat["salaire_net"]
            
        except ValueError as e:
            erreurs.append({
                "employe_id": employe.id,
                "nom": employe.nom,
                "prenom": employe.prenom,
                "erreur": str(e)
            })
    
    # Convertir les Decimal en float pour la réponse JSON
    totaux_str = {k: float(v) for k, v in totaux.items()}
    
    return {
        "annee": annee,
        "mois": mois,
        "total_employes": len(employes),
        "calcules": len(resultats),
        "erreurs_count": len(erreurs),
        "salaires": resultats,
        "erreurs": erreurs,
        "totaux": totaux_str
    }

@router.get("/employe/{employe_id}")
def get_historique_salaires(
    employe_id: int,
    annee: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Obtenir l'historique des salaires d'un employé"""
    
    employe = db.query(Employe).filter(Employe.id == employe_id).first()
    
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    # TODO: Stocker les calculs de salaire en base pour avoir un historique
    # Pour l'instant, on retourne juste les informations de l'employé
    
    return {
        "employe_id": employe.id,
        "nom": employe.nom,
        "prenom": employe.prenom,
        "message": "Fonctionnalité d'historique à implémenter avec stockage des calculs"
    }

@router.get("/rapport/{annee}/{mois}")
def generer_rapport_salaires(
    annee: int,
    mois: int,
    db: Session = Depends(get_db)
):
    """Générer un rapport complet des salaires pour un mois"""
    
    # Récupérer tous les employés actifs
    employes = db.query(Employe).filter(
        Employe.statut_contrat == StatutContrat.ACTIF
    ).all()
    
    calculator = SalaireCalculator(db)
    rapport = []
    
    for employe in employes:
        try:
            resultat = calculator.calculer_salaire(
                employe_id=employe.id,
                annee=annee,
                mois=mois
            )
            rapport.append(resultat)
        except ValueError:
            # Ignorer les employés sans pointage
            pass
    
    return {
        "annee": annee,
        "mois": mois,
        "rapport": rapport
    }
