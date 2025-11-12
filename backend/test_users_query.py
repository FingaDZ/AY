from database import SessionLocal
from models import User

db = SessionLocal()
try:
    print('Testing User query...')
    users = db.query(User).all()
    print(f'Users found: {len(users)}')
    for u in users:
        print(f'  - {u.email} ({u.role})')
except Exception as e:
    print(f'ERROR: {e}')
finally:
    db.close()
