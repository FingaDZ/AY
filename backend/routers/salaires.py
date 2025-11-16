from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from decimal import Decimal
from datetime import date
from io import BytesIO
import zipfile

from database import get_db
from models import Employe, StatutContrat
from schemas import SalaireCalculCreate, SalaireCalculTousCreate, SalaireDetailResponse
from services import SalaireCalculator
from services.pdf_generator import PDFGenerator

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
    params: SalaireCalculTousCreate,
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
                annee=params.annee,
                mois=params.mois,
                jours_supplementaires=params.jours_supplementaires,
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
        "annee": params.annee,
        "mois": params.mois,
        "total_employes": len(employes),
        "calcules": len(resultats),
        "erreurs_count": len(erreurs),
        "salaires": resultats,
        "erreurs": erreurs,
        "totaux": totaux_str
    }

@router.post("/bulletins-paie/generer")
def generer_bulletins_paie(
    params: SalaireCalculTousCreate,
    db: Session = Depends(get_db)
):
    """Générer tous les bulletins de paie en PDF (ZIP)"""
    
    # Récupérer tous les employés actifs
    employes = db.query(Employe).filter(
        Employe.statut_contrat == StatutContrat.ACTIF
    ).all()
    
    if not employes:
        raise HTTPException(status_code=404, detail="Aucun employé actif trouvé")
    
    calculator = SalaireCalculator(db)
    pdf_generator = PDFGenerator(db=db)
    
    # Créer un fichier ZIP en mémoire
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for employe in employes:
            try:
                # Calculer le salaire
                salaire_data = calculator.calculer_salaire(
                    employe_id=employe.id,
                    annee=params.annee,
                    mois=params.mois,
                    jours_supplementaires=params.jours_supplementaires,
                    prime_objectif=Decimal(0),
                    prime_variable=Decimal(0)
                )
                
                # Préparer les données de l'employé
                employe_data = {
                    'nom': employe.nom,
                    'prenom': employe.prenom,
                    'poste_travail': employe.poste_travail,
                    'numero_secu_sociale': employe.numero_secu_sociale or 'N/A',
                    'date_recrutement': employe.date_recrutement.strftime('%d/%m/%Y') if employe.date_recrutement else 'N/A',
                    'salaire_base': float(employe.salaire_base)
                }
                
                # Convertir les Decimal en float pour le PDF
                salaire_data_float = {k: float(v) if isinstance(v, Decimal) else v 
                                     for k, v in salaire_data.items()}
                
                # Générer le bulletin PDF
                pdf_buffer = pdf_generator.generate_bulletin_paie(
                    employe_data=employe_data,
                    salaire_data=salaire_data_float,
                    periode={'mois': params.mois, 'annee': params.annee}
                )
                
                # Ajouter au ZIP
                filename = f"bulletin_{employe.prenom}_{employe.nom}_{params.mois:02d}_{params.annee}.pdf"
                # Nettoyer le nom de fichier (supprimer les caractères spéciaux)
                filename = "".join(c for c in filename if c.isalnum() or c in ('_', '-', '.')).rstrip()
                
                zip_file.writestr(filename, pdf_buffer.getvalue())
                
            except ValueError as e:
                # Ignorer les employés sans pointage
                continue
    
    zip_buffer.seek(0)
    
    # Retourner le ZIP
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=bulletins_paie_{params.mois:02d}_{params.annee}.zip"
        }
    )

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

@router.post("/rapport-pdf")
def generer_rapport_pdf_salaires(
    params: SalaireCalculTousCreate,
    db: Session = Depends(get_db)
):
    """Générer un rapport PDF complet des salaires de tous les employés"""
    
    # Récupérer tous les employés actifs
    employes = db.query(Employe).filter(
        Employe.statut_contrat == StatutContrat.ACTIF
    ).all()
    
    if not employes:
        raise HTTPException(status_code=404, detail="Aucun employé actif trouvé")
    
    calculator = SalaireCalculator(db)
    salaires_data = []
    
    # Calculer les salaires
    for employe in employes:
        try:
            resultat = calculator.calculer_salaire(
                employe_id=employe.id,
                annee=params.annee,
                mois=params.mois
            )
            salaires_data.append(resultat)
        except ValueError:
            # Ignorer les employés sans pointage
            pass
    
    if not salaires_data:
        raise HTTPException(status_code=404, detail="Aucune donnée de salaire disponible pour cette période")
    
    # Calculer TOUS les totaux nécessaires
    totaux = {
        'total_base': sum(Decimal(str(s.get('salaire_base_proratis', 0))) for s in salaires_data),
        'total_heures_supp': sum(Decimal(str(s.get('heures_supplementaires', 0))) for s in salaires_data),
        'total_in': sum(Decimal(str(s.get('indemnite_nuisance', 0))) for s in salaires_data),
        'total_ifsp': sum(Decimal(str(s.get('ifsp', 0))) for s in salaires_data),
        'total_iep': sum(Decimal(str(s.get('iep', 0))) for s in salaires_data),
        'total_encouragement': sum(Decimal(str(s.get('prime_encouragement', 0))) for s in salaires_data),
        'total_chauffeur': sum(Decimal(str(s.get('prime_chauffeur', 0))) for s in salaires_data),
        'total_nuit': sum(Decimal(str(s.get('prime_nuit_agent_securite', 0))) for s in salaires_data),
        'total_deplacement': sum(Decimal(str(s.get('prime_deplacement', 0))) for s in salaires_data),
        'total_panier': sum(Decimal(str(s.get('panier', 0))) for s in salaires_data),
        'total_transport': sum(Decimal(str(s.get('prime_transport', 0))) for s in salaires_data),
        'total_cotisable': sum(Decimal(str(s.get('salaire_cotisable', 0))) for s in salaires_data),
        'total_ss': sum(Decimal(str(s.get('retenue_securite_sociale', 0))) for s in salaires_data),
        'total_imposable': sum(Decimal(str(s.get('salaire_imposable', 0))) for s in salaires_data),
        'total_irg': sum(Decimal(str(s.get('irg', 0))) for s in salaires_data),
        'total_femme_foyer': sum(Decimal(str(s.get('prime_femme_foyer', 0))) for s in salaires_data),
        'total_avances': sum(Decimal(str(s.get('total_avances', 0))) for s in salaires_data),
        'total_credits': sum(Decimal(str(s.get('retenue_credit', 0))) for s in salaires_data),
        'total_net': sum(Decimal(str(s.get('salaire_net', 0))) for s in salaires_data),
    }
    
    # Générer le PDF
    pdf_generator = PDFGenerator(db=db)
    periode = {'mois': params.mois, 'annee': params.annee}
    
    pdf_buffer = pdf_generator.generate_rapport_salaires(
        salaires_data=salaires_data,
        periode=periode,
        totaux=totaux
    )
    
    # Préparer le nom du fichier
    filename = f"rapport_salaires_{params.mois:02d}_{params.annee}.pdf"
    
    # Retourner le PDF
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

