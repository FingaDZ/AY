from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from database import get_db
from models import Pointage, Employe, StatutContrat, Parametres, ActionType, User
from schemas import (
    PointageCreate,
    PointageUpdate,
    PointageVerrouillage,
    PointageResponse,
    PointageListResponse,
    PointageTotaux,
)
from services.pdf_generator import PDFGenerator
from services.logging_service import log_action
from middleware.auth import get_current_user

router = APIRouter(prefix="/pointages", tags=["Pointages"])

def _pointage_to_response(pointage: Pointage) -> PointageResponse:
    """Convertir un modèle Pointage en PointageResponse"""
    jours_dict = {}
    for i in range(1, 32):
        valeur = pointage.get_jour(i)
        # N'envoyer que les jours qui ont une valeur (0 ou 1), pas NULL
        # Cela évite que le frontend écrase les jours NULL avec des 0
        if valeur is not None:
            jours_dict[i] = valeur
    
    totaux_dict = pointage.calculer_totaux()
    totaux = PointageTotaux(**totaux_dict)
    
    return PointageResponse(
        id=pointage.id,
        employe_id=pointage.employe_id,
        annee=pointage.annee,
        mois=pointage.mois,
        verrouille=bool(pointage.verrouille),
        jours=jours_dict,
        totaux=totaux
    )

@router.post("/", response_model=PointageResponse, status_code=201)
def create_pointage(
    pointage: PointageCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer un nouveau pointage mensuel pour un employé"""
    
    # Vérifier que l'employé existe
    employe = db.query(Employe).filter(Employe.id == pointage.employe_id).first()
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    # Vérifier qu'un pointage n'existe pas déjà pour ce mois
    existing = db.query(Pointage).filter(
        Pointage.employe_id == pointage.employe_id,
        Pointage.annee == pointage.annee,
        Pointage.mois == pointage.mois
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Un pointage existe déjà pour cet employé et cette période"
        )
    
    db_pointage = Pointage(**pointage.model_dump())
    db.add(db_pointage)
    db.commit()
    db.refresh(db_pointage)
    
    # Log l'action
    log_action(
        db=db,
        module_name="pointages",
        action_type=ActionType.CREATE,
        record_id=db_pointage.id,
        new_data={"employe_id": pointage.employe_id, "annee": pointage.annee, "mois": pointage.mois},
        description=f"Création pointage {pointage.mois}/{pointage.annee} - Employé #{pointage.employe_id}",
        user=current_user,
        request=request
    )
    
    return _pointage_to_response(db_pointage)

@router.get("/", response_model=PointageListResponse)
def list_pointages(
    annee: Optional[int] = Query(None, ge=2000, le=2100),
    mois: Optional[int] = Query(None, ge=1, le=12),
    employe_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Lister les pointages avec filtres"""
    
    query = db.query(Pointage)
    
    if annee:
        query = query.filter(Pointage.annee == annee)
    if mois:
        query = query.filter(Pointage.mois == mois)
    if employe_id:
        query = query.filter(Pointage.employe_id == employe_id)
    
    total = query.count()
    pointages = query.offset(skip).limit(limit).all()
    
    pointages_response = [_pointage_to_response(p) for p in pointages]
    
    return PointageListResponse(total=total, pointages=pointages_response)

@router.get("/employes-actifs")
def get_employes_actifs_mois(
    annee: int = Query(..., ge=2000, le=2100),
    mois: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db)
):
    """Obtenir les employés actifs pour un mois donné (contrat valide)"""
    
    # Calculer la date du premier jour du mois
    from datetime import datetime
    premier_jour = datetime(annee, mois, 1).date()
    
    # Calculer le dernier jour du mois
    if mois == 12:
        dernier_jour = datetime(annee + 1, 1, 1).date()
    else:
        dernier_jour = datetime(annee, mois + 1, 1).date()
    
    # Employés avec contrat actif et dates valides
    employes = db.query(Employe).filter(
        Employe.statut_contrat == StatutContrat.ACTIF,
        Employe.date_recrutement <= dernier_jour,
        (Employe.date_fin_contrat.is_(None)) | (Employe.date_fin_contrat >= premier_jour)
    ).all()
    
    return {
        "annee": annee,
        "mois": mois,
        "total": len(employes),
        "employes": [
            {
                "id": e.id,
                "nom": e.nom,
                "prenom": e.prenom,
                "poste": e.poste_travail
            }
            for e in employes
        ]
    }

@router.get("/{pointage_id}", response_model=PointageResponse)
def get_pointage(pointage_id: int, db: Session = Depends(get_db)):
    """Obtenir un pointage par son ID"""
    
    pointage = db.query(Pointage).filter(Pointage.id == pointage_id).first()
    
    if not pointage:
        raise HTTPException(status_code=404, detail="Pointage non trouvé")
    
    return _pointage_to_response(pointage)

@router.put("/{pointage_id}", response_model=PointageResponse)
def update_pointage(
    pointage_id: int,
    pointage_update: PointageUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mettre à jour un pointage"""
    
    pointage = db.query(Pointage).filter(Pointage.id == pointage_id).first()
    
    if not pointage:
        raise HTTPException(status_code=404, detail="Pointage non trouvé")
    
    if pointage.verrouille:
        raise HTTPException(
            status_code=400,
            detail="Le pointage est verrouillé et ne peut pas être modifié"
        )
    
    # Sauvegarder l'ancien état pour le log
    old_jours = {i: pointage.get_jour(i) for i in range(1, 32)}
    
    # Log pour debug
    print(f"[DEBUG] Updating pointage {pointage_id} for employee {pointage.employe_id}")
    print(f"[DEBUG] Received jours: {pointage_update.jours}")
    
    # Mettre à jour les jours (valeurs numériques: 0 ou 1)
    # Le frontend envoie SEULEMENT les jours avec valeur (pas NULL)
    for jour, valeur in pointage_update.jours.items():
        if jour < 1 or jour > 31:
            raise HTTPException(status_code=400, detail=f"Numéro de jour invalide: {jour}")
        
        # Valider que c'est bien 0, 1 ou None
        if valeur is not None and valeur not in (0, 1):
            raise HTTPException(
                status_code=400, 
                detail=f"Valeur invalide pour le jour {jour}: {valeur}. Doit être 0, 1 ou null"
            )
        
        pointage.set_jour(jour, valeur)
    
    db.commit()
    db.refresh(pointage)
    
    # Log l'action
    log_action(
        db=db,
        module_name="pointages",
        action_type=ActionType.UPDATE,
        record_id=pointage_id,
        old_data={"jours": {k: v for k, v in old_jours.items() if v is not None}},
        new_data={"jours": pointage_update.jours},
        description=f"Modification pointage {pointage.mois}/{pointage.annee} - Employé #{pointage.employe_id}",
        user=current_user,
        request=request
    )
    
    return _pointage_to_response(pointage)

@router.post("/{pointage_id}/verrouiller", response_model=PointageResponse)
def verrouiller_pointage(
    pointage_id: int,
    verrouillage: PointageVerrouillage,
    db: Session = Depends(get_db)
):
    """Verrouiller ou déverrouiller un pointage"""
    
    pointage = db.query(Pointage).filter(Pointage.id == pointage_id).first()
    
    if not pointage:
        raise HTTPException(status_code=404, detail="Pointage non trouvé")
    
    pointage.verrouille = 1 if verrouillage.verrouille else 0
    
    db.commit()
    db.refresh(pointage)
    
    return _pointage_to_response(pointage)

@router.post("/copier")
def copier_pointage(
    employe_id: int = Query(...),
    annee_source: int = Query(..., ge=2000, le=2100),
    mois_source: int = Query(..., ge=1, le=12),
    annee_dest: int = Query(..., ge=2000, le=2100),
    mois_dest: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db)
):
    """Copier un pointage d'un mois vers un autre mois"""
    
    # Vérifier que le pointage source existe
    pointage_source = db.query(Pointage).filter(
        Pointage.employe_id == employe_id,
        Pointage.annee == annee_source,
        Pointage.mois == mois_source
    ).first()
    
    if not pointage_source:
        raise HTTPException(status_code=404, detail="Pointage source non trouvé")
    
    # Vérifier que le pointage destination n'existe pas
    pointage_dest = db.query(Pointage).filter(
        Pointage.employe_id == employe_id,
        Pointage.annee == annee_dest,
        Pointage.mois == mois_dest
    ).first()
    
    if pointage_dest:
        raise HTTPException(
            status_code=400,
            detail="Un pointage existe déjà pour la période de destination"
        )
    
    # Créer le nouveau pointage
    nouveau_pointage = Pointage(
        employe_id=employe_id,
        annee=annee_dest,
        mois=mois_dest,
        verrouille=0
    )
    
    # Copier tous les jours
    for jour in range(1, 32):
        valeur = pointage_source.get_jour(jour)
        if valeur:
            nouveau_pointage.set_jour(jour, valeur)
    
    db.add(nouveau_pointage)
    db.commit()
    db.refresh(nouveau_pointage)
    
    return {
        "message": "Pointage copié avec succès",
        "pointage_id": nouveau_pointage.id
    }

@router.put("/{pointage_id}/verrouiller", response_model=PointageResponse)
def toggle_verrouillage_pointage(pointage_id: int, verrouillage: PointageVerrouillage, db: Session = Depends(get_db)):
    """Verrouiller ou déverrouiller un pointage"""
    
    pointage = db.query(Pointage).filter(Pointage.id == pointage_id).first()
    
    if not pointage:
        raise HTTPException(status_code=404, detail="Pointage non trouvé")
    
    # Changer l'état de verrouillage
    pointage.verrouille = verrouillage.verrouille
    
    db.commit()
    db.refresh(pointage)
    
    return _pointage_to_response(pointage)

@router.delete("/{pointage_id}", status_code=204)
def delete_pointage(
    pointage_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprimer un pointage"""
    
    pointage = db.query(Pointage).filter(Pointage.id == pointage_id).first()
    
    if not pointage:
        raise HTTPException(status_code=404, detail="Pointage non trouvé")
    
    if pointage.verrouille:
        raise HTTPException(
            status_code=400,
            detail="Le pointage est verrouillé et ne peut pas être supprimé"
        )
    
    # Sauvegarder les données avant suppression
    old_data = {
        "employe_id": pointage.employe_id,
        "annee": pointage.annee,
        "mois": pointage.mois
    }
    
    db.delete(pointage)
    db.commit()
    
    # Log l'action
    log_action(
        db=db,
        module_name="pointages",
        action_type=ActionType.DELETE,
        record_id=pointage_id,
        old_data=old_data,
        description=f"Suppression pointage {old_data['mois']}/{old_data['annee']} - Employé #{old_data['employe_id']}",
        user=current_user,
        request=request
    )
    
    return None

@router.get("/rapport-pdf/mensuel")
def generer_rapport_pointages_mensuel(
    annee: int = Query(..., description="Année"),
    mois: int = Query(..., description="Mois"),
    db: Session = Depends(get_db)
):
    """Générer un rapport PDF des pointages du mois"""
    
    # Récupérer les pointages du mois
    pointages = db.query(Pointage).join(Employe).filter(
        Pointage.annee == annee,
        Pointage.mois == mois,
        Employe.statut_contrat == StatutContrat.ACTIF
    ).all()
    
    if not pointages:
        raise HTTPException(
            status_code=404, 
            detail=f"Aucun pointage trouvé pour {mois}/{annee}"
        )
    
    # Préparer les données - regrouper par employé
    employes_pointages = {}
    for p in pointages:
        emp_id = p.employe_id
        if emp_id not in employes_pointages:
            employes_pointages[emp_id] = {
                'employe': p.employe,
                'pointage': p
            }
    
    # Construire les données du rapport avec calcul des congés
    from models.conge import Conge
    from datetime import datetime
    
    pointages_data = []
    for idx, (emp_id, data) in enumerate(employes_pointages.items(), 1):
        emp = data['employe']
        p = data['pointage']
        totaux = p.calculer_totaux()
        jours_travailles_brut = totaux.get('jours_travailles', 0)
        
        # RÈGLE 4 v3.5.1: Récupérer les jours de congés PRIS ce mois pour les EXCLURE
        conge_existant = db.query(Conge).filter(
            Conge.employe_id == emp_id,
            Conge.annee == annee,
            Conge.mois == mois
        ).first()
        
        jours_conges_pris = int(conge_existant.jours_conges_pris) if conge_existant else 0
        
        # IMPORTANT: Exclure les congés pris du calcul des jours travaillés
        # jours_travailles_brut contient TOUT (travail réel + congés car valeur=1)
        # On doit calculer les droits SEULEMENT sur les jours réellement travaillés
        jours_reellement_travailles = max(0, jours_travailles_brut - jours_conges_pris)
        
        # Vérifier si l'employé est nouveau (moins de 3 mois depuis le recrutement)
        est_nouveau_recrue = False
        if emp.date_recrutement:
            mois_anciennete = (datetime.now().year - emp.date_recrutement.year) * 12 + \
                             (datetime.now().month - emp.date_recrutement.month)
            est_nouveau_recrue = mois_anciennete < 3
        
        # Calculer les jours de congés acquis (NOUVELLE RÈGLE: 8j = 1j, pas de décimal)
        jours_conges_acquis = Conge.calculer_jours_conges(jours_reellement_travailles, est_nouveau_recrue)
        
        # Enregistrer ou mettre à jour dans la table conges
        conge_record = db.query(Conge).filter(
            Conge.employe_id == emp_id,
            Conge.annee == annee,
            Conge.mois == mois
        ).first()
        
        if conge_existant:
            # Mettre à jour l'enregistrement existant
            conge_existant.jours_travailles = jours_reellement_travailles
            conge_existant.jours_conges_acquis = jours_conges_acquis
            # jours_conges_pris reste inchangé (saisi manuellement)
            conge_existant.jours_conges_restants = int(conge_existant.jours_conges_acquis) - int(conge_existant.jours_conges_pris)
        else:
            # Créer un nouvel enregistrement
            conge_record = Conge(
                employe_id=emp_id,
                annee=annee,
                mois=mois,
                jours_travailles=jours_reellement_travailles,
                jours_conges_acquis=jours_conges_acquis,
                jours_conges_pris=0,
                jours_conges_restants=jours_conges_acquis
            )
            db.add(conge_record)
        
        db.commit()
        
        pointages_data.append({
            'numero': idx,
            'matricule': str(emp.id) if emp else '-',
            'nom_complet': f"{emp.nom} {emp.prenom}" if emp else '-',
            'poste_travail': emp.poste_travail if emp else '-',
            'jours_travailles': jours_reellement_travailles,  # Jours RÉELLEMENT travaillés (sans congés)
            'absences': totaux.get('jours_absences', 0),
            'jours_conges_acquis': jours_conges_acquis,
            'statut': 'Verrouillé' if p.verrouille else 'En cours'
        })
    
    # Récupérer les paramètres de l'entreprise
    company = db.query(Parametres).first()
    company_info = company.to_dict() if company else None
    
    # Générer le PDF
    pdf_generator = PDFGenerator()
    periode = {'annee': annee, 'mois': mois}
    pdf_buffer = pdf_generator.generate_rapport_pointages(
        pointages_data=pointages_data,
        periode=periode,
        company_info=company_info
    )
    
    # Nom du fichier
    filename = f"pointages_{mois:02d}_{annee}.pdf"
    
    # Retourner le PDF
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
