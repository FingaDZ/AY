content = """DATABASE_URL=mysql+pymysql://ay_dev:AyHrDev%212025@192.168.20.53:3306/ay_hr
APP_NAME=AIRBAND HR
APP_VERSION=1.0.0
DEBUG=True
CORS_ORIGINS=*
SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
"""

with open(".env", "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed .env file")
