from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import Employe, Pointage, StatutContrat
from services import SalaireCalculator, RapportGenerator, ExcelGenerator

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
