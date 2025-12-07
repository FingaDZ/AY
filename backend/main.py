from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
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
    parametres,
    utilisateurs,
    database_config,
    logs,
    postes_travail,
    conges,
    attendance_integration,
    incomplete_logs,
    logistics_types,
    parametres_salaires
)

# Lifespan event handler moderne
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
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
