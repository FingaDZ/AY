#!/usr/bin/env python
"""Script pour afficher les statistiques de l'application"""

import requests
import sys

BASE_URL = "http://localhost:8000/api"

def print_header(title):
    print(f"\n{'='*70}")
    print(f" {title}")
    print(f"{'='*70}")

def get_stats():
    """Récupère et affiche les statistiques"""
    
    try:
        # Employés
        response = requests.get(f"{BASE_URL}/employes/")
        employes = response.json()
        print_header("📋 EMPLOYÉS")
        if employes.get('employes'):
            for emp in employes['employes']:
                statut = "✅" if emp['statut_contrat'] == "Actif" else "❌"
                salaire = float(emp['salaire_base'])
                print(f"   {statut} {emp['prenom']} {emp['nom']}")
                print(f"      Poste: {emp['poste_travail']} | Salaire: {salaire:,.2f} DA")
        print(f"\n   📊 Total: {employes.get('total', 0)} employés")
        
        # Clients
        response = requests.get(f"{BASE_URL}/clients/")
        clients = response.json()
        print_header("🏢 CLIENTS")
        if isinstance(clients, list):
            for client in clients:
                print(f"   • {client['prenom']} {client['nom']}")
                print(f"      Distance: {client['distance']} km | Tél: {client['telephone']}")
        print(f"\n   📊 Total: {len(clients)} clients")
        
        # Pointages
        response = requests.get(f"{BASE_URL}/pointages/?annee=2025&mois=11")
        pointages = response.json()
        print_header("📅 POINTAGES NOVEMBRE 2025")
        if isinstance(pointages, list):
            for p in pointages:
                # Calculer les totaux
                jours = [p.get(f'jour_{i:02d}') for i in range(1, 32)]
                travailles = sum(1 for j in jours if j == "Travaillé")
                absences = sum(1 for j in jours if j == "Absent")
                conges = sum(1 for j in jours if j == "Congé")
                print(f"   • Employé ID {p['employe_id']}")
                print(f"      Travaillés: {travailles} | Absences: {absences} | Congés: {conges}")
        print(f"\n   📊 Total: {len(pointages)} pointages")
        
        # Missions
        response = requests.get(f"{BASE_URL}/missions/")
        missions = response.json()
        print_header("🚗 MISSIONS")
        total_primes = 0
        if isinstance(missions, list):
            for m in missions:
                print(f"   • {m['date_mission']} - Chauffeur ID {m['chauffeur_id']}")
                print(f"      Distance: {m['distance']} km × {m['tarif_km']} DA/km = {m['prime_calculee']} DA")
                total_primes += float(m['prime_calculee'])
        print(f"\n   📊 Total: {len(missions)} missions | Primes: {total_primes:,.2f} DA")
        
        # Avances
        response = requests.get(f"{BASE_URL}/avances/")
        avances = response.json()
        print_header("💵 AVANCES")
        total_avances = 0
        if isinstance(avances, list):
            for a in avances:
                print(f"   • Employé ID {a['employe_id']} - {a['date_avance']}")
                print(f"      Montant: {a['montant']} DA | Déduction: {a['mois_deduction']}/{a['annee_deduction']}")
                total_avances += float(a['montant'])
        print(f"\n   📊 Total: {len(avances)} avances | Montant: {total_avances:,.2f} DA")
        
        # Crédits
        response = requests.get(f"{BASE_URL}/credits/")
        credits = response.json()
        print_header("🏦 CRÉDITS")
        total_credits = 0
        if isinstance(credits, list):
            for c in credits:
                statut = "🔵" if c['statut'] == "En cours" else "🟢"
                print(f"   {statut} Employé ID {c['employe_id']} - {c['date_octroi']}")
                print(f"      Total: {c['montant_total']} DA | Mensualité: {c['montant_mensualite']} DA")
                print(f"      Retenu: {c['montant_retenu']} DA | Restant: {float(c['montant_total']) - float(c['montant_retenu'])} DA")
                total_credits += float(c['montant_total'])
        print(f"\n   📊 Total: {len(credits)} crédits | Montant: {total_credits:,.2f} DA")
        
        print("\n" + "="*70)
        print("✅ Statistiques récupérées avec succès")
        print("="*70)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Erreur: Impossible de se connecter à l'API")
        print("   Assurez-vous que le serveur est démarré (python main.py)")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("\n" + "="*70)
    print(" 📊 TABLEAU DE BORD - AY HR MANAGEMENT")
    print("="*70)
    get_stats()
    print()
