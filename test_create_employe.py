"""Script pour tester la création d'un employé et voir l'erreur exacte"""
import requests
import json
from datetime import date

# Données test minimales
from datetime import datetime
timestamp = datetime.now().strftime("%H%M%S")
employe_data = {
    "nom": f"TEST{timestamp}",
    "prenom": "Employé",
    "date_naissance": "1990-01-01",
    "lieu_naissance": "Alger",
    "adresse": "Rue Test 123",
    "mobile": "0555999999",
    "numero_secu_sociale": f"TEST{timestamp}",
    "numero_compte_bancaire": f"001{timestamp}",
    "situation_familiale": "Célibataire",
    "femme_au_foyer": False,
    "date_recrutement": "2025-01-15",
    "poste_travail": "Test",
    "salaire_base": 30000,
    "prime_nuit_agent_securite": False,
    "statut_contrat": "Actif",
    "actif": True
}

# Obtenir d'abord un token valide
login_data = {"email": "admin@ayhr.dz", "password": "admin123"}
try:
    login_response = requests.post("http://localhost:8000/api/utilisateurs/login", json=login_data)
    login_response.raise_for_status()
    user_data = login_response.json()
    token = user_data.get("user", {}).get("id")
    print(f"✓ Login réussi, token: {token}")
except Exception as e:
    print(f"✗ Erreur login: {e}")
    exit(1)

# Tenter de créer l'employé
headers = {"Authorization": f"Bearer {token}"}
try:
    response = requests.post(
        "http://localhost:8000/api/employes/",
        json=employe_data,
        headers=headers
    )
    print(f"\n=== Réponse HTTP {response.status_code} ===")
    print(response.text)
    
    if response.status_code == 201:
        print("\n✓ Employé créé avec succès!")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    else:
        print(f"\n✗ Erreur {response.status_code}")
        try:
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except:
            print(response.text)
            
except Exception as e:
    print(f"\n✗ Exception: {e}")
