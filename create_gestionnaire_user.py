import sys
import os
sys.path.append('/opt/ay-hr/backend')

# 0. Hack: Définir les variables d'env AVANT d'importer les modèles
os.environ["DATABASE_URL"] = "mysql+pymysql://root:%21Yara%402014@localhost/ay_hr"
os.environ["SECRET_KEY"] = "temp_secret_key_for_script_execution"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from models.user import User

# 1. Config DB
DATABASE_URL = "mysql+pymysql://root:%21Yara%402014@localhost/ay_hr"

# 2. Config Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_gestionnaire_user():
    print("👤 Création de l'utilisateur Gestionnaire...")
    
    try:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        email = "gestionnaire@test.com"
        password = "gest123456"
        
        # Vérifier si l'utilisateur existe déjà
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"⚠️  L'utilisateur {email} existe déjà.")
            print(f"   ID: {existing_user.id}")
            print(f"   Nom: {existing_user.nom}")
            print(f"   Rôle: {existing_user.role}")
            db.close()
            return
        
        # Créer l'utilisateur
        hashed_password = pwd_context.hash(password)
        
        new_user = User(
            email=email,
            hashed_password=hashed_password,
            nom="Test",
            prenom="Gestionnaire",
            role="Gestionnaire",  # ⭐ v3.6.0: Nouveau rôle
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"✅ Utilisateur Gestionnaire créé avec succès!")
        print(f"   Email: {email}")
        print(f"   Mot de passe: {password}")
        print(f"   Nom: {new_user.nom} {new_user.prenom}")
        print(f"   Rôle: {new_user.role}")
        print(f"   ID: {new_user.id}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'utilisateur : {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_gestionnaire_user()
