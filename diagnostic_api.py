"""
Script de diagnostic via l'API REST
"""
import requests
import json

BASE_URL = "http://192.168.20.55:8000"

# Token d'authentification (à adapter)
TOKEN = "votre_token_ici"  # Vous devrez le remplacer

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

def analyser_conges():
    print("="*80)
    print("ANALYSE VIA API: CONGÉS → SALAIRE → BULLETIN")
    print("="*80)
    
    # 1. Récupérer liste des congés
    print("\n📊 RÉCUPÉRATION DES CONGÉS...")
    response = requests.get(f"{BASE_URL}/conges/?annee=2025", headers=headers)
    
    if response.status_code == 200:
        conges = response.json()
        
        # Filtrer SAFI et ZERROUG
        conges_safi = [c for c in conges if 'SAFI' in c['employe_nom']]
        conges_zerroug = [c for c in conges if 'ZERROUG' in c['employe_nom']]
        
        print(f"\n{'='*80}")
        print("EMPLOYÉ: SALAH EDDINE SAFI")
        print(f"{'='*80}")
        print(f"{'Période':<12} {'Acquis':<10} {'Pris':<10} {'Solde':<10} {'Déd.Période':<15}")
        print("-" * 70)
        
        for c in sorted(conges_safi, key=lambda x: (x['annee'], x['mois'])):
            ded = f"{c.get('mois_deduction') or '-'}/{c.get('annee_deduction') or '-'}"
            print(f"{c['mois']:02d}/{c['annee']:<7} {c['jours_conges_acquis']:<10.2f} {c['jours_conges_pris']:<10.2f} {c['jours_conges_restants']:<10.2f} {ded:<15}")
        
        print(f"\n{'='*80}")
        print("EMPLOYÉ: ABDELHALIM ZERROUG")
        print(f"{'='*80}")
        print(f"{'Période':<12} {'Acquis':<10} {'Pris':<10} {'Solde':<10} {'Déd.Période':<15}")
        print("-" * 70)
        
        for c in sorted(conges_zerroug, key=lambda x: (x['annee'], x['mois'])):
            ded = f"{c.get('mois_deduction') or '-'}/{c.get('annee_deduction') or '-'}"
            print(f"{c['mois']:02d}/{c['annee']:<7} {c['jours_conges_acquis']:<10.2f} {c['jours_conges_pris']:<10.2f} {c['jours_conges_restants']:<10.2f} {ded:<15}")
    else:
        print(f"❌ Erreur API: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # Version sans auth pour test
    print("⚠️  Ce script nécessite un token d'authentification")
    print("Alternative: Vérifier manuellement via l'interface web")
    
    # analyser_conges()
