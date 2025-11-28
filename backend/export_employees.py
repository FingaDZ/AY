import csv
import os
from sqlalchemy.orm import Session
from database import SessionLocal
from models.employe import Employe

def export_employees():
    db: Session = SessionLocal()
    try:
        # Fetch all employees
        employees = db.query(Employe).all()
        active_count = sum(1 for e in employees if e.actif)
        inactive_count = len(employees) - active_count
        
        print(f"Found {len(employees)} total employees.")
        print(f" - Active: {active_count}")
        print(f" - Inactive: {inactive_count}")
        
        # 1. Export to CSV
        csv_filename = "employees_dump.csv"
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as csv_file:
            fieldnames = ['id', 'first_name', 'last_name', 'full_name', 'department', 'pin', 'ssn', 'birth_date']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            
            writer.writeheader()
            for emp in employees:
                pin = str(emp.date_naissance.year) if emp.date_naissance else ""
                writer.writerow({
                    'id': emp.id,
                    'first_name': emp.prenom,
                    'last_name': emp.nom,
                    'full_name': f"{emp.nom} {emp.prenom}",
                    'department': emp.poste_travail,
                    'pin': pin,
                    'ssn': emp.numero_secu_sociale,
                    'birth_date': emp.date_naissance
                })
        
        print(f"Exported to {csv_filename}")
        
        # 2. Export to SQL (Generic INSERT)
        sql_filename = "employees_dump.sql"
        with open(sql_filename, mode='w', encoding='utf-8') as sql_file:
            sql_file.write("-- Dump of employees from HR System\n")
            sql_file.write("-- Target Table assumed: personnel_employee (Adjust if necessary)\n\n")
            
            for emp in employees:
                pin = str(emp.date_naissance.year) if emp.date_naissance else "NULL"
                full_name = f"{emp.nom} {emp.prenom}".replace("'", "''")
                dept = emp.poste_travail.replace("'", "''")
                
                # Assuming a generic schema compatible with ZKTeco or similar
                # INSERT INTO personnel_employee (first_name, last_name, department_id, emp_code, ...)
                # Since we don't know the IDs, we just dump values
                
                sql = f"INSERT INTO personnel_employee (first_name, last_name, nickname, emp_code, department_id) VALUES ('{emp.prenom}', '{emp.nom}', '{full_name}', '{pin}', 1);\n"
                sql_file.write(sql)
                
        print(f"Exported to {sql_filename}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    export_employees()
