"""
Import Preview Endpoint - Refactored
Uses AttendanceCalculationService for proper daily calculations
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
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
from services.calculation_service import AttendanceCalculationService
from services.attendance_service import AttendanceService

# In-memory cache for preview sessions
preview_sessions = {}

async def preview_import_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> ImportPreviewResponse:
    """
    Preview attendance import with daily calculations
    """
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(400, "Format de fichier non supporté")
    
    content = await file.read()
    
    # 1. Parse file
    import_service = ImportService()
    try:
        logs = import_service.parse_excel(content)
    except Exception as e:
        raise HTTPException(400, f"Erreur de parsing: {str(e)}")
    
    # 2. Initialize services
    matching_service = EmployeeMatchingService(db)
    calculation_service = AttendanceCalculationService(db)
    
    # 3. Match employees for all logs first
    for log in logs:
        employee_id, match_method, confidence, alternatives = matching_service.match_employee(
            log.get('employee_name', ''),
            log.get('employee_id')
        )
        log['matched_employee_id'] = employee_id
        log['match_method'] = match_method
        log['match_confidence'] = confidence
        log['alternative_matches'] = alternatives
    
    # 4. Group logs by employee + date
    grouped_logs = calculation_service.group_logs_by_employee_date(logs)
    
    # 5. Process each day
    preview_items = []
    stats = {
        'total_logs': 0,
        'ok_count': 0,
        'warning_count': 0,
        'error_count': 0,
        'matched_employees': 0,
        'unmatched_employees': 0,
        'conflicts_detected': 0,
        'duplicates_detected': 0
    }
    
    processed_employees = set()
    
    for (employee_id, work_date), day_logs in grouped_logs.items():
        stats['total_logs'] += 1
        
        # Track unique employees
        if employee_id:
            processed_employees.add(employee_id)
        
        # Get employee details
        employee_details = None
        employee_name = day_logs[0].get('employee_name', 'Inconnu')
        match_method = day_logs[0].get('match_method', 'none')
        match_confidence = day_logs[0].get('match_confidence', 0)
        alternatives = day_logs[0].get('alternative_matches', [])
        
        if employee_id:
            employee_details = matching_service.get_employee_details(employee_id)
        
        # Extract entry and exit
        entry_time, exit_time = calculation_service.extract_entry_exit(day_logs)
        
        # Calculate daily attendance
        if employee_id:
            calculation = calculation_service.calculate_daily_attendance(
                entry_time, exit_time, work_date, employee_id
            )
        else:
            # Employee not matched
            calculation = {
                'worked_minutes': 0,
                'worked_hours': 0.0,
                'is_valid_day': False,
                'overtime_hours': 0.0,
                'status': 'error',
                'warnings': [],
                'errors': ['Employé non trouvé dans le système'],
                'day_value': 0,
                'entry_time': entry_time,
                'exit_time': exit_time,
                'was_estimated': False
            }
        
        # Update stats
        if calculation['status'] == 'ok':
            stats['ok_count'] += 1
        elif calculation['status'] == 'warning':
            stats['warning_count'] += 1
        else:
            stats['error_count'] += 1
        
        # Check for conflicts
        has_conflict = 'Conflit' in ' '.join(calculation['warnings'])
        if has_conflict:
            stats['conflicts_detected'] += 1
        
        # Create preview item
        preview_item = LogPreviewItem(
            log_id=f"{employee_id}_{work_date.isoformat()}",
            employee_name=employee_name,
            timestamp=datetime.combine(work_date, datetime.min.time()),
            log_type='DAILY',  # Changed to daily view
            worked_minutes=calculation['worked_minutes'],
            matched_employee_id=employee_id,
            matched_employee_name=employee_details['name'] if employee_details else None,
            matched_employee_poste=employee_details['poste'] if employee_details else None,
            match_confidence=match_confidence,
            match_method=MatchMethod(match_method),
            alternative_matches=alternatives,
            status=LogPreviewStatus(calculation['status']),
            warnings=calculation['warnings'],
            errors=calculation['errors'],
            has_conflict=has_conflict,
            existing_value=None,
            conflict_date=work_date.isoformat() if has_conflict else None
        )
        
        # Add custom fields for display
        preview_item_dict = preview_item.model_dump()
        preview_item_dict['work_date'] = work_date.isoformat()
        preview_item_dict['entry_time'] = calculation['entry_time'].isoformat() if calculation['entry_time'] else None
        preview_item_dict['exit_time'] = calculation['exit_time'].isoformat() if calculation['exit_time'] else None
        preview_item_dict['worked_hours'] = calculation['worked_hours']
        preview_item_dict['overtime_hours'] = calculation['overtime_hours']
        preview_item_dict['day_value'] = calculation['day_value']
        preview_item_dict['was_estimated'] = calculation['was_estimated']
        
        preview_items.append(preview_item_dict)
    
    # Final stats
    stats['matched_employees'] = len(processed_employees)
    stats['unmatched_employees'] = stats['total_logs'] - stats['matched_employees']
    
    # Generate session ID and cache
    session_id = str(uuid.uuid4())
    preview_sessions[session_id] = {
        'items': preview_items,
        'created_at': datetime.now(),
        'original_logs': logs,
        'grouped_logs': grouped_logs
    }
    
    return ImportPreviewResponse(
        session_id=session_id,
        items=[LogPreviewItem(**item) for item in preview_items],
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
    
    # Get selected items
    selected_items = [
        item for item in session['items']
        if item['log_id'] in request.selected_log_ids
    ]
    
    if not selected_items:
        raise HTTPException(400, "Aucun log sélectionné")
    
    # Execute import using attendance service
    attendance_service = AttendanceService(db)
    
    # Convert preview items to pointage updates
    imported = 0
    errors = 0
    
    # Cache local pour éviter les requêtes répétitives et les doublons dans la même transaction
    pointage_cache = {}

    for item in selected_items:
        try:
            employee_id = item.get('matched_employee_id')
            work_date_str = item.get('work_date')
            day_value = item.get('day_value')
            
            if not employee_id or not work_date_str or day_value is None:
                print(f"Skipping item {item.get('log_id')}: missing required fields")
                errors += 1
                continue
            
            work_date = datetime.fromisoformat(work_date_str).date()
            
            # Update pointage
            year = work_date.year
            month = work_date.month
            day = work_date.day
            
            # Clé unique pour le cache
            cache_key = (employee_id, year, month)
            
            # Vérifier dans le cache d'abord
            if cache_key in pointage_cache:
                pointage = pointage_cache[cache_key]
            else:
                # Sinon chercher en DB
                from models import Pointage
                pointage = db.query(Pointage).filter(
                    Pointage.employe_id == employee_id,
                    Pointage.annee == year,
                    Pointage.mois == month
                ).first()
                
                if not pointage:
                    pointage = Pointage(
                        employe_id=employee_id,
                        annee=year,
                        mois=month
                    )
                    db.add(pointage)
                    # Important: flush pour avoir un ID si besoin, mais surtout pour que SQLAlchemy le gère
                    db.flush() 
                
                # Mettre en cache
                pointage_cache[cache_key] = pointage
            
            # Set day value
            pointage.set_jour(day, day_value)
            imported += 1
            
        except Exception as e:
            errors += 1
            print(f"Error importing {item.get('log_id', 'unknown')}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error committing changes: {str(e)}")
        raise HTTPException(500, f"Erreur lors de l'enregistrement: {str(e)}")
    
    # Clean up session
    del preview_sessions[request.session_id]
    
    return AttendanceImportSummary(
    total_logs=len(selected_items),
    imported=imported,
    skipped_duplicate=0,
    skipped_no_mapping=0,
    conflicts=0,
    errors=errors,
    incomplete_pending_validation=0,
    details=[]
)
