"""
Script de migration v3.6.0 - Ajout table camions
"""
import sys
import os

# Ajouter le chemin backend au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from database import engine, SessionLocal, Base
from models import Camion

def migrate_v3_6_0():
    """Migration v3.6.0: Création table camions et ajout camion_id à missions"""
    
    print("=" * 60)
    print("MIGRATION v3.6.0 - Gestion Camions")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # 1. Créer table camions
        print("\n1. Création table 'camions'...")
        
        # Vérifier si la table existe déjà
        result = db.execute(text("SHOW TABLES LIKE 'camions'"))
        if result.fetchone():
            print("   ⚠️  Table 'camions' existe déjà, passage à l'étape suivante...")
        else:
            Camion.__table__.create(bind=engine, checkfirst=True)
            print("   ✅ Table 'camions' créée")
        
        # 2. Ajouter colonne camion_id à missions
        print("\n2. Ajout colonne 'camion_id' à table 'missions'...")
        
        try:
            # Vérifier si la colonne existe
            result = db.execute(text("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'missions' 
                AND COLUMN_NAME = 'camion_id'
            """))
            
            if result.fetchone()[0] > 0:
                print("   ⚠️  Colonne 'camion_id' existe déjà")
            else:
                # Ajouter la colonne
                db.execute(text("""
                    ALTER TABLE missions 
                    ADD COLUMN camion_id INT NULL,
                    ADD CONSTRAINT fk_missions_camion 
                    FOREIGN KEY (camion_id) REFERENCES camions(id) ON DELETE RESTRICT
                """))
                db.commit()
                print("   ✅ Colonne 'camion_id' ajoutée avec contrainte FK")
        
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("   ⚠️  Colonne 'camion_id' existe déjà")
            else:
                raise
        
        # 3. Ajouter des camions de test (optionnel)
        print("\n3. Création camions de test...")
        
        existing_camions = db.query(Camion).count()
        
        if existing_camions > 0:
            print(f"   ⚠️  {existing_camions} camion(s) déjà présent(s)")
        else:
            test_camions = [
                Camion(
                    marque="HYUNDAI",
                    modele="HD35",
                    immatriculation="152455-109-43",
                    annee_fabrication=2018,
                    capacite_charge=3500,
                    actif=True,
                    notes="Camion principal pour livraisons locales"
                ),
                Camion(
                    marque="ISUZU",
                    modele="NQR",
                    immatriculation="165432-109-16",
                    annee_fabrication=2020,
                    capacite_charge=5000,
                    actif=True,
                    notes="Camion pour longues distances"
                ),
                Camion(
                    marque="MERCEDES",
                    modele="Sprinter",
                    immatriculation="178965-109-16",
                    annee_fabrication=2019,
                    capacite_charge=2000,
                    actif=True,
                    notes="Fourgon pour petites livraisons"
                )
            ]
            
            for camion in test_camions:
                db.add(camion)
            
            db.commit()
            print(f"   ✅ {len(test_camions)} camions de test créés")
        
        print("\n" + "=" * 60)
        print("✅ MIGRATION v3.6.0 TERMINÉE AVEC SUCCÈS")
        print("=" * 60)
        print("\nRésumé:")
        print(f"  - Table 'camions' créée")
        print(f"  - Colonne 'camion_id' ajoutée à 'missions'")
        print(f"  - {db.query(Camion).count()} camion(s) dans la base")
        print("\nVous pouvez maintenant:")
        print("  1. Accéder à l'API /api/camions")
        print("  2. Assigner des camions aux missions")
        print("  3. Suivre l'utilisation du parc de véhicules")
        print("\n")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ ERREUR lors de la migration: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close()
    
    return True


if __name__ == "__main__":
    success = migrate_v3_6_0()
    sys.exit(0 if success else 1)
