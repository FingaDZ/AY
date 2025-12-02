from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import LogisticsType
from schemas.logistics_type import LogisticsTypeCreate, LogisticsTypeUpdate, LogisticsTypeResponse

router = APIRouter(
    prefix="/logistics-types",
    tags=["Logistics Types"]
)

@router.get("/", response_model=List[LogisticsTypeResponse])
def get_logistics_types(db: Session = Depends(get_db)):
    return db.query(LogisticsType).filter(LogisticsType.is_active == True).all()

@router.post("/", response_model=LogisticsTypeResponse)
def create_logistics_type(type_in: LogisticsTypeCreate, db: Session = Depends(get_db)):
    db_type = LogisticsType(**type_in.model_dump())
    db.add(db_type)
    db.commit()
    db.refresh(db_type)
    return db_type

@router.put("/{type_id}", response_model=LogisticsTypeResponse)
def update_logistics_type(type_id: int, type_in: LogisticsTypeUpdate, db: Session = Depends(get_db)):
    db_type = db.query(LogisticsType).filter(LogisticsType.id == type_id).first()
    if not db_type:
        raise HTTPException(status_code=404, detail="Type not found")
    
    for key, value in type_in.model_dump().items():
        setattr(db_type, key, value)
    
    db.commit()
    db.refresh(db_type)
    return db_type

@router.delete("/{type_id}")
def delete_logistics_type(type_id: int, db: Session = Depends(get_db)):
    db_type = db.query(LogisticsType).filter(LogisticsType.id == type_id).first()
    if not db_type:
        raise HTTPException(status_code=404, detail="Type not found")
    
    db_type.is_active = False # Soft delete
    db.commit()
    return {"message": "Type deleted"}
