import logging
from datetime import datetime, date
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Employe, Pointage, AttendanceEmployeeMapping, AttendanceSyncLog, IncompleteAttendanceLog
from services.attendance_service import AttendanceService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_incomplete_log_import():
    db: Session = SessionLocal()
    try:
        # Ensure tables exist
        Base.metadata.create_all(bind=engine)
        
        # 1. Create a dummy employee if not exists
        emp = db.query(Employe).filter(Employe.numero_secu_sociale == "TEST_SSN_999").first()
        if not emp:
            emp = Employe(
                nom="TEST", prenom="USER", date_naissance=date(1990, 1, 1),
                lieu_naissance="Test", adresse="Test", mobile="0000000000",
                numero_secu_sociale="TEST_SSN_999", numero_compte_bancaire="000",
                situation_familiale="Célibataire", date_recrutement=date(2025, 1, 1),
                poste_travail="TESTER", salaire_base=30000
            )
            db.add(emp)
            db.commit()
            db.refresh(emp)
            print(f"Created dummy employee ID: {emp.id}")
        
        # 2. Create mapping
        mapping = db.query(AttendanceEmployeeMapping).filter(AttendanceEmployeeMapping.hr_employee_id == emp.id).first()
        if not mapping:
            mapping = AttendanceEmployeeMapping(
                hr_employee_id=emp.id,
                attendance_employee_id=9999,
                attendance_employee_name="TEST USER",
                sync_method=SyncMethod.SECU_SOCIALE
            )
            db.add(mapping)
            db.commit()
            print("Created dummy mapping")

        # 3. Simulate an incomplete log (ENTRY only)
        # Mocking the log dictionary that comes from the API
        mock_log = {
            "id": 123456,
            "employee_id": 9999,
            "timestamp": datetime.now().isoformat(),
            "type": "ENTRY",
            "worked_minutes": None # Simulate incomplete log
        }
        
        print(f"Simulating import for log: {mock_log}")
        
        service = AttendanceService(db)
        
        # We need to bypass fetch_attendance_logs and call the logic inside import_attendance_logs directly
        # Or we can mock fetch_attendance_logs. 
        # For simplicity, let's extract the core logic we want to test.
        
        # ... (Copying relevant logic from import_attendance_logs) ...
        
        log = mock_log
        attendance_log_id = log["id"]
        attendance_emp_id = log["employee_id"]
        log_timestamp = datetime.fromisoformat(log["timestamp"])
        log_date = log_timestamp.date()
        log_type = log.get("type", "EXIT")
        
        # Calculate smart minutes
        worked_minutes, estimation_rule, status = service.calculate_worked_minutes_smart(log, log_date)
        print(f"Smart Calc Result: {worked_minutes} min, Rule: {estimation_rule}, Status: {status}")
        
        # Create Sync Log
        sync_log = AttendanceSyncLog(
            attendance_log_id=attendance_log_id,
            hr_employee_id=emp.id,
            sync_date=log_date,
            worked_minutes=worked_minutes,
            overtime_minutes=0,
            log_type=log_type
        )
        db.add(sync_log)
        db.flush()
        print(f"Created SyncLog ID: {sync_log.id}")
        
        # Create Incomplete Log
        if status in ["incomplete_entry", "incomplete_exit"]:
            incomplete_log = IncompleteAttendanceLog(
                attendance_log_id=attendance_log_id,
                attendance_sync_log_id=sync_log.id,
                hr_employee_id=emp.id,
                employee_name=f"{emp.nom} {emp.prenom}",
                log_date=log_date,
                log_type=log_type,
                log_timestamp=log_timestamp,
                estimated_minutes=worked_minutes,
                estimation_rule=estimation_rule,
                status='pending'
            )
            db.add(incomplete_log)
            print("Added IncompleteAttendanceLog to session")
            
        db.commit()
        print("SUCCESS: Log imported and saved.")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_incomplete_log_import()
