"""Test direct du modèle Employe"""
import sys
sys.path.append("backend")

from backend.models.employe import Employe, SituationFamiliale, StatutContrat
from datetime import date
from decimal import Decimal

# Test 1: Créer un employé avec les ENUMs
try:
    employe_data = {
        "nom": "TEST",
        "prenom": "Direct",
        "date_naissance": date(1995, 5, 15),
        "lieu_naissance": "Constantine",
        "adresse": "Test Address",
        "mobile": "0666000000",
        "numero_secu_sociale": "TEST000",
        "numero_compte_bancaire": "002000",
        "situation_familiale": "Marié",  # String
        "femme_au_foyer": True,
        "date_recrutement": date(2025, 2, 1),
        "date_fin_contrat": date(2026, 2, 1),
        "poste_travail": "Chauffeur",
        "salaire_base": Decimal("25000"),
        "prime_nuit_agent_securite": False,
        "statut_contrat": "Actif",  # String
        "actif": True,
        "numero_anem": "ANEM123"
    }
    
    print("Test 1: Création avec strings")
    employe = Employe(**employe_data)
    print(f"✓ Succès: {employe.nom} {employe.prenom}")
    print(f"  Situation: {employe.situation_familiale} (type: {type(employe.situation_familiale)})")
    print(f"  Statut: {employe.statut_contrat} (type: {type(employe.statut_contrat)})")
except Exception as e:
    print(f"✗ Erreur: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60 + "\n")

# Test 2: Avec ENUMs explicites
try:
    employe_data2 = employe_data.copy()
    employe_data2["situation_familiale"] = SituationFamiliale.MARIE
    employe_data2["statut_contrat"] = StatutContrat.ACTIF
    employe_data2["nom"] = "TEST2"
    employe_data2["numero_secu_sociale"] = "TEST222"
    employe_data2["numero_compte_bancaire"] = "002222"
    
    print("Test 2: Création avec ENUMs")
    employe2 = Employe(**employe_data2)
    print(f"✓ Succès: {employe2.nom} {employe2.prenom}")
    print(f"  Situation: {employe2.situation_familiale} (type: {type(employe2.situation_familiale)})")
    print(f"  Statut: {employe2.statut_contrat} (type: {type(employe2.statut_contrat)})")
except Exception as e:
    print(f"✗ Erreur: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
