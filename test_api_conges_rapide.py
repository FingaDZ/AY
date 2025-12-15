#!/usr/bin/env python3
"""Test RAPIDE: Vérifier que jours_conges arrive au PDF"""
import requests
import json

# Test sur l'employé SAIFI qui a 1 jour de congé en décembre
BASE_URL = "http://192.168.20.55:8000"

try:
    # 1. Calculer le salaire pour SAIFI (ID probablement 1 ou chercher d'abord)
    print("=== RECHERCHE EMPLOYÉ SAIFI ===")
    resp = requests.get(f"{BASE_URL}/employes")
    if resp.status_code == 200:
        employes = resp.json()
        saifi = [e for e in employes if e.get('nom') == 'SAIFI']
        if saifi:
            employe_id = saifi[0]['id']
            print(f"✓ SAIFI trouvé - ID: {employe_id}")
            
            # 2. Calculer son salaire pour décembre 2025
            print(f"\n=== CALCUL SALAIRE (ID={employe_id}, 12/2025) ===")
            calc_data = {
                "employe_id": employe_id,
                "annee": 2025,
                "mois": 12,
                "jours_supplementaires": 0,
                "prime_objectif": 0,
                "prime_variable": 0
            }
            
            resp2 = requests.post(f"{BASE_URL}/salaires/calculer", json=calc_data)
            if resp2.status_code == 200:
                salaire_data = resp2.json()
                
                # 3. Afficher les champs pertinents
                print(f"✓ Salaire calculé:")
                print(f"  - jours_travailles: {salaire_data.get('jours_travailles', 'ABSENT!')}")
                print(f"  - jours_conges: {salaire_data.get('jours_conges', 'ABSENT!')}")
                print(f"  - salaire_net: {salaire_data.get('salaire_net', 0)}")
                
                # 4. Vérifier si jours_conges est présent et > 0
                if 'jours_conges' in salaire_data:
                    if salaire_data['jours_conges'] > 0:
                        print(f"\n✅ SUCCÈS: jours_conges = {salaire_data['jours_conges']}")
                        print("→ La ligne DOIT apparaître dans le PDF!")
                    else:
                        print(f"\n⚠️ jours_conges = 0")
                        print("→ Vérifier si données existent dans table conges")
                else:
                    print("\n❌ PROBLÈME: 'jours_conges' ABSENT du dictionnaire!")
                    print("→ salaire_calculator.py ne retourne pas le champ")
            else:
                print(f"❌ Erreur calcul: {resp2.status_code}")
                print(resp2.text)
        else:
            print("❌ SAIFI non trouvé")
    else:
        print(f"❌ Erreur API: {resp.status_code}")
        
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
