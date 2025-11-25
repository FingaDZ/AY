"""
Attendance Integration API Router
Endpoints for syncing employees and importing attendance logs
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from database import get_db
from models import (
    AttendanceEmployeeMapping,
    AttendanceImportConflict,
    ConflictStatus,
    Employe
)
from schemas import (
    AttendanceEmployeeMappingResponse,
    AttendanceImportConflictResponse,
    ConflictResolution,
    AttendanceImportRequest,
    AttendanceImportSummary,
    EmployeeSyncRequest,
    EmployeeSyncResponse,
)
from services.attendance_service import AttendanceService

router = APIRouter(prefix="/attendance-integration", tags=["Attendance Integration"])

# ============ Employee Sync ============

@router.post("/sync-employee", response_model=EmployeeSyncResponse)
def sync_employee_to_attendance(
    request: EmployeeSyncRequest,
    db: Session = Depends(get_db)
):
    """
    Sync a single employee from HR to Attendance system
    Note: Photos must be uploaded manually in Attendance UI
    """
    service = AttendanceService(db)
    
    # Check if employee exists
    employee = db.query(Employe).filter(Employe.id == request.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    mapping = service.sync_employee_to_attendance(request.employee_id)
    
    if mapping:
        return EmployeeSyncResponse(
            success=True,
            message=f"Employé {employee.nom} {employee.prenom} synchronisé avec succès",
            mapping=AttendanceEmployeeMappingResponse.from_orm(mapping)
        )
    else:
        return EmployeeSyncResponse(
            success=False,
            message="Employé non trouvé dans Attendance. Veuillez le créer manuellement avec photos.",
            mapping=None
        )

@router.post("/sync-all-employees")
def sync_all_employees(db: Session = Depends(get_db)):
    """Sync all active employees to Attendance system"""
    service = AttendanceService(db)
    
    employees = db.query(Employe).filter(Employe.actif == True).all()
    
    results = {
        "total": len(employees),
        "synced": 0,
        "failed": 0,
        "not_found": 0
    }
    
    for emp in employees:
        mapping = service.sync_employee_to_attendance(emp.id)
        if mapping:
            results["synced"] += 1
        else:
            results["not_found"] += 1
    
    return results

# ============ Mapping Management ============

@router.get("/mappings", response_model=List[AttendanceEmployeeMappingResponse])
def list_employee_mappings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all employee mappings"""
    mappings = db.query(AttendanceEmployeeMapping).offset(skip).limit(limit).all()
    return [AttendanceEmployeeMappingResponse.from_orm(m) for m in mappings]

@router.delete("/mappings/{mapping_id}")
def delete_employee_mapping(mapping_id: int, db: Session = Depends(get_db)):
    """Delete an employee mapping"""
    mapping = db.query(AttendanceEmployeeMapping).filter(
        AttendanceEmployeeMapping.id == mapping_id
    ).first()
    
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping non trouvé")
    
    db.delete(mapping)
    db.commit()
    
    return {"message": "Mapping supprimé avec succès"}

# ============ Attendance Import ============

@router.post("/import-logs", response_model=AttendanceImportSummary)
def import_attendance_logs(
    request: AttendanceImportRequest,
    db: Session = Depends(get_db)
):
    """
    Import attendance logs from Attendance system
    Converts minutes to pointage grid and handles conflicts
    """
    service = AttendanceService(db)
    
    summary = service.import_attendance_logs(
        start_date=request.start_date,
        end_date=request.end_date,
        employee_id=request.employee_id
    )
    
    return AttendanceImportSummary(**summary)

# ============ Conflict Management ============

@router.get("/conflicts", response_model=List[AttendanceImportConflictResponse])
def list_conflicts(
    status: Optional[str] = Query(None, description="Filter by status: pending, resolved_keep_hr, resolved_use_attendance"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List attendance import conflicts"""
    query = db.query(AttendanceImportConflict)
    
    if status:
        try:
            conflict_status = ConflictStatus(status)
            query = query.filter(AttendanceImportConflict.status == conflict_status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    conflicts = query.order_by(AttendanceImportConflict.created_at.desc()).offset(skip).limit(limit).all()
    return [AttendanceImportConflictResponse.from_orm(c) for c in conflicts]

@router.post("/conflicts/{conflict_id}/resolve")
def resolve_conflict(
    conflict_id: int,
    resolution: ConflictResolution,
    db: Session = Depends(get_db)
):
    """Resolve an attendance import conflict"""
    service = AttendanceService(db)
    
    success = service.resolve_conflict(
        conflict_id=conflict_id,
        resolution=resolution.resolution,
        resolved_by=resolution.resolved_by
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Conflit non trouvé")
    
    return {"message": "Conflit résolu avec succès"}

@router.delete("/conflicts/{conflict_id}")
def delete_conflict(conflict_id: int, db: Session = Depends(get_db)):
    """Delete a conflict (if no longer relevant)"""
    conflict = db.query(AttendanceImportConflict).filter(
        AttendanceImportConflict.id == conflict_id
    ).first()
    
    if not conflict:
        raise HTTPException(status_code=404, detail="Conflit non trouvé")
    
    db.delete(conflict)
    db.commit()
    
    return {"message": "Conflit supprimé avec succès"}
