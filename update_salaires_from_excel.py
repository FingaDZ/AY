"""
Script pour mettre à jour les salaires de base depuis le fichier Excel
"""
import sys
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Numeric

# Définir la base
Base = declarative_base()

# Définir le modèle Employe (simplifié pour la mise à jour)
class Employe(Base):
    __tablename__ = "employes"
    
    id = Column(Integer, primary_key=True)
    nom = Column(String(100))
    prenom = Column(String(100))
    salaire_base = Column(Numeric(12, 2))

# Configuration
DATABASE_URL = "mysql+pymysql://ayhr_user:%21Yara%402014@localhost/ay_hr"
EXCEL_FILE = "PLAN SALAIRE OCTOBRE 2025.xlsx"

def update_salaires_from_excel(excel_file: str, db_url: str):
    """Mettre à jour les salaires de base depuis Excel"""
    
    print(f"📊 Lecture du fichier Excel: {excel_file}")
    df = pd.read_excel(excel_file, sheet_name='LIST DES EMPLOYES')
    print(f"✓ {len(df)} lignes trouvées")
    
    # Créer la connexion
    engine = create_engine(db_url, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        updated_count = 0
        not_found_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                nom = str(row['NOM']).strip()
                prenom = str(row['PRENOM']).strip()
                
                # Lire le salaire de base (colonne "S Base")
                salaire_base = row.get('S Base')
                if pd.isna(salaire_base):
                    print(f"   ⊘ Ligne {index + 2} ({prenom} {nom}): Salaire manquant")
                    continue
                
                # Convertir en float
                try:
                    salaire_base = float(salaire_base)
                except:
                    print(f"   ⊘ Ligne {index + 2} ({prenom} {nom}): Salaire invalide '{salaire_base}'")
                    continue
                
                # Trouver l'employé dans la base
                employe = session.query(Employe).filter(
                    Employe.nom == nom,
                    Employe.prenom == prenom
                ).first()
                
                if employe:
                    employe.salaire_base = salaire_base
                    updated_count += 1
                    if (updated_count % 10) == 0:
                        print(f"   ... {updated_count} salaires mis à jour")
                else:
                    not_found_count += 1
                    print(f"   ⊘ Employé non trouvé: {prenom} {nom}")
                    
            except Exception as e:
                errors.append(f"Ligne {index + 2}: {str(e)}")
                print(f"   ❌ Erreur ligne {index + 2}: {e}")
        
        # Valider les changements
        session.commit()
        
        print(f"\n✅ Mise à jour terminée:")
        print(f"   - Salaires mis à jour: {updated_count}")
        print(f"   - Employés non trouvés: {not_found_count}")
        
        if errors:
            print(f"\n⚠️  Erreurs: {len(errors)}")
            for error in errors[:5]:
                print(f"   - {error}")
        
        return True
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Erreur critique: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        session.close()

if __name__ == "__main__":
    print("=" * 70)
    print("MISE À JOUR DES SALAIRES DEPUIS EXCEL")
    print("=" * 70)
    
    success = update_salaires_from_excel(EXCEL_FILE, DATABASE_URL)
    
    if success:
        print("\n✅ Mise à jour réussie!")
    else:
        print("\n❌ La mise à jour a échoué")
        sys.exit(1)
