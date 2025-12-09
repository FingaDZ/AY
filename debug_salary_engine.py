import sys
import os
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
load_dotenv(os.path.join(os.getcwd(), 'backend', '.env'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.config import settings
from backend.services.salary_engine import SalaryEngine
from backend.models import Employe

def reproduce():
    print("Connecting to DB...")
    # Use config settings
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    print("Initializing SalaryEngine...")
    try:
        salary_engine = SalaryEngine(db)
        print("SalaryEngine initialized.")
    except Exception as e:
        print(f"CRITICAL: Failed to init SalaryEngine: {e}")
        return

    print("Fetching one active employee...")
    employee = db.query(Employe).filter(Employe.actif == True).first()
    if not employee:
        print("No active employee found. Cannot test calculation.")
        return
    
    print(f"Testing calculation for {employee.nom}...")
    try:
        result = salary_engine.calculate_for_employee(employee.id, 2025, 12)
        print("Calculation Successful!")
        print(result)
    except Exception as e:
        print(f"Calculation Failed as expected: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    reproduce()
