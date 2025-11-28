from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, selectinload
from typing import Optional
from datetime import date

from database import get_db
from models import Employe, StatutContrat, SituationFamiliale, Parametres, User, ActionType
from schemas import (
    EmployeCreate,
    EmployeUpdate,
    EmployeResponse,
    EmployeListResponse,
)
from services.pdf_generator import PDFGenerator
from services.logging_service import log_action, clean_data_for_logging
from middleware import require_admin, require_auth

router = APIRouter(prefix="/employes", tags=["Employés"])

@router.post("/", response_model=EmployeResponse, status_code=201)
def create_employe(employe: EmployeCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Créer un nouvel employé"""
    try:
        # Vérification 1: Doublon par nom + prénom + date de naissance (seulement employés actifs)
        existing_by_identity = db.query(Employe).filter(
            Employe.nom == employe.nom,
            Employe.prenom == employe.prenom,
            Employe.date_naissance == employe.date_naissance,
            Employe.actif == True  # Exclure les employés désactivés
        ).first()
        
        if existing_by_identity:
            raise HTTPException(
                status_code=400,
                detail=f"Un employé actif avec le même nom ({employe.nom}), prénom ({employe.prenom}) et date de naissance existe déjà"
            )
        
        # Vérification 2: Doublon par numéro de sécurité sociale (seulement employés actifs)
        existing_by_secu = db.query(Employe).filter(
            Employe.numero_secu_sociale == employe.numero_secu_sociale,
            Employe.actif == True  # Exclure les employés désactivés
        ).first()
        
        if existing_by_secu:
            raise HTTPException(
                status_code=400,
                detail=f"Un employé actif avec ce numéro de sécurité sociale ({employe.numero_secu_sociale}) existe déjà"
            )
        
        # Vérification 3: Doublon par numéro de compte bancaire (seulement employés actifs)
        existing_by_compte = db.query(Employe).filter(
            Employe.numero_compte_bancaire == employe.numero_compte_bancaire,
            Employe.actif == True  # Exclure les employés désactivés
        ).first()
        
        if existing_by_compte:
            raise HTTPException(
                status_code=400,
                detail=f"Un employé actif avec ce numéro de compte bancaire ({employe.numero_compte_bancaire}) existe déjà"
            )
        
        # Créer l'employé avec données
        employe_data = employe.model_dump()
        
        # Calculer automatiquement date_fin_contrat si duree_contrat est fournie
        if employe_data.get('duree_contrat') and employe_data.get('date_recrutement'):
            from dateutil.relativedelta import relativedelta
            employe_data['date_fin_contrat'] = employe_data['date_recrutement'] + relativedelta(months=employe_data['duree_contrat'])
        
        db_employe = Employe(**employe_data)
        db.add(db_employe)
        db.commit()
        db.refresh(db_employe)
        
        # Log de la création
        try:
            log_action(
                db=db,
                module_name="employes",
                action_type=ActionType.CREATE,
                record_id=db_employe.id,
                new_data=clean_data_for_logging(db_employe),
                description=f"Création employé: {db_employe.nom} {db_employe.prenom}",
                user=current_user,
                request=request
            )
        except Exception as e:
            print(f"Erreur logging: {e}")
        
        return db_employe
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@router.get("/", response_model=EmployeListResponse)
def list_employes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    statut: Optional[str] = Query(None, description="Filtrer par statut (Actif/Inactif)"),
    search: Optional[str] = Query(None, description="Rechercher par nom ou prénom"),
    poste: Optional[str] = Query(None, description="Filtrer par poste"),
    inclure_inactifs: bool = Query(False, description="Inclure les employés inactifs/désactivés"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth)
):
    """Lister tous les employés avec filtres - Par défaut, exclut les employés désactivés"""
    
    query = db.query(Employe)
    
    # Filtrer les employés actifs par défaut (soft delete)
    if not inclure_inactifs:
        query = query.filter(Employe.actif == True)
    
    # Filtrer par statut
    if statut:
        if statut not in ["Actif", "Inactif"]:
            raise HTTPException(status_code=400, detail="Statut invalide")
        from models.employe import StatutContrat
        statut_enum = StatutContrat.ACTIF if statut == "Actif" else StatutContrat.INACTIF
        query = query.filter(Employe.statut_contrat == statut_enum)
    
    # Recherche par nom ou prénom
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Employe.nom.like(search_pattern)) | 
            (Employe.prenom.like(search_pattern))
        )
    
    # Filtrer par poste
    if poste:
        query = query.filter(Employe.poste_travail.like(f"%{poste}%"))
    
    total = query.count()
    employes = query.offset(skip).limit(limit).all()
    
    return EmployeListResponse(total=total, employes=employes)

@router.get("/{employe_id}", response_model=EmployeResponse)
def get_employe(employe_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_auth)):
    """Obtenir un employé par son ID"""
    
    employe = db.query(Employe).filter(Employe.id == employe_id).first()
    
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    return employe

@router.put("/{employe_id}", response_model=EmployeResponse)
def update_employe(
    employe_id: int,
    employe_update: EmployeUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Mettre à jour un employé"""
    
    employe = db.query(Employe).filter(Employe.id == employe_id).first()
    
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    # Sauvegarder les anciennes données pour le log
    old_data = clean_data_for_logging(employe)
    
    # Vérification 1: Doublon par nom + prénom + date de naissance (si modifiés)
    if employe_update.nom or employe_update.prenom or employe_update.date_naissance:
        nom_check = employe_update.nom if employe_update.nom else employe.nom
        prenom_check = employe_update.prenom if employe_update.prenom else employe.prenom
        date_check = employe_update.date_naissance if employe_update.date_naissance else employe.date_naissance
        
        existing_by_identity = db.query(Employe).filter(
            Employe.nom == nom_check,
            Employe.prenom == prenom_check,
            Employe.date_naissance == date_check,
            Employe.id != employe_id
        ).first()
        
        if existing_by_identity:
            raise HTTPException(
                status_code=400,
                detail=f"Un autre employé avec le même nom ({nom_check}), prénom ({prenom_check}) et date de naissance existe déjà"
            )
    
    # Vérification 2: Doublon par numéro de sécurité sociale (si modifié)
    if employe_update.numero_secu_sociale:
        existing_by_secu = db.query(Employe).filter(
            Employe.numero_secu_sociale == employe_update.numero_secu_sociale,
            Employe.id != employe_id
        ).first()
        
        if existing_by_secu:
            raise HTTPException(
                status_code=400,
                detail=f"Un autre employé avec ce numéro de sécurité sociale ({employe_update.numero_secu_sociale}) existe déjà"
            )
    
    # Vérification 3: Doublon par numéro de compte bancaire (si modifié)
    if employe_update.numero_compte_bancaire:
        existing_by_compte = db.query(Employe).filter(
            Employe.numero_compte_bancaire == employe_update.numero_compte_bancaire,
            Employe.id != employe_id
        ).first()
        
        if existing_by_compte:
            raise HTTPException(
                status_code=400,
                detail=f"Un autre employé avec ce numéro de compte bancaire ({employe_update.numero_compte_bancaire}) existe déjà"
            )
    
    # Mettre à jour les champs
    update_data = employe_update.model_dump(exclude_unset=True)
    
    # Calculer automatiquement date_fin_contrat si duree_contrat ou date_recrutement est modifiée
    if 'duree_contrat' in update_data or 'date_recrutement' in update_data:
        duree = update_data.get('duree_contrat', employe.duree_contrat)
        date_recrutement = update_data.get('date_recrutement', employe.date_recrutement)
        
        if duree and date_recrutement:
            from dateutil.relativedelta import relativedelta
            update_data['date_fin_contrat'] = date_recrutement + relativedelta(months=duree)
    
    for field, value in update_data.items():
        setattr(employe, field, value)
    
    db.commit()
    db.refresh(employe)
    
    # Log de la modification
    try:
        log_action(
            db=db,
            module_name="employes",
            action_type=ActionType.UPDATE,
            record_id=employe.id,
            old_data=old_data,
            new_data=clean_data_for_logging(employe),
            description=f"Modification employé: {employe.nom} {employe.prenom}",
            user=current_user,
            request=request
        )
    except Exception as e:
        print(f"Erreur logging: {e}")
    
    return employe

@router.get("/{employe_id}/check-delete", status_code=200)
def check_can_delete(employe_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_auth)):
    """Vérifier si un employé peut être supprimé ou doit être désactivé"""
    from models import Pointage
    
    employe = db.query(Employe).filter(Employe.id == employe_id).first()
    
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    # Vérifier uniquement les pointages
    has_pointages = db.query(Pointage).filter(Pointage.employe_id == employe_id).count() > 0
    
    can_delete = not has_pointages
    
    return {
        "can_delete": can_delete,
        "employe_id": employe_id,
        "employe_nom": f"{employe.nom} {employe.prenom}",
        "has_data": {
            "pointages": has_pointages
        }
    }

@router.delete("/{employe_id}", status_code=200)
def delete_employe(employe_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Supprimer définitivement un employé (seulement si aucun pointage)"""
    from models import Pointage
    
    employe = db.query(Employe).filter(Employe.id == employe_id).first()
    
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    # Vérifier s'il existe des pointages
    has_pointages = db.query(Pointage).filter(Pointage.employe_id == employe_id).count() > 0
    
    if has_pointages:
        raise HTTPException(
            status_code=400, 
            detail="Impossible de supprimer cet employé car il possède des pointages dans la base de données."
        )
    
    # Aucune donnée liée - suppression définitive
    employe_data = clean_data_for_logging(employe)
    employe_name = f"{employe.nom} {employe.prenom}"
    
    # Log de la suppression AVANT de supprimer
    try:
        log_action(
            db=db,
            module_name="employes",
            action_type=ActionType.DELETE,
            record_id=employe_id,
            old_data=employe_data,
            description=f"Suppression définitive employé: {employe_name}",
            user=current_user,
            request=request
        )
    except Exception as e:
        print(f"Erreur logging: {e}")
    
    # Suppression définitive
    db.delete(employe)
    db.commit()
    
    return {
        "message": "Employé supprimé définitivement avec succès",
        "employe_id": employe_id
    }

@router.post("/{employe_id}/deactivate", status_code=200)
def deactivate_employe(employe_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Désactiver un employé (soft delete)"""
    employe = db.query(Employe).filter(Employe.id == employe_id).first()
    
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    if not employe.actif:
        raise HTTPException(status_code=400, detail="L'employé est déjà désactivé")
    
    employe_data = clean_data_for_logging(employe)
    employe_name = f"{employe.nom} {employe.prenom}"
    
    # Désactiver l'employé
    employe.actif = False
    employe.statut_contrat = StatutContrat.INACTIF
    
    db.commit()
    db.refresh(employe)
    
    # Log de la désactivation
    try:
        log_action(
            db=db,
            module_name="employes",
            action_type=ActionType.UPDATE,
            record_id=employe_id,
            old_data=employe_data,
            new_data=clean_data_for_logging(employe),
            description=f"Désactivation employé: {employe_name}",
            user=current_user,
            request=request
        )
    except Exception as e:
        print(f"Erreur logging: {e}")
    
    return {
        "message": "Employé désactivé avec succès",
        "employe_id": employe_id
    }

@router.post("/{employe_id}/reactivate", status_code=200)
def reactivate_employe(employe_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Réactiver un employé désactivé"""
    employe = db.query(Employe).filter(Employe.id == employe_id).first()
    
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    if employe.actif:
        raise HTTPException(status_code=400, detail="L'employé est déjà actif")
    
    employe_data_before = clean_data_for_logging(employe)
    employe_name = f"{employe.nom} {employe.prenom}"
    
    # Réactiver l'employé
    employe.actif = True
    employe.statut_contrat = StatutContrat.ACTIF
    
    db.commit()
    db.refresh(employe)
    
    # Log de la réactivation
    try:
        log_action(
            db=db,
            module_name="employes",
            action_type=ActionType.UPDATE,
            record_id=employe_id,
            old_data=employe_data_before,
            new_data=clean_data_for_logging(employe),
            description=f"Réactivation employé: {employe_name}",
            user=current_user,
            request=request
        )
    except Exception as e:
        print(f"Erreur logging: {e}")
    
    return {
        "message": "Employé réactivé avec succès",
        "employe_id": employe_id
    }

@router.post("/{employe_id}/valider-contrat")
def valider_contrat(employe_id: int, db: Session = Depends(get_db)):
    """Valider automatiquement le statut du contrat selon les dates"""
    
    employe = db.query(Employe).filter(Employe.id == employe_id).first()
    
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    today = date.today()
    
    # Si la date de fin de contrat est passée, marquer comme inactif
    if employe.date_fin_contrat and employe.date_fin_contrat < today:
        employe.statut_contrat = StatutContrat.INACTIF
    # Si la date de recrutement n'est pas encore arrivée, marquer comme inactif
    elif employe.date_recrutement > today:
        employe.statut_contrat = StatutContrat.INACTIF
    else:
        employe.statut_contrat = StatutContrat.ACTIF
    
    db.commit()
    db.refresh(employe)
    
    return {
        "employe_id": employe.id,
        "statut": employe.statut_contrat.value,
        "message": "Statut du contrat validé"
    }

@router.post("/valider-tous-contrats")
def valider_tous_contrats(db: Session = Depends(get_db)):
    """Valider tous les contrats automatiquement"""
    
    employes = db.query(Employe).all()
    today = date.today()
    updated_count = 0
    
    for employe in employes:
        old_statut = employe.statut_contrat
        
        if employe.date_fin_contrat and employe.date_fin_contrat < today:
            employe.statut_contrat = StatutContrat.INACTIF
        elif employe.date_recrutement > today:
            employe.statut_contrat = StatutContrat.INACTIF
        else:
            employe.statut_contrat = StatutContrat.ACTIF
        
        if old_statut != employe.statut_contrat:
            updated_count += 1
    
    db.commit()
    
    return {
        "total_employes": len(employes),
        "employes_mis_a_jour": updated_count,
        "message": "Validation des contrats terminée"
    }

@router.get("/rapport-pdf/actifs")
def generer_rapport_employes_actifs(
    annee: Optional[int] = Query(None, description="Année pour le filtre"),
    mois: Optional[int] = Query(None, description="Mois pour le filtre"),
    db: Session = Depends(get_db)
):
    """Générer un rapport PDF de la liste des employés actifs"""
    
    # Récupérer les employés actifs
    employes = db.query(Employe).filter(
        Employe.statut_contrat == StatutContrat.ACTIF
    ).all()
    
    if not employes:
        raise HTTPException(status_code=404, detail="Aucun employé actif trouvé")
    
    # Préparer les données
    employes_data = []
    for idx, emp in enumerate(employes, 1):
        employes_data.append({
            'numero': idx,
            'matricule': str(emp.id),
            'nom_complet': f"{emp.nom} {emp.prenom}",
            'date_naissance': emp.date_naissance.strftime('%d/%m/%Y') if emp.date_naissance else '-',
            'poste_travail': emp.poste_travail or '-',
            'numero_secu_sociale': emp.numero_secu_sociale or '-',
            'date_recrutement': emp.date_recrutement.strftime('%d/%m/%Y') if emp.date_recrutement else '-',
            'statut': emp.statut_contrat.value if emp.statut_contrat else 'Actif'
        })
    
    # Période optionnelle
    periode = None
    if annee and mois:
        periode = {'annee': annee, 'mois': mois}
    
    # Récupérer les paramètres de l'entreprise
    company = db.query(Parametres).first()
    company_info = company.to_dict() if company else None
    
    # Générer le PDF
    pdf_generator = PDFGenerator()
    pdf_buffer = pdf_generator.generate_rapport_employes(
        employes_data=employes_data,
        periode=periode,
        company_info=company_info
    )
    
    # Nom du fichier
    if periode:
        filename = f"employes_actifs_{mois:02d}_{annee}.pdf"
    else:
        filename = f"employes_actifs_{date.today().strftime('%d%m%Y')}.pdf"
    
    # Retourner le PDF
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@router.get("/{employe_id}/attestation-travail")
def generate_attestation_travail(
    employe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth)
):
    """Générer une attestation de travail pour un employé actif"""
    # Récupérer l'employé
    employe = db.query(Employe).filter(Employe.id == employe_id).first()
    
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    # Vérifier que l'employé est actif
    if not employe.actif:
        raise HTTPException(
            status_code=400, 
            detail="Impossible de générer une attestation de travail pour un employé inactif. Utilisez le certificat de travail."
        )
    
    # Préparer les données
    employe_data = {
        'nom': employe.nom,
        'prenom': employe.prenom,
        'date_naissance': employe.date_naissance.strftime('%d/%m/%Y') if employe.date_naissance else 'N/A',
        'lieu_naissance': employe.lieu_naissance or 'N/A',
        'adresse': employe.adresse or 'N/A',
        'numero_secu_sociale': employe.numero_secu_sociale or 'N/A',
        'poste_travail': employe.poste_travail or 'N/A',
        'date_recrutement': employe.date_recrutement,
        'salaire_base': employe.salaire_base
    }
    
    # Générer le PDF
    pdf_generator = PDFGenerator(db=db)
    pdf_buffer = pdf_generator.generate_attestation_travail(employe_data)
    
    # Nom du fichier
    filename = f"attestation_travail_{employe.nom}_{employe.prenom}_{date.today().strftime('%d%m%Y')}.pdf"
    
    # Retourner le PDF
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@router.get("/{employe_id}/certificat-travail")
def generate_certificat_travail(
    employe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth)
):
    """Générer un certificat de travail pour un employé ayant quitté l'entreprise"""
    # Récupérer l'employé
    employe = db.query(Employe).filter(Employe.id == employe_id).first()
    
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    # Vérifier que l'employé a une date de fin de contrat ou est inactif
    if employe.actif and not employe.date_fin_contrat:
        raise HTTPException(
            status_code=400, 
            detail="Impossible de générer un certificat de travail pour un employé actif. Utilisez l'attestation de travail."
        )
    
    # Préparer les données
    employe_data = {
        'nom': employe.nom,
        'prenom': employe.prenom,
        'date_naissance': employe.date_naissance.strftime('%d/%m/%Y') if employe.date_naissance else 'N/A',
        'lieu_naissance': employe.lieu_naissance or 'N/A',
        'adresse': employe.adresse or 'N/A',
        'numero_secu_sociale': employe.numero_secu_sociale or 'N/A',
        'poste_travail': employe.poste_travail or 'N/A',
        'date_recrutement': employe.date_recrutement,
        'date_fin_contrat': employe.date_fin_contrat,
        'salaire_base': employe.salaire_base
    }
    
    # Générer le PDF
    pdf_generator = PDFGenerator(db=db)
    pdf_buffer = pdf_generator.generate_certificat_travail(employe_data)
    
    # Nom du fichier
    filename = f"certificat_travail_{employe.nom}_{employe.prenom}_{date.today().strftime('%d%m%Y')}.pdf"
    
    # Retourner le PDF
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@router.get("/{employe_id}/contrat-travail")
def generate_contrat_travail(
    employe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth)
):
    """Générer un contrat de travail pour un employé"""
    # Récupérer l'employé
    employe = db.query(Employe).filter(Employe.id == employe_id).first()
    
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    # Préparer les données
    employe_data = {
        'nom': employe.nom,
        'prenom': employe.prenom,
        'date_naissance': employe.date_naissance.strftime('%d/%m/%Y') if employe.date_naissance else 'N/A',
        'lieu_naissance': employe.lieu_naissance or 'N/A',
        'adresse': employe.adresse or 'N/A',
        'mobile': employe.mobile or 'N/A',
        'numero_secu_sociale': employe.numero_secu_sociale or 'N/A',
        'numero_compte_bancaire': employe.numero_compte_bancaire or 'N/A',
        'situation_familiale': employe.situation_familiale or 'N/A',
        'poste_travail': employe.poste_travail or 'N/A',
        'date_recrutement': employe.date_recrutement.strftime('%d/%m/%Y') if employe.date_recrutement else 'N/A',
        'duree_contrat': employe.duree_contrat,
        'date_fin_contrat': employe.date_fin_contrat.strftime('%d/%m/%Y') if employe.date_fin_contrat else None,
        'salaire_base': employe.salaire_base
    }
    
    # Générer le PDF
    pdf_generator = PDFGenerator(db=db)
    pdf_buffer = pdf_generator.generate_contrat_travail(employe_data)
    
    # Nom du fichier
    filename = f"contrat_travail_{employe.nom}_{employe.prenom}_{date.today().strftime('%d%m%Y')}.pdf"
    
    # Retourner le PDF
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )



@router.get("/export/excel")
def export_employes_excel(db: Session = Depends(get_db), current_user: User = Depends(require_auth)):
    """Exporter la liste des employés en Excel (format compatible import)"""
    import pandas as pd
    from io import BytesIO
    from datetime import date
    
    employes = db.query(Employe).all()
    
    data = []
    for emp in employes:
        data.append({
            'NOM': emp.nom,
            'PRENOM': emp.prenom,
            ' NAISSANCE': emp.date_naissance,
            'LIEU': emp.lieu_naissance or '',
            'ADRESSE': emp.adresse or '',
            'TELEPHONE': emp.mobile or '',
            'N Sécurité Sociale': emp.numero_secu_sociale or '',
            'N° COMPTE': emp.numero_compte_bancaire or '',
            'SITUATION': emp.situation_familiale or 'Célibataire',
            'FOF': 'Oui' if emp.femme_au_foyer else 'Non',
            'ENTRE': emp.date_recrutement,
            'SORTIE': emp.date_fin_contrat,
            'POSTE': emp.poste_travail
        })
    
    df = pd.DataFrame(data)
    
    # Créer le fichier Excel en mémoire
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='LIST DES EMPLOYES', index=False)
    
    output.seek(0)
    
    filename = f"employes_export_{date.today().strftime('%d%m%Y')}.xlsx"
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/export/csv")
def export_employes_csv(db: Session = Depends(get_db), current_user: User = Depends(require_auth)):
    """Exporter la liste des employés en CSV"""
    import csv
    from io import StringIO
    from datetime import date
    
    employes = db.query(Employe).all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # En-têtes
    headers = [
        'NOM', 'PRENOM', 'NAISSANCE', 'LIEU', 'ADRESSE', 'TELEPHONE', 
        'N Sécurité Sociale', 'N° COMPTE', 'SITUATION', 'FOF', 
        'ENTRE', 'SORTIE', 'POSTE'
    ]
    writer.writerow(headers)
    
    for emp in employes:
        writer.writerow([
            emp.nom,
            emp.prenom,
            emp.date_naissance,
            emp.lieu_naissance or '',
            emp.adresse or '',
            emp.mobile or '',
            emp.numero_secu_sociale or '',
            emp.numero_compte_bancaire or '',
            emp.situation_familiale or 'Célibataire',
            'Oui' if emp.femme_au_foyer else 'Non',
            emp.date_recrutement,
            emp.date_fin_contrat or '',
            emp.poste_travail
        ])
    
    output.seek(0)
    
    filename = f"employes_export_{date.today().strftime('%d%m%Y')}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
