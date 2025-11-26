"""
Attendance Integration Service
Handles synchronization between AY HR and Attendance System
"""

import requests
import logging
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from models import (
    Employe,
    Pointage,
    AttendanceEmployeeMapping,
    AttendanceSyncLog,
    AttendanceImportConflict,
    SyncMethod,
    ConflictStatus,
    ConflictStatus,
    LogType,
    IncompleteAttendanceLog
)

logger = logging.getLogger(__name__)

# Configuration
ATTENDANCE_API_URL = "http://192.168.20.56:8000/api"
ATTENDANCE_API_TIMEOUT = 30

# Constants
STANDARD_DAY_MINUTES = 480  # 8 hours
MINIMUM_WORK_MINUTES = 240  # 4 hours to count as worked day

class AttendanceService:
    """Service for Attendance System integration"""
    
    def __init__(self, db: Session):
        self.db = db
        self.api_url = ATTENDANCE_API_URL
    
    # ============ Smart Calculation ============
    
    def calculate_worked_minutes_smart(
        self, 
        log: Dict, 
        log_date: date
    ) -> Tuple[int, str, str]:
        """
        Calcul intelligent des minutes travaillées pour logs incomplets
        
        Returns:
            (worked_minutes, estimation_rule, status)
            
        Règles:
        - ENTRY seul: Assume EXIT à 17:00
        - EXIT seul: Assume ENTRY à 08:00
        - Complet: Utilise worked_minutes de l'API
        """
        log_type = log.get("type", "EXIT")
        worked_minutes = log.get("worked_minutes")
        timestamp = datetime.fromisoformat(log["timestamp"])
        
        # Horaires par défaut (configurables)
        DEFAULT_START_HOUR = 8  # 08:00
        DEFAULT_END_HOUR = 17   # 17:00
        DEFAULT_WORK_HOURS = 8  # 8 heures
        
        # Cas 1: Log complet (ENTRY + EXIT)
        if worked_minutes is not None and worked_minutes > 0:
            return worked_minutes, "complete", "complete"
        
        # Cas 2: ENTRY seul (pas encore d'EXIT)
        if log_type == "ENTRY":
            assumed_exit = timestamp.replace(hour=DEFAULT_END_HOUR, minute=0, second=0)
            
            if timestamp.hour >= DEFAULT_END_HOUR:
                # ENTRY après 17h → assume 8h de travail
                minutes = DEFAULT_WORK_HOURS * 60
                rule = f"entry_late_assume_{DEFAULT_WORK_HOURS}h"
            else:
                # ENTRY avant 17h → calcule jusqu'à 17h
                minutes = int((assumed_exit - timestamp).total_seconds() / 60)
                rule = f"entry_assume_exit_{DEFAULT_END_HOUR}h"
            
            return max(0, minutes), rule, "incomplete_entry"
        
        # Cas 3: EXIT seul (pas d'ENTRY)
        if log_type == "EXIT":
            assumed_entry = timestamp.replace(hour=DEFAULT_START_HOUR, minute=0, second=0)
            
            if timestamp.hour <= DEFAULT_START_HOUR:
                # EXIT avant 8h → assume 8h de travail
                minutes = DEFAULT_WORK_HOURS * 60
                rule = f"exit_early_assume_{DEFAULT_WORK_HOURS}h"
            else:
                # EXIT après 8h → calcule depuis 8h
                minutes = int((timestamp - assumed_entry).total_seconds() / 60)
                rule = f"exit_assume_entry_{DEFAULT_START_HOUR}h"
            
            return max(0, minutes), rule, "incomplete_exit"
        
        # Cas 4: Aucune donnée valide
        return 0, "no_data", "missing"

    # ============ Employee Mapping ============
    
    def get_or_create_mapping(self, hr_employee_id: int) -> Optional[AttendanceEmployeeMapping]:
        """Get existing mapping or create new one by syncing employee"""
        mapping = self.db.query(AttendanceEmployeeMapping).filter(
            AttendanceEmployeeMapping.hr_employee_id == hr_employee_id
        ).first()
        
        if mapping:
            return mapping
        
        # No mapping exists, try to sync
        return self.sync_employee_to_attendance(hr_employee_id)
    
    def find_employee_in_attendance(self, employee: Employe) -> Optional[int]:
        """Find employee in Attendance system by name"""
        try:
            response = requests.get(
                f"{self.api_url}/employees/",
                timeout=ATTENDANCE_API_TIMEOUT
            )
            response.raise_for_status()
            attendance_employees = response.json()
            
            # Search by name match
            full_name = f"{employee.nom} {employee.prenom}".upper()
            for att_emp in attendance_employees:
                att_name = att_emp.get("name", "").upper()
                if att_name == full_name:
                    return att_emp["id"]
            
            return None
        except Exception as e:
            logger.error(f"Error finding employee in Attendance: {e}")
            return None
    
    def sync_employee_to_attendance(self, hr_employee_id: int) -> Optional[AttendanceEmployeeMapping]:
        """
        Sync employee from HR to Attendance system
        Note: Photos are NOT synced (handled in Attendance UI)
        """
        employee = self.db.query(Employe).filter(Employe.id == hr_employee_id).first()
        if not employee:
            logger.error(f"Employee {hr_employee_id} not found in HR")
            return None
        
        # Check if already exists in Attendance
        attendance_emp_id = self.find_employee_in_attendance(employee)
        
        if attendance_emp_id:
            # Employee exists, update info (name, department, pin)
            try:
                # Prepare PIN (year of birth)
                pin = str(employee.date_naissance.year) if employee.date_naissance else None
                
                # Note: We don't send photos (file1-file6) as they're managed in Attendance UI
                data = {
                    "name": f"{employee.nom} {employee.prenom}",
                    "department": employee.poste_travail,
                    "pin": pin
                }
                
                response = requests.put(
                    f"{self.api_url}/employees/{attendance_emp_id}",
                    data=data,
                    timeout=ATTENDANCE_API_TIMEOUT
                )
                response.raise_for_status()
                logger.info(f"Updated employee {employee.nom} in Attendance (ID: {attendance_emp_id})")
            except Exception as e:
                logger.error(f"Error updating employee in Attendance: {e}")
        else:
            # Employee doesn't exist, create (without photos)
            try:
                pin = str(employee.date_naissance.year) if employee.date_naissance else None
                
                data = {
                    "name": f"{employee.nom} {employee.prenom}",
                    "department": employee.poste_travail,
                    "pin": pin
                }
                
                # Note: POST /employees/ requires photos (file1-file6)
                # Since we don't manage photos in HR, we skip creation via API
                # Admin must create employee manually in Attendance UI with photos
                logger.warning(
                    f"Employee {employee.nom} not found in Attendance. "
                    "Please create manually in Attendance UI with photos."
                )
                return None
                
            except Exception as e:
                logger.error(f"Error creating employee in Attendance: {e}")
                return None
        
        # Create or update mapping
        sync_method = SyncMethod.SECU_SOCIALE if employee.numero_secu_sociale else SyncMethod.NAME_DOB
        
        mapping = self.db.query(AttendanceEmployeeMapping).filter(
            AttendanceEmployeeMapping.hr_employee_id == hr_employee_id
        ).first()
        
        if mapping:
            mapping.attendance_employee_id = attendance_emp_id
            mapping.attendance_employee_name = f"{employee.nom} {employee.prenom}"
            mapping.sync_method = sync_method
        else:
            mapping = AttendanceEmployeeMapping(
                hr_employee_id=hr_employee_id,
                attendance_employee_id=attendance_emp_id,
                attendance_employee_name=f"{employee.nom} {employee.prenom}",
                sync_method=sync_method
            )
            self.db.add(mapping)
        
        self.db.commit()
        self.db.refresh(mapping)
        return mapping
    
    # ============ Attendance Log Import ============
    
    def fetch_attendance_logs(
        self,
        start_date: date,
        end_date: date,
        employee_id: Optional[int] = None
    ) -> List[Dict]:
        """Fetch attendance logs from Attendance system"""
        try:
            params = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "limit": 1000
            }
            
            if employee_id:
                params["employee_id"] = employee_id
            
            response = requests.get(
                f"{self.api_url}/attendance/",
                params=params,
                timeout=ATTENDANCE_API_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching attendance logs: {e}")
            return []
    
    def convert_minutes_to_pointage(self, worked_minutes: int) -> Tuple[int, float]:
        """
        Convert worked minutes to pointage status and overtime hours
        Returns: (day_status, overtime_hours)
        """
        if worked_minutes >= MINIMUM_WORK_MINUTES:
            day_status = 1  # Worked
            overtime_minutes = max(0, worked_minutes - STANDARD_DAY_MINUTES)
            overtime_hours = round(overtime_minutes / 60, 2)
        else:
            day_status = 0  # Absent
            overtime_hours = 0.0
        
        return day_status, overtime_hours
    
    def import_attendance_logs(
        self,
        start_date: date,
        end_date: date,
        employee_id: Optional[int] = None
    ) -> Dict:
        """
        Import attendance logs and update pointage grid
        Returns summary: {imported, skipped, conflicts}
        """
        logs = self.fetch_attendance_logs(start_date, end_date, employee_id)
        
        summary = {
            "total_logs": len(logs),
            "imported": 0,
            "incomplete_pending_validation": 0,
            "skipped_duplicate": 0,
            "skipped_no_mapping": 0,
            "conflicts": 0,
            "errors": 0
        }
        
        for log in logs:
            try:
                attendance_log_id = log["id"]
                attendance_emp_id = log["employee_id"]
                log_timestamp = datetime.fromisoformat(log["timestamp"])
                log_date = log_timestamp.date()
                log_type = log.get("type", "EXIT")
                
                # Check if already imported
                existing_sync = self.db.query(AttendanceSyncLog).filter(
                    AttendanceSyncLog.attendance_log_id == attendance_log_id
                ).first()
                
                if existing_sync:
                    summary["skipped_duplicate"] += 1
                    continue
                
                # Find HR employee via mapping
                mapping = self.db.query(AttendanceEmployeeMapping).filter(
                    AttendanceEmployeeMapping.attendance_employee_id == attendance_emp_id
                ).first()
                
                if not mapping:
                    summary["skipped_no_mapping"] += 1
                    logger.warning(f"No mapping for Attendance employee {attendance_emp_id}")
                    continue
                
                hr_emp_id = mapping.hr_employee_id
                employee = self.db.query(Employe).filter(Employe.id == hr_emp_id).first()
                
                # ===== Smart Calculation =====
                worked_minutes, estimation_rule, status = self.calculate_worked_minutes_smart(
                    log, log_date
                )
                
                year = log_date.year
                month = log_date.month
                day = log_date.day
                
                # Get or create pointage for this month
                pointage = self.db.query(Pointage).filter(
                    Pointage.employe_id == hr_emp_id,
                    Pointage.annee == year,
                    Pointage.mois == month
                ).first()
                
                if not pointage:
                    pointage = Pointage(
                        employe_id=hr_emp_id,
                        annee=year,
                        mois=month,
                        verrouille=0,
                        heures_supplementaires=0
                    )
                    self.db.add(pointage)
                    self.db.flush()
                
                # Check for conflict (day already manually set)
                existing_value = pointage.get_jour(day)
                
                if existing_value is not None:
                    # Conflict: day already set in HR
                    conflict = AttendanceImportConflict(
                        hr_employee_id=hr_emp_id,
                        attendance_log_id=attendance_log_id,
                        conflict_date=log_date,
                        hr_existing_value=existing_value,
                        attendance_worked_minutes=worked_minutes,
                        status=ConflictStatus.PENDING
                    )
                    self.db.add(conflict)
                    summary["conflicts"] += 1
                    logger.info(f"Conflict detected for {log_date} - Employee {hr_emp_id}")
                else:
                    # No conflict, import
                    day_status, overtime_hours = self.convert_minutes_to_pointage(worked_minutes)
                    pointage.set_jour(day, day_status)
                    
                    # Add overtime to monthly total
                    current_overtime = float(pointage.heures_supplementaires or 0)
                    pointage.heures_supplementaires = round(current_overtime + overtime_hours, 2)
                    
                    # Log the import
                    sync_log = AttendanceSyncLog(
                        attendance_log_id=attendance_log_id,
                        hr_employee_id=hr_emp_id,
                        sync_date=log_date,
                        worked_minutes=worked_minutes,
                        overtime_minutes=max(0, worked_minutes - STANDARD_DAY_MINUTES),
                        log_type=LogType(log_type) if log_type in ["ENTRY", "EXIT"] else LogType.EXIT
                    )
                    self.db.add(sync_log)
                    self.db.flush()
                    
                    # ===== Incomplete Log Tracking =====
                    if status in ["incomplete_entry", "incomplete_exit"]:
                        incomplete_log = IncompleteAttendanceLog(
                            attendance_log_id=attendance_log_id,
                            attendance_sync_log_id=sync_log.id,
                            hr_employee_id=hr_emp_id,
                            employee_name=f"{employee.nom} {employee.prenom}",
                            log_date=log_date,
                            log_type=log_type,
                            log_timestamp=log_timestamp,
                            estimated_minutes=worked_minutes,
                            estimation_rule=estimation_rule,
                            status='pending'
                        )
                        self.db.add(incomplete_log)
                        summary["incomplete_pending_validation"] += 1
                        
                    summary["imported"] += 1
                
                self.db.commit()
                
            except Exception as e:
                logger.error(f"Error importing log {log.get('id')}: {e}")
                summary["errors"] += 1
                self.db.rollback()
        
        return summary
    
    # ============ Conflict Resolution ============
    
    def resolve_conflict(
        self,
        conflict_id: int,
        resolution: str,
        resolved_by: str
    ) -> bool:
        """
        Resolve an import conflict
        resolution: 'keep_hr' or 'use_attendance'
        """
        conflict = self.db.query(AttendanceImportConflict).filter(
            AttendanceImportConflict.id == conflict_id
        ).first()
        
        if not conflict:
            return False
        
        if resolution == "use_attendance":
            # Apply attendance data to pointage
            year = conflict.conflict_date.year
            month = conflict.conflict_date.month
            day = conflict.conflict_date.day
            
            pointage = self.db.query(Pointage).filter(
                Pointage.employe_id == conflict.hr_employee_id,
                Pointage.annee == year,
                Pointage.mois == month
            ).first()
            
            if pointage:
                day_status, overtime_hours = self.convert_minutes_to_pointage(
                    conflict.attendance_worked_minutes
                )
                pointage.set_jour(day, day_status)
                
                # Add overtime
                current_overtime = float(pointage.heures_supplementaires or 0)
                pointage.heures_supplementaires = round(current_overtime + overtime_hours, 2)
            
            conflict.status = ConflictStatus.RESOLVED_USE_ATTENDANCE
        else:
            # Keep HR data (do nothing to pointage)
            conflict.status = ConflictStatus.RESOLVED_KEEP_HR
        
        conflict.resolved_at = datetime.now()
        conflict.resolved_by = resolved_by
        
        self.db.commit()
        return True
