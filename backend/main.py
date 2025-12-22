from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from config import settings
from database import init_db
import models
from database import engine

# Import des routers
from routers import (
    employes,
    pointages,
    clients,
    camions,
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
    deductions_conges,  # v3.7.0: Nouvelle architecture déductions
    attendance_integration,
    incomplete_logs,
    logistics_types,
    parametres_salaires,
    edition_salaires,  # Ancien système (deprecated)
    traitement_salaires  # Nouveau système v3.0
)

# Lifespan event handler moderne
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    print("Base de donnees initialisee")
    yield
    # Shutdown (rien à faire pour l'instant)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API de gestion des ressources humaines",
    lifespan=lifespan,
)

# Configuration CORS - Accepter toutes les origines (réseau LAN)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Utilise la config
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os

# Servir les fichiers statiques (images, justificatifs)
static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Inclure les routers
app.include_router(employes.router, prefix="/api")
app.include_router(pointages.router, prefix="/api")
app.include_router(clients.router, prefix="/api")
app.include_router(camions.router, prefix="/api")
app.include_router(missions.router, prefix="/api")
app.include_router(avances.router, prefix="/api")
app.include_router(credits.router, prefix="/api")
app.include_router(salaires.router, prefix="/api")
app.include_router(edition_salaires.router, prefix="/api") # Ancien système (deprecated)
app.include_router(traitement_salaires.router, prefix="/api") # Nouveau système v3.0
app.include_router(rapports.router, prefix="/api")
app.include_router(parametres.router, prefix="/api")
app.include_router(utilisateurs.router, prefix="/api")
app.include_router(database_config.router, prefix="/api")
app.include_router(logs.router, prefix="/api")
app.include_router(postes_travail.router, prefix="/api")
app.include_router(conges.router, prefix="/api")
app.include_router(deductions_conges.router, prefix="/api")  # v3.7.0: Déductions congés
app.include_router(attendance_integration.router, prefix="/api")
app.include_router(incomplete_logs.router, prefix="/api")
app.include_router(logistics_types.router, prefix="/api")
app.include_router(parametres_salaires.router, prefix="/api")

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
