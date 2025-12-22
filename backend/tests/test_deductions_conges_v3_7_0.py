"""
Script de test pour la nouvelle architecture v3.7.0 des congés
"""
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://192.168.20.55:8000/api"
# BASE_URL = "http://localhost:8000/api"  # Pour test local

# Identifiants de test (à ajuster)
TEST_EMPLOYE_ID = 1
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin"

def login():
    """Se connecter et récupérer le token"""
    response = requests.post(f"{BASE_URL}/users/login", data={
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Connexion réussie")
        return {"Authorization": f"Bearer {token}"}
    else:
        print("❌ Échec connexion:", response.text)
        return None

def test_synthese(headers):
    """Tester l'endpoint synthèse (v3.7.0)"""
    print("\n--- Test Synthèse Congés ---")
    response = requests.get(f"{BASE_URL}/conges/synthese/{TEST_EMPLOYE_ID}", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Employé: {data['employe']}")
        print(f"   Total Acquis: {data['total_acquis']}j")
        print(f"   Total Déduit: {data['total_deduit']}j")
        print(f"   Solde: {data['solde']}j")
        print(f"   Nombre de périodes: {len(data['periodes'])}")
        
        if len(data['periodes']) > 0:
            print("   Dernière période:")
            derniere = data['periodes'][-1]
            print(f"     - {derniere['mois']}/{derniere['annee']}: {derniere['jours_acquis']}j acquis, solde cumulé: {derniere['solde_cumule']}j")
        
        return data['solde']
    else:
        print("❌ Erreur:", response.status_code, response.text)
        return None

def test_create_deduction(headers, jours_deduits, mois_deduction, annee_deduction):
    """Tester la création d'une déduction"""
    print(f"\n--- Test Création Déduction ({jours_deduits}j pour {mois_deduction}/{annee_deduction}) ---")
    
    payload = {
        "employe_id": TEST_EMPLOYE_ID,
        "jours_deduits": jours_deduits,
        "mois_deduction": mois_deduction,
        "annee_deduction": annee_deduction,
        "type_conge": "ANNUEL",
        "motif": "Test automatique v3.7.0"
    }
    
    response = requests.post(f"{BASE_URL}/deductions-conges/", json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Déduction créée (ID: {data['deduction_id']})")
        print(f"   Ancien solde: {data['ancien_solde']}j")
        print(f"   Nouveau solde: {data['nouveau_solde']}j")
        print(f"   Jours déduits: {data['jours_deduits']}j")
        return data['deduction_id']
    else:
        print("❌ Erreur:", response.status_code, response.text)
        return None

def test_list_deductions(headers):
    """Lister toutes les déductions d'un employé"""
    print("\n--- Test Liste Déductions ---")
    response = requests.get(f"{BASE_URL}/deductions-conges/employe/{TEST_EMPLOYE_ID}", headers=headers)
    
    if response.status_code == 200:
        deductions = response.json()
        print(f"✅ {len(deductions)} déduction(s) trouvée(s)")
        
        for i, d in enumerate(deductions[:5], 1):  # Afficher max 5
            print(f"   {i}. ID:{d['id']} - {d['jours_deduits']}j pour bulletin {d['mois_deduction']}/{d['annee_deduction']}")
        
        if len(deductions) > 5:
            print(f"   ... et {len(deductions) - 5} autre(s)")
        
        return deductions
    else:
        print("❌ Erreur:", response.status_code, response.text)
        return []

def test_delete_deduction(headers, deduction_id):
    """Supprimer une déduction"""
    print(f"\n--- Test Suppression Déduction (ID: {deduction_id}) ---")
    response = requests.delete(f"{BASE_URL}/deductions-conges/{deduction_id}", headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Déduction {deduction_id} supprimée")
        return True
    else:
        print("❌ Erreur:", response.status_code, response.text)
        return False

def test_solde_calcul(headers):
    """Tester le calcul détaillé du solde"""
    print("\n--- Test Calcul Solde Détaillé ---")
    response = requests.get(f"{BASE_URL}/deductions-conges/solde/{TEST_EMPLOYE_ID}", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Solde calculé pour {data['employe_nom']}")
        print(f"   Total acquis: {data['total_acquis']}j")
        print(f"   Total déduit: {data['total_deduit']}j")
        print(f"   Solde disponible: {data['solde_disponible']}j")
        print(f"   Périodes détaillées: {len(data['periodes'])}")
        
        return data
    else:
        print("❌ Erreur:", response.status_code, response.text)
        return None

def test_validation_solde_insuffisant(headers):
    """Tester que le système rejette une déduction avec solde insuffisant"""
    print("\n--- Test Validation Solde Insuffisant ---")
    
    # D'abord, récupérer le solde actuel
    solde_response = requests.get(f"{BASE_URL}/deductions-conges/solde/{TEST_EMPLOYE_ID}", headers=headers)
    if solde_response.status_code != 200:
        print("❌ Impossible de récupérer le solde")
        return False
    
    solde = solde_response.json()['solde_disponible']
    
    # Essayer de déduire plus que le solde
    jours_impossibles = solde + 10.0
    
    payload = {
        "employe_id": TEST_EMPLOYE_ID,
        "jours_deduits": jours_impossibles,
        "mois_deduction": 12,
        "annee_deduction": 2024
    }
    
    response = requests.post(f"{BASE_URL}/deductions-conges/", json=payload, headers=headers)
    
    if response.status_code == 400:
        print(f"✅ Validation OK: Système a rejeté {jours_impossibles}j (solde: {solde}j)")
        print(f"   Message: {response.json()['detail']}")
        return True
    else:
        print(f"❌ PROBLÈME: Le système a accepté une déduction impossible!")
        print(f"   Status: {response.status_code}")
        return False

def run_all_tests():
    """Exécuter tous les tests"""
    print("="*60)
    print(" TEST SUITE v3.7.0 - Architecture Déductions Congés")
    print("="*60)
    
    # Connexion
    headers = login()
    if not headers:
        print("\n❌ Abandon: connexion impossible")
        return
    
    # Test 1: Synthèse initiale
    solde_initial = test_synthese(headers)
    if solde_initial is None:
        print("\n❌ Abandon: synthèse échouée")
        return
    
    # Test 2: Calcul détaillé
    test_solde_calcul(headers)
    
    # Test 3: Lister les déductions existantes
    deductions_avant = test_list_deductions(headers)
    
    # Test 4: Créer une nouvelle déduction
    nouvelle_deduction_id = test_create_deduction(headers, 2.5, 12, 2024)
    if not nouvelle_deduction_id:
        print("\n⚠️ Création de déduction échouée, tests suivants sautés")
    else:
        # Test 5: Vérifier que la synthèse a changé
        solde_apres = test_synthese(headers)
        if solde_apres is not None and solde_initial is not None:
            difference = solde_initial - solde_apres
            if abs(difference - 2.5) < 0.01:
                print(f"\n✅ Cohérence: Solde réduit de {difference}j (attendu: 2.5j)")
            else:
                print(f"\n❌ INCOHÉRENCE: Solde réduit de {difference}j (attendu: 2.5j)")
        
        # Test 6: Liste après création
        deductions_apres = test_list_deductions(headers)
        if len(deductions_apres) == len(deductions_avant) + 1:
            print(f"\n✅ Cohérence: +1 déduction ({len(deductions_avant)} → {len(deductions_apres)})")
        else:
            print(f"\n❌ INCOHÉRENCE: Nombre de déductions ({len(deductions_avant)} → {len(deductions_apres)})")
        
        # Test 7: Supprimer la déduction de test
        if test_delete_deduction(headers, nouvelle_deduction_id):
            solde_final = test_synthese(headers)
            if solde_final is not None and abs(solde_final - solde_initial) < 0.01:
                print(f"\n✅ Cohérence: Solde restauré après suppression ({solde_final}j)")
            else:
                print(f"\n❌ INCOHÉRENCE: Solde non restauré (initial: {solde_initial}j, final: {solde_final}j)")
    
    # Test 8: Validation solde insuffisant
    test_validation_solde_insuffisant(headers)
    
    print("\n" + "="*60)
    print(" FIN DES TESTS")
    print("="*60)

if __name__ == "__main__":
    run_all_tests()
