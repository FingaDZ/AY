"""
Service pour la gestion automatique des employés
"""
from sqlalchemy.orm import Session
from models import Employe
from datetime import date
from typing import List, Dict


def verifier_contrats_expires(db: Session) -> List[Dict]:
    """
    Vérifie tous les employés actifs avec date de fin de contrat dépassée
    et les désactive automatiquement.
    
    Returns:
        Liste des employés désactivés avec leurs informations
    """
    aujourd_hui = date.today()
    
    # Récupérer tous les employés actifs avec date de fin de contrat dépassée
    employes_a_desactiver = db.query(Employe).filter(
        Employe.actif == True,
        Employe.date_fin_contrat.isnot(None),
        Employe.date_fin_contrat < aujourd_hui
    ).all()
    
    employes_desactives = []
    
    for employe in employes_a_desactiver:
        # Désactiver l'employé
        employe.actif = False
        
        employes_desactives.append({
            "id": employe.id,
            "nom": employe.nom,
            "prenom": employe.prenom,
            "date_fin_contrat": employe.date_fin_contrat,
            "jours_expires": (aujourd_hui - employe.date_fin_contrat).days
        })
    
    if employes_desactives:
        db.commit()
    
    return employes_desactives


def calculer_date_fin_contrat(employe: Employe) -> date:
    """
    Calcule la date de fin de contrat basée sur la date de recrutement et la durée
    
    Args:
        employe: Instance de l'employé
        
    Returns:
        Date de fin de contrat calculée ou None si durée non définie
    """
    if not employe.duree_contrat or not employe.date_recrutement:
        return None
    
    from dateutil.relativedelta import relativedelta
    
    # Ajouter la durée en mois à la date de recrutement
    date_fin = employe.date_recrutement + relativedelta(months=employe.duree_contrat)
    
    return date_fin


def mettre_a_jour_dates_fin_contrat(db: Session) -> List[Dict]:
    """
    Met à jour automatiquement les dates de fin de contrat pour les employés
    qui ont une durée de contrat définie mais pas de date de fin
    
    Returns:
        Liste des employés mis à jour
    """
    employes_a_mettre_a_jour = db.query(Employe).filter(
        Employe.duree_contrat.isnot(None),
        Employe.date_fin_contrat.is_(None)
    ).all()
    
    employes_mis_a_jour = []
    
    for employe in employes_a_mettre_a_jour:
        date_fin = calculer_date_fin_contrat(employe)
        if date_fin:
            employe.date_fin_contrat = date_fin
            employes_mis_a_jour.append({
                "id": employe.id,
                "nom": employe.nom,
                "prenom": employe.prenom,
                "date_recrutement": employe.date_recrutement,
                "duree_contrat": employe.duree_contrat,
                "date_fin_contrat": date_fin
            })
    
    if employes_mis_a_jour:
        db.commit()
    
    return employes_mis_a_jour
