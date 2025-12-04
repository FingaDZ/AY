from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from decimal import Decimal
from datetime import date as date_type

from database import get_db
from models import Avance, Employe, Parametres
from schemas import (
    AvanceCreate,
    AvanceUpdate,
    AvanceResponse,
    AvanceListResponse,
    AvanceTotalMensuel,
)
from services.pdf_generator import PDFGenerator
from services.logging_service import log_action, clean_data_for_logging, ActionType

router = APIRouter(prefix="/avances", tags=["Avances"])

@router.post("/", response_model=AvanceResponse, status_code=201)
def create_avance(avance: AvanceCreate, db: Session = Depends(get_db)):
    """Créer une nouvelle avance"""
    
    # Vérifier que l'employé existe
    employe = db.query(Employe).filter(Employe.id == avance.employe_id).first()
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    # Calculer la limite autorisée (70% du salaire de base)
    limite_autorisee = employe.salaire_base * Decimal('0.70')
    
    # Calculer le total des avances déjà accordées pour ce mois
    total_avances_mois = db.query(func.sum(Avance.montant)).filter(
        Avance.employe_id == avance.employe_id,
        Avance.mois_deduction == avance.mois_deduction,
        Avance.annee_deduction == avance.annee_deduction
    ).scalar() or Decimal('0')
    
    # Vérifier que le total (avances existantes + nouvelle avance) ne dépasse pas 70%
    total_avec_nouvelle = total_avances_mois + avance.montant
    
    if total_avec_nouvelle > limite_autorisee:
        raise HTTPException(
            status_code=400,
            detail=f"Le total des avances pour {avance.mois_deduction}/{avance.annee_deduction} "
                   f"({total_avec_nouvelle:.2f} DA) dépasserait la limite autorisée de 70% du salaire "
                   f"({limite_autorisee:.2f} DA). Avances déjà accordées: {total_avances_mois:.2f} DA. "
                   f"Montant maximum restant: {(limite_autorisee - total_avances_mois):.2f} DA"
        )
    
    db_avance = Avance(**avance.model_dump())
    db.add(db_avance)
    db.commit()
    db.refresh(db_avance)
    
    # Log action
    log_action(
        db=db,
        module_name="avances",
        action_type=ActionType.CREATE,
        description=f"Création avance #{db_avance.id} pour {employe.prenom} {employe.nom} - Montant: {avance.montant} DA",
        new_data=clean_data_for_logging(db_avance)
    )
    
    return db_avance

@router.get("/", response_model=AvanceListResponse)
def list_avances(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    employe_id: Optional[int] = None,
    annee: Optional[int] = None,
    mois: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Lister toutes les avances avec filtres"""
    
    query = db.query(Avance)
    
    if employe_id:
        query = query.filter(Avance.employe_id == employe_id)
    
    if annee:
        query = query.filter(Avance.annee_deduction == annee)
    
    if mois:
        query = query.filter(Avance.mois_deduction == mois)
    
    total = query.count()
    avances = query.offset(skip).limit(limit).all()
    
    return AvanceListResponse(total=total, avances=avances)

@router.get("/total-mensuel")
def get_total_mensuel(
    annee: int = Query(..., ge=2000, le=2100),
    mois: int = Query(..., ge=1, le=12),
    employe_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Obtenir le total des avances par employé pour un mois"""
    
    query = db.query(
        Avance.employe_id,
        func.sum(Avance.montant).label("total_avances"),
        func.count(Avance.id).label("nombre_avances")
    ).filter(
        Avance.annee_deduction == annee,
        Avance.mois_deduction == mois
    )
    
    if employe_id:
        query = query.filter(Avance.employe_id == employe_id)
    
    results = query.group_by(Avance.employe_id).all()
    
    # Enrichir avec les informations de l'employé
    totaux = []
    for result in results:
        employe = db.query(Employe).filter(Employe.id == result.employe_id).first()
        if employe:
            totaux.append(AvanceTotalMensuel(
                employe_id=employe.id,
                employe_nom=employe.nom,
                employe_prenom=employe.prenom,
                mois=mois,
                annee=annee,
                total_avances=result.total_avances or Decimal(0),
                nombre_avances=result.nombre_avances
            ))
    
    return {
        "annee": annee,
        "mois": mois,
        "totaux": totaux
    }

@router.get("/{avance_id}", response_model=AvanceResponse)
def get_avance(avance_id: int, db: Session = Depends(get_db)):
    """Obtenir une avance par son ID"""
    
    avance = db.query(Avance).filter(Avance.id == avance_id).first()
    
    if not avance:
        raise HTTPException(status_code=404, detail="Avance non trouvée")
    
    return avance

@router.put("/{avance_id}", response_model=AvanceResponse)
def update_avance(
    avance_id: int,
    avance_update: AvanceUpdate,
    db: Session = Depends(get_db)
):
    """Mettre à jour une avance avec validation de la limite 70%"""
    
    # Récupérer l'avance existante
    avance = db.query(Avance).filter(Avance.id == avance_id).first()
    
    if not avance:
        raise HTTPException(status_code=404, detail="Avance non trouvée")
    
    # Récupérer l'employé
    employe_id = avance_update.employe_id if avance_update.employe_id else avance.employe_id
    employe = db.query(Employe).filter(Employe.id == employe_id).first()
    
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    # Déterminer les valeurs à utiliser pour la validation
    nouveau_montant = avance_update.montant if avance_update.montant else avance.montant
    nouveau_mois = avance_update.mois_deduction if avance_update.mois_deduction else avance.mois_deduction
    nouvelle_annee = avance_update.annee_deduction if avance_update.annee_deduction else avance.annee_deduction
    
    # Calculer la limite autorisée (70% du salaire de base)
    limite_autorisee = employe.salaire_base * Decimal('0.70')
    
    # Calculer le total des autres avances du même mois (excluant l'avance actuelle)
    total_autres_avances = db.query(func.sum(Avance.montant)).filter(
        Avance.employe_id == employe_id,
        Avance.mois_deduction == nouveau_mois,
        Avance.annee_deduction == nouvelle_annee,
        Avance.id != avance_id  # Exclure l'avance en cours de modification
    ).scalar() or Decimal('0')
    
    # Vérifier que le total ne dépasse pas 70%
    total_avec_modification = total_autres_avances + nouveau_montant
    
    if total_avec_modification > limite_autorisee:
        raise HTTPException(
            status_code=400,
            detail=f"Le total des avances pour {nouveau_mois}/{nouvelle_annee} "
                   f"({total_avec_modification:.2f} DA) dépasserait la limite autorisée de 70% "
                   f"du salaire ({limite_autorisee:.2f} DA). "
                   f"Autres avances du mois: {total_autres_avances:.2f} DA. "
                   f"Montant maximum pour cette avance: {(limite_autorisee - total_autres_avances):.2f} DA"
        )
    
    # Appliquer les modifications
    update_data = avance_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(avance, field, value)
    
    # Log action
    log_action(
        db=db,
        module_name="avances",
        action_type=ActionType.UPDATE,
        description=f"Modification avance #{avance_id}",
        new_data=clean_data_for_logging(avance)
    )
    
    db.commit()
    db.refresh(avance)
    
    return avance

@router.delete("/{avance_id}", status_code=204)
def delete_avance(avance_id: int, db: Session = Depends(get_db)):
    """Supprimer une avance"""
    
    avance = db.query(Avance).filter(Avance.id == avance_id).first()
    
    if not avance:
        raise HTTPException(status_code=404, detail="Avance non trouvée")
    
    # Log action before delete
    log_action(
        db=db,
        module_name="avances",
        action_type=ActionType.DELETE,
        description=f"Suppression avance #{avance_id}",
        old_data=clean_data_for_logging(avance)
    )
    
    db.delete(avance)
    db.commit()
    
    return None

@router.get("/rapport-pdf/mensuel")
def generer_rapport_avances_mensuel(
    annee: int = Query(..., description="Année"),
    mois: int = Query(..., description="Mois"),
    db: Session = Depends(get_db)
):
    """Générer un rapport PDF des avances du mois"""
    
    # Récupérer les avances du mois
    avances = db.query(Avance).join(Employe).filter(
        func.extract('year', Avance.date_avance) == annee,
        func.extract('month', Avance.date_avance) == mois
    ).all()
    
    if not avances:
        raise HTTPException(
            status_code=404,
            detail=f"Aucune avance trouvée pour {mois}/{annee}"
        )
    
    # Préparer les données
    avances_data = []
    for avance in avances:
        avances_data.append({
            'date_avance': avance.date_avance.strftime('%d/%m/%Y'),
            'employe_nom': avance.employe.nom if avance.employe else '-',
            'employe_prenom': avance.employe.prenom if avance.employe else '-',
            'montant': float(avance.montant),
            'motif': avance.motif or '-',
            'statut': 'Validée' if avance.date_avance else 'En attente'
        })
    
    # Récupérer les paramètres de l'entreprise
    company = db.query(Parametres).first()
    company_info = company.to_dict() if company else None
    
    # Générer le PDF
    pdf_generator = PDFGenerator()
    periode = {'annee': annee, 'mois': mois}
    pdf_buffer = pdf_generator.generate_rapport_avances(
        avances_data=avances_data,
        periode=periode,
        company_info=company_info
    )
    
    # Nom du fichier
    filename = f"avances_{mois:02d}_{annee}.pdf"
    
    # Retourner le PDF
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
