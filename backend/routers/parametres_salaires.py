"""Routes API pour les paramètres de salaire"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from datetime import date
import openpyxl
from decimal import Decimal

from database import get_db
from models import ParametresSalaire, IRGBareme, ReportAvanceCredit
from schemas import (
    ParametresSalaireResponse,
    ParametresSalaireUpdate,
    IRGBaremeResponse,
    IRGBaremeCreate,
    ReportAvanceCreditResponse,
    ReportAvanceCreditCreate,
)

router = APIRouter(prefix="/parametres-salaires", tags=["Paramètres Salaires"])


@router.get("/", response_model=ParametresSalaireResponse)
def get_parametres_salaires(db: Session = Depends(get_db)):
    """Récupérer les paramètres de salaire actuels"""
    params = db.query(ParametresSalaire).first()
    
    if not params:
        # Créer paramètres par défaut si n'existent pas
        params = ParametresSalaire()
        db.add(params)
        db.commit()
        db.refresh(params)
    
    return params


@router.put("/", response_model=ParametresSalaireResponse)
def update_parametres_salaires(
    params_update: ParametresSalaireUpdate,
    db: Session = Depends(get_db)
):
    """Mettre à jour les paramètres de salaire"""
    params = db.query(ParametresSalaire).first()
    
    if not params:
        params = ParametresSalaire()
        db.add(params)
    
    # Mettre à jour les champs
    for field, value in params_update.dict(exclude_unset=True).items():
        setattr(params, field, value)
    
    db.commit()
    db.refresh(params)
    
    return params


@router.get("/irg-bareme", response_model=List[IRGBaremeResponse])
def get_irg_bareme(
    actif_only: bool = True,
    db: Session = Depends(get_db)
):
    """Récupérer le barème IRG actif"""
    query = db.query(IRGBareme)
    
    if actif_only:
        query = query.filter(IRGBareme.actif == True)
    
    bareme = query.order_by(IRGBareme.salaire_min).all()
    return bareme


@router.post("/irg-bareme", response_model=IRGBaremeResponse)
def create_irg_tranche(
    tranche: IRGBaremeCreate,
    db: Session = Depends(get_db)
):
    """Créer une nouvelle tranche IRG"""
    nouvelle_tranche = IRGBareme(**tranche.dict())
    db.add(nouvelle_tranche)
    db.commit()
    db.refresh(nouvelle_tranche)
    
    return nouvelle_tranche


@router.delete("/irg-bareme/{tranche_id}")
def delete_irg_tranche(
    tranche_id: int,
    db: Session = Depends(get_db)
):
    """Supprimer une tranche IRG"""
    tranche = db.query(IRGBareme).filter(IRGBareme.id == tranche_id).first()
    
    if not tranche:
        raise HTTPException(status_code=404, detail="Tranche IRG non trouvée")
    
    db.delete(tranche)
    db.commit()
    
    return {"message": "Tranche IRG supprimée avec succès"}


@router.post("/irg-bareme/importer")
async def importer_bareme_irg(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Importer barème IRG depuis Excel (2 colonnes: MONTANT, IRG)"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(400, "Format de fichier non supporté (Excel requis)")
        
    try:
        # Lire fichier Excel
        wb = openpyxl.load_workbook(file.file, data_only=True)
        sheet = wb.active
        
        # Désactiver ancien barème
        db.query(IRGBareme).update({"actif": False})
        
        count = 0
        errors = []
        
        # Importer nouveau (colonnes: MONTANT, IRG)
        for idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            if row[0] is not None and row[1] is not None:
                try:
                    bareme = IRGBareme(
                        salaire=Decimal(str(row[0])),      # Colonne MONTANT
                        montant_irg=Decimal(str(row[1])),  # Colonne IRG
                        actif=True
                    )
                    db.add(bareme)
                    count += 1
                except Exception as e:
                    errors.append(f"Ligne {idx}: {str(e)}")
                    continue
        
        db.commit()
        
        # Invalider cache IRG
        from services.irg_calculator import get_irg_calculator
        calc = get_irg_calculator(db)
        calc.recharger_bareme()
        
        message = f"Barème importé avec succès ({count} tranches)"
        if errors:
            message += f" - {len(errors)} erreurs ignorées"
        
        return {"message": message, "count": count, "errors": errors[:5]}
        
    except Exception as e:
        db.rollback()
        import traceback
        error_detail = f"Erreur lors de l'import: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)
        raise HTTPException(500, f"Erreur lors de l'import: {str(e)}")



@router.post("/irg-bareme/desactiver-tout")
def desactiver_bareme_actif(db: Session = Depends(get_db)):
    """Désactiver tout le barème actif (avant nouvel import)"""
    try:
        db.query(IRGBareme).update({"actif": False})
        db.commit()
        
        # Invalider cache aussi - CORRECTION: passer db
        from services.irg_calculator import get_irg_calculator
        calc = get_irg_calculator(db)
        calc.recharger_bareme()
        
        return {"message": "Barème désactivé"}
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Erreur lors de la désactivation: {str(e)}")



@router.get("/reports", response_model=List[ReportAvanceCreditResponse])
def get_reports_en_attente(
    employe_id: int = None,
    mois: int = None,
    annee: int = None,
    db: Session = Depends(get_db)
):
    """Récupérer les reports en attente"""
    query = db.query(ReportAvanceCredit).filter(
        ReportAvanceCredit.traite == False
    )
    
    if employe_id:
        query = query.filter(ReportAvanceCredit.employe_id == employe_id)
    
    if mois and annee:
        query = query.filter(
            ReportAvanceCredit.mois_destination == mois,
            ReportAvanceCredit.annee_destination == annee
        )
    
    reports = query.all()
    return reports


@router.post("/reports", response_model=ReportAvanceCreditResponse)
def create_report_manuel(
    report: ReportAvanceCreditCreate,
    db: Session = Depends(get_db)
):
    """Créer un report manuel d'avance ou crédit"""
    from datetime import datetime
    
    # Validation: motif obligatoire pour report manuel
    if not report.motif:
        raise HTTPException(
            status_code=400,
            detail="Le motif est obligatoire pour un report manuel"
        )
    
    # Créer le report
    nouveau_report = ReportAvanceCredit(
        **report.dict(),
        mois_origine=datetime.now().month,
        annee_origine=datetime.now().year,
        automatique=False
    )
    
    db.add(nouveau_report)
    db.commit()
    db.refresh(nouveau_report)
    
    return nouveau_report
