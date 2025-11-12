from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, selectinload
from typing import Optional
from datetime import date

from database import get_db
from models import Employe, StatutContrat, Parametres, User
from schemas import (
    EmployeCreate,
    EmployeUpdate,
    EmployeResponse,
    EmployeListResponse,
)
from services.pdf_generator import PDFGenerator
from middleware import require_admin, require_auth

router = APIRouter(prefix="/employes", tags=["Employés"])

@router.post("/", response_model=EmployeResponse, status_code=201)
def create_employe(employe: EmployeCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Créer un nouvel employé"""
    
    # Vérification 1: Doublon par nom + prénom + date de naissance
    existing_by_identity = db.query(Employe).filter(
        Employe.nom == employe.nom,
        Employe.prenom == employe.prenom,
        Employe.date_naissance == employe.date_naissance
    ).first()
    
    if existing_by_identity:
        raise HTTPException(
            status_code=400,
            detail=f"Un employé avec le même nom ({employe.nom}), prénom ({employe.prenom}) et date de naissance existe déjà"
        )
    
    # Vérification 2: Doublon par numéro de sécurité sociale
    existing_by_secu = db.query(Employe).filter(
        Employe.numero_secu_sociale == employe.numero_secu_sociale
    ).first()
    
    if existing_by_secu:
        raise HTTPException(
            status_code=400,
            detail=f"Un employé avec ce numéro de sécurité sociale ({employe.numero_secu_sociale}) existe déjà"
        )
    
    # Vérification 3: Doublon par numéro de compte bancaire
    existing_by_compte = db.query(Employe).filter(
        Employe.numero_compte_bancaire == employe.numero_compte_bancaire
    ).first()
    
    if existing_by_compte:
        raise HTTPException(
            status_code=400,
            detail=f"Un employé avec ce numéro de compte bancaire ({employe.numero_compte_bancaire}) existe déjà"
        )
    
    db_employe = Employe(**employe.model_dump())
    db.add(db_employe)
    db.commit()
    db.refresh(db_employe)
    
    return db_employe

@router.get("/", response_model=EmployeListResponse)
def list_employes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    statut: Optional[str] = Query(None, description="Filtrer par statut (Actif/Inactif)"),
    search: Optional[str] = Query(None, description="Rechercher par nom ou prénom"),
    poste: Optional[str] = Query(None, description="Filtrer par poste"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth)
):
    """Lister tous les employés avec filtres"""
    
    query = db.query(Employe)
    
    # Filtrer par statut
    if statut:
        if statut not in ["Actif", "Inactif"]:
            raise HTTPException(status_code=400, detail="Statut invalide")
        query = query.filter(Employe.statut_contrat == statut)
    
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
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Mettre à jour un employé"""
    
    employe = db.query(Employe).filter(Employe.id == employe_id).first()
    
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
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
    for field, value in update_data.items():
        setattr(employe, field, value)
    
    db.commit()
    db.refresh(employe)
    
    return employe

@router.delete("/{employe_id}", status_code=204)
def delete_employe(employe_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Supprimer un employé"""
    
    employe = db.query(Employe).filter(Employe.id == employe_id).first()
    
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    db.delete(employe)
    db.commit()
    
    return None

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
