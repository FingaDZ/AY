"""
Script de migration des données pointages
Convertit les noms d'enum (TRAVAILLE, FERIE) en valeurs courtes (Tr, Fe)
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import engine
from sqlalchemy import text

def migrate_pointages():
    """Migrer les valeurs enum dans la table pointages"""
    
    # Lire le script SQL
    script_path = os.path.join(os.path.dirname(__file__), 'fix_pointages_enum.sql')
    with open(script_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # Exécuter le script
    with engine.begin() as connection:
        # Séparer les commandes
        commands = [cmd.strip() for cmd in sql_script.split(';') if cmd.strip() and not cmd.strip().startswith('--')]
        
        for i, command in enumerate(commands):
            if command.upper().startswith('USE'):
                # Ignorer la commande USE, on utilise déjà la bonne DB
                continue
            
            print(f"\n🔄 Exécution commande {i+1}/{len(commands)}...")
            result = connection.execute(text(command))
            
            if result.returns_rows:
                rows = result.fetchall()
                for row in rows:
                    print(f"   ✅ {row}")
    
    print("\n✅ Migration terminée avec succès!")

if __name__ == "__main__":
    print("🚀 Démarrage de la migration des données pointages...")
    print("   Conversion: TRAVAILLE → Tr, FERIE → Fe, etc.")
    
    try:
        migrate_pointages()
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
