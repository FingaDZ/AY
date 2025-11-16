import pymysql

# Hash généré par generate_hash.py pour le mot de passe admin123
password_hash = "$2b$12$7ekJy0DVuaDyKxO/d33aEOa34lq/bVtzaTG09T0lwqVjReRfKDFDy"

conn = pymysql.connect(
    host="localhost",
    user="ayhr_user",
    password="!Yara@2014",
    database="ay_hr"
)

try:
    cursor = conn.cursor()
    
    # Insérer l'utilisateur avec des paramètres (pour éviter les problèmes d'échappement)
    sql = "INSERT INTO users (username, email, hashed_password, role, actif) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql, ("sghellam@gmail.com", "sghellam@gmail.com", password_hash, "admin", 1))
    conn.commit()
    
    print("Utilisateur créé avec succès!")
    
    # Vérifier
    cursor.execute("SELECT id, username, email, LENGTH(hashed_password) as len, LEFT(hashed_password, 15) as hash_start FROM users WHERE username=%s", ("sghellam@gmail.com",))
    result = cursor.fetchone()
    print(f"ID: {result[0]}, Username: {result[1]}, Email: {result[2]}, Hash length: {result[3]}, Hash start: {result[4]}")
    
finally:
    conn.close()
