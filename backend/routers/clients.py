from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from database import get_db
from models import Client, User
from schemas import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientListResponse,
)
from services.pdf_generator import PDFGenerator
from models import Parametres
from services.logging_service import log_action, clean_data_for_logging, ActionType
from middleware.auth import require_gestionnaire  # ⭐ v3.6.0: Permissions

router = APIRouter(prefix="/clients", tags=["Clients"])

@router.post("/", response_model=ClientResponse, status_code=201)
def create_client(client: ClientCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_gestionnaire)):
    """Créer un nouveau client"""
    
    db_client = Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    
    # Log action
    log_action(
        db=db,
        module_name="clients",
        action_type=ActionType.CREATE,
        record_id=db_client.id,
        description=f"Création client #{db_client.id} - {client.prenom} {client.nom}",
        new_data=clean_data_for_logging(db_client),
        user=current_user,
        request=request
    )
    
    return db_client

@router.get("/", response_model=ClientListResponse)
def list_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, description="Rechercher par nom ou prénom"),
    db: Session = Depends(get_db)
):
    """Lister tous les clients avec recherche"""
    
    query = db.query(Client)
    
    # Recherche par nom ou prénom
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Client.nom.like(search_pattern)) | 
            (Client.prenom.like(search_pattern))
        )
    
    total = query.count()
    clients = query.offset(skip).limit(limit).all()
    
    return ClientListResponse(total=total, clients=clients)

@router.get("/{client_id}", response_model=ClientResponse)
def get_client(client_id: int, db: Session = Depends(get_db)):
    """Obtenir un client par son ID"""
    
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    return client

@router.put("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: int,
    client_update: ClientUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_gestionnaire)
):
    """Mettre à jour un client"""
    
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    # Mettre à jour les champs
    update_data = client_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)
    
    # Log action
    log_action(
        db=db,
        module_name="clients",
        action_type=ActionType.UPDATE,
        record_id=client_id,
        description=f"Modification client #{client_id}",
        new_data=clean_data_for_logging(client),
        user=current_user,
        request=request
    )
        description=f"Modification client #{client_id}",
        new_data=clean_data_for_logging(client)
    )
    
    db.commit()
    db.refresh(client)
    
    return client

@router.delete("/{client_id}", status_code=204)
def delete_client(client_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_gestionnaire)):
    """Supprimer un client"""
    from models.mission_client_detail import MissionClientDetail
    
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    # Vérifier si le client a des mouvements logistiques
    details_count = db.query(MissionClientDetail).filter(
        MissionClientDetail.client_id == client_id
    ).count()
    
    if details_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Impossible de supprimer ce client : il a {details_count} mouvement(s) logistique(s) enregistré(s)."
        )
    
    # Log action before delete
    log_action(
        db=db,
        module_name="clients",
        action_type=ActionType.DELETE,
        record_id=client_id,
        description=f"Suppression client #{client_id}",
        old_data=clean_data_for_logging(client),
        user=current_user,
        request=request
    )
    
    db.delete(client)
    db.commit()
    
    return None

@router.get("/rapport-pdf/liste")
def generer_rapport_clients(db: Session = Depends(get_db)):
    """Générer un rapport PDF de la liste de tous les clients"""
    
    # Récupérer tous les clients
    clients = db.query(Client).all()
    
    if not clients:
        raise HTTPException(status_code=404, detail="Aucun client trouvé")
    
    # Préparer les données
    clients_data = []
    for idx, client in enumerate(clients, 1):
        clients_data.append({
            'numero': idx,
            'nom': f"{client.prenom or ''} {client.nom or ''}".strip() or '-',
            'distance': f"{client.distance or 0} km" if client.distance else '-',
            'telephone': client.telephone or '-',
            'tarif_km': f"{client.tarif_km or 0} DA/km" if client.tarif_km else '-'
        })
    
    # Récupérer les paramètres de l'entreprise (si existants)
    company = db.query(Parametres).first()
    company_info = company.to_dict() if company else None

    # Générer le PDF
    pdf_generator = PDFGenerator()
    pdf_buffer = pdf_generator.generate_rapport_clients(clients_data=clients_data, company_info=company_info)
    
    # Nom du fichier
    filename = f"clients_{date.today().strftime('%d%m%Y')}.pdf"
    
    # Retourner le PDF
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/{client_id}/logistics-balance")
def get_client_logistics_balance(client_id: int, db: Session = Depends(get_db)):
    """Récupérer le solde logistique pour un client"""
    from models.mission_client_detail import MissionClientDetail, MissionLogisticsMovement
    from models.logistics_type import LogisticsType
    from sqlalchemy import func
    
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    query = db.query(
        LogisticsType.id.label('type_id'),
        LogisticsType.name.label('type_name'),
        func.sum(MissionLogisticsMovement.quantity_out).label('total_out'),
        func.sum(MissionLogisticsMovement.quantity_in).label('total_in')
    ).join(
        MissionLogisticsMovement, 
        MissionLogisticsMovement.logistics_type_id == LogisticsType.id
    ).join(
        MissionClientDetail,
        MissionClientDetail.id == MissionLogisticsMovement.mission_client_detail_id
    ).filter(
        MissionClientDetail.client_id == client_id,
        LogisticsType.is_active == True
    ).group_by(
        LogisticsType.id,
        LogisticsType.name
    ).all()
    
    balance = []
    for row in query:
        total_out = row.total_out or 0
        total_in = row.total_in or 0
        solde = total_out - total_in
        
        balance.append({
            'type_id': row.type_id,
            'type_name': row.type_name,
            'total_prises': total_out,
            'total_retournees': total_in,
            'solde': solde
        })
    
    return {
        'client_id': client_id,
        'client_nom': f"{client.prenom} {client.nom}",
        'logistics_balance': balance
    }


@router.get("/{client_id}/logistics-balance/pdf")
def get_client_logistics_pdf(client_id: int, db: Session = Depends(get_db)):
    """Générer PDF du solde logistique pour un client"""
    from models.mission_client_detail import MissionClientDetail, MissionLogisticsMovement
    from models.logistics_type import LogisticsType
    from sqlalchemy import func
    
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    # Récupérer les soldes
    query = db.query(
        LogisticsType.id.label('type_id'),
        LogisticsType.name.label('type_name'),
        func.sum(MissionLogisticsMovement.quantity_out).label('total_out'),
        func.sum(MissionLogisticsMovement.quantity_in).label('total_in')
    ).join(
        MissionLogisticsMovement, 
        MissionLogisticsMovement.logistics_type_id == LogisticsType.id
    ).join(
        MissionClientDetail,
        MissionClientDetail.id == MissionLogisticsMovement.mission_client_detail_id
    ).filter(
        MissionClientDetail.client_id == client_id,
        LogisticsType.is_active == True
    ).group_by(
        LogisticsType.id,
        LogisticsType.name
    ).all()
    
    balance = []
    for row in query:
        total_out = row.total_out or 0
        total_in = row.total_in or 0
        solde = total_out - total_in
        balance.append({
            'type_name': row.type_name,
            'total_prises': total_out,
            'total_retournees': total_in,
            'solde': solde
        })
    
    # Générer PDF
    pdf_generator = PDFGenerator()
    client_data = {
        'client_nom': f"{client.prenom} {client.nom}",
        'balance': balance
    }
    pdf_buffer = pdf_generator.generate_client_logistics_balance(client_data)
    
    filename = f"logistique_{client.nom}_{date.today().strftime('%d%m%Y')}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/logistics-balance/all/pdf")
def get_all_clients_logistics_pdf(db: Session = Depends(get_db)):
    """Générer PDF global des soldes logistiques de tous les clients"""
    from models.mission_client_detail import MissionClientDetail, MissionLogisticsMovement
    from models.logistics_type import LogisticsType
    from sqlalchemy import func
    
    # Récupérer tous les clients avec mouvements logistiques
    clients_data = []
    clients = db.query(Client).all()
    
    for client in clients:
        query = db.query(
            LogisticsType.id.label('type_id'),
            LogisticsType.name.label('type_name'),
            func.sum(MissionLogisticsMovement.quantity_out).label('total_out'),
            func.sum(MissionLogisticsMovement.quantity_in).label('total_in')
        ).join(
            MissionLogisticsMovement, 
            MissionLogisticsMovement.logistics_type_id == LogisticsType.id
        ).join(
            MissionClientDetail,
            MissionClientDetail.id == MissionLogisticsMovement.mission_client_detail_id
        ).filter(
            MissionClientDetail.client_id == client.id,
            LogisticsType.is_active == True
        ).group_by(
            LogisticsType.id,
            LogisticsType.name
        ).all()
        
        if query:  # Seulement les clients avec mouvements
            balance = []
            for row in query:
                total_out = row.total_out or 0
                total_in = row.total_in or 0
                solde = total_out - total_in
                balance.append({
                    'type_name': row.type_name,
                    'total_prises': total_out,
                    'total_retournees': total_in,
                    'solde': solde
                })
            
            clients_data.append({
                'client_nom': f"{client.prenom} {client.nom}",
                'balance': balance
            })
    
    # Générer PDF
    pdf_generator = PDFGenerator()
    pdf_buffer = pdf_generator.generate_all_clients_logistics_balance(clients_data)
    
    filename = f"logistique_tous_clients_{date.today().strftime('%d%m%Y')}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/{client_id}/can-delete")
def check_can_delete_client(client_id: int, db: Session = Depends(get_db)):
    """Vérifier si un client peut être supprimé"""
    from models.mission_client_detail import MissionClientDetail
    
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    # Compter les détails de mission pour ce client
    details_count = db.query(MissionClientDetail).filter(
        MissionClientDetail.client_id == client_id
    ).count()
    
    can_delete = details_count == 0
    reason = "" if can_delete else "Ce client a des mouvements logistiques enregistrés et ne peut pas être supprimé."
    
    return {
        "can_delete": can_delete,
        "reason": reason,
        "movements_count": details_count
    }
