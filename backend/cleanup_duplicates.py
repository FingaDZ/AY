import sys
import os

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, engine
from models import Pointage
from sqlalchemy import func, text

def cleanup_duplicates():
    db = SessionLocal()
    try:
        print("Recherche de doublons...")
        
        # Trouver les groupes de doublons
        duplicates = db.query(
            Pointage.employe_id, 
            Pointage.annee, 
            Pointage.mois, 
            func.count(Pointage.id).label('count')
        ).group_by(
            Pointage.employe_id, 
            Pointage.annee, 
            Pointage.mois
        ).having(func.count(Pointage.id) > 1).all()
        
        if not duplicates:
            print("Aucun doublon trouvé.")
            return

        print(f"Trouvé {len(duplicates)} groupes de doublons.")
        
        total_deleted = 0
        
        for emp_id, annee, mois, count in duplicates:
            print(f"Traitement: Employé {emp_id}, {mois}/{annee} ({count} enregistrements)")
            
            # Récupérer tous les enregistrements pour ce groupe
            records = db.query(Pointage).filter(
                Pointage.employe_id == emp_id,
                Pointage.annee == annee,
                Pointage.mois == mois
            ).order_by(Pointage.id.asc()).all()
            
            # Le premier est celui qu'on garde (ou le dernier, peu importe, mais on va merger)
            master = records[0]
            to_delete = records[1:]
            
            # Merger les données: si master a NULL et doublon a une valeur, on prend la valeur
            for duplicate in to_delete:
                for i in range(1, 32):
                    val = duplicate.get_jour(i)
                    if val is not None:
                        # Si le master est vide ou si on veut écraser, ici on complète seulement
                        if master.get_jour(i) is None:
                            master.set_jour(i, val)
                
                # Supprimer le doublon
                db.delete(duplicate)
                total_deleted += 1
            
            print(f"  -> Fusionné et supprimé {len(to_delete)} doublons.")
            
        db.commit()
        print(f"Terminé. Total supprimés: {total_deleted}")
        
    except Exception as e:
        print(f"Erreur: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_duplicates()
