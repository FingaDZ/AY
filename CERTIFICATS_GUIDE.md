# Guide - Génération des Certificats de Travail

## Vue d'ensemble

Le système génère maintenant deux types de documents officiels pour les employés :

1. **Attestation de Travail** - Pour les employés actuellement en poste
2. **Certificat de Travail** - Pour les employés ayant quitté l'entreprise

## Attestation de Travail

### Objectif
Document certifiant qu'un employé travaille **actuellement** dans l'entreprise.

### Conditions d'utilisation
- L'employé doit être **actif** (`actif = true`)
- Utilisé pour prouver l'emploi actuel (banques, administrations, etc.)

### Contenu du document
- En-tête avec informations entreprise (Raison Sociale, RC, NIF, Adresse)
- Identité complète de l'employé (nom, prénom, date/lieu naissance, adresse, n° SS)
- Date de recrutement
- **Calcul automatique de l'ancienneté** (années et mois depuis le recrutement)
- Poste occupé actuellement
- Date de génération
- Section signature et cachet

### Utilisation API
```bash
GET /api/employes/{employe_id}/attestation-travail
```

**Exemple de requête :**
```bash
curl -X GET "http://192.168.20.53:8000/api/employes/5/attestation-travail" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output attestation.pdf
```

**Réponse :**
- Statut 200 : PDF téléchargé
- Statut 400 : Employé inactif (utiliser certificat à la place)
- Statut 404 : Employé non trouvé

## Certificat de Travail

### Objectif
Document certifiant qu'un employé **a travaillé** dans l'entreprise (passé).

### Conditions d'utilisation
- L'employé doit avoir une `date_fin_contrat` **OU** être inactif (`actif = false`)
- Utilisé lors du départ d'un employé
- Mentionne "libre de tout engagement"

### Contenu du document
- En-tête avec informations entreprise (Raison Sociale, RC, NIF, Adresse)
- Identité complète de l'employé (nom, prénom, date/lieu naissance, adresse, n° SS)
- Période d'emploi (date début → date fin)
- **Calcul automatique de la durée totale** (années et mois)
- Poste occupé durant cette période
- Mention : "Il/Elle quitte l'entreprise libre de tout engagement"
- Date de génération
- Section signature et cachet

### Utilisation API
```bash
GET /api/employes/{employe_id}/certificat-travail
```

**Exemple de requête :**
```bash
curl -X GET "http://192.168.20.53:8000/api/employes/12/certificat-travail" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output certificat.pdf
```

**Réponse :**
- Statut 200 : PDF téléchargé
- Statut 400 : Employé actif sans date_fin_contrat (utiliser attestation)
- Statut 404 : Employé non trouvé

## Différences Principales

| Critère | Attestation | Certificat |
|---------|-------------|------------|
| **Pour qui** | Employés actifs | Employés partis |
| **Temps** | Présent | Passé |
| **Calcul** | Ancienneté actuelle | Durée totale emploi |
| **Période** | "Depuis le..." | "Du ... au ..." |
| **Phrase clé** | "Est employé(e)" | "A été employé(e)" |
| **Engagement** | Non mentionné | "Libre de tout engagement" |

## Format des Fichiers Générés

**Attestation :**
```
attestation_travail_NOM_PRENOM_DDMMYYYY.pdf
```

**Certificat :**
```
certificat_travail_NOM_PRENOM_DDMMYYYY.pdf
```

## Intégration Frontend (À faire)

Pour intégrer ces fonctionnalités au frontend :

### 1. Dans la liste des employés (`EmployesList.jsx`)

Ajouter des boutons conditionnels :

```jsx
// Pour chaque employé dans la table
{
  title: 'Actions',
  key: 'actions',
  render: (text, record) => (
    <Space>
      <Button onClick={() => navigate(`/employes/edit/${record.id}`)}>
        Modifier
      </Button>
      
      {/* Attestation pour employés actifs */}
      {record.actif && (
        <Button 
          type="primary"
          icon={<FileTextOutlined />}
          onClick={() => handleGenerateAttestation(record.id)}
        >
          Attestation
        </Button>
      )}
      
      {/* Certificat pour employés inactifs ou avec date_fin */}
      {(!record.actif || record.date_fin_contrat) && (
        <Button 
          type="default"
          icon={<FilePdfOutlined />}
          onClick={() => handleGenerateCertificat(record.id)}
        >
          Certificat
        </Button>
      )}
    </Space>
  )
}
```

### 2. Fonctions de génération

```javascript
const handleGenerateAttestation = async (employeId) => {
  try {
    const response = await fetch(
      `http://192.168.20.53:8000/api/employes/${employeId}/attestation-travail`,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      }
    );
    
    if (!response.ok) {
      const error = await response.json();
      message.error(error.detail);
      return;
    }
    
    // Télécharger le PDF
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `attestation_travail_${employeId}.pdf`;
    a.click();
    
    message.success('Attestation générée avec succès');
  } catch (error) {
    message.error('Erreur lors de la génération de l\'attestation');
  }
};

const handleGenerateCertificat = async (employeId) => {
  // Même structure que handleGenerateAttestation
  // Remplacer 'attestation-travail' par 'certificat-travail'
};
```

### 3. Service API (recommandé)

Créer ou mettre à jour `frontend/src/services/employes.js` :

```javascript
export const generateAttestation = async (employeId) => {
  const response = await api.get(
    `/employes/${employeId}/attestation-travail`,
    { responseType: 'blob' }
  );
  return response.data;
};

export const generateCertificat = async (employeId) => {
  const response = await api.get(
    `/employes/${employeId}/certificat-travail`,
    { responseType: 'blob' }
  );
  return response.data;
};
```

## Logging

Toutes les générations sont automatiquement loggées dans la table `logs` :

- **Action Type** : `EXPORT`
- **Table** : `Employes`
- **Description** : "Génération attestation/certificat de travail pour [Prénom Nom]"
- **Utilisateur** : ID de l'utilisateur authentifié
- **Timestamp** : Date et heure de génération

## Données Entreprise

Les documents utilisent les paramètres de la table `parametres_entreprise` :

- Raison Sociale (ou Nom Entreprise si null)
- RC (Registre de Commerce)
- NIF (Numéro d'Identification Fiscale)
- Adresse (avec gestion automatique des lignes longues)

**Important :** S'assurer que ces paramètres sont correctement renseignés dans la base de données.

## Test Local

Pour tester depuis votre machine locale :

```bash
# Démarrer le backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Tester l'endpoint attestation
curl -X GET "http://localhost:8000/api/employes/1/attestation-travail" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output test_attestation.pdf

# Tester l'endpoint certificat
curl -X GET "http://localhost:8000/api/employes/2/certificat-travail" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output test_certificat.pdf
```

## Déploiement sur Serveur

### 1. Copier les fichiers modifiés

```bash
# Depuis votre machine locale
scp backend/services/pdf_generator.py user@192.168.20.53:/var/www/ayhr/backend/services/
scp backend/routers/employes.py user@192.168.20.53:/var/www/ayhr/backend/routers/
```

### 2. Redémarrer le service backend

```bash
ssh user@192.168.20.53
sudo systemctl restart ayhr-backend
sudo systemctl status ayhr-backend
```

### 3. Vérifier les logs

```bash
sudo journalctl -u ayhr-backend -f
```

### 4. Tester depuis le serveur

```bash
curl -X GET "http://localhost:8000/api/employes/1/attestation-travail" \
  -H "Authorization: Bearer TOKEN" \
  --output test.pdf
```

## Troubleshooting

### Erreur 400 : "Impossible de générer une attestation pour un employé inactif"

**Cause :** L'employé a `actif = false`

**Solution :** Utiliser l'endpoint certificat à la place (`/certificat-travail`)

### Erreur 400 : "Impossible de générer un certificat pour un employé actif"

**Cause :** L'employé est actif et n'a pas de `date_fin_contrat`

**Solution :** 
1. Si l'employé est parti : Définir `date_fin_contrat` et/ou `actif = false`
2. Si l'employé est toujours là : Utiliser attestation (`/attestation-travail`)

### Erreur 404 : "Employé non trouvé"

**Cause :** L'ID employé n'existe pas dans la base

**Solution :** Vérifier l'ID avec `SELECT * FROM employes WHERE id = X;`

### Le PDF affiche "Entreprise" ou "N/A"

**Cause :** Paramètres entreprise non configurés

**Solution :**
```sql
SELECT * FROM parametres_entreprise;
-- Vérifier que raison_sociale, rc, nif, adresse sont renseignés
UPDATE parametres_entreprise 
SET raison_sociale = 'Votre Entreprise',
    rc = 'XX/XXXXXXX',
    nif = 'XXXXXXXXXX',
    adresse = 'Votre adresse complète'
WHERE id = 1;
```

### Ancienneté/Durée incorrecte

**Cause :** Données `date_recrutement` ou `date_fin_contrat` manquantes/incorrectes

**Solution :**
```sql
SELECT id, nom, prenom, date_recrutement, date_fin_contrat 
FROM employes 
WHERE id = X;
-- Corriger si nécessaire
```

## Notes Légales

Ces documents sont des **modèles génériques**. Vérifier qu'ils sont conformes :

- À la législation du travail locale
- Aux conventions collectives applicables
- Aux pratiques de l'entreprise

Adapter le contenu si nécessaire en modifiant les méthodes dans `pdf_generator.py`.
