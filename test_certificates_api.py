#!/usr/bin/env python3
"""
Script de test pour les endpoints de génération de certificats
"""
import requests
import sys

BASE_URL = "http://192.168.20.53:8000"

def test_certificates():
    print("=== Test des nouveaux endpoints de certificats ===\n")
    
    # 1. Connexion
    print("1. Connexion...")
    login_response = requests.post(
        f"{BASE_URL}/api/utilisateurs/login",
        json={"email": "sghellam@gmail.com", "password": "admin"}
    )
    
    if login_response.status_code != 200:
        print(f"   ✗ Échec de connexion: {login_response.status_code}")
        return False
    
    token = login_response.json()["access_token"]
    print(f"   ✓ Token obtenu: {token[:30]}...\n")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Test attestation pour employé actif (ID=4)
    print("2. Test attestation de travail (employé actif ID=4)...")
    response = requests.get(
        f"{BASE_URL}/api/employes/4/attestation-travail",
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"   ✓ Attestation générée (Code: {response.status_code}, Taille: {len(response.content)} octets)")
        with open("attestation_test.pdf", "wb") as f:
            f.write(response.content)
        print("   ✓ Fichier sauvegardé: attestation_test.pdf")
    else:
        print(f"   ✗ Erreur HTTP {response.status_code}: {response.text}")
    print()
    
    # 3. Test certificat pour employé inactif (ID=7)
    print("3. Test certificat de travail (employé inactif ID=7)...")
    response = requests.get(
        f"{BASE_URL}/api/employes/7/certificat-travail",
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"   ✓ Certificat généré (Code: {response.status_code}, Taille: {len(response.content)} octets)")
        with open("certificat_test.pdf", "wb") as f:
            f.write(response.content)
        print("   ✓ Fichier sauvegardé: certificat_test.pdf")
    else:
        print(f"   ✗ Erreur HTTP {response.status_code}: {response.text}")
    print()
    
    # 4. Test validation (attestation sur employé inactif, doit échouer)
    print("4. Test validation (attestation sur employé inactif, doit échouer)...")
    response = requests.get(
        f"{BASE_URL}/api/employes/7/attestation-travail",
        headers=headers
    )
    
    if response.status_code == 400:
        print(f"   ✓ Validation fonctionne (Code: {response.status_code} - Attendu)")
        print(f"   Message: {response.json().get('detail', '')}")
    else:
        print(f"   ✗ Validation incorrecte (Code: {response.status_code}, attendu: 400)")
    print()
    
    # 5. Test certificat sur employé actif (doit échouer)
    print("5. Test validation (certificat sur employé actif sans date_fin, doit échouer)...")
    response = requests.get(
        f"{BASE_URL}/api/employes/4/certificat-travail",
        headers=headers
    )
    
    if response.status_code == 400:
        print(f"   ✓ Validation fonctionne (Code: {response.status_code} - Attendu)")
        print(f"   Message: {response.json().get('detail', '')}")
    else:
        print(f"   ✗ Validation incorrecte (Code: {response.status_code}, attendu: 400)")
    print()
    
    print("=== Tests terminés ===")
    return True

if __name__ == "__main__":
    try:
        test_certificates()
    except Exception as e:
        print(f"Erreur: {e}")
        sys.exit(1)
