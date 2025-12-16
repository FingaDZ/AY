# 🐳 Guide d'Installation Docker - AY HR System v3.6.0

## 📋 Table des Matières
1. [Prérequis](#prérequis)
2. [Installation Rapide](#installation-rapide)
3. [Configuration Avancée](#configuration-avancée)
4. [Commandes Docker](#commandes-docker)
5. [Dépannage](#dépannage)

---

## 🔧 Prérequis

### Installer Docker

**Linux (Ubuntu/Debian):**
```bash
# Installer Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Installer Docker Compose
sudo apt install docker-compose-plugin

# Vérifier l'installation
docker --version
docker compose version
```

**Windows/Mac:**
- Télécharger [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Installer et démarrer Docker Desktop

---

## 🚀 Installation Rapide

### Étape 1: Cloner le Projet

```bash
git clone https://github.com/VotreOrg/ay-hr.git
cd ay-hr
```

### Étape 2: Configuration

**Créer le fichier `.env` à la racine du projet:**

```env
# Base de données
MYSQL_ROOT_PASSWORD=rootpassword123!
MYSQL_DATABASE=ay_hr
MYSQL_USER=ayhr_user
MYSQL_PASSWORD=ayhr_password_2024!

# Backend
SECRET_KEY=votre-cle-secrete-aleatoire-tres-longue
DEBUG=False
BACKEND_PORT=8000

# Frontend
FRONTEND_PORT=80
VITE_API_URL=http://localhost:8000

# Admin par défaut
ADMIN_EMAIL=admin@ay-hr.com
ADMIN_PASSWORD=Admin@2024!
```

**Générer une clé secrète:**
```bash
openssl rand -hex 32
```

### Étape 3: Lancer les Conteneurs

```bash
# Build et démarrage
docker compose up -d --build

# Vérifier le statut
docker compose ps

# Voir les logs
docker compose logs -f
```

### Étape 4: Accès à l'Application

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **Documentation API**: http://localhost:8000/docs

**Credentials par défaut:**
- Email: `admin@ay-hr.com`
- Password: `Admin@2024!`

---

## 📦 Structure Docker

### docker-compose.yml

```yaml
version: '3.8'

services:
  # Base de données MySQL
  mysql:
    image: mysql:8.0
    container_name: ayhr-mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./database/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql:ro
      - ./database/seed.sql:/docker-entrypoint-initdb.d/02-seed.sql:ro
    networks:
      - ayhr-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p${MYSQL_ROOT_PASSWORD}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: ayhr-backend
    restart: always
    environment:
      DATABASE_URL: mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@mysql:3306/${MYSQL_DATABASE}
      SECRET_KEY: ${SECRET_KEY}
      DEBUG: ${DEBUG}
      CORS_ORIGINS: http://localhost,http://localhost:${FRONTEND_PORT}
    ports:
      - "${BACKEND_PORT}:8000"
    depends_on:
      mysql:
        condition: service_healthy
    volumes:
      - ./backend:/app
      - backend_logs:/app/logs
    networks:
      - ayhr-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        VITE_API_URL: ${VITE_API_URL}
    container_name: ayhr-frontend
    restart: always
    ports:
      - "${FRONTEND_PORT}:80"
    depends_on:
      - backend
    networks:
      - ayhr-network

  # Nginx Reverse Proxy (Optionnel)
  nginx:
    image: nginx:alpine
    container_name: ayhr-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - frontend
      - backend
    networks:
      - ayhr-network
    profiles:
      - production

volumes:
  mysql_data:
    driver: local
  backend_logs:
    driver: local

networks:
  ayhr-network:
    driver: bridge
```

### backend/Dockerfile

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements.txt
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Créer le répertoire logs
RUN mkdir -p /app/logs

# Exposer le port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# Commande de démarrage
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### frontend/Dockerfile

```dockerfile
# Frontend Dockerfile - Multi-stage build
FROM node:20-alpine AS builder

WORKDIR /app

# Copier package.json et package-lock.json
COPY package*.json ./

# Installer les dépendances
RUN npm ci

# Copier le code source
COPY . .

# Argument pour l'URL de l'API
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

# Build de production
RUN npm run build

# Stage 2: Nginx
FROM nginx:alpine

# Copier la configuration Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copier les fichiers build depuis le stage précédent
COPY --from=builder /app/dist /usr/share/nginx/html

# Exposer le port
EXPOSE 80

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

### frontend/nginx.conf

```nginx
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    # Gzip
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Frontend SPA
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache des assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Désactiver le cache pour index.html
    location = /index.html {
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }
}
```

### database/seed.sql

```sql
-- Seed data pour initialisation
USE ay_hr;

-- Insérer l'utilisateur admin
INSERT INTO users (email, nom, prenom, password_hash, role, actif)
VALUES (
    'admin@ay-hr.com',
    'Admin',
    'System',
    -- Password: Admin@2024! (hasher avec bcrypt)
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5oeQx/i6F6Wuy',
    'Admin',
    1
)
ON DUPLICATE KEY UPDATE password_hash=VALUES(password_hash);

-- Paramètres de salaire par défaut
INSERT INTO parametres_salaire (
    taux_in, taux_ifsp, taux_iep_par_an, taux_prime_encouragement,
    anciennete_min_encouragement, prime_chauffeur_jour, prime_nuit_securite,
    panier_jour, transport_jour, prime_femme_foyer, taux_securite_sociale,
    calculer_heures_supp, mode_calcul_conges, jours_ouvrables_base,
    irg_proratise, km_supplementaire_par_client
)
VALUES (
    5.0, 5.0, 1.0, 10.0,
    1, 100.0, 750.0,
    100.0, 100.0, 1000.0, 9.0,
    1, 'complet', 30,
    1, 10
)
ON DUPLICATE KEY UPDATE id=id;

-- Paramètres généraux entreprise
INSERT INTO parametres (
    raison_sociale, nom_entreprise, adresse,
    rc, nif, nis, art, numero_secu_employeur,
    telephone, banque, compte_bancaire
)
VALUES (
    'SARL AY Ressources Humaines',
    'AY HR',
    'Alger, Algérie',
    '12345678', '098765432101234', '098765432101', '16011234567890',
    '12345678901234567890',
    '+213 21 23 45 67',
    'BNA - Agence Alger Centre',
    '0123456789012345678'
)
ON DUPLICATE KEY UPDATE id=id;
```

---

## ⚙️ Configuration Avancée

### Variables d'Environnement

**Fichier `.env` complet:**

```env
# MySQL
MYSQL_ROOT_PASSWORD=rootpassword123!
MYSQL_DATABASE=ay_hr
MYSQL_USER=ayhr_user
MYSQL_PASSWORD=ayhr_password_2024!
MYSQL_PORT=3306

# Backend
SECRET_KEY=your-secret-key-here-generate-with-openssl
DEBUG=False
BACKEND_PORT=8000
CORS_ORIGINS=http://localhost,http://localhost:80,http://localhost:3000
ATTENDANCE_API_URL=http://localhost:8000/api
ATTENDANCE_API_TIMEOUT=30

# Frontend
FRONTEND_PORT=80
VITE_API_URL=http://localhost:8000

# Admin
ADMIN_EMAIL=admin@ay-hr.com
ADMIN_PASSWORD=Admin@2024!

# Timezone
TZ=Africa/Algiers
```

### Volumes et Persistance

**Backup des données:**
```bash
# Backup MySQL
docker exec ayhr-mysql mysqldump -u root -p${MYSQL_ROOT_PASSWORD} ay_hr > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup complet (avec volumes)
docker run --rm \
  -v ayhr_mysql_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/mysql_backup_$(date +%Y%m%d_%H%M%S).tar.gz /data
```

**Restore:**
```bash
# Restore MySQL
docker exec -i ayhr-mysql mysql -u root -p${MYSQL_ROOT_PASSWORD} ay_hr < backup_20241216_143000.sql
```

### SSL/TLS avec Let's Encrypt

**docker-compose.override.yml:**

```yaml
version: '3.8'

services:
  certbot:
    image: certbot/certbot
    container_name: ayhr-certbot
    volumes:
      - ./nginx/ssl:/etc/letsencrypt
      - ./nginx/certbot:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"

  nginx:
    volumes:
      - ./nginx/certbot:/var/www/certbot
```

**Obtenir certificat:**
```bash
docker compose run --rm certbot certonly --webroot \
  -w /var/www/certbot \
  -d votre-domaine.com \
  --email votre-email@example.com \
  --agree-tos --no-eff-email
```

---

## 🔧 Commandes Docker

### Gestion des Conteneurs

```bash
# Démarrer tous les services
docker compose up -d

# Arrêter tous les services
docker compose down

# Redémarrer un service
docker compose restart backend

# Voir les logs
docker compose logs -f
docker compose logs -f backend
docker compose logs -f mysql

# Statut des conteneurs
docker compose ps

# Statistiques ressources
docker stats
```

### Accès aux Conteneurs

```bash
# Shell backend
docker exec -it ayhr-backend bash

# Shell MySQL
docker exec -it ayhr-mysql mysql -u root -p

# Shell frontend (Nginx)
docker exec -it ayhr-frontend sh
```

### Nettoyage

```bash
# Arrêter et supprimer tout
docker compose down -v

# Supprimer les images
docker compose down --rmi all

# Nettoyer le système Docker
docker system prune -a
```

### Mise à Jour

```bash
# Pull du code
git pull

# Rebuild et redémarrage
docker compose up -d --build

# Ou rebuild un seul service
docker compose up -d --build backend
```

---

## 📊 Monitoring et Logs

### Logs en Temps Réel

```bash
# Tous les services
docker compose logs -f --tail=100

# Service spécifique
docker compose logs -f backend --tail=50
```

### Logs Persistants

Les logs du backend sont sauvegardés dans le volume `backend_logs`:

```bash
# Voir les logs backend
docker exec ayhr-backend ls -la /app/logs

# Copier les logs localement
docker cp ayhr-backend:/app/logs ./backend_logs_backup
```

---

## 🔒 Sécurité

### Bonnes Pratiques

1. **Changer les mots de passe par défaut**
2. **Utiliser des secrets Docker** (pour production)
3. **Activer SSL/TLS**
4. **Limiter l'exposition des ports**
5. **Scanner les images régulièrement**

```bash
# Scanner les vulnérabilités
docker scan ayhr-backend
docker scan ayhr-frontend
```

### Secrets Docker (Production)

**docker-compose.prod.yml:**

```yaml
version: '3.8'

services:
  backend:
    environment:
      DATABASE_URL: mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@mysql:3306/${MYSQL_DATABASE}
      SECRET_KEY_FILE: /run/secrets/secret_key
    secrets:
      - secret_key

secrets:
  secret_key:
    file: ./secrets/secret_key.txt
```

---

## 🐛 Dépannage

### Conteneur ne démarre pas

```bash
# Voir les logs détaillés
docker compose logs backend

# Inspecter le conteneur
docker inspect ayhr-backend
```

### Problème de connexion MySQL

```bash
# Vérifier que MySQL est prêt
docker exec ayhr-mysql mysqladmin ping -h localhost

# Tester la connexion
docker exec -it ayhr-mysql mysql -u ayhr_user -p ay_hr
```

### Problème de permissions

```bash
# Changer les permissions des volumes
docker exec -it ayhr-backend chown -R nobody:nogroup /app/logs
```

### Port déjà utilisé

```bash
# Trouver le processus
sudo lsof -i :8000

# Modifier le port dans .env
echo "BACKEND_PORT=8001" >> .env
docker compose up -d
```

---

## 📈 Scaling (Optionnel)

Pour scaler l'application:

```bash
# Démarrer plusieurs instances backend
docker compose up -d --scale backend=3

# Avec load balancer Nginx
# Voir docker-compose.scale.yml
```

---

## 🆘 Support

En cas de problème:
1. Vérifier les logs: `docker compose logs -f`
2. Consulter la santé: `docker compose ps`
3. Vérifier la configuration: `docker compose config`
4. Redémarrer les services: `docker compose restart`

