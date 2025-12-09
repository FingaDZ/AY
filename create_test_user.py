import sys
import os
sys.path.append('/opt/ay-hr/backend')

# 0. Hack: Définir les variables d'env AVANT d'importer les modèles
# Cela évite que pydantic ne crie si le .env n'est pas chargé
os.environ["DATABASE_URL"] = "mysql+pymysql://root:%21Yara%402014@localhost/ay_hr"
os.environ["SECRET_KEY"] = "temp_secret_key_for_script_execution"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from models.user import User  # Assure-toi que ce chemin est correct via sys.path

# 1. Config DB (Mot de passe encodé pour éviter les erreurs)
DATABASE_URL = "mysql+pymysql://root:%21Yara%402014@localhost/ay_hr"

# 2. Config Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_user():
    print("👤 Création de l'utilisateur de test...")
    
    try:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        email = "teste@g.com"
        password = "user123456"
        
        # Vérifier si existe
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"⚠️ L'utilisateur {email} existe déjà. Mise à jour du mot de passe...")
            existing_user.password_hash = pwd_context.hash(password)
            existing_user.role = "Admin" # On le met admin pour tester
            existing_user.actif = True
        else:
            print(f"➕ Création de l'utilisateur {email}...")
            new_user = User(
                email=email,
                nom="Test",
                prenom="User",
                password_hash=pwd_context.hash(password),
                role="Admin",
                actif=True
            )
            db.add(new_user)
        
        db.commit()
        print(f"✅ Utilisateur {email} opérationnel (Pass: {password})")
        print("   Rôle: Admin")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print("🔍 Vérifiez que vous avez bien lancé le script de correction de schéma avant !")

    try:
        import bcrypt
        print(f"DEBUG: bcrypt version: {bcrypt.__version__}")
        
        # Vérification immédiate
        print("🔐 Vérification immédiate du mot de passe...")
        db = SessionLocal()
        u = db.query(User).filter(User.email == email).first()
        if u and pwd_context.verify(password, u.password_hash):
            print("✅ Vérification locale RÉUSSIE. Le hash est valide.")
            print("👉 Vous pouvez maintenant vous connecter sur le site.")
        else:
            print("❌ Vérification locale ÉCHOUÉE. Le mot de passe ne correspond pas au hash.")
    except Exception as e:
        print(f"❌ Erreur de vérification: {e}")

if __name__ == "__main__":
    create_test_user()
