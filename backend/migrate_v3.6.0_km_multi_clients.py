"""
Script de migration v3.6.0 - Ajout paramètre km_supplementaire_par_client
"""
import sys
import os

# Ajouter le chemin backend au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from database import engine, SessionLocal

def migrate_km_multi_clients():
    """Migration v3.6.0: Ajout paramètre km_supplementaire_par_client"""
    
    print("=" * 60)
    print("MIGRATION v3.6.0 - Paramètre Km Multi-Clients")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # 1. Ajouter colonne km_supplementaire_par_client dans parametres_salaire
        print("\n1. Vérification colonne 'km_supplementaire_par_client'...")
        result = db.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'parametres_salaire' 
            AND COLUMN_NAME = 'km_supplementaire_par_client'
        """))
        exists = result.scalar() > 0
        
        if exists:
            print("   ⚠️  Colonne 'km_supplementaire_par_client' existe déjà")
        else:
            db.execute(text("""
                ALTER TABLE parametres_salaire
                ADD COLUMN km_supplementaire_par_client INT NOT NULL DEFAULT 10
                COMMENT 'Kilomètres supplémentaires par client additionnel'
            """))
            db.commit()
            print("   ✅ Colonne 'km_supplementaire_par_client' ajoutée (défaut: 10)")
        
        # 2. Ajouter colonne distance_km dans mission_client_details
        print("\n2. Vérification colonne 'distance_km' dans mission_client_details...")
        result = db.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'mission_client_details' 
            AND COLUMN_NAME = 'distance_km'
        """))
        exists = result.scalar() > 0
        
        if exists:
            print("   ⚠️  Colonne 'distance_km' existe déjà")
        else:
            db.execute(text("""
                ALTER TABLE mission_client_details
                ADD COLUMN distance_km DECIMAL(10,2) NULL
                COMMENT 'Distance en km pour ce client'
            """))
            db.commit()
            print("   ✅ Colonne 'distance_km' ajoutée à mission_client_details")
        
        print("\n" + "=" * 60)
        print("✅ MIGRATION v3.6.0 KM MULTI-CLIENTS TERMINÉE AVEC SUCCÈS")
        print("=" * 60)
        
        print("\nRésumé:")
        print("  - Colonne 'km_supplementaire_par_client' ajoutée à 'parametres_salaire'")
        print("  - Colonne 'distance_km' ajoutée à 'mission_client_details'")
        print("  - Valeur par défaut: 10 km par client supplémentaire")
        print("\nFormule calcul kilométrage:")
        print("  km_total = dernier_client_km + (nb_clients - 1) × km_supplementaire_par_client")
        print("\nExemple avec 3 clients:")
        print("  - Client A: 50 km")
        print("  - Client B: 30 km")
        print("  - Client C: 20 km (dernier)")
        print("  → km_total = 20 + (3-1)×10 = 20 + 20 = 40 km")
        
    except Exception as e:
        print(f"\n❌ ERREUR lors de la migration: {e}")
        db.rollback()
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    migrate_km_multi_clients()
