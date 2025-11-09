from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal
from datetime import date

from database import get_db
from models import Credit, RetenueCredit, ProrogationCredit, Employe, StatutCredit
from schemas import (
    CreditCreate,
    CreditUpdate,
    CreditResponse,
    CreditListResponse,
    ProrogationCreditCreate,
    ProrogationCreditResponse,
)

router = APIRouter(prefix="/credits", tags=["Crédits"])

@router.post("/", response_model=CreditResponse, status_code=201)
def create_credit(credit: CreditCreate, db: Session = Depends(get_db)):
    """Créer un nouveau crédit"""
    
    # Vérifier que l'employé existe
    employe = db.query(Employe).filter(Employe.id == credit.employe_id).first()
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    # Calculer la mensualité
    montant_mensualite = credit.montant_total / Decimal(credit.nombre_mensualites)
    
    db_credit = Credit(
        employe_id=credit.employe_id,
        date_octroi=credit.date_octroi,
        montant_total=credit.montant_total,
        nombre_mensualites=credit.nombre_mensualites,
        montant_mensualite=montant_mensualite,
        montant_retenu=Decimal(0),
        statut=StatutCredit.EN_COURS
    )
    
    db.add(db_credit)
    db.commit()
    db.refresh(db_credit)
    
    return db_credit

@router.get("/", response_model=CreditListResponse)
def list_credits(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    employe_id: Optional[int] = None,
    statut: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lister tous les crédits avec filtres"""
    
    query = db.query(Credit)
    
    if employe_id:
        query = query.filter(Credit.employe_id == employe_id)
    
    if statut:
        if statut not in ["En cours", "Soldé"]:
            raise HTTPException(status_code=400, detail="Statut invalide")
        query = query.filter(Credit.statut == statut)
    
    total = query.count()
    credits = query.offset(skip).limit(limit).all()
    
    return CreditListResponse(total=total, credits=credits)

@router.get("/{credit_id}", response_model=CreditResponse)
def get_credit(credit_id: int, db: Session = Depends(get_db)):
    """Obtenir un crédit par son ID"""
    
    credit = db.query(Credit).filter(Credit.id == credit_id).first()
    
    if not credit:
        raise HTTPException(status_code=404, detail="Crédit non trouvé")
    
    return credit

@router.get("/{credit_id}/historique")
def get_historique_credit(credit_id: int, db: Session = Depends(get_db)):
    """Obtenir l'historique complet d'un crédit (retenues et prorogations)"""
    
    credit = db.query(Credit).filter(Credit.id == credit_id).first()
    
    if not credit:
        raise HTTPException(status_code=404, detail="Crédit non trouvé")
    
    retenues = db.query(RetenueCredit).filter(
        RetenueCredit.credit_id == credit_id
    ).order_by(RetenueCredit.annee, RetenueCredit.mois).all()
    
    prorogations = db.query(ProrogationCredit).filter(
        ProrogationCredit.credit_id == credit_id
    ).order_by(ProrogationCredit.date_prorogation).all()
    
    return {
        "credit": credit,
        "retenues": retenues,
        "prorogations": prorogations
    }

@router.put("/{credit_id}", response_model=CreditResponse)
def update_credit(
    credit_id: int,
    credit_update: CreditUpdate,
    db: Session = Depends(get_db)
):
    """Mettre à jour un crédit (nombre de mensualités)"""
    
    credit = db.query(Credit).filter(Credit.id == credit_id).first()
    
    if not credit:
        raise HTTPException(status_code=404, detail="Crédit non trouvé")
    
    if credit_update.nombre_mensualites:
        credit.nombre_mensualites = credit_update.nombre_mensualites
        # Recalculer la mensualité
        credit.montant_mensualite = credit.montant_total / Decimal(credit.nombre_mensualites)
    
    db.commit()
    db.refresh(credit)
    
    return credit

@router.post("/{credit_id}/prorogation", response_model=ProrogationCreditResponse)
def create_prorogation(
    credit_id: int,
    prorogation: ProrogationCreditCreate,
    db: Session = Depends(get_db)
):
    """Créer une prorogation (report de mensualité)"""
    
    credit = db.query(Credit).filter(Credit.id == credit_id).first()
    
    if not credit:
        raise HTTPException(status_code=404, detail="Crédit non trouvé")
    
    if prorogation.credit_id != credit_id:
        raise HTTPException(status_code=400, detail="ID de crédit incohérent")
    
    db_prorogation = ProrogationCredit(**prorogation.model_dump())
    db.add(db_prorogation)
    db.commit()
    db.refresh(db_prorogation)
    
    return db_prorogation

@router.post("/{credit_id}/retenue")
def enregistrer_retenue(
    credit_id: int,
    mois: int = Query(..., ge=1, le=12),
    annee: int = Query(..., ge=2000),
    db: Session = Depends(get_db)
):
    """Enregistrer une retenue mensuelle pour un crédit"""
    
    credit = db.query(Credit).filter(Credit.id == credit_id).first()
    
    if not credit:
        raise HTTPException(status_code=404, detail="Crédit non trouvé")
    
    if credit.statut == StatutCredit.SOLDE:
        raise HTTPException(status_code=400, detail="Le crédit est déjà soldé")
    
    # Vérifier si une retenue existe déjà pour ce mois
    retenue_existante = db.query(RetenueCredit).filter(
        RetenueCredit.credit_id == credit_id,
        RetenueCredit.mois == mois,
        RetenueCredit.annee == annee
    ).first()
    
    if retenue_existante:
        raise HTTPException(
            status_code=400,
            detail="Une retenue existe déjà pour ce mois"
        )
    
    # Vérifier s'il y a une prorogation pour ce mois
    prorogation = db.query(ProrogationCredit).filter(
        ProrogationCredit.credit_id == credit_id,
        ProrogationCredit.mois_initial == mois,
        ProrogationCredit.annee_initiale == annee
    ).first()
    
    if prorogation:
        return {
            "message": "Retenue prorogée",
            "prorogation": prorogation
        }
    
    # Calculer le montant de la retenue
    montant_restant = credit.montant_restant
    montant_retenue = min(credit.montant_mensualite, montant_restant)
    
    # Créer la retenue
    retenue = RetenueCredit(
        credit_id=credit_id,
        mois=mois,
        annee=annee,
        montant=montant_retenue,
        date_retenue=date.today()
    )
    
    db.add(retenue)
    
    # Mettre à jour le crédit
    credit.montant_retenu += montant_retenue
    
    # Vérifier si le crédit est soldé
    if credit.montant_retenu >= credit.montant_total:
        credit.statut = StatutCredit.SOLDE
    
    db.commit()
    db.refresh(credit)
    
    return {
        "message": "Retenue enregistrée",
        "credit": credit,
        "retenue": retenue
    }

@router.delete("/{credit_id}", status_code=204)
def delete_credit(credit_id: int, db: Session = Depends(get_db)):
    """Supprimer un crédit"""
    
    credit = db.query(Credit).filter(Credit.id == credit_id).first()
    
    if not credit:
        raise HTTPException(status_code=404, detail="Crédit non trouvé")
    
    db.delete(credit)
    db.commit()
    
    return None
