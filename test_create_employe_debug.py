"""Script pour déboguer l'erreur 500 avec traceback complet"""
import requests
import json
from datetime import datetime
import traceback

timestamp = datetime.now().strftime("%H%M%S%f")[:-3]  # Timestamp avec millisecondes

employe_data = {
    "nom": f"DEBUG{timestamp}",
    "prenom": "Test",
    "date_naissance": "1995-05-15",
    "lieu_naissance": "Constantine",
    "adresse": "Rue Debug 456",
    "mobile": "0666" + timestamp[:6],
    "numero_secu_sociale": f"DEBUG{timestamp}",
    "numero_compte_bancaire": f"002{timestamp}",
    "situation_familiale": "Marié",
    "femme_au_foyer": True,
    "date_recrutement": "2025-02-01",
    "date_fin_contrat": "2026-02-01",
    "poste_travail": "Chauffeur",
    "salaire_base": 25000,
    "prime_nuit_agent_securite": False,
    "statut_contrat": "Actif",
    "actif": True,
    "numero_anem": "ANEM123"
}

print("=== Données envoyées ===")
print(json.dumps(employe_data, indent=2, ensure_ascii=False))

# Login
login_data = {"email": "admin@ayhr.dz", "password": "admin123"}
try:
    login_response = requests.post("http://localhost:8000/api/utilisateurs/login", json=login_data)
    login_response.raise_for_status()
    user_data = login_response.json()
    token = user_data.get("user", {}).get("id")
    print(f"\nOK Login, token: {token}")
except Exception as e:
    print(f"\nERROR Login: {e}")
    traceback.print_exc()
    exit(1)

# Création
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
try:
    print("\n=== Envoi de la requête POST /api/employes/ ===")
    response = requests.post(
        "http://localhost:8000/api/employes/",
        json=employe_data,
        headers=headers
    )
    
    print(f"\nStatus: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code == 201:
        print("\n>>> SUCCESS EMPLOYE CREE <<<")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    else:
        print(f"\n>>> ERREUR {response.status_code} <<<")
        print("Response text:", response.text)
        try:
            print("Response JSON:", json.dumps(response.json(), indent=2, ensure_ascii=False))
        except:
            pass
            
except Exception as e:
    print(f"\n✗✗✗ EXCEPTION ✗✗✗")
    print(f"Type: {type(e).__name__}")
    print(f"Message: {e}")
    traceback.print_exc()
