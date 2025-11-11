#!/usr/bin/env python3
"""
Script pour migrer les colonnes de pointage de ENUM vers TINYINT(1)
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import engine
from sqlalchemy import text

def migrate_to_integer():
    """Convertit les colonnes jour_XX de ENUM vers TINYINT(1)"""
    try:
        print("Connexion à la base de données...")
        
        print("Migration des colonnes de ENUM vers TINYINT(1)...")
        
        # Construire la requête ALTER TABLE pour toutes les colonnes
        alter_statements = []
        for i in range(1, 32):
            col_name = f"jour_{i:02d}"
            alter_statements.append(f"MODIFY COLUMN {col_name} TINYINT(1) NULL")
        
        alter_query = f"""
        ALTER TABLE pointages
        {', '.join(alter_statements)}
        """
        
        print("Exécution de la requête ALTER TABLE...")
        with engine.connect() as connection:
            connection.execute(text(alter_query))
            connection.commit()
        
        print("✓ Migration réussie!")
        
        # Vérifier la structure
        print("\nVérification de la structure modifiée:")
        with engine.connect() as connection:
            result = connection.execute(text("DESCRIBE pointages"))
            columns = result.fetchall()
        
            print("\nColonnes jour_XX modifiées:")
            for col in columns:
                if col[0].startswith('jour_'):
                    print(f"  {col[0]}: {col[1]}")
        
        return True
        
    except Exception as e:
        print(f"✗ Erreur lors de la migration: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = migrate_to_integer()
    sys.exit(0 if success else 1)
