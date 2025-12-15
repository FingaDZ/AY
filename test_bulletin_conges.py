#!/usr/bin/env python3
"""
Test génération bulletin avec congés - v3.5.3
"""
import sys
import os
sys.path.insert(0, '/opt/ay-hr/backend')

from database import SessionLocal
from models import Employe
from services.salary_processor import SalaryProcessor
from services.pdf_generator import PDFGenerator

def test_bulletin_avec_conges():
    db = SessionLocal()
    try:
        # Trouver SAIFI qui a des congés en décembre 2025
        employe = db.query(Employe).filter(
            Employe.nom == 'SAIFI',
            Employe.prenom == 'SALAH EDDINE'
        ).first()
        
        if not employe:
            print("❌ Employé SAIFI non trouvé")
            return
        
        print(f"✓ Employé trouvé: {employe.nom} {employe.prenom} (ID: {employe.id})")
        
        # Calculer salaire décembre 2025
        processor = SalaryProcessor(db)
        salaire_data = processor.calculer_salaire_mensuel(employe.id, 2025, 12)
        
        print(f"\n📊 Données salaire:")
        print(f"  - jours_travailles: {salaire_data.get('jours_travailles', 'N/A')}")
        print(f"  - jours_conges: {salaire_data.get('jours_conges', 'N/A')}")
        print(f"  - salaire_base: {salaire_data.get('salaire_base', 'N/A')}")
        
        # Générer PDF
        pdf_gen = PDFGenerator()
        pdf_path = f"/tmp/test_bulletin_{employe.id}_202512.pdf"
        pdf_gen.generate_bulletin_paie(salaire_data, pdf_path)
        
        print(f"\n✓ PDF généré: {pdf_path}")
        print(f"\n🔍 Vérifier si la ligne 'Jours de congé pris ce mois' apparaît avec '1.0 j'")
        
        # Vérifier la taille du fichier
        if os.path.exists(pdf_path):
            size = os.path.getsize(pdf_path)
            print(f"✓ Fichier PDF créé ({size} bytes)")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_bulletin_avec_conges()
