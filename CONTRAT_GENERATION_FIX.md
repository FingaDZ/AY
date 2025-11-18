# Fix: Erreur 500 lors de la Génération de Contrat

## Problème Rencontré

Lors du clic sur le bouton de génération de contrat, l'erreur suivante apparaissait dans la console :

```
GET http://192.168.20.53:3000/api/employes/29/contrat-travail 500 (Internal Server Error)
AxiosError: Request failed with status code 500
```

## Causes Identifiées

### 1. Packages Python Manquants (Erreur Principale)

**Log Backend:**
```
ModuleNotFoundError: No module named 'PyPDF2'
```

**Cause:** Les packages nécessaires pour la génération de contrats n'étaient pas installés dans l'environnement virtuel du serveur.

**Packages Requis:**
- `PyPDF2==3.0.1` - Manipulation de fichiers PDF
- `arabic-reshaper==3.0.0` - Reshaping du texte arabe
- `python-bidi==0.4.2` - Support du texte bidirectionnel (RTL)

### 2. Template PDF Manquant

**Fichier Manquant:** `/opt/ay-hr/backend/files/contrat Arabe.pdf`

Le template de contrat arabe n'avait pas été copié sur le serveur lors du déploiement initial.

## Solution Appliquée

### Étape 1: Installation des Packages Python

```bash
ssh root@192.168.20.53
cd /opt/ay-hr/backend
source .venv/bin/activate
pip install PyPDF2==3.0.1 arabic-reshaper==3.0.0 python-bidi==0.4.2
```

**Résultat:**
```
Successfully installed PyPDF2-3.0.1 arabic-reshaper-3.0.0 python-bidi-0.4.2
```

### Étape 2: Création du Répertoire Files

```bash
ssh root@192.168.20.53
mkdir -p /opt/ay-hr/backend/files
```

### Étape 3: Copie du Template PDF

```bash
scp "F:\Code\AY HR\files\contrat Arabe.pdf" root@192.168.20.53:/opt/ay-hr/backend/files/
```

**Résultat:**
- Fichier copié: 487 KB (486 KB)
- Emplacement: `/opt/ay-hr/backend/files/contrat Arabe.pdf`

### Étape 4: Redémarrage du Backend

```bash
ssh root@192.168.20.53
systemctl restart ayhr-backend
systemctl status ayhr-backend
```

**Résultat:**
- Service: ✅ Active (running)
- PID: 30254
- Status: Application startup complete

## Vérification Post-Fix

### Backend Logs
```bash
journalctl -u ayhr-backend -f
```

Aucune erreur détectée après le redémarrage.

### Structure des Fichiers

```
/opt/ay-hr/backend/
├── .venv/
│   └── lib/python3.11/site-packages/
│       ├── PyPDF2/           ✅ Installé
│       ├── arabic_reshaper/  ✅ Installé
│       └── bidi/             ✅ Installé (python-bidi)
└── files/
    └── contrat Arabe.pdf     ✅ 487 KB
```

## Test de la Fonctionnalité

### Étapes de Test

1. Accéder à `http://192.168.20.53:3000`
2. Naviguer vers la page **Employés**
3. Cliquer sur le bouton violet 🛡️ (contrat) d'un employé
4. Vérifier que le PDF se télécharge correctement

### Comportement Attendu

- ✅ Aucune erreur 500
- ✅ Téléchargement automatique du PDF
- ✅ Nom du fichier: `contrat_travail_{nom}_{prenom}_{date}.pdf`
- ✅ Contenu: Template arabe avec données superposées

### Comportement de Fallback

Si le template est absent ou corrompu, le système génère automatiquement un contrat complet avec ReportLab (méthode `_generate_simple_contrat()`).

## Procédure de Déploiement Complète (pour référence future)

### 1. Déploiement du Code

```bash
# Backend
scp backend/services/pdf_generator.py root@192.168.20.53:/opt/ay-hr/backend/services/
scp backend/routers/employes.py root@192.168.20.53:/opt/ay-hr/backend/routers/

# Frontend
scp frontend/src/services/index.js root@192.168.20.53:/opt/ay-hr/frontend/src/services/
scp frontend/src/pages/Employes/EmployesList.jsx root@192.168.20.53:/opt/ay-hr/frontend/src/pages/Employes/
```

### 2. Installation des Dépendances

```bash
ssh root@192.168.20.53
cd /opt/ay-hr/backend
source .venv/bin/activate
pip install PyPDF2==3.0.1 arabic-reshaper==3.0.0 python-bidi==0.4.2
deactivate
```

### 3. Copie des Fichiers de Ressources

```bash
# Créer le répertoire si nécessaire
ssh root@192.168.20.53 'mkdir -p /opt/ay-hr/backend/files'

# Copier le template
scp "files/contrat Arabe.pdf" root@192.168.20.53:/opt/ay-hr/backend/files/
```

### 4. Redémarrage des Services

```bash
ssh root@192.168.20.53
systemctl restart ayhr-backend
systemctl status ayhr-backend --no-pager

# Frontend (si nécessaire)
systemctl restart ayhr-frontend
```

### 5. Vérification

```bash
# Vérifier les packages
ssh root@192.168.20.53 'cd /opt/ay-hr/backend && source .venv/bin/activate && pip list | grep -E "PyPDF2|arabic|bidi"'

# Vérifier les fichiers
ssh root@192.168.20.53 'ls -lh /opt/ay-hr/backend/files/'

# Vérifier les logs
ssh root@192.168.20.53 'journalctl -u ayhr-backend -n 20 --no-pager'
```

## Mise à Jour de requirements.txt

Pour éviter ce problème à l'avenir, ajouter dans `backend/requirements.txt` :

```txt
PyPDF2==3.0.1
arabic-reshaper==3.0.0
python-bidi==0.4.2
```

Ensuite, l'installation devient simplement :

```bash
cd /opt/ay-hr/backend
source .venv/bin/activate
pip install -r requirements.txt
```

## Checklist de Déploiement des Nouvelles Fonctionnalités

- [ ] Copier les fichiers de code source (backend + frontend)
- [ ] Installer les nouvelles dépendances Python (`pip install`)
- [ ] Copier les fichiers de ressources (templates, images, etc.)
- [ ] Mettre à jour `requirements.txt` si applicable
- [ ] Redémarrer les services (backend + frontend si nécessaire)
- [ ] Vérifier les logs pour les erreurs
- [ ] Tester la fonctionnalité via l'interface web

## Résumé des Commandes Exécutées

```bash
# 1. Installation des packages
ssh root@192.168.20.53 'cd /opt/ay-hr/backend && source .venv/bin/activate && pip install PyPDF2==3.0.1 arabic-reshaper==3.0.0 python-bidi==0.4.2'

# 2. Création du répertoire
ssh root@192.168.20.53 'mkdir -p /opt/ay-hr/backend/files'

# 3. Copie du template
scp "F:\Code\AY HR\files\contrat Arabe.pdf" root@192.168.20.53:/opt/ay-hr/backend/files/

# 4. Redémarrage
ssh root@192.168.20.53 'systemctl restart ayhr-backend'

# 5. Vérification
ssh root@192.168.20.53 'systemctl status ayhr-backend --no-pager'
ssh root@192.168.20.53 'ls -lh /opt/ay-hr/backend/files/'
```

## Status Final

✅ **Problème Résolu**

- Backend: Active et fonctionnel (PID 30254)
- Packages: PyPDF2, arabic-reshaper, python-bidi installés
- Template: Présent dans `/opt/ay-hr/backend/files/contrat Arabe.pdf`
- Logs: Aucune erreur détectée
- Fonctionnalité: Prête à être testée

---

**Date de Fix:** 18 Novembre 2025, 07:58 UTC  
**Serveur:** 192.168.20.53 (AIRBAND-HR)  
**Backend PID:** 30254
