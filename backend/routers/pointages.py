from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from database import get_db
from models import Pointage, Employe, StatutContrat
from schemas import (
    PointageCreate,
    PointageUpdate,
    PointageVerrouillage,
    PointageResponse,
    PointageListResponse,
    PointageTotaux,
)

router = APIRouter(prefix="/pointages", tags=["Pointages"])

def _pointage_to_response(pointage: Pointage) -> PointageResponse:
    """Convertir un modèle Pointage en PointageResponse"""
    jours_dict = {}
    for i in range(1, 32):
        valeur = pointage.get_jour(i)
        # valeur est déjà une string ('Tr', 'Ab', etc.) ou None
        jours_dict[i] = valeur if valeur else None
    
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
def create_pointage(pointage: PointageCreate, db: Session = Depends(get_db)):
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
    db: Session = Depends(get_db)
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
    
    # Mettre à jour les jours
    for jour, valeur in pointage_update.jours.items():
        if jour < 1 or jour > 31:
            raise HTTPException(status_code=400, detail=f"Numéro de jour invalide: {jour}")
        
        if valeur:
            try:
                type_jour = TypeJour(valeur)
                pointage.set_jour(jour, type_jour)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Valeur invalide pour le jour {jour}: {valeur}")
        else:
            pointage.set_jour(jour, None)
    
    db.commit()
    db.refresh(pointage)
    
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

@router.delete("/{pointage_id}", status_code=204)
def delete_pointage(pointage_id: int, db: Session = Depends(get_db)):
    """Supprimer un pointage"""
    
    pointage = db.query(Pointage).filter(Pointage.id == pointage_id).first()
    
    if not pointage:
        raise HTTPException(status_code=404, detail="Pointage non trouvé")
    
    if pointage.verrouille:
        raise HTTPException(
            status_code=400,
            detail="Le pointage est verrouillé et ne peut pas être supprimé"
        )
    
    db.delete(pointage)
    db.commit()
    
    return None
