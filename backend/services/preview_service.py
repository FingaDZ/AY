"""
Import Preview Endpoint
Allows users to preview and validate attendance data before importing
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid

from database import get_db
from schemas import (
    ImportPreviewResponse,
    LogPreviewItem,
    LogPreviewStatus,
    MatchMethod,
    ImportPreviewStats,
    ImportConfirmRequest,
    AttendanceImportSummary
)
from services.import_service import ImportService
from services.matching_service import EmployeeMatchingService
from services.attendance_service import AttendanceService
from models import Pointage

# In-memory cache for preview sessions (consider Redis for production)
preview_sessions = {}

def validate_log(log: dict, employee_id: int, db: Session) -> tuple:
    """
    Validate a log and detect conflicts
    Returns: (status, warnings, errors, has_conflict, existing_value)
    """
    warnings = []
    errors = []
    has_conflict = False
    existing_value = None
    
    # Check if employee not found
    if not employee_id:
        errors.append("Employé non trouvé dans le système")
        return LogPreviewStatus.ERROR, warnings, errors, False, None
    
    # Parse timestamp
    try:
        if isinstance(log['timestamp'], str):
            timestamp = datetime.fromisoformat(log['timestamp'])
        else:
            timestamp = log['timestamp']
        log_date = timestamp.date()
    except Exception as e:
        errors.append(f"Format de date invalide: {str(e)}")
        return LogPreviewStatus.ERROR, warnings, errors, False, None
    
    # Check for conflicts (existing pointage data)
    year = log_date.year
    month = log_date.month
    day = log_date.day
    
    pointage = db.query(Pointage).filter(
        Pointage.employe_id == employee_id,
        Pointage.annee == year,
        Pointage.mois == month
    ).first()
    
    if pointage:
        existing_value = pointage.get_jour(day)
        if existing_value is not None:
            has_conflict = True
            warnings.append(f"Conflit: Jour {day} déjà rempli (valeur: {existing_value})")
    
    # Check if log is incomplete
    if not log.get('worked_minutes'):
        warnings.append("Log incomplet - estimation sera appliquée")
    
    # Determine status
    if errors:
        status = LogPreviewStatus.ERROR
    elif warnings:
        status = LogPreviewStatus.WARNING
    else:
        status = LogPreviewStatus.OK
    
    return status, warnings, errors, has_conflict, existing_value

async def preview_import_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> ImportPreviewResponse:
    """
    Preview attendance import without applying changes
    """
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(400, "Format de fichier non supporté")
    
    content = await file.read()
    
    # Parse file
    import_service = ImportService()
    try:
        logs = import_service.parse_excel(content)
    except Exception as e:
        raise HTTPException(400, f"Erreur de parsing: {str(e)}")
    
    # Match and validate each log
    matching_service = EmployeeMatchingService(db)
    preview_items = []
    
    stats = {
        'total_logs': len(logs),
        'ok_count': 0,
        'warning_count': 0,
        'error_count': 0,
        'matched_employees': 0,
        'unmatched_employees': 0,
        'conflicts_detected': 0,
        'duplicates_detected': 0
    }
    
    seen_log_ids = set()
    
    for log in logs:
        # Check for duplicates
        log_id = log.get('id', str(uuid.uuid4()))
        if log_id in seen_log_ids:
            stats['duplicates_detected'] += 1
            continue
        seen_log_ids.add(log_id)
        
        # Match employee
        employee_id, match_method, confidence, alternatives = matching_service.match_employee(
            log.get('employee_name', ''),
            log.get('employee_id')
        )
        
        # Get employee details
        employee_details = None
        if employee_id:
            employee_details = matching_service.get_employee_details(employee_id)
            stats['matched_employees'] += 1
        else:
            stats['unmatched_employees'] += 1
        
        # Validate log
        status, warnings, errors, has_conflict, existing_value = validate_log(
            log, employee_id, db
        )
        
        if has_conflict:
            stats['conflicts_detected'] += 1
        
        # Count by status
        if status == LogPreviewStatus.OK:
            stats['ok_count'] += 1
        elif status == LogPreviewStatus.WARNING:
            stats['warning_count'] += 1
        else:
            stats['error_count'] += 1
        
        # Create preview item
        preview_item = LogPreviewItem(
            log_id=log_id,
            employee_name=log.get('employee_name', 'Inconnu'),
            timestamp=log['timestamp'],
            log_type=log.get('type', 'EXIT'),
            worked_minutes=log.get('worked_minutes'),
            matched_employee_id=employee_id,
            matched_employee_name=employee_details['name'] if employee_details else None,
            matched_employee_poste=employee_details['poste'] if employee_details else None,
            match_confidence=confidence,
            match_method=MatchMethod(match_method),
            alternative_matches=alternatives,
            status=status,
            warnings=warnings,
            errors=errors,
            has_conflict=has_conflict,
            existing_value=existing_value,
            conflict_date=log.get('timestamp')[:10] if has_conflict else None
        )
        
        preview_items.append(preview_item)
    
    # Generate session ID and cache
    session_id = str(uuid.uuid4())
    preview_sessions[session_id] = {
        'items': preview_items,
        'created_at': datetime.now(),
        'original_logs': logs
    }
    
    return ImportPreviewResponse(
        session_id=session_id,
        items=preview_items,
        stats=ImportPreviewStats(**stats)
    )

async def confirm_import_endpoint(
    request: ImportConfirmRequest,
    db: Session = Depends(get_db)
) -> AttendanceImportSummary:
    """
    Execute import after user confirmation
    """
    # Retrieve session
    session = preview_sessions.get(request.session_id)
    if not session:
        raise HTTPException(404, "Session de preview expirée ou introuvable")
    
    # Filter logs based on selected IDs
    selected_logs = []
    for log in session['original_logs']:
        if log['id'] in request.selected_log_ids:
            # Apply manual mappings if provided
            if log['id'] in request.employee_mappings:
                log['_manual_employee_id'] = request.employee_mappings[log['id']]
            selected_logs.append(log)
    
    # Execute import
    attendance_service = AttendanceService(db)
    summary = attendance_service.process_attendance_logs(selected_logs)
    
    # Clean up session
    del preview_sessions[request.session_id]
    
    return summary
