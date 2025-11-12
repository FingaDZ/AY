from database import SessionLocal
from models import User
import bcrypt

db = SessionLocal()

# Récupérer l'admin
admin = db.query(User).filter(User.email == "admin@ayhr.dz").first()
if admin:
    print(f"Admin trouvé: {admin.email}")
    print(f"Hash stocké: {admin.password_hash[:50]}...")
    
    # Tester le mot de passe
    password = "admin123"
    is_valid = bcrypt.checkpw(password.encode('utf-8'), admin.password_hash.encode('utf-8'))
    print(f"Mot de passe valide: {is_valid}")
    
    # Tester avec le hash directement
    test_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    print(f"Nouveau hash exemple: {test_hash[:50]}...")
else:
    print("Admin non trouvé!")

db.close()
