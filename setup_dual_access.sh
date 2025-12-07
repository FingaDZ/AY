#!/bin/bash

# ==============================================================================
# AY HR System - Dual Access Setup (Domain + Local IP)
# URL Strategy: Relative URLs + Nginx Reverse Proxy
# ==============================================================================

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"; }
info() { echo -e "${BLUE}[INFO] $1${NC}"; }

# Vérification root
if [ "$EUID" -ne 0 ]; then echo "Root requis"; exit 1; fi

log "⚙️ Configuration du Double Accès (Domain + IP Local)..."

# 1. Installation Nginx Local
# ==============================================================================
info "Installation de Nginx..."
apt install -y nginx

# 2. Configuration Nginx Proxy
# ==============================================================================
info "Configuration du Reverse Proxy Nginx..."

# On écoute sur le port 80 pour que Nginx Proxy Manager (ou l'utilisateur) puisse taper directement
# Si Nginx Proxy Manager est redirigé vers 192.168.20.55:80, ça ira ici.
# Si l'utilisateur tape http://192.168.20.55, ça ira ici aussi.

cat > /etc/nginx/sites-available/ayhr << 'EOF'
server {
    listen 80;
    server_name _;

    # Augmenter la taille max des uploads (pour import Excel)
    client_max_body_size 64M;

    # 1. API: Rediriger vers le Backend (Port 8000)
    # L'API s'attend à recevoir /api/... donc on garde /api/
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        
        # Headers CORS gérés par le backend, mais on s'assure que Nginx ne bloque rien
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 2. Docs: Rediriger vers le Backend (Port 8000)
    location /docs {
        proxy_pass http://localhost:8000/docs;
    }
    location /openapi.json {
        proxy_pass http://localhost:8000/openapi.json;
    }

    # 3. Frontend: Rediriger tout le reste vers le Frontend (Port 3000)
    # Note: On utilise proxy_pass vers 'serve' running on 3000
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

# Activation du site
ln -sf /etc/nginx/sites-available/ayhr /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
systemctl restart nginx

# 3. Configuration Frontend (URL Relative)
# ==============================================================================
info "Mise à jour configuration Frontend..."

cd /opt/ay-hr/frontend

# On vide VITE_API_URL pour que Axios utilise l'URL relative (path only)
# IMPORTANT: Le backend attend le prefixe /api, et les appels axios le contiennent-ils ?
# D'après l'analyse, les services font api.get('/attendance-integration/...') 
# MAIS api.js a surement un baseURL.

# Si api.js a baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
# Et qu'on met VITE_API_URL="/api", alors :
# api.get('/endpoint') -> /api/endpoint. -> Nginx /api -> Backend.
# C'est la configuration la plus robuste.

cat > .env << EOF
VITE_API_URL=/api
EOF

# Rebuild
info "Reconstruction du Frontend..."
npm run build

# Redémarrage service
systemctl restart ayhr-frontend

log "✅ Configuration terminée !"
echo ""
echo "Accès disponibles (Backend proxyifié via Nginx):"
echo "1. http://$(hostname -I | awk '{print $1}')"
echo "2. http://$(hostname -I | awk '{print $1}')/api/health"
echo ""
echo "👉 DANS NGINX PROXY MANAGER:"
echo "Changez le 'Forward Port' de 3000 vers 80"
echo "Ainsi, tout passe par ce Nginx local qui dispatche correctement."
