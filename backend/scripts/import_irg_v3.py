"""
Script d'importation du barème IRG depuis Excel vers la BDD
"""
import os
import sys
import openpyxl
from decimal import Decimal
from datetime import date

# Ajouter le dossier parent au path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from database import SessionLocal
from models import IRGBareme

def import_irg_from_excel():
    """Lire irg.xlsx et insérer dans irg_bareme"""
    excel_path = os.path.join(parent_dir, "data", "irg.xlsx")
    
    # Si pas dans data/, chercher à la racine
    if not os.path.exists(excel_path):
        excel_path = os.path.join(parent_dir, "irg.xlsx")
        
    if not os.path.exists(excel_path):
        excel_path = os.path.abspath(os.path.join(parent_dir, "..", "irg.xlsx"))
        
    if not os.path.exists(excel_path):
        print(f"❌ Erreur : Fichier irg.xlsx non trouvé")
        return

    print(f"✅ Lecture du fichier Excel : {excel_path}")
    
    db = SessionLocal()
    try:
        # 1. Désactiver ancien barème
        print("🔄 Désactivation ancien barème...")
        db.query(IRGBareme).update({"actif": False})
        
        # 2. Lire Excel
        wb = openpyxl.load_workbook(excel_path, data_only=True)
        sheet = wb.active
        
        count = 0
        salaire_min_prev = Decimal(0)
        
        print("🚀 Importation des tranches...")
        # Ignorer header (supposé ligne 1)
        rows = list(sheet.iter_rows(min_row=2, values_only=True))
        
        # Trier par salaire au cas où
        rows.sort(key=lambda x: x[0] if x[0] else 0)
        
        for i, row in enumerate(rows):
            if row[0] is None or row[1] is None:
                continue
                
            salaire = Decimal(str(row[0]))
            irg = Decimal(str(row[1]))
            
            # Salaire max de la tranche PRÉCÉDENTE = salaire actuel - 0.01 (ou salaire actuel)
            # En fait, notre modèle a 'salaire_min', on suppose que c'est des seuils
            # La logique : Si salaire < X alors IRG = Y
            # Dans le fichier Excel, c'est généralement [Salaire, IRG]
            # On va stocker tel quel: salaire_min = Salaire du fichier
            
            bareme = IRGBareme(
                salaire_min=salaire,
                # salaire_max sera rempli si besoin, ou NULL pour dernier
                irg=irg,
                actif=True,
                date_debut=date.today()
            )
            db.add(bareme)
            count += 1
            
        db.commit()
        print(f"✅ Succès : {count} tranches IRG importées dans la BDD")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur : {e}")
    finally:
        db.close()

if __name__ == "__main__":
    confirm = input("Voulez-vous importer le barème IRG depuis Excel vers la BDD ? (o/n) : ")
    if confirm.lower() == 'o':
        import_irg_from_excel()
    else:
        print("Annulé.")
