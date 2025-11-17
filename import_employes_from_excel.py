"""
Script d'importation des employés depuis un fichier Excel
Ce script remplace toutes les données employés dans la base de données
"""
import sys
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, text, Column, Integer, String, Date, Boolean, Enum as SQLEnum
from sqlalchemy.types import Numeric
from sqlalchemy.orm import sessionmaker, declarative_base
import enum

# Définir les enums localement
class SituationFamiliale(str, enum.Enum):
    CELIBATAIRE = "Célibataire"
    MARIE = "Marié"

class StatutContrat(str, enum.Enum):
    ACTIF = "Actif"
    INACTIF = "Inactif"

# Définir la base
Base = declarative_base()

# Définir le modèle Employe localement (pour éviter les dépendances)
class Employe(Base):
    __tablename__ = "employes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nom = Column(String(100), nullable=False, index=True)
    prenom = Column(String(100), nullable=False, index=True)
    date_naissance = Column(Date, nullable=False)
    lieu_naissance = Column(String(200), nullable=False)
    adresse = Column(String(500), nullable=False)
    mobile = Column(String(20), nullable=False)
    numero_secu_sociale = Column(String(50), unique=True, nullable=False)
    numero_compte_bancaire = Column(String(50), nullable=False)
    numero_anem = Column(String(50), nullable=True, index=True)
    situation_familiale = Column(SQLEnum(SituationFamiliale), nullable=False)
    femme_au_foyer = Column(Boolean, default=False, nullable=False)
    date_recrutement = Column(Date, nullable=False)
    duree_contrat = Column(Integer, nullable=True)
    date_fin_contrat = Column(Date, nullable=True)
    poste_travail = Column(String(100), nullable=False, index=True)
    salaire_base = Column(Numeric(12, 2), nullable=False)
    prime_nuit_agent_securite = Column(Boolean, default=False, nullable=False)
    statut_contrat = Column(SQLEnum(StatutContrat), default=StatutContrat.ACTIF, nullable=False, index=True)
    actif = Column(Boolean, default=True, nullable=False, index=True)

# Configuration de la base de données
# Sur le serveur, utiliser localhost
DATABASE_URL = "mysql+pymysql://ayhr_user:%21Yara%402014@localhost/ay_hr"

def parse_date(date_value):
    """Convertir une valeur de date Excel en objet date Python"""
    if pd.isna(date_value):
        return None
    
    if isinstance(date_value, datetime):
        return date_value.date()
    
    # Si c'est un nombre (format Excel serial date)
    if isinstance(date_value, (int, float)):
        try:
            # Excel serial date (nombre de jours depuis 1900-01-01)
            excel_epoch = datetime(1899, 12, 30)
            return (excel_epoch + pd.Timedelta(days=date_value)).date()
        except:
            return None
    
    if isinstance(date_value, str):
        # Essayer différents formats
        for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%d.%m.%Y', '%Y/%m/%d']:
            try:
                return datetime.strptime(date_value, fmt).date()
            except ValueError:
                continue
    
    return None

def parse_situation_familiale(value):
    """Convertir la situation familiale du Excel vers l'enum"""
    if pd.isna(value):
        return SituationFamiliale.CELIBATAIRE
    
    value_clean = str(value).strip().lower()
    if 'mari' in value_clean:
        return SituationFamiliale.MARIE
    else:
        return SituationFamiliale.CELIBATAIRE

def parse_boolean(value):
    """Convertir une valeur vers booléen"""
    if pd.isna(value):
        return False
    
    if isinstance(value, bool):
        return value
    
    value_clean = str(value).strip().lower()
    return value_clean in ['oui', 'yes', 'true', '1', 'x']

def import_employes_from_excel(excel_file: str, db_url: str, delete_existing: bool = True):
    """
    Importer les employés depuis un fichier Excel
    
    Args:
        excel_file: Chemin vers le fichier Excel
        db_url: URL de connexion à la base de données
        delete_existing: Si True, supprime tous les employés existants
    """
    print(f"📊 Lecture du fichier Excel: {excel_file}")
    
    # Lire le fichier Excel
    try:
        df = pd.read_excel(excel_file, sheet_name='LIST DES EMPLOYES')
        print(f"✓ Fichier Excel lu avec succès: {len(df)} lignes trouvées")
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier Excel: {e}")
        return False
    
    # Afficher les colonnes disponibles
    print(f"\n📋 Colonnes trouvées: {', '.join(df.columns.tolist())}")
    
    # Créer la connexion à la base de données
    engine = create_engine(db_url, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Supprimer les employés existants si demandé
        if delete_existing:
            print("\n⚠️  ATTENTION: Suppression de tous les employés existants...")
            
            # Compter les employés actuels
            count_existing = session.query(Employe).count()
            print(f"   Nombre d'employés à supprimer: {count_existing}")
            
            if count_existing > 0:
                response = input(f"\n   Voulez-vous vraiment supprimer {count_existing} employé(s)? (oui/non): ")
                if response.lower() != 'oui':
                    print("❌ Importation annulée par l'utilisateur")
                    return False
                
                # Supprimer d'abord les dépendances
                print("   Suppression des dépendances (pointages, avances, crédits, missions, congés)...")
                session.execute(text("DELETE FROM conges"))
                session.execute(text("DELETE FROM missions"))
                session.execute(text("DELETE FROM credits"))
                session.execute(text("DELETE FROM avances"))
                session.execute(text("DELETE FROM pointages"))
                
                # Puis supprimer les employés
                print("   Suppression des employés...")
                session.execute(text("DELETE FROM employes"))
                session.commit()
                print("✓ Tous les employés ont été supprimés")
        
        # Importer les nouveaux employés
        print(f"\n📥 Importation de {len(df)} employés...")
        
        imported_count = 0
        skipped_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Vérifier que les champs essentiels sont présents
                if pd.isna(row.get('NOM')) or pd.isna(row.get('PRENOM')):
                    skipped_count += 1
                    print(f"   ⊘ Ligne {index + 2} ignorée: Nom ou prénom manquant")
                    continue
                
                # Extraire les données
                nom = str(row['NOM']).strip()
                prenom = str(row['PRENOM']).strip()
                
                # Date de naissance
                date_naissance_raw = row.get(' NAISSANCE')
                date_naissance = parse_date(date_naissance_raw)
                if not date_naissance:
                    print(f"   [DEBUG] Ligne {index + 2} ({prenom} {nom}): Date brute='{date_naissance_raw}', type={type(date_naissance_raw)}")
                    skipped_count += 1
                    print(f"   ⊘ Ligne {index + 2} ({prenom} {nom}): Date de naissance invalide")
                    continue
                
                # Lieu de naissance
                lieu_naissance = str(row.get('LIEU', 'N/A')).strip()
                if pd.isna(row.get('LIEU')):
                    lieu_naissance = 'N/A'
                
                # Adresse
                adresse = str(row.get('ADRESSE', 'N/A')).strip()
                if pd.isna(row.get('ADRESSE')):
                    adresse = 'N/A'
                
                # Mobile
                mobile = str(row.get('TELEPHONE', '0000000000')).strip()
                if pd.isna(row.get('TELEPHONE')):
                    mobile = '0000000000'
                
                # N° Sécurité Sociale
                numero_secu_sociale = str(row.get('N Sécurité Sociale', '')).strip()
                if pd.isna(row.get('N Sécurité Sociale')) or not numero_secu_sociale:
                    # Générer un numéro temporaire unique
                    numero_secu_sociale = f"TEMP{datetime.now().strftime('%Y%m%d%H%M%S')}{index}"
                
                # N° Compte Bancaire
                numero_compte_bancaire = str(row.get('N° COMPTE', '0000000000000000')).strip()
                if pd.isna(row.get('N° COMPTE')):
                    numero_compte_bancaire = '0000000000000000'
                
                # Situation familiale
                situation_familiale = parse_situation_familiale(row.get('SITUATION'))
                
                # Femme au foyer
                femme_au_foyer = parse_boolean(row.get('FOF'))
                
                # Date de recrutement
                date_recrutement = parse_date(row.get('ENTRE'))
                if not date_recrutement:
                    date_recrutement = datetime.now().date()
                
                # Date de fin de contrat
                date_fin_contrat = parse_date(row.get('SORTIE'))
                
                # Poste de travail
                poste_travail = str(row.get('POSTE', 'Non spécifié')).strip()
                if pd.isna(row.get('POSTE')):
                    poste_travail = 'Non spécifié'
                
                # Catégorie du poste (non utilisé dans le modèle actuel, mais on le garde en commentaire)
                categorie_poste = row.get('Categorie', '')
                
                # Déterminer le salaire base (colonne Q contient les avances, pas le salaire)
                # Le salaire devra être défini manuellement ou via une autre source
                salaire_base = 0.0  # À définir manuellement
                
                # Déterminer si actif (si date_fin_contrat est dans le passé ou None)
                actif = True
                statut_contrat = StatutContrat.ACTIF
                if date_fin_contrat and date_fin_contrat < datetime.now().date():
                    actif = False
                    statut_contrat = StatutContrat.INACTIF
                
                # Créer l'employé
                employe = Employe(
                    nom=nom,
                    prenom=prenom,
                    date_naissance=date_naissance,
                    lieu_naissance=lieu_naissance,
                    adresse=adresse,
                    mobile=mobile,
                    numero_secu_sociale=numero_secu_sociale,
                    numero_compte_bancaire=numero_compte_bancaire,
                    situation_familiale=situation_familiale,
                    femme_au_foyer=femme_au_foyer,
                    date_recrutement=date_recrutement,
                    date_fin_contrat=date_fin_contrat,
                    poste_travail=poste_travail,
                    salaire_base=salaire_base,
                    prime_nuit_agent_securite=False,
                    statut_contrat=statut_contrat,
                    actif=actif
                )
                
                session.add(employe)
                imported_count += 1
                
                if (imported_count % 10) == 0:
                    print(f"   ... {imported_count} employés importés")
                
            except Exception as e:
                skipped_count += 1
                error_msg = f"Ligne {index + 2}: {str(e)}"
                errors.append(error_msg)
                print(f"   ❌ Erreur {error_msg}")
        
        # Valider les changements
        session.commit()
        
        print(f"\n✅ Importation terminée:")
        print(f"   - Employés importés: {imported_count}")
        print(f"   - Lignes ignorées: {skipped_count}")
        
        if errors:
            print(f"\n⚠️  Erreurs rencontrées ({len(errors)}):")
            for error in errors[:10]:  # Afficher les 10 premières erreurs
                print(f"   - {error}")
            if len(errors) > 10:
                print(f"   ... et {len(errors) - 10} autres erreurs")
        
        return True
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Erreur critique lors de l'importation: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        session.close()

if __name__ == "__main__":
    # Chemin vers le fichier Excel
    excel_file = "PLAN SALAIRE OCTOBRE 2025.xlsx"
    
    # Vérifier que le fichier existe
    if not os.path.exists(excel_file):
        print(f"❌ Fichier non trouvé: {excel_file}")
        sys.exit(1)
    
    print("=" * 70)
    print("IMPORTATION DES EMPLOYÉS DEPUIS EXCEL")
    print("=" * 70)
    print(f"Fichier source: {excel_file}")
    print(f"Base de données: {DATABASE_URL}")
    print("=" * 70)
    
    # Exécuter l'importation
    success = import_employes_from_excel(excel_file, DATABASE_URL, delete_existing=True)
    
    if success:
        print("\n✅ Importation réussie!")
        print("\n⚠️  IMPORTANT: Les salaires de base sont définis à 0.0 DA")
        print("   Vous devez les mettre à jour manuellement via l'interface web")
    else:
        print("\n❌ L'importation a échoué")
        sys.exit(1)
