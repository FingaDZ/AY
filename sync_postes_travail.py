"""
Script pour synchroniser les postes de travail
Ce script remplace les postes de travail par ceux réellement utilisés par les employés
Attention: Conserve le poste "Chauffeur" pour les calculs de salaire
"""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configuration
DATABASE_URL = "mysql+pymysql://ayhr_user:%21Yara%402014@localhost/ay_hr"

def sync_postes_travail(db_url: str):
    """Synchroniser les postes de travail avec ceux utilisés par les employés"""
    
    engine = create_engine(db_url, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("=" * 70)
        print("SYNCHRONISATION DES POSTES DE TRAVAIL")
        print("=" * 70)
        
        # 1. Récupérer les postes actuellement utilisés par les employés
        print("\n📊 Récupération des postes utilisés par les employés...")
        result = session.execute(text("""
            SELECT DISTINCT poste_travail 
            FROM employes 
            WHERE poste_travail IS NOT NULL 
            ORDER BY poste_travail
        """))
        postes_employes = [row[0] for row in result.fetchall()]
        print(f"✓ {len(postes_employes)} postes distincts trouvés:")
        for poste in postes_employes:
            print(f"   - {poste}")
        
        # 2. Identifier les postes "Chauffeur" existants (à conserver)
        print("\n🚗 Vérification des postes Chauffeur...")
        result = session.execute(text("""
            SELECT id, libelle, est_chauffeur 
            FROM postes_travail 
            WHERE est_chauffeur = 1
        """))
        postes_chauffeur = result.fetchall()
        print(f"✓ {len(postes_chauffeur)} poste(s) chauffeur trouvé(s):")
        for poste in postes_chauffeur:
            print(f"   - ID {poste[0]}: {poste[1]} (chauffeur={poste[2]})")
        
        # 3. Confirmer la suppression
        print("\n⚠️  ATTENTION: Cette opération va:")
        print("   1. Supprimer tous les postes de travail existants")
        print("   2. SAUF les postes marqués comme 'chauffeur'")
        print("   3. Créer de nouveaux postes basés sur ceux utilisés par les employés")
        
        response = input("\n   Voulez-vous continuer? (oui/non): ")
        if response.lower() != 'oui':
            print("❌ Synchronisation annulée")
            return False
        
        # 4. Supprimer les postes qui ne sont pas chauffeur
        print("\n🗑️  Suppression des postes non-chauffeur...")
        result = session.execute(text("""
            DELETE FROM postes_travail 
            WHERE est_chauffeur = 0
        """))
        session.commit()
        print(f"✓ {result.rowcount} poste(s) supprimé(s)")
        
        # 5. Créer les nouveaux postes
        print("\n➕ Création des nouveaux postes...")
        created_count = 0
        for poste in postes_employes:
            # Vérifier si le poste existe déjà
            result = session.execute(
                text("SELECT COUNT(*) FROM postes_travail WHERE libelle = :libelle"),
                {"libelle": poste}
            )
            count = result.fetchone()[0]
            
            if count == 0:
                # Déterminer si c'est un poste de chauffeur
                est_chauffeur = 'chauffeur' in poste.lower()
                
                # Insérer le nouveau poste
                session.execute(text("""
                    INSERT INTO postes_travail (libelle, est_chauffeur, modifiable, actif)
                    VALUES (:libelle, :est_chauffeur, 1, 1)
                """), {
                    "libelle": poste,
                    "est_chauffeur": est_chauffeur
                })
                created_count += 1
                symbol = "🚗" if est_chauffeur else "📋"
                print(f"   {symbol} Créé: {poste}")
            else:
                print(f"   ✓ Existe déjà: {poste}")
        
        session.commit()
        print(f"\n✅ {created_count} nouveau(x) poste(s) créé(s)")
        
        # 6. Afficher le résultat final
        print("\n📋 Liste finale des postes de travail:")
        result = session.execute(text("""
            SELECT id, libelle, est_chauffeur, actif 
            FROM postes_travail 
            ORDER BY libelle
        """))
        postes_finaux = result.fetchall()
        for poste in postes_finaux:
            symbol = "🚗" if poste[2] else "📋"
            status = "✓" if poste[3] else "✗"
            print(f"   {symbol} {status} ID {poste[0]}: {poste[1]}")
        
        print(f"\n✅ Total: {len(postes_finaux)} poste(s) de travail")
        
        return True
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        session.close()

if __name__ == "__main__":
    success = sync_postes_travail(DATABASE_URL)
    
    if success:
        print("\n✅ Synchronisation réussie!")
    else:
        print("\n❌ La synchronisation a échoué")
        sys.exit(1)
