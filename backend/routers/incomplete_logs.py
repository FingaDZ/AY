from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime

from database import get_db
from models import IncompleteAttendanceLog, AttendanceSyncLog, Pointage, Employe
from schemas import (
    IncompleteLogResponse,
    IncompleteLogValidation,
    IncompleteLogStats
)

router = APIRouter(prefix="/incomplete-logs", tags=["Incomplete Logs"])

@router.get("/", response_model=List[IncompleteLogResponse])
def list_incomplete_logs(
    status: Optional[str] = Query(None, description="pending, validated, corrected, rejected"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    employee_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Liste des logs incomplets nécessitant validation"""
    query = db.query(IncompleteAttendanceLog)
    
    if status:
        query = query.filter(IncompleteAttendanceLog.status == status)
    if start_date:
        query = query.filter(IncompleteAttendanceLog.log_date >= start_date)
    if end_date:
        query = query.filter(IncompleteAttendanceLog.log_date <= end_date)
    if employee_id:
        query = query.filter(IncompleteAttendanceLog.hr_employee_id == employee_id)
    
    logs = query.order_by(IncompleteAttendanceLog.log_date.desc()).offset(skip).limit(limit).all()
    return logs

@router.get("/stats", response_model=IncompleteLogStats)
def get_incomplete_logs_stats(db: Session = Depends(get_db)):
    """Statistiques des logs incomplets"""
    total = db.query(IncompleteAttendanceLog).count()
    pending = db.query(IncompleteAttendanceLog).filter(
        IncompleteAttendanceLog.status == 'pending'
    ).count()
    validated = db.query(IncompleteAttendanceLog).filter(
        IncompleteAttendanceLog.status == 'validated'
    ).count()
    corrected = db.query(IncompleteAttendanceLog).filter(
        IncompleteAttendanceLog.status == 'corrected'
    ).count()
    
    return {
        "total": total,
        "pending": pending,
        "validated": validated,
        "corrected": corrected
    }

@router.post("/{log_id}/validate")
def validate_incomplete_log(
    log_id: int,
    validation: IncompleteLogValidation,
    db: Session = Depends(get_db)
):
    """
    Valider ou corriger un log incomplet
    
    Actions possibles:
    - validate: Accepter l'estimation automatique
    - correct: Corriger avec temps manuel
    - reject: Marquer comme absent
    """
    incomplete_log = db.query(IncompleteAttendanceLog).filter(
        IncompleteAttendanceLog.id == log_id
    ).first()
    
    if not incomplete_log:
        raise HTTPException(status_code=404, detail="Log incomplet non trouvé")
    
    # Update incomplete log
    incomplete_log.validated_by = validation.validated_by
    incomplete_log.validated_at = datetime.now()
    
    if validation.action == "validate":
        # Accept automatic estimation
        incomplete_log.status = "validated"
        final_minutes = incomplete_log.estimated_minutes
        
    elif validation.action == "correct":
        # Manual correction
        if validation.corrected_minutes is None:
            raise HTTPException(status_code=400, detail="corrected_minutes requis pour action 'correct'")
        
        incomplete_log.status = "corrected"
        incomplete_log.corrected_minutes = validation.corrected_minutes
        incomplete_log.correction_note = validation.note
        final_minutes = validation.corrected_minutes
        
        # Update pointage with corrected value
        sync_log = db.query(AttendanceSyncLog).filter(
            AttendanceSyncLog.id == incomplete_log.attendance_sync_log_id
        ).first()
        
        if sync_log:
            # Recalculate pointage
            year = incomplete_log.log_date.year
            month = incomplete_log.log_date.month
            day = incomplete_log.log_date.day
            
            pointage = db.query(Pointage).filter(
                Pointage.employe_id == incomplete_log.hr_employee_id,
                Pointage.annee == year,
                Pointage.mois == month
            ).first()
            
            if pointage:
                # Remove old overtime
                old_overtime = max(0, incomplete_log.estimated_minutes - 480) / 60
                current_overtime = float(pointage.heures_supplementaires or 0)
                pointage.heures_supplementaires = max(0, current_overtime - old_overtime)
                
                # Add new overtime
                new_overtime = max(0, final_minutes - 480) / 60
                pointage.heures_supplementaires = round(pointage.heures_supplementaires + new_overtime, 2)
                
                # Update day status if needed
                if final_minutes < 240:  # Less than 4h
                    pointage.set_jour(day, 0)  # Absent
                else:
                    pointage.set_jour(day, 1)  # Present
            
            # Update sync log
            sync_log.worked_minutes = final_minutes
            sync_log.overtime_minutes = max(0, final_minutes - 480)
    
    elif validation.action == "reject":
        # Mark as absent
        incomplete_log.status = "rejected"
        incomplete_log.correction_note = validation.note
        
        # Update pointage to absent
        year = incomplete_log.log_date.year
        month = incomplete_log.log_date.month
        day = incomplete_log.log_date.day
        
        pointage = db.query(Pointage).filter(
            Pointage.employe_id == incomplete_log.hr_employee_id,
            Pointage.annee == year,
            Pointage.mois == month
        ).first()
        
        if pointage:
            pointage.set_jour(day, 0)  # Absent
    
    else:
        raise HTTPException(status_code=400, detail="Action invalide: validate, correct ou reject")
    
    db.commit()
    
    return {
        "message": "Log validé avec succès",
        "status": incomplete_log.status
    }

@router.delete("/{log_id}")
def delete_incomplete_log(log_id: int, db: Session = Depends(get_db)):
    """Supprimer un log incomplet (après validation)"""
    log = db.query(IncompleteAttendanceLog).filter(
        IncompleteAttendanceLog.id == log_id
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Log non trouvé")
    
    db.delete(log)
    db.commit()
    
    return {"message": "Log supprimé"}
