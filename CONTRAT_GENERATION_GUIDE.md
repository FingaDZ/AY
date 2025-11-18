# Guide de Génération des Contrats de Travail

## Vue d'ensemble

Le système AY HR permet maintenant de générer automatiquement des contrats de travail pour les employés en utilisant le modèle de contrat arabe comme base.

## Fonctionnalité

### Bouton de Génération
- **Emplacement** : Liste des employés (page Employés)
- **Icône** : 🛡️ (FileProtectOutlined - violet)
- **Disponible pour** : Tous les employés (actifs et inactifs)
- **Tooltip** : "Générer contrat de travail"

### Données Incluses dans le Contrat

#### Informations de l'Entreprise (depuis `parametres_entreprise`)
- Raison sociale
- Adresse complète
- RC (Registre de Commerce)
- NIF (Numéro d'Identification Fiscale)
- NIS (Numéro d'Identification Statistique)

#### Informations de l'Employé (depuis `employes`)
- Nom et prénom complets
- Date de naissance (format: DD/MM/YYYY)
- Lieu de naissance
- Adresse personnelle
- Numéro de téléphone mobile
- Numéro de Sécurité Sociale
- Numéro de compte bancaire
- Situation familiale
- Poste de travail
- Date de recrutement
- Durée du contrat (si CDD)
- Date de fin de contrat (si applicable)
- Salaire de base (en DA)

## Fonctionnement Technique

### Backend

#### 1. Méthode PDF Generator
**Fichier** : `backend/services/pdf_generator.py`

```python
def generate_contrat_travail(self, employe_data: Dict) -> BytesIO
```

**Logique** :
1. **Avec Template** (si `files/contrat Arabe.pdf` existe) :
   - Charge le PDF template arabe avec PyPDF2
   - Crée une overlay avec les données via ReportLab Canvas
   - Fusionne l'overlay avec le template
   - Support du texte arabe via `arabic-reshaper` et `python-bidi`
   
2. **Sans Template** (fallback) :
   - Génère un contrat complet avec ReportLab
   - Mise en page professionnelle avec :
     - En-tête entreprise (raison sociale, RC, NIF, NIS)
     - Titre "CONTRAT DE TRAVAIL"
     - Articles du contrat (engagement, date, rémunération, etc.)
     - Section signatures (employeur + salarié)
   - Location : Chelghoum Laid

#### 2. Endpoint API
**Route** : `GET /api/employes/{employe_id}/contrat-travail`
**Fichier** : `backend/routers/employes.py`

**Paramètres** :
- `employe_id` : ID de l'employé
- Authentification : Token JWT requis

**Réponse** :
- Type : `application/pdf`
- Nom de fichier : `contrat_travail_{nom}_{prenom}_{date}.pdf`
- Exemple : `contrat_travail_BENALI_Ahmed_18112025.pdf`

### Frontend

#### 1. Service API
**Fichier** : `frontend/src/services/index.js`

```javascript
generateContrat: (id) => api.get(`/employes/${id}/contrat-travail`, { 
  responseType: 'blob' 
})
```

#### 2. Handler dans EmployesList
**Fichier** : `frontend/src/pages/Employes/EmployesList.jsx`

```javascript
const handleGenerateContrat = async (employe) => {
  // 1. Appel API avec responseType: 'blob'
  // 2. Création d'un Blob URL
  // 3. Déclenchement du téléchargement automatique
  // 4. Nettoyage des ressources
  // 5. Message de succès
}
```

#### 3. Bouton dans Actions
- **Actifs** : Attestation + **Contrat** + Supprimer
- **Inactifs** : Certificat + **Contrat** + Réactiver

## Dépendances Python

Les packages suivants ont été installés pour supporter la génération de contrats :

```bash
PyPDF2==3.0.1           # Manipulation de PDF (lecture/écriture)
reportlab==4.0.7        # Génération de PDF (déjà installé)
arabic-reshaper==3.0.0  # Reshaping du texte arabe (connexions de lettres)
python-bidi==0.4.2      # Support du texte bidirectionnel (RTL)
```

## Installation sur le Serveur

```bash
# 1. Copier les fichiers modifiés
scp backend/services/pdf_generator.py root@192.168.20.53:/opt/ay-hr/backend/services/
scp backend/routers/employes.py root@192.168.20.53:/opt/ay-hr/backend/routers/
scp frontend/src/services/index.js root@192.168.20.53:/opt/ay-hr/frontend/src/services/
scp frontend/src/pages/Employes/EmployesList.jsx root@192.168.20.53:/opt/ay-hr/frontend/src/pages/Employes/

# 2. Installer les packages Python (si nécessaire)
ssh root@192.168.20.53
cd /opt/ay-hr/backend
source .venv/bin/activate
pip install PyPDF2==3.0.1 arabic-reshaper==3.0.0 python-bidi==0.4.2

# 3. Redémarrer le backend
systemctl restart ayhr-backend

# 4. Vérifier le statut
systemctl status ayhr-backend --no-pager

# 5. Frontend (Vite HMR détectera automatiquement les changements)
# Si nécessaire, redémarrer :
systemctl restart ayhr-frontend
```

## Utilisation

### Via l'Interface Web

1. Accéder à la page **Employés**
2. Localiser l'employé dans la liste
3. Cliquer sur le bouton violet 🛡️ (icône contrat)
4. Le PDF se télécharge automatiquement

### Nom du Fichier Généré
Format : `contrat_travail_{NOM}_{PRENOM}_{DDMMYYYY}.pdf`

Exemples :
- `contrat_travail_BENALI_Ahmed_18112025.pdf`
- `contrat_travail_KHELIFI_Fatima_18112025.pdf`

## Template de Contrat

### Emplacement
`files/contrat Arabe.pdf`

### Personnalisation du Template
Pour modifier le template :
1. Ouvrir `files/contrat Arabe.pdf` avec un éditeur PDF
2. Modifier le texte arabe et la mise en page
3. Sauvegarder le fichier
4. Les positions d'overlay dans le code doivent être ajustées en conséquence

### Positions d'Overlay (à ajuster selon votre template)
Dans `pdf_generator.py`, ligne ~2095+ :

```python
# En-tête entreprise : y_position = height - 100
# Date du contrat : (400, height - 200)
# Nom complet : (200, height - 300)
# Date de naissance : (200, height - 330)
# Lieu de naissance : (200, height - 350)
# Adresse : (200, height - 380)
# N° SS : (200, height - 410)
# Poste : (200, height - 450)
# Date de début : (200, height - 480)
# Durée : (200, height - 510)
# Salaire : (200, height - 550)
```

**Note** : Coordonnées en points (72 points = 1 pouce), origine en bas à gauche.

## Gestion des Erreurs

### Erreurs Possibles

1. **Template non trouvé**
   - Le système génère automatiquement un contrat simple
   - Message dans les logs : "Erreur lors de la génération du contrat"
   - Solution : Vérifier que `files/contrat Arabe.pdf` existe

2. **Employé non trouvé**
   - HTTP 404
   - Message : "Employé non trouvé"

3. **Problème de génération PDF**
   - Le système utilise le fallback `_generate_simple_contrat()`
   - Génère un contrat professionnel sans utiliser le template

4. **Erreur de téléchargement Frontend**
   - Message : "Erreur lors de la génération du contrat"
   - Vérifier la console du navigateur
   - Vérifier que l'API est accessible

## Support du Texte Arabe

### Arabic Reshaper
Transforme le texte arabe pour la connexion correcte des lettres :
```python
reshaped_text = arabic_reshaper.reshape("مثال")
```

### Python BiDi
Gère l'affichage right-to-left (RTL) :
```python
display_text = get_display(reshaped_text)
```

### Exemple d'Utilisation
```python
def format_arabic(text):
    if text:
        reshaped_text = arabic_reshaper.reshape(str(text))
        return get_display(reshaped_text)
    return ""
```

## Maintenance

### Vérifier la Génération
```bash
# Logs backend
ssh root@192.168.20.53
journalctl -u ayhr-backend -f

# Tester l'endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://192.168.20.53:8000/api/employes/1/contrat-travail \
  -o test_contrat.pdf
```

### Mise à Jour du Template
1. Sauvegarder l'ancien : `cp files/contrat\ Arabe.pdf files/contrat\ Arabe.pdf.backup`
2. Copier le nouveau template
3. Ajuster les positions d'overlay si nécessaire
4. Tester avec plusieurs employés

## Commit Git
```
commit f2149d3
Author: [Your Name]
Date: Mon Nov 18 2025

Add contract generation feature for employees
- Added generate_contrat_travail() method to PDFGenerator class
- Method overlays employee/company data on Arabic contract template
- Falls back to programmatically generated contract if template missing
- Added /api/employes/{id}/contrat-travail endpoint
- Added generateContrat() service method in frontend
- Added contract generation button (FileProtectOutlined icon) for all employees
- Installed PyPDF2, arabic-reshaper, python-bidi for Arabic PDF support
```

## Références

- **ReportLab Documentation** : https://www.reportlab.com/docs/reportlab-userguide.pdf
- **PyPDF2 Documentation** : https://pypdf2.readthedocs.io/
- **Arabic Reshaper** : https://github.com/mpcabd/python-arabic-reshaper
- **Python BiDi** : https://github.com/MeirKriheli/python-bidi

## Support

Pour toute question ou problème :
1. Vérifier les logs du backend : `journalctl -u ayhr-backend -n 50`
2. Vérifier l'état du service : `systemctl status ayhr-backend`
3. Tester l'endpoint directement avec curl/Postman
4. Vérifier que le template PDF existe dans `files/contrat Arabe.pdf`
