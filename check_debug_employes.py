"""Vérifier si des employés DEBUG existent dans la BDD"""
import sys
sys.path.append("backend")

# Charger les variables d'environnement
import os
os.environ["DATABASE_URL"] = "mysql+pymysql://root:@localhost:3306/ay_hr"
os.environ["SECRET_KEY"] = "temp_secret_for_testing"

from backend.database import SessionLocal
from backend.models.employe import Employe

db = SessionLocal()
try:
    employes_debug = db.query(Employe).filter(Employe.nom.like('DEBUG%')).all()
    print(f"Employes DEBUG trouves: {len(employes_debug)}")
    for emp in employes_debug[:5]:
        print(f"  - ID:{emp.id} {emp.nom} {emp.prenom} | Situation:{emp.situation_familiale} | Statut:{emp.statut_contrat}")
        print(f"    Types: situation={type(emp.situation_familiale)} statut={type(emp.statut_contrat)}")
finally:
    db.close()
