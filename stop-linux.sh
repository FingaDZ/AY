#!/bin/bash
# ============================================================================
# Script d'Arrêt - AY HR Management
# Pour Linux
# ============================================================================

echo ""
echo "========================================"
echo " Arrêt AIRBAND HR"
echo "========================================"
echo ""

# Vérifier si les services systemd sont installés
if systemctl list-unit-files | grep -q "ayhr-backend.service"; then
    echo -n "  → Arrêt du service Backend... "
    sudo systemctl stop ayhr-backend
    echo "OK"
    
    echo -n "  → Arrêt du service Frontend... "
    sudo systemctl stop ayhr-frontend
    echo "OK"
else
    # Arrêter le backend
    if [ -f "logs/backend.pid" ]; then
        BACKEND_PID=$(cat logs/backend.pid)
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            echo -n "  → Arrêt du Backend (PID: $BACKEND_PID)... "
            kill $BACKEND_PID 2>/dev/null
            echo "OK"
        fi
        rm logs/backend.pid
    fi
    
    # Arrêter le frontend
    if [ -f "logs/frontend.pid" ]; then
        FRONTEND_PID=$(cat logs/frontend.pid)
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            echo -n "  → Arrêt du Frontend (PID: $FRONTEND_PID)... "
            kill $FRONTEND_PID 2>/dev/null
            echo "OK"
        fi
        rm logs/frontend.pid
    fi
    
    if [ ! -f "logs/backend.pid" ] && [ ! -f "logs/frontend.pid" ]; then
        echo "  Aucun processus en cours d'exécution"
    fi
fi

echo ""
echo "Application arrêtée"
echo ""
