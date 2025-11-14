import requests

# Test avec token admin
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc2MzE0NjU0Mn0.VjYpk9r2T9YB3TUBZaT1ynGl-gFO3LAxfbZsjxE_pNk"
}

print("\n" + "="*80)
print("TEST 1: Récupération des employés INACTIFS")
print("="*80)

response = requests.get("http://localhost:8000/employes?statut=Inactif", headers=headers)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"Total: {data['total']}")
    print(f"Nombre retourné: {len(data['employes'])}\n")
    
    for emp in data['employes']:
        print(f"ID: {emp['id']:3d} | Nom: {emp['nom']:20s} | Actif: {emp['actif']} | Statut: {emp['statut_contrat']}")
else:
    print(f"Erreur: {response.text}")

print("\n" + "="*80)
print("TEST 2: Récupération des employés ACTIFS")
print("="*80)

response = requests.get("http://localhost:8000/employes?statut=Actif", headers=headers)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"Total: {data['total']}")
    print(f"Nombre retourné: {len(data['employes'])}")
else:
    print(f"Erreur: {response.text}")
