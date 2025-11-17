#!/usr/bin/env python3
"""
Test de génération de PDF sur le serveur
"""
from database import SessionLocal
from models import Employe
from services.pdf_generator import PDFGenerator

db = SessionLocal()
try:
    employe = db.query(Employe).filter(Employe.id == 4).first()
    if not employe:
        print("Employé non trouvé")
        exit(1)
    
    print(f"Employé trouvé: {employe.prenom} {employe.nom}")
    print(f"Date recrutement: {employe.date_recrutement}")
    print(f"Date naissance: {employe.date_naissance}")
    
    employe_data = {
        'nom': employe.nom,
        'prenom': employe.prenom,
        'date_naissance': employe.date_naissance.strftime('%d/%m/%Y') if employe.date_naissance else 'N/A',
        'lieu_naissance': employe.lieu_naissance or 'N/A',
        'adresse': employe.adresse or 'N/A',
        'numero_secu_sociale': employe.numero_secu_sociale or 'N/A',
        'poste_travail': employe.poste_travail or 'N/A',
        'date_recrutement': employe.date_recrutement,
        'salaire_base': employe.salaire_base
    }
    
    print("\nGénération du PDF...")
    pdf_gen = PDFGenerator(db=db)
    pdf = pdf_gen.generate_attestation_travail(employe_data)
    print(f"✓ PDF généré avec succès, taille: {len(pdf.getvalue())} bytes")
    
except Exception as e:
    print(f"✗ Erreur: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
