#!/bin/bash
# Quick Start Script pour Docker - AY HR System v3.6.0

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}  AY HR System v3.6.0 - Docker Setup  ${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker n'est pas installé${NC}"
    echo "Installez Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check Docker Compose
if ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose n'est pas installé${NC}"
    echo "Installez Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker installé: $(docker --version)${NC}"
echo -e "${GREEN}✓ Docker Compose installé: $(docker compose version)${NC}"
echo ""

# Check .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ Fichier .env non trouvé${NC}"
    echo -e "Création de .env depuis .env.docker..."
    cp .env.docker .env
    
    # Generate SECRET_KEY
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/your-secret-key-generate-with-openssl-rand-hex-32/$SECRET_KEY/" .env
    
    echo -e "${GREEN}✓ Fichier .env créé${NC}"
    echo -e "${YELLOW}⚠ Modifiez le fichier .env avec vos paramètres${NC}"
    echo ""
    
    read -p "Voulez-vous éditer .env maintenant? (y/N): " edit_env
    if [[ "$edit_env" =~ ^[Yy]$ ]]; then
        ${EDITOR:-nano} .env
    fi
fi

# Build and start
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Démarrage des conteneurs Docker...  ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

docker compose up -d --build

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Attente du démarrage des services... ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Wait for services
echo -n "MySQL: "
for i in {1..30}; do
    if docker exec ayhr-mysql mysqladmin ping -h localhost --silent &> /dev/null; then
        echo -e "${GREEN}✓ Prêt${NC}"
        break
    fi
    sleep 2
    echo -n "."
done

echo -n "Backend: "
for i in {1..30}; do
    if curl -f http://localhost:8000 &> /dev/null; then
        echo -e "${GREEN}✓ Prêt${NC}"
        break
    fi
    sleep 2
    echo -n "."
done

echo -n "Frontend: "
for i in {1..10}; do
    if curl -f http://localhost &> /dev/null; then
        echo -e "${GREEN}✓ Prêt${NC}"
        break
    fi
    sleep 1
    echo -n "."
done

echo ""
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}    ✓ Installation terminée !          ${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📊 Statut des conteneurs:${NC}"
docker compose ps
echo ""
echo -e "${BLUE}🌐 URLs d'accès:${NC}"
echo -e "  • Frontend:   ${GREEN}http://localhost${NC}"
echo -e "  • Backend:    ${GREEN}http://localhost:8000${NC}"
echo -e "  • API Docs:   ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "${BLUE}🔐 Credentials par défaut:${NC}"
echo -e "  • Email:      ${YELLOW}admin@ay-hr.com${NC}"
echo -e "  • Password:   ${YELLOW}Admin@2024!${NC}"
echo ""
echo -e "${BLUE}📝 Commandes utiles:${NC}"
echo -e "  • Voir les logs:    ${YELLOW}docker compose logs -f${NC}"
echo -e "  • Arrêter:          ${YELLOW}docker compose down${NC}"
echo -e "  • Redémarrer:       ${YELLOW}docker compose restart${NC}"
echo -e "  • Shell backend:    ${YELLOW}docker exec -it ayhr-backend bash${NC}"
echo -e "  • MySQL console:    ${YELLOW}docker exec -it ayhr-mysql mysql -u root -p${NC}"
echo ""
echo -e "${GREEN}✓ Accédez à l'application: ${BLUE}http://localhost${NC}"
echo ""
