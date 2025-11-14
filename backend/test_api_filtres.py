import requests

headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc2MzE0NjU0Mn0.VjYpk9r2T9YB3TUBZaT1ynGl-gFO3LAxfbZsjxE_pNk"
}

print("\n" + "="*80)
print("TEST 1: statut=Inactif SANS inclure_inactifs")
print("="*80)
response = requests.get("http://localhost:8000/employes?statut=Inactif", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Total: {data['total']}")
    print(f"Employés retournés: {len(data['employes'])}\n")

print("="*80)
print("TEST 2: statut=Inactif AVEC inclure_inactifs=true")
print("="*80)
response = requests.get("http://localhost:8000/employes?statut=Inactif&inclure_inactifs=true", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Total: {data['total']}")
    print(f"Employés retournés: {len(data['employes'])}")
    for emp in data['employes']:
        print(f"  - ID {emp['id']}: {emp['nom']} (actif={emp['actif']}, statut={emp['statut_contrat']})")

print("\n" + "="*80)
print("TEST 3: statut=Actif")
print("="*80)
response = requests.get("http://localhost:8000/employes?statut=Actif", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Total: {data['total']}")
    print(f"Employés retournés: {len(data['employes'])}")

print("\n" + "="*80)
print("TEST 4: statut='' (Tous) AVEC inclure_inactifs=true")
print("="*80)
response = requests.get("http://localhost:8000/employes?inclure_inactifs=true", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Total: {data['total']}")
    actifs = [e for e in data['employes'] if e['actif']]
    inactifs = [e for e in data['employes'] if not e['actif']]
    print(f"  - Actifs: {len(actifs)}")
    print(f"  - Inactifs: {len(inactifs)}")
