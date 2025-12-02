from sqlalchemy import create_engine, text
from config import settings

def test_connection():
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as connection:
            result = connection.execute(text("SHOW DATABASES;"))
            print("Connected successfully! Databases:")
            for row in result:
                print(f"- {row[0]}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_connection()
