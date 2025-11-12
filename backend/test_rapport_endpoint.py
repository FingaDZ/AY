#!/usr/bin/env python
# Test des endpoints de rapport

import sys
sys.path.insert(0, 'f:/Code/AY HR/backend')

from database import get_db
from models import Employe
from services.pdf_generator import PDFGenerator

def test_rapport_employes():
    print("Test génération rapport employés...")
    
    db = next(get_db())
    employes = db.query(Employe).limit(3).all()
    
    if not employes:
        print("❌ Aucun employé trouvé")
        return
    
    print(f"✓ {len(employes)} employés trouvés")
    
    # Préparer les données
    employes_data = []
    for emp in employes:
        employes_data.append({
            'matricule': str(emp.id),
            'nom': emp.nom,
            'prenom': emp.prenom,
            'poste': emp.poste_travail,
            'numero_securite_sociale': emp.numero_secu_sociale,
            'date_recrutement': emp.date_recrutement.strftime('%d/%m/%Y') if emp.date_recrutement else '-',
            'salaire_base': float(emp.salaire_base) if emp.salaire_base else 0,
            'statut_contrat': emp.statut_contrat.value if emp.statut_contrat else 'Actif'
        })
    
    print(f"✓ Données préparées: {employes_data[0]}")
    
    # Générer le PDF
    try:
        pdf_generator = PDFGenerator()
        pdf_buffer = pdf_generator.generate_rapport_employes(
            employes_data=employes_data,
            periode={'annee': 2025, 'mois': 11}
        )
        print(f"✓ PDF généré: {len(pdf_buffer.getvalue())} bytes")
    except Exception as e:
        print(f"❌ Erreur génération PDF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rapport_employes()
