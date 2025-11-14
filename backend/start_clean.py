"""Script de démarrage backend avec rechargement forcé des modules"""
import sys
import os

# Supprimer tous les modules en cache
if 'services.logging_service' in sys.modules:
    del sys.modules['services.logging_service']
if 'services' in sys.modules:
    del sys.modules['services']

# Nettoyer le cache Python
import importlib
importlib.invalidate_caches()

print("✅ Cache des modules nettoyé")
print("🚀 Démarrage du backend...")

# Démarrer uvicorn
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Pas de reload pour éviter les problèmes de cache
        log_level="info"
    )
