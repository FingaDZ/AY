#!/bin/bash
# ============================================================================
# Script de Démarrage - AY HR Management
# Pour Linux
# ============================================================================

echo ""
echo "========================================"
echo " Démarrage AIRBAND HR"
echo "========================================"
echo ""

# Vérifier si les services systemd sont installés
if systemctl list-unit-files | grep -q "ayhr-backend.service"; then
    echo "Services systemd détectés"
    echo ""
    echo -n "  → Démarrage du service Backend... "
    sudo systemctl start ayhr-backend
    echo "OK"
    
    echo -n "  → Démarrage du service Frontend... "
    sudo systemctl start ayhr-frontend
    echo "OK"
else
    echo "Démarrage manuel"
    echo ""
    
    # Créer le dossier logs si nécessaire
    mkdir -p logs
    
    # Vérifier si déjà en cours
    if [ -f "logs/backend.pid" ]; then
        BACKEND_PID=$(cat logs/backend.pid)
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            echo "  ⚠️  Backend déjà en cours (PID: $BACKEND_PID)"
        else
            rm logs/backend.pid
        fi
    fi
    
    if [ -f "logs/frontend.pid" ]; then
        FRONTEND_PID=$(cat logs/frontend.pid)
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            echo "  ⚠️  Frontend déjà en cours (PID: $FRONTEND_PID)"
        else
            rm logs/frontend.pid
        fi
    fi
    
    # Démarrer le backend
    if [ ! -f "logs/backend.pid" ]; then
        echo -n "  → Démarrage du Backend... "
        cd backend
        source .venv/bin/activate
        nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
        BACKEND_PID=$!
        echo $BACKEND_PID > ../logs/backend.pid
        deactivate
        cd ..
        echo "OK (PID: $BACKEND_PID)"
        sleep 2
    fi
    
    # Démarrer le frontend
    if [ ! -f "logs/frontend.pid" ]; then
        echo -n "  → Démarrage du Frontend... "
        cd frontend
        nohup npm run dev > ../logs/frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > ../logs/frontend.pid
        cd ..
        echo "OK (PID: $FRONTEND_PID)"
        sleep 2
    fi
fi

echo ""
echo "========================================"
echo " Application Démarrée!"
echo "========================================"
echo ""
echo "Accès à l'application:"
echo "  Interface Web    : http://localhost:3000"
echo "  API Backend      : http://localhost:8000"
echo "  Documentation API: http://localhost:8000/docs"
echo ""
echo "Pour arrêter l'application:"
echo "  ./stop-linux.sh"
echo ""
echo "Pour voir les logs:"
echo "  tail -f logs/backend.log"
echo "  tail -f logs/frontend.log"
echo ""
