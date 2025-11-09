from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import init_db

# Import des routers
from routers import (
    employes,
    pointages,
    clients,
    missions,
    avances,
    credits,
    salaires,
    rapports,
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API de gestion des ressources humaines",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialiser la base de données au démarrage
@app.on_event("startup")
async def startup_event():
    init_db()
    print("✅ Base de données initialisée")

# Inclure les routers
app.include_router(employes.router, prefix="/api")
app.include_router(pointages.router, prefix="/api")
app.include_router(clients.router, prefix="/api")
app.include_router(missions.router, prefix="/api")
app.include_router(avances.router, prefix="/api")
app.include_router(credits.router, prefix="/api")
app.include_router(salaires.router, prefix="/api")
app.include_router(rapports.router, prefix="/api")

@app.get("/")
def root():
    return {
        "message": "Bienvenue sur l'API AY HR Management",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
