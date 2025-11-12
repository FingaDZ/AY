"""
Test complet du système de crédits
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

def test_create_credit():
    """Créer un crédit de test"""
    print("\n=== Test 1: Création d'un crédit ===")
    data = {
        "employe_id": 4,  # ID de l'employé existant
        "date_octroi": "2025-01-01",
        "montant_total": 120000,
        "nombre_mensualites": 12
    }
    
    response = requests.post(f"{BASE_URL}/credits/", json=data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        credit = response.json()
        print(f"✓ Crédit créé: ID={credit['id']}, Mensualité={credit['montant_mensualite']} DA")
        return credit['id']
    else:
        print(f"✗ Erreur: {response.text}")
        return None

def test_get_echeancier(credit_id):
    """Tester l'échéancier"""
    print(f"\n=== Test 2: Échéancier du crédit #{credit_id} ===")
    
    response = requests.get(f"{BASE_URL}/credits/{credit_id}/echeancier")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        echeancier = response.json()
        print(f"✓ Échéancier généré: {len(echeancier)} mensualités")
        print("\nDétail des 3 premières mensualités:")
        for i, mens in enumerate(echeancier[:3], 1):
            print(f"  {i}. {mens['mois']:02d}/{mens['annee']} - {mens['montant']} DA - {mens['statut']}")
        return echeancier
    else:
        print(f"✗ Erreur: {response.text}")
        return None

def test_enregistrer_retenue(credit_id):
    """Enregistrer une retenue"""
    print(f"\n=== Test 3: Enregistrer retenue Janvier 2025 ===")
    
    response = requests.post(
        f"{BASE_URL}/credits/{credit_id}/retenue",
        params={"mois": 1, "annee": 2025}
    )
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Retenue enregistrée")
        print(f"  Montant retenu total: {result['credit']['montant_retenu']} DA")
        print(f"  Montant restant: {float(result['credit']['montant_total']) - float(result['credit']['montant_retenu'])} DA")
        return True
    else:
        print(f"✗ Erreur: {response.text}")
        return False

def test_get_credit(credit_id):
    """Récupérer les détails du crédit"""
    print(f"\n=== Test 4: Détails du crédit #{credit_id} ===")
    
    response = requests.get(f"{BASE_URL}/credits/{credit_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        credit = response.json()
        print(f"✓ Crédit récupéré")
        print(f"  Montant total: {credit['montant_total']} DA")
        print(f"  Montant retenu: {credit['montant_retenu']} DA")
        print(f"  Montant restant: {float(credit['montant_total']) - float(credit['montant_retenu'])} DA")
        print(f"  Statut: {credit['statut']}")
        return credit
    else:
        print(f"✗ Erreur: {response.text}")
        return None

def test_verify_echeancier_after_payment(credit_id):
    """Vérifier l'échéancier après paiement"""
    print(f"\n=== Test 5: Vérifier échéancier après paiement ===")
    
    response = requests.get(f"{BASE_URL}/credits/{credit_id}/echeancier")
    
    if response.status_code == 200:
        echeancier = response.json()
        paye = sum(1 for m in echeancier if m['statut'] == 'payé')
        non_paye = sum(1 for m in echeancier if m['statut'] == 'non payé')
        print(f"✓ Mensualités payées: {paye}")
        print(f"✓ Mensualités non payées: {non_paye}")
        
        print("\nÉchéancier complet:")
        for i, mens in enumerate(echeancier, 1):
            statut_icon = "✓" if mens['statut'] == 'payé' else "○"
            mois_nom = ["", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
                       "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"][mens['mois']]
            print(f"  {statut_icon} {i:2d}. {mois_nom:10s} {mens['annee']} - {mens['montant']:>10.2f} DA - {mens['statut']}")
        
        return True
    else:
        print(f"✗ Erreur: {response.text}")
        return False

def main():
    print("=" * 60)
    print("TEST COMPLET DU SYSTÈME DE CRÉDITS")
    print("=" * 60)
    
    try:
        # Test 1: Créer un crédit
        credit_id = test_create_credit()
        if not credit_id:
            print("\n✗ Échec de la création du crédit")
            return
        
        # Test 2: Obtenir l'échéancier
        echeancier = test_get_echeancier(credit_id)
        if not echeancier:
            print("\n✗ Échec de la récupération de l'échéancier")
            return
        
        # Test 3: Enregistrer une retenue
        if not test_enregistrer_retenue(credit_id):
            print("\n✗ Échec de l'enregistrement de la retenue")
            return
        
        # Test 4: Récupérer le crédit mis à jour
        credit = test_get_credit(credit_id)
        if not credit:
            print("\n✗ Échec de la récupération du crédit")
            return
        
        # Test 5: Vérifier l'échéancier après paiement
        test_verify_echeancier_after_payment(credit_id)
        
        print("\n" + "=" * 60)
        print("✓ TOUS LES TESTS RÉUSSIS")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
