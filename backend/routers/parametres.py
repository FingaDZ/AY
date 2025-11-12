from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import Parametres, User
from pydantic import BaseModel
from middleware import require_admin

router = APIRouter(prefix="/parametres", tags=["Parametres"])


class ParametresUpdate(BaseModel):
    raison_sociale: Optional[str] = None
    nom_entreprise: Optional[str] = None
    adresse: Optional[str] = None
    rc: Optional[str] = None
    nif: Optional[str] = None
    nis: Optional[str] = None
    art: Optional[str] = None
    numero_secu_employeur: Optional[str] = None
    telephone: Optional[str] = None
    compte_bancaire: Optional[str] = None
    banque: Optional[str] = None


@router.get("/", response_model=dict)
def get_parametres(db: Session = Depends(get_db)):
    p = db.query(Parametres).first()
    if not p:
        # retourner un dict vide plutôt qu'HTTP 404 pour faciliter l'affichage
        return {}
    return p.to_dict()


@router.put("/", response_model=dict)
def update_parametres(
    payload: ParametresUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    p = db.query(Parametres).first()
    if not p:
        p = Parametres()
        db.add(p)

    data = payload.dict(exclude_unset=True)
    for k, v in data.items():
        setattr(p, k, v)

    db.commit()
    db.refresh(p)
    return p.to_dict()
