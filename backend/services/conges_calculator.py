"""
Service de calcul automatique des congés
Permet de calculer et enregistrer les congés dès qu'un pointage est créé/modifié
"""

from sqlalchemy.orm import Session
from models import Conge, Pointage, Employe
from datetime import datetime
from typing import Optional


def calculer_et_enregistrer_conges(
    db: Session,
    employe_id: int,
    annee: int,
    mois: int
) -> Optional[Conge]:
    """
    Calculer et enregistrer/mettre à jour les congés pour un employé/période
    
    Cette fonction est appelée automatiquement après chaque création/modification de pointage
    
    Args:
        db: Session SQLAlchemy
        employe_id: ID de l'employé
        annee: Année concernée
        mois: Mois concerné (1-12)
    
    Returns:
        L'enregistrement Conge créé/mis à jour, ou None si pas de pointage
    
    Logique:
        1. Récupère le pointage pour cette période
        2. Calcule les totaux (jours_travailles)
        3. Récupère les congés PRIS déjà saisis (préservation)
        4. Calcule jours_reellement_travailles (RÈGLE 4: exclut congés pris)
        5. Détermine si employé nouveau recruté (<3 mois)
        6. Calcule jours_conges_acquis avec formule v3.5.3
        7. Enregistre/Met à jour dans table conges
    """
    
    # 1. Récupérer le pointage
    pointage = db.query(Pointage).filter(
        Pointage.employe_id == employe_id,
        Pointage.annee == annee,
        Pointage.mois == mois
    ).first()
    
    if not pointage:
        # Pas de pointage = pas de congés à calculer
        print(f"[CONGES] Aucun pointage trouvé pour employé {employe_id}, {mois}/{annee}")
        return None
    
    # 2. Calculer totaux depuis pointage
    totaux = pointage.calculer_totaux()
    jours_travailles_brut = totaux.get('jours_travailles', 0)
    
    print(f"[CONGES] Employé {employe_id}, {mois}/{annee}: jours_travailles_brut = {jours_travailles_brut}")
    
    # 3. Récupérer congés existants (pour préserver jours_pris)
    conge_existant = db.query(Conge).filter(
        Conge.employe_id == employe_id,
        Conge.annee == annee,
        Conge.mois == mois
    ).first()
    
    jours_conges_pris = float(conge_existant.jours_conges_pris or 0) if conge_existant else 0.0
    
    # 4. RÈGLE 4 v3.5.1/v3.5.3: Exclure congés pris du calcul
    # Les congés PRIS ne doivent PAS compter pour les droits
    jours_reellement_travailles = max(0, jours_travailles_brut - int(jours_conges_pris))
    
    print(f"[CONGES] jours_conges_pris = {jours_conges_pris}, jours_reellement_travailles = {jours_reellement_travailles}")
    
    # 5. Vérifier si nouveau recruté (<3 mois d'ancienneté)
    employe = db.query(Employe).filter(Employe.id == employe_id).first()
    est_nouveau_recrue = False
    
    if employe and employe.date_recrutement:
        mois_anciennete = (datetime.now().year - employe.date_recrutement.year) * 12 + \
                         (datetime.now().month - employe.date_recrutement.month)
        est_nouveau_recrue = mois_anciennete < 3
        print(f"[CONGES] Ancienneté: {mois_anciennete} mois, nouveau_recrue = {est_nouveau_recrue}")
    
    # 6. Calculer congés acquis avec la formule du modèle (v3.5.3 ou v3.5.1 selon version)
    jours_conges_acquis = Conge.calculer_jours_conges(jours_reellement_travailles, est_nouveau_recrue)
    
    print(f"[CONGES] jours_conges_acquis calculés = {jours_conges_acquis}")
    
    # 7. Enregistrer ou mettre à jour
    if conge_existant:
        # Mise à jour (préserver jours_conges_pris)
        conge_existant.jours_travailles = jours_reellement_travailles
        conge_existant.jours_conges_acquis = jours_conges_acquis
        # jours_conges_pris reste inchangé (saisi manuellement par utilisateur)
        conge_existant.jours_conges_restants = float(jours_conges_acquis) - float(conge_existant.jours_conges_pris or 0)
        
        print(f"[CONGES] Mise à jour conge #{conge_existant.id}")
        
        db.commit()
        db.refresh(conge_existant)
        return conge_existant
    else:
        # Création
        nouveau_conge = Conge(
            employe_id=employe_id,
            annee=annee,
            mois=mois,
            jours_travailles=jours_reellement_travailles,
            jours_conges_acquis=jours_conges_acquis,
            jours_conges_pris=0.0,  # Initialisé à 0, sera saisi manuellement
            jours_conges_restants=jours_conges_acquis
        )
        
        db.add(nouveau_conge)
        db.commit()
        db.refresh(nouveau_conge)
        
        print(f"[CONGES] Création nouveau conge #{nouveau_conge.id}")
        
        return nouveau_conge


def recalculer_conges_periode(
    db: Session,
    annee: int,
    mois: int
) -> dict:
    """
    Recalculer tous les congés pour une période donnée
    
    Utile après:
    - Vidage de la base de données
    - Corrections massives de pointages
    - Migration de version
    
    Args:
        db: Session SQLAlchemy
        annee: Année à recalculer
        mois: Mois à recalculer (1-12)
    
    Returns:
        Dictionnaire avec statistiques du recalcul
    """
    
    print(f"[CONGES] Début recalcul période {mois}/{annee}")
    
    # Récupérer tous les pointages de la période
    pointages = db.query(Pointage).filter(
        Pointage.annee == annee,
        Pointage.mois == mois
    ).all()
    
    print(f"[CONGES] {len(pointages)} pointages trouvés")
    
    results = {
        "recalcules": 0,
        "erreurs": 0,
        "details": []
    }
    
    for p in pointages:
        try:
            conge = calculer_et_enregistrer_conges(
                db=db,
                employe_id=p.employe_id,
                annee=annee,
                mois=mois
            )
            
            if conge:
                results["recalcules"] += 1
                results["details"].append({
                    "employe_id": p.employe_id,
                    "jours_acquis": float(conge.jours_conges_acquis),
                    "jours_pris": float(conge.jours_conges_pris),
                    "status": "recalculé"
                })
        except Exception as e:
            results["erreurs"] += 1
            results["details"].append({
                "employe_id": p.employe_id,
                "status": "erreur",
                "message": str(e)
            })
            print(f"[CONGES] Erreur employé {p.employe_id}: {e}")
    
    print(f"[CONGES] Recalcul terminé: {results['recalcules']} réussis, {results['erreurs']} erreurs")
    
    return results
