import bcrypt

password = "admin123"
# Générer le hash
hash1 = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
print(f"Hash 1: {hash1}")

# Vérifier qu'il fonctionne
is_valid = bcrypt.checkpw(password.encode('utf-8'), hash1.encode('utf-8'))
print(f"Hash 1 valide: {is_valid}")

# Générer un autre pour comparer
hash2 = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
print(f"Hash 2: {hash2}")

# Tester le hash de la base
db_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYILY8Z6K5i"
print(f"\nHash de la base: {db_hash}")
print(f"Longueur: {len(db_hash)}")

try:
    is_valid_db = bcrypt.checkpw(password.encode('utf-8'), db_hash.encode('utf-8'))
    print(f"Hash DB valide: {is_valid_db}")
except Exception as e:
    print(f"Erreur: {e}")

# Générer un hash propre qu'on peut mettre à jour
print(f"\nHash à utiliser pour UPDATE:")
new_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
print(new_hash)
