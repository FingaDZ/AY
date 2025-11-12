"""
Script pour ajouter la colonne tarif_km à la table clients
"""
from database import engine
from sqlalchemy import text

def add_tarif_km_column():
    with engine.connect() as conn:
        try:
            # Ajouter la colonne tarif_km
            conn.execute(text("""
                ALTER TABLE clients
                ADD COLUMN tarif_km DECIMAL(10,2) DEFAULT 3.00 NOT NULL
                COMMENT 'Tarif kilométrique spécifique au client (DA/km)'
            """))
            conn.commit()
            print("✅ Colonne tarif_km ajoutée avec succès à la table clients")
            
            # Vérifier
            result = conn.execute(text("SELECT id, nom, prenom, distance, tarif_km FROM clients"))
            print("\nClients avec tarif_km:")
            for row in result:
                print(f"  ID={row[0]}, {row[1]} {row[2]}, distance={row[3]}km, tarif={row[4]}DA/km")
                
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("ℹ️  La colonne tarif_km existe déjà")
            else:
                print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    add_tarif_km_column()
