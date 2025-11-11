"""
Script pour modifier la structure de la table pointages
Change la définition ENUM de ('TRAVAILLE','ABSENT',...) à ('Tr','Ab',...)
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import engine
from sqlalchemy import text

def alter_pointages_structure():
    """Modifier la structure de la table pointages"""
    
    # Lire le script SQL
    script_path = os.path.join(os.path.dirname(__file__), 'alter_pointages_enum.sql')
    with open(script_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # Exécuter le script
    with engine.begin() as connection:
        # Séparer les commandes
        commands = [cmd.strip() for cmd in sql_script.split(';') if cmd.strip() and not cmd.strip().startswith('--')]
        
        for i, command in enumerate(commands):
            if command.upper().startswith('USE'):
                continue
            
            print(f"\n🔄 Exécution commande {i+1}/{len(commands)}...")
            result = connection.execute(text(command))
            
            if result.returns_rows:
                rows = result.fetchall()
                for row in rows:
                    print(f"   ✅ {row}")
    
    print("\n✅ Structure modifiée avec succès!")

if __name__ == "__main__":
    print("🚀 Modification de la structure de la table pointages...")
    print("   ENUM('TRAVAILLE',...) → ENUM('Tr',...)")
    
    try:
        alter_pointages_structure()
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
