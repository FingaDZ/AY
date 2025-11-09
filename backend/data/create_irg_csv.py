"""
Script simple pour créer un fichier IRG CSV si openpyxl n'est pas disponible
"""
import csv
from pathlib import Path

def creer_fichier_irg_csv():
    """Créer un fichier irg.csv comme alternative"""
    
    # Barème IRG exemple
    bareme = [
        ("Salaire", "IRG"),
        (0, 0),
        (10000, 0),
        (15000, 0),
        (20000, 0),
        (25000, 0),
        (30000, 0),
        (35000, 500),
        (40000, 1000),
        (42000, 1300),
        (45000, 1750),
        (48000, 2250),
        (50000, 2500),
        (52000, 2900),
        (55000, 3500),
        (58000, 4200),
        (60000, 4500),
        (65000, 5750),
        (70000, 7000),
        (75000, 8500),
        (80000, 9500),
        (85000, 11000),
        (90000, 12500),
        (95000, 14000),
        (100000, 15500),
        (110000, 19000),
        (120000, 22500),
        (130000, 26500),
        (140000, 30000),
        (150000, 33000),
        (160000, 37000),
        (180000, 44000),
        (200000, 51000),
    ]
    
    # Créer le fichier CSV
    filepath = Path(__file__).parent / "irg.csv"
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(bareme)
    
    print(f"✅ Fichier IRG CSV créé : {filepath}")
    print(f"   Nombre de tranches : {len(bareme) - 1}")
    print()
    print("⚠️  Pour utiliser Excel (.xlsx), installez openpyxl:")
    print("   pip install openpyxl")
    print("   puis exécutez: python create_irg.py")

if __name__ == "__main__":
    creer_fichier_irg_csv()
