#!/usr/bin/env python3
"""
Script de régénération de TOUS les congés depuis les pointages
À utiliser après vidage de la table conges
"""

import requests
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
ANNEE = 2025

# Mois à recalculer (tous les mois de l'année)
MOIS_A_RECALCULER = range(1, 13)  # Janvier à Décembre

def recalculer_periode(annee: int, mois: int):
    """Appeler l'API pour recalculer une période"""
    url = f"{BASE_URL}/conges/recalculer-periode"
    params = {"annee": annee, "mois": mois}
    
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ {mois:02d}/{annee}: {data['recalcules']} congés recalculés, {data['erreurs']} erreurs")
        
        if data['erreurs'] > 0:
            print(f"   ⚠️  Détails erreurs:")
            for detail in data['details']:
                if detail.get('status') == 'erreur':
                    print(f"      - Employé {detail['employe_id']}: {detail.get('message', 'Erreur inconnue')}")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ {mois:02d}/{annee}: Erreur API - {e}")
        return None

def main():
    print(f"🔄 Régénération des congés pour l'année {ANNEE}")
    print(f"{'='*60}")
    
    total_recalcules = 0
    total_erreurs = 0
    
    for mois in MOIS_A_RECALCULER:
        result = recalculer_periode(ANNEE, mois)
        
        if result:
            total_recalcules += result.get('recalcules', 0)
            total_erreurs += result.get('erreurs', 0)
    
    print(f"{'='*60}")
    print(f"✅ Terminé!")
    print(f"   Total recalculés: {total_recalcules}")
    print(f"   Total erreurs: {total_erreurs}")
    
    if total_erreurs > 0:
        print(f"\n⚠️  Des erreurs se sont produites. Vérifiez les logs ci-dessus.")
        sys.exit(1)

if __name__ == "__main__":
    main()
