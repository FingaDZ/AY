from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal
from datetime import date
from dateutil.relativedelta import relativedelta

from database import get_db
from models import Credit, RetenueCredit, ProrogationCredit, Employe, StatutCredit, User
from schemas import (
    CreditCreate,
    CreditUpdate,
    CreditResponse,
    CreditListResponse,
    ProrogationCreditCreate,
    ProrogationCreditResponse,
)
from services.pdf_generator import PDFGenerator
from services.logging_service import log_action, clean_data_for_logging, ActionType
from middleware.auth import require_gestionnaire  # ⭐ v3.6.0: Permissions

router = APIRouter(prefix="/credits", tags=["Crédits"])

@router.post("/", response_model=CreditResponse, status_code=201)
def create_credit(credit: CreditCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_gestionnaire)):
    """Créer un nouveau crédit"""
    
    # Vérifier que l'employé existe
    employe = db.query(Employe).filter(Employe.id == credit.employe_id).first()
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    # Calculer la mensualité
    montant_mensualite = credit.montant_total / Decimal(credit.nombre_mensualites)
    
    # Calculer mois/année de début (mois suivant la date d'octroi)
    date_debut = credit.date_octroi + relativedelta(months=1)
    mois_debut = date_debut.month
    annee_debut = date_debut.year
    
    # Calculer mois/année de fin prévu
    date_fin_prevu = date_debut + relativedelta(months=credit.nombre_mensualites - 1)
    mois_fin_prevu = date_fin_prevu.month
    annee_fin_prevu = date_fin_prevu.year
    
    db_credit = Credit(
        employe_id=credit.employe_id,
        date_octroi=credit.date_octroi,
        montant_total=credit.montant_total,
        nombre_mensualites=credit.nombre_mensualites,
        montant_mensualite=montant_mensualite,
        montant_retenu=Decimal(0),
        statut=StatutCredit.EN_COURS,
        mois_debut=mois_debut,
        annee_debut=annee_debut,
        mois_fin_prevu=mois_fin_prevu,
        annee_fin_prevu=annee_fin_prevu
    )
    
    db.add(db_credit)
    db.commit()
    db.refresh(db_credit)
    
    # Log action
    log_action(
        db=db,
        module_name="credits",
        action_type=ActionType.CREATE,
        record_id=db_credit.id,
        description=f"Création crédit #{db_credit.id} pour {employe.prenom} {employe.nom} - Montant: {credit.montant_total} DA",
        new_data=clean_data_for_logging(db_credit),
        user=current_user,
        request=request
    )
    
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

@router.get("/pdf")
def get_credits_pdf(
    employe_id: Optional[int] = None,
    statut: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Générer un PDF de la liste des crédits"""
    
    # Récupérer les crédits avec filtres
    query = db.query(Credit)
    
    if employe_id:
        query = query.filter(Credit.employe_id == employe_id)
    
    if statut:
        if statut not in ["En cours", "Soldé"]:
            raise HTTPException(status_code=400, detail="Statut invalide")
        query = query.filter(Credit.statut == statut)
    
    credits = query.all()
    
    # Préparer les données pour le PDF
    credits_data = []
    filters_data = {}
    
    for credit in credits:
        employe = db.query(Employe).filter(Employe.id == credit.employe_id).first()
        employe_nom = f"{employe.prenom} {employe.nom}" if employe else f"ID {credit.employe_id}"
        
        credits_data.append({
            'employe_nom': employe_nom,
            'date_octroi': credit.date_octroi.strftime('%d/%m/%Y'),
            'montant_total': float(credit.montant_total),
            'nombre_mensualites': credit.nombre_mensualites,
            'montant_retenu': float(credit.montant_retenu),
            'statut': credit.statut.value if hasattr(credit.statut, 'value') else str(credit.statut)
        })
        
        # Ajouter le nom de l'employé aux filtres si un seul employé
        if employe_id and not filters_data.get('employe_nom'):
            filters_data['employe_nom'] = employe_nom
    
    if statut:
        filters_data['statut'] = statut
    
    # Générer le PDF
    pdf_generator = PDFGenerator()
    pdf_buffer = pdf_generator.generate_credits_pdf(credits_data, filters_data)
    
    # Retourner le PDF
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=credits_{date.today().strftime('%Y%m%d')}.pdf"
        }
    )

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

@router.get("/{credit_id}/echeancier")
def get_echeancier_credit(credit_id: int, db: Session = Depends(get_db)):
    """Obtenir l'échéancier complet d'un crédit avec statuts de paiement"""
    
    credit = db.query(Credit).filter(Credit.id == credit_id).first()
    
    if not credit:
        raise HTTPException(status_code=404, detail="Crédit non trouvé")
    
    # Récupérer les retenues existantes
    retenues = db.query(RetenueCredit).filter(
        RetenueCredit.credit_id == credit_id
    ).all()
    
    # Récupérer les prorogations
    prorogations = db.query(ProrogationCredit).filter(
        ProrogationCredit.credit_id == credit_id
    ).all()
    
    # Créer un dictionnaire des retenues par (mois, année)
    retenues_dict = {(r.mois, r.annee): r for r in retenues}
    
    # Créer un dictionnaire des prorogations par (mois_initial, année_initiale)
    prorogations_dict = {(p.mois_initial, p.annee_initiale): p for p in prorogations}
    
    # Générer l'échéancier complet
    echeancier = []
    date_debut = credit.date_octroi
    
    for i in range(credit.nombre_mensualites):
        date_mensualite = date_debut + relativedelta(months=i)
        mois = date_mensualite.month
        annee = date_mensualite.year
        
        # Vérifier si retenue existe
        retenue = retenues_dict.get((mois, annee))
        
        # Vérifier si prorogation existe
        prorogation = prorogations_dict.get((mois, annee))
        
        echeancier.append({
            "mois": mois,
            "annee": annee,
            "montant": float(credit.montant_mensualite),
            "statut": "payé" if retenue else "non payé",
            "date_retenue": retenue.date_retenue if retenue else None,
            "prorogation": {
                "mois_reporte": prorogation.mois_reporte,
                "annee_reportee": prorogation.annee_reportee,
                "motif": prorogation.motif
            } if prorogation else None
        })
    
    return echeancier

@router.put("/{credit_id}", response_model=CreditResponse)
def update_credit(
    credit_id: int,
    credit_update: CreditUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_gestionnaire)
):
    """Mettre à jour un crédit (nombre de mensualités)"""
    
    credit = db.query(Credit).filter(Credit.id == credit_id).first()
    
    if not credit:
        raise HTTPException(status_code=404, detail="Crédit non trouvé")
    
    if credit_update.nombre_mensualites:
        credit.nombre_mensualites = credit_update.nombre_mensualites
        # Recalculer la mensualité
        credit.montant_mensualite = credit.montant_total / Decimal(credit.nombre_mensualites)
    
    # Log action
    log_action(
        db=db,
        module_name="credits",
        action_type=ActionType.UPDATE,
        record_id=credit_id,
        description=f"Modification crédit #{credit_id}",
        new_data=clean_data_for_logging(credit),
        user=current_user,
        request=request
    )
    
    db.commit()
    db.refresh(credit)
    
    return credit

@router.post("/{credit_id}/prorogation", response_model=ProrogationCreditResponse)
def create_prorogation(
    credit_id: int,
    prorogation: ProrogationCreditCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_gestionnaire)
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
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_gestionnaire)
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
def delete_credit(credit_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_gestionnaire)):
    """Supprimer un crédit"""
    
    credit = db.query(Credit).filter(Credit.id == credit_id).first()
    
    if not credit:
        raise HTTPException(status_code=404, detail="Crédit non trouvé")
    
    # Log action before delete
    log_action(
        db=db,
        module_name="credits",
        action_type=ActionType.DELETE,
        record_id=credit_id,
        description=f"Suppression crédit #{credit_id}",
        old_data=clean_data_for_logging(credit),
        user=current_user,
        request=request
    )
    
    db.delete(credit)
    db.commit()
    
    return None
