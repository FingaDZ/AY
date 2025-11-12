"""Script de migration pour créer la table parametres (utiliser si mysql CLI indisponible)
"""
from sqlalchemy import text
from database import engine

SQL = open('..\\database\\add_parametres_table.sql', 'r', encoding='utf-8').read()

def main():
    # Split statements and execute separately to avoid multi-statement issues
    statements = [s.strip() for s in SQL.split(';') if s.strip()]
    with engine.connect() as conn:
        try:
            for stmt in statements:
                conn.execute(text(stmt))
            conn.commit()
            print("✅ Table 'parametres_entreprise' créée avec succès!")
        except Exception as e:
            print("❌ Erreur lors de la création de la table parametres_entreprise:", e)

if __name__ == '__main__':
    main()
