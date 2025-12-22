"""
Script de diagnostic pour analyser le flux Congés → Salaire → Bulletin
"""
import sys
sys.path.append('f:/Code/AY HR/backend')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

# Connexion à la base (à adapter selon vos credentials)
DATABASE_URL = "mysql+pymysql://root:Aa123456789%40@192.168.20.55:3306/ay_hr"
engine = create_engine(DATABASE_URL)

def analyse_conges_salaire():
    with Session(engine) as db:
        print("="*80)
        print("ANALYSE COMPLETE: CONGES → SALAIRE → BULLETIN")
        print("="*80)
        
        # 1. Récupérer les employés SAFI et ZERROUG
        query_employes = text("""
            SELECT id, nom, prenom 
            FROM employes 
            WHERE nom IN ('SAFI', 'ZERROUG')
            ORDER BY nom
        """)
        employes = db.execute(query_employes).fetchall()
        
        for emp in employes:
            emp_id, nom, prenom = emp
            print(f"\n{'='*80}")
            print(f"EMPLOYÉ: {prenom} {nom} (ID: {emp_id})")
            print(f"{'='*80}")
            
            # 2. Congés enregistrés
            query_conges = text("""
                SELECT 
                    mois, annee, 
                    jours_travailles,
                    jours_conges_acquis, 
                    jours_conges_pris,
                    jours_conges_restants,
                    mois_deduction,
                    annee_deduction
                FROM conges 
                WHERE employe_id = :emp_id
                ORDER BY annee, mois
            """)
            conges = db.execute(query_conges, {"emp_id": emp_id}).fetchall()
            
            print("\n📊 TABLE CONGES:")
            print(f"{'Période':<12} {'Trav':<6} {'Acquis':<8} {'Pris':<8} {'Solde':<8} {'Déd.Mois':<10} {'Déd.Année':<10}")
            print("-" * 80)
            
            total_acquis = 0
            total_pris = 0
            
            for c in conges:
                mois, annee, trav, acquis, pris, solde, ded_mois, ded_annee = c
                total_acquis += float(acquis or 0)
                total_pris += float(pris or 0)
                
                ded_info = f"{ded_mois or '-'}/{ded_annee or '-'}"
                print(f"{mois:02d}/{annee:<7} {trav:<6} {float(acquis):<8.2f} {float(pris):<8.2f} {float(solde):<8.2f} {ded_info:<20}")
            
            print("-" * 80)
            print(f"{'TOTAUX':<12} {'':6} {total_acquis:<8.2f} {total_pris:<8.2f} {total_acquis - total_pris:<8.2f}")
            
            # 3. Vérifier ce qui serait déduit pour décembre 2025
            print(f"\n🔍 CONGÉS DÉDUITS DU BULLETIN DÉCEMBRE 2025:")
            query_deduction_dec = text("""
                SELECT 
                    mois as periode_acquisition_mois,
                    annee as periode_acquisition_annee,
                    jours_conges_pris,
                    mois_deduction,
                    annee_deduction
                FROM conges
                WHERE employe_id = :emp_id
                AND (
                    (mois_deduction = 12 AND annee_deduction = 2025)
                    OR (mois_deduction IS NULL AND mois = 12 AND annee = 2025)
                )
            """)
            ded_dec = db.execute(query_deduction_dec, {"emp_id": emp_id}).fetchall()
            
            if ded_dec:
                print(f"{'Période Acquis':<18} {'Jours Pris':<12} {'Mois Déduction':<20}")
                print("-" * 60)
                total_ded_dec = 0
                for d in ded_dec:
                    acq_mois, acq_annee, pris, ded_mois, ded_annee = d
                    total_ded_dec += float(pris or 0)
                    print(f"{acq_mois:02d}/{acq_annee:<13} {float(pris):<12.2f} {ded_mois or 'NULL'}/{ded_annee or 'NULL'}")
                print("-" * 60)
                print(f"TOTAL DÉDUIT DEC 2025: {total_ded_dec:.2f}j")
            else:
                print("❌ Aucun congé à déduire pour décembre 2025")
            
            # 4. Pointage décembre 2025
            query_pointage = text("""
                SELECT jours_travailles, jours_feries, absences_total
                FROM pointages
                WHERE employe_id = :emp_id AND mois = 12 AND annee = 2025
            """)
            pointage = db.execute(query_pointage, {"emp_id": emp_id}).fetchone()
            
            if pointage:
                trav, feries, abs_total = pointage
                print(f"\n📅 POINTAGE DÉCEMBRE 2025:")
                print(f"  Jours travaillés: {trav}")
                print(f"  Jours fériés: {feries}")
                print(f"  Absences: {abs_total}")
            else:
                print(f"\n❌ Pas de pointage pour décembre 2025")
        
        print(f"\n{'='*80}")
        print("FIN DE L'ANALYSE")
        print(f"{'='*80}")

if __name__ == "__main__":
    try:
        analyse_conges_salaire()
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
