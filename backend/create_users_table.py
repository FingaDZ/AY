"""Script de migration pour créer la table users
"""
from sqlalchemy import text
from database import engine

SQL = open('..\\database\\add_users_table.sql', 'r', encoding='utf-8').read()

def main():
    statements = [s.strip() for s in SQL.split(';') if s.strip()]
    with engine.connect() as conn:
        try:
            for stmt in statements:
                conn.execute(text(stmt))
            conn.commit()
            print("✅ Table 'users' créée avec succès!")
            print("   Email admin par défaut: admin@ayhr.dz")
            print("   Mot de passe: admin123")
        except Exception as e:
            print("❌ Erreur lors de la création de la table users:", e)

if __name__ == '__main__':
    main()
