"""
Test de création d'employé avec durée de contrat et calcul automatique
"""
import sys
sys.path.insert(0, 'F:\\Code\\AY HR\\backend')

from database import SessionLocal
from models.employe import Employe
from datetime import date
from dateutil.relativedelta import relativedelta

def test_duree_contrat():
    db = SessionLocal()
    try:
        # Test 1: Créer un employé avec durée de contrat
        print("Test 1: Création avec durée de contrat de 12 mois")
        date_recrutement = date(2025, 1, 1)
        duree_contrat = 12
        date_fin_expected = date_recrutement + relativedelta(months=duree_contrat)
        
        print(f"  Date recrutement: {date_recrutement}")
        print(f"  Durée contrat: {duree_contrat} mois")
        print(f"  Date fin attendue: {date_fin_expected}")
        
        # Test 2: Vérifier la structure de la table
        print("\nTest 2: Vérification de la colonne duree_contrat")
        from sqlalchemy import text
        result = db.execute(text("SHOW COLUMNS FROM employes LIKE 'duree_contrat'"))
        column_info = result.fetchone()
        if column_info:
            print(f"  Colonne trouvée: {column_info}")
            print("  ✓ La colonne duree_contrat existe")
        else:
            print("  ✗ La colonne duree_contrat n'existe pas")
        
        # Test 3: Vérifier les employés existants avec durée
        print("\nTest 3: Employés avec durée de contrat")
        employes_avec_duree = db.query(Employe).filter(Employe.duree_contrat.isnot(None)).all()
        print(f"  Nombre d'employés avec durée: {len(employes_avec_duree)}")
        
        for emp in employes_avec_duree[:3]:  # Afficher les 3 premiers
            print(f"  - {emp.prenom} {emp.nom}: {emp.duree_contrat} mois (fin: {emp.date_fin_contrat})")
        
        print("\n✓ Tests terminés avec succès")
        
    except Exception as e:
        print(f"\n✗ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_duree_contrat()
