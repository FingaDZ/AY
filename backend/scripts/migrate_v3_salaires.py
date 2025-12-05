"""
Script de migration pour le module Salaires V3.0
Ce script permet d'appliquer le fichier SQL de migration sur la base de données.
"""
import os
import sys
from sqlalchemy import text

# Ajouter le dossier parent au path pour importer database
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from database import engine

def run_migration():
    """Exécuter le fichier SQL de migration"""
    migration_file = os.path.join(parent_dir, "migrations", "v3_0_salaires_migration.sql")
    
    if not os.path.exists(migration_file):
        print(f"❌ Erreur : Fichier de migration non trouvé : {migration_file}")
        return
    
    print(f"✅ Lecture du fichier de migration : {migration_file}")
    
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Séparer les commandes par point-virgule (simple parsing)
    # Note: Ce parsing est basique et peut échouer sur des commandes complexes (procédures, triggers)
    # mais suffisant pour CREATE TABLE et ALTER TABLE
    commands = sql_content.split(';')
    
    try:
        with engine.connect() as connection:
            print("🚀 Début de l'exécution des commandes SQL...")
            count = 0
            for command in commands:
                command = command.strip()
                if command and not command.startswith('--') and not command.startswith('/*'):
                    try:
                        connection.execute(text(command))
                        count += 1
                        print(f"   ✓ Commande {count} exécutée")
                    except Exception as e:
                        # Ignorer erreurs "Duplicate column" ou "Table exists" si on relance
                        if "Duplicate column name" in str(e) or "already exists" in str(e):
                            print(f"   ⚠️ Commande {count} ignorée (déjà appliquée)")
                        else:
                            print(f"   ❌ Erreur sur commande {count}: {e}")
                            print(f"   Commande: {command[:100]}...")
                            raise e
                            
            connection.commit()
            print(f"✅ Migration terminée avec succès ! ({count} commandes)")
            
    except Exception as e:
        print(f"❌ Erreur critique lors de la migration : {e}")

if __name__ == "__main__":
    print(f"🔌 Connexion BDD : {engine.url}")
    confirm = input("Voulez-vous exécuter la migration Salaires V3.0 ? (o/n) : ")
    if confirm.lower() == 'o':
        run_migration()
    else:
        print("Annulé.")
