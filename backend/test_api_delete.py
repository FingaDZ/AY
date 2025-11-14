"""Test complet de suppression via l'API"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

print("🧪 Test de suppression d'employé via l'API")
print("=" * 50)

# 1. Login pour obtenir un token
print("\n1️⃣ Connexion...")
login_data = {
    "email": "admin@ayhr.dz",
    "password": "Admin@2025"
}

try:
    login_resp = requests.post(f"{BASE_URL}/utilisateurs/login", json=login_data)
    if login_resp.status_code == 200:
        token = login_resp.json()["access_token"]
        print(f"✅ Token obtenu: {token[:30]}...")
    else:
        print(f"❌ Erreur login: {login_resp.status_code} - {login_resp.text}")
        exit(1)
except Exception as e:
    print(f"❌ Erreur connexion: {e}")
    exit(1)

# 2. Tester la suppression
print("\n2️⃣ Tentative de suppression de l'employé ID 26...")
headers = {"Authorization": f"Bearer {token}"}

try:
    delete_resp = requests.delete(f"{BASE_URL}/employes/26", headers=headers)
    print(f"\n📊 Réponse du serveur:")
    print(f"   Status Code: {delete_resp.status_code}")
    print(f"   Contenu: {delete_resp.text[:500]}")
    
    if delete_resp.status_code == 200:
        print("\n✅ SUCCÈS! L'employé a été supprimé/désactivé")
        result = delete_resp.json()
        print(f"   Action: {result.get('action', 'N/A')}")
        print(f"   Message: {result.get('message', 'N/A')}")
    else:
        print(f"\n❌ ÉCHEC! Erreur {delete_resp.status_code}")
        
except Exception as e:
    print(f"\n❌ Erreur lors de la suppression: {e}")
    import traceback
    traceback.print_exc()
