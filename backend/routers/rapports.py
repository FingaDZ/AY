from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal

from database import get_db
from models import Employe, Pointage, StatutContrat
from models.salaire import Salaire
from schemas.salaire import G29Response, G29DataRecap, G29DataEmploye
from services import SalaireCalculator, RapportGenerator, ExcelGenerator
from services.pdf_generator import PDFGenerator
from middleware.auth import require_auth

router = APIRouter(prefix="/rapports", tags=["Rapports"])

@router.get("/pointages/pdf")
def generer_rapport_pointages_pdf(
    annee: int = Query(..., ge=2000, le=2100),
    mois: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db)
):
    """Générer un rapport PDF des pointages pour un mois"""
    
    # Récupérer les pointages du mois
    pointages = db.query(Pointage).filter(
        Pointage.annee == annee,
        Pointage.mois == mois
    ).all()
    
    # Préparer les données
    donnees_pointages = []
    for p in pointages:
        employe = db.query(Employe).filter(Employe.id == p.employe_id).first()
        if employe:
            totaux = p.calculer_totaux()
            donnees_pointages.append({
                "employe_id": employe.id,
                "employe_nom": employe.nom,
                "employe_prenom": employe.prenom,
                "totaux": totaux
            })
    
    # Générer le PDF
    generator = RapportGenerator()
    pdf_buffer = generator.generer_rapport_pointages(donnees_pointages, annee, mois)
    
    # Retourner le PDF
    filename = f"pointages_{annee}_{mois:02d}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/pointages/excel")
def generer_rapport_pointages_excel(
    annee: int = Query(..., ge=2000, le=2100),
    mois: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db)
):
    """Générer un rapport Excel des pointages pour un mois"""
    
    # Récupérer les pointages du mois
    pointages = db.query(Pointage).filter(
        Pointage.annee == annee,
        Pointage.mois == mois
    ).all()
    
    # Préparer les données
    donnees_pointages = []
    for p in pointages:
        employe = db.query(Employe).filter(Employe.id == p.employe_id).first()
        if employe:
            totaux = p.calculer_totaux()
            donnees_pointages.append({
                "employe_id": employe.id,
                "employe_nom": employe.nom,
                "employe_prenom": employe.prenom,
                "totaux": totaux
            })
    
    # Générer l'Excel
    generator = ExcelGenerator()
    excel_buffer = generator.generer_rapport_pointages_excel(donnees_pointages, annee, mois)
    
    # Retourner l'Excel
    filename = f"pointages_{annee}_{mois:02d}.xlsx"
    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/salaires/pdf")
def generer_rapport_salaires_pdf(
    annee: int = Query(..., ge=2000, le=2100),
    mois: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db)
):
    """Générer un rapport PDF des salaires pour un mois"""
    
    # Récupérer tous les employés actifs
    employes = db.query(Employe).filter(
        Employe.statut_contrat == StatutContrat.ACTIF
    ).all()
    
    calculator = SalaireCalculator(db)
    salaires = []
    
    from decimal import Decimal
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
                mois=mois
            )
            salaires.append(resultat)
            
            # Ajouter aux totaux
            totaux["salaire_cotisable"] += resultat["salaire_cotisable"]
            totaux["retenue_securite_sociale"] += resultat["retenue_securite_sociale"]
            totaux["irg"] += resultat["irg"]
            totaux["total_avances"] += resultat["total_avances"]
            totaux["retenue_credit"] += resultat["retenue_credit"]
            totaux["salaire_imposable"] += resultat["salaire_imposable"]
            totaux["salaire_net"] += resultat["salaire_net"]
        except ValueError:
            # Ignorer les employés sans pointage
            pass
    
    # Générer le PDF
    generator = RapportGenerator()
    pdf_buffer = generator.generer_rapport_salaires(salaires, annee, mois, totaux)
    
    # Retourner le PDF
    filename = f"salaires_{annee}_{mois:02d}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/salaires/excel")
def generer_rapport_salaires_excel(
    annee: int = Query(..., ge=2000, le=2100),
    mois: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db)
):
    """Générer un rapport Excel des salaires pour un mois"""
    
    # Récupérer tous les employés actifs
    employes = db.query(Employe).filter(
        Employe.statut_contrat == StatutContrat.ACTIF
    ).all()
    
    calculator = SalaireCalculator(db)
    salaires = []
    
    from decimal import Decimal
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
                mois=mois
            )
            salaires.append(resultat)
            
            # Ajouter aux totaux
            totaux["salaire_cotisable"] += resultat["salaire_cotisable"]
            totaux["retenue_securite_sociale"] += resultat["retenue_securite_sociale"]
            totaux["irg"] += resultat["irg"]
            totaux["total_avances"] += resultat["total_avances"]
            totaux["retenue_credit"] += resultat["retenue_credit"]
            totaux["salaire_imposable"] += resultat["salaire_imposable"]
            totaux["salaire_net"] += resultat["salaire_net"]
        except ValueError:
            # Ignorer les employés sans pointage
            pass
    
    # Générer l'Excel
    generator = ExcelGenerator()
    excel_buffer = generator.generer_rapport_salaires_excel(salaires, annee, mois, totaux)
    
    # Retourner l'Excel
    filename = f"salaires_{annee}_{mois:02d}.xlsx"
    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/g29/{annee}")
async def get_g29_data(
    annee: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Récupère les données G29 pour une année donnée
    """
    try:
        # Validation année
        if annee < 2020 or annee > 2100:
            raise HTTPException(status_code=400, detail="Année invalide")
        
        # Récupérer tous les employés actifs
        employes = db.query(Employe).filter(Employe.actif == True).all()
        
        if not employes:
            raise HTTPException(status_code=404, detail="Aucun employé trouvé")
        
        # Initialiser les données récapitulatives
        recap_data = {
            "annee": annee,
            "janvier_brut": Decimal(0), "janvier_irg": Decimal(0),
            "fevrier_brut": Decimal(0), "fevrier_irg": Decimal(0),
            "mars_brut": Decimal(0), "mars_irg": Decimal(0),
            "avril_brut": Decimal(0), "avril_irg": Decimal(0),
            "mai_brut": Decimal(0), "mai_irg": Decimal(0),
            "juin_brut": Decimal(0), "juin_irg": Decimal(0),
            "juillet_brut": Decimal(0), "juillet_irg": Decimal(0),
            "aout_brut": Decimal(0), "aout_irg": Decimal(0),
            "septembre_brut": Decimal(0), "septembre_irg": Decimal(0),
            "octobre_brut": Decimal(0), "octobre_irg": Decimal(0),
            "novembre_brut": Decimal(0), "novembre_irg": Decimal(0),
            "decembre_brut": Decimal(0), "decembre_irg": Decimal(0),
            "total_brut": Decimal(0),
            "total_irg": Decimal(0)
        }
        
        employes_data = []
        
        # Pour chaque employé, récupérer ses salaires de l'année
        for employe in employes:
            salaires = db.query(Salaire).filter(
                Salaire.employe_id == employe.id,
                Salaire.annee == annee
            ).all()
            
            # Initialiser les données de l'employé
            employe_data = {
                "id": employe.id,
                "nom": employe.nom,
                "prenom": employe.prenom,
                "situation_familiale": employe.situation_familiale or "C",
                "janvier_net": Decimal(0), "janvier_irg": Decimal(0),
                "fevrier_net": Decimal(0), "fevrier_irg": Decimal(0),
                "mars_net": Decimal(0), "mars_irg": Decimal(0),
                "avril_net": Decimal(0), "avril_irg": Decimal(0),
                "mai_net": Decimal(0), "mai_irg": Decimal(0),
                "juin_net": Decimal(0), "juin_irg": Decimal(0),
                "juillet_net": Decimal(0), "juillet_irg": Decimal(0),
                "aout_net": Decimal(0), "aout_irg": Decimal(0),
                "septembre_net": Decimal(0), "septembre_irg": Decimal(0),
                "octobre_net": Decimal(0), "octobre_irg": Decimal(0),
                "novembre_net": Decimal(0), "novembre_irg": Decimal(0),
                "decembre_net": Decimal(0), "decembre_irg": Decimal(0),
                "total_imposable": Decimal(0),
                "total_irg": Decimal(0)
            }
            
            # Mapper les mois aux noms de champs
            mois_map = {
                1: "janvier", 2: "fevrier", 3: "mars", 4: "avril",
                5: "mai", 6: "juin", 7: "juillet", 8: "aout",
                9: "septembre", 10: "octobre", 11: "novembre", 12: "decembre"
            }
            
            # Remplir les données mensuelles
            for salaire in salaires:
                mois_nom = mois_map.get(salaire.mois)
                if mois_nom:
                    # Données employé - utiliser salaire_imposable au lieu de salaire_net
                    employe_data[f"{mois_nom}_net"] = salaire.salaire_imposable or Decimal(0)
                    employe_data[f"{mois_nom}_irg"] = salaire.irg or Decimal(0)
                    employe_data["total_imposable"] += salaire.salaire_imposable or Decimal(0)
                    employe_data["total_irg"] += salaire.irg or Decimal(0)
                    
                    # Données récapitulatives - utiliser salaire_cotisable comme brut
                    recap_data[f"{mois_nom}_brut"] += salaire.salaire_cotisable or Decimal(0)
                    recap_data[f"{mois_nom}_irg"] += salaire.irg or Decimal(0)
                    recap_data["total_brut"] += salaire.salaire_cotisable or Decimal(0)
                    recap_data["total_irg"] += salaire.irg or Decimal(0)
            
            employes_data.append(employe_data)
        
        # Créer les objets de réponse
        recap = G29DataRecap(**recap_data)
        employes_list = [G29DataEmploye(**emp) for emp in employes_data]
        
        return G29Response(recap=recap, employes=employes_list)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des données G29: {str(e)}")


@router.get("/g29/{annee}/pdf")
async def generate_g29_pdf(
    annee: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Génère le PDF G29 pour une année donnée
    """
    try:
        # Récupérer les données G29
        g29_data_dict = await get_g29_data(annee, db, current_user)
        
        # Convertir en objet G29Response si nécessaire
        if isinstance(g29_data_dict, dict):
            g29_data = G29Response(**g29_data_dict)
        else:
            g29_data = g29_data_dict
        
        # Générer le PDF
        pdf_generator = PDFGenerator()
        pdf_bytes = pdf_generator.generate_g29(annee, g29_data)
        
        # Retourner le PDF
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=G29_{annee}.pdf"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération du PDF G29: {str(e)}")
