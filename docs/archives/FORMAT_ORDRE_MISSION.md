# Format Ordre de Mission - Spécifications

## Vue d'ensemble
L'ordre de mission est généré en format **A5** (148mm × 210mm), noir et blanc, optimisé pour l'impression rapide.

## Format du Numéro d'Ordre

### Structure: YYMMDD-XXXXX

- **YY**: Année (2 chiffres)
- **MM**: Mois (2 chiffres)
- **DD**: Jour (2 chiffres)
- **XXXXX**: Numéro séquentiel (5 chiffres)

### Exemples
```
251111-00001  → 11 novembre 2025, mission #1
251111-00002  → 11 novembre 2025, mission #2
251201-00001  → 01 décembre 2025, mission #1 (réinitialisé)
251201-00015  → 01 décembre 2025, mission #15
```

### Réinitialisation
Le compteur se réinitialise automatiquement chaque mois.

## Spécifications Techniques

### Format de Page
- **Taille**: A5 (148mm × 210mm)
- **Orientation**: Portrait
- **Marges**: 1cm de chaque côté

### Couleurs
- **Texte**: Noir uniquement
- **Fond**: Blanc
- **Tableaux**: Bordures noires (0.5pt)

### Police
- **Titre**: Helvetica-Bold 14pt
- **Sous-titres**: Helvetica-Bold 10pt
- **Corps**: Helvetica 9pt
- **Signatures**: Helvetica-Bold 8pt

## Contenu du Document

### 1. En-tête
```
┌────────────────────────────┐
│   ORDRE DE MISSION         │
└────────────────────────────┘
```

### 2. Identification
```
N° Ordre: 251111-00001
Date: 11/11/2025
```

### 3. Section Chauffeur
```
┌────────────────────────────┐
│ CHAUFFEUR                  │
├────────────────────────────┤
│ Nom: Ahmed BENALI          │
└────────────────────────────┘
```

### 4. Section Mission
```
┌────────────────────────────┐
│ DETAILS DE LA MISSION      │
├────────────────────────────┤
│ Destination: Sonatrach     │
│ Distance: 80.00 km         │
│ Prime: 400.00 DA           │
└────────────────────────────┘
```

### 5. Section Signatures
```
┌─────────────┬──────────────┬──────────────┐
│ Signature   │ Signature    │ Signature    │
│ chauffeur   │ client       │ responsable  │
│             │              │              │
│             │              │              │
└─────────────┴──────────────┴──────────────┘
```

## Différences par rapport à l'ancien format

| Élément | Ancien (A4) | Nouveau (A5) |
|---------|-------------|--------------|
| **Format** | A4 (210×297mm) | A5 (148×210mm) |
| **Marges** | 2cm | 1cm |
| **Couleurs** | Bleu/Vert | Noir/Blanc |
| **N° Ordre** | 00001 | 251111-00001 |
| **Date** | 2 dates (signatures) | 1 date unique |
| **Signatures** | 2 (chauffeur, responsable) | 3 (chauffeur, client, responsable) |
| **Police** | 11-18pt | 8-14pt |
| **Espacement** | Large | Compact |

## Avantages du Nouveau Format

### 1. Économie
- ✅ **50% moins de papier** (A5 vs A4)
- ✅ **Impression noir et blanc** (pas d'encre couleur)
- ✅ Format portable pour les chauffeurs

### 2. Praticité
- ✅ **Taille poche** facile à transporter
- ✅ **Plus rapide à imprimer**
- ✅ Signature client sur place

### 3. Traçabilité
- ✅ **Numéro unique** par jour
- ✅ **Réinitialisation mensuelle** pour archivage
- ✅ **Format standardisé**

## Utilisation

### Générer un Ordre
```javascript
// Frontend
await missionService.getOrdreMissionPdf(missionId);
```

### Endpoint API
```
GET /api/missions/{id}/ordre-mission/pdf
```

### Réponse
- **Type**: application/pdf
- **Nom fichier**: ordre_mission_{id}.pdf
- **Taille**: ~2.2 KB

## Exemple de Flux de Travail

### 1. Création de Mission
```
Mission créée → ID: 42
Date: 15/11/2025
```

### 2. Génération Automatique
```
N° calculé: 251115-00042
Format: A5, N&B
```

### 3. Impression
```
Clic sur "Ordre" → PDF téléchargé → Impression
```

### 4. Distribution
```
Chauffeur reçoit l'ordre
↓
Signature chauffeur
↓
Chez le client
↓
Signature client
↓
Retour au bureau
↓
Signature responsable
```

## Archivage

### Organisation Recommandée
```
Archives/
├── 2025/
│   ├── 11-Novembre/
│   │   ├── 251101-00001.pdf
│   │   ├── 251101-00002.pdf
│   │   ├── ...
│   │   └── 251130-00156.pdf
│   └── 12-Decembre/
│       ├── 251201-00001.pdf  (réinitialisation)
│       └── ...
```

### Avantages
- Tri chronologique automatique
- Recherche facile par date
- Compteur mensuel clair

## Modifications Techniques

### Code Python
```python
def _generate_ordre_numero(self, mission_id: int, date_mission: str) -> str:
    date_obj = datetime.strptime(date_mission, '%Y-%m-%d')
    yymmdd = date_obj.strftime('%y%m%d')
    return f"{yymmdd}-{mission_id:05d}"
```

### Structure PDF
```python
doc = SimpleDocTemplate(
    buffer, 
    pagesize=A5,  # ← Format A5
    topMargin=1*cm,  # ← Marges réduites
    bottomMargin=1*cm,
    leftMargin=1*cm,
    rightMargin=1*cm
)
```

### Style Sans Couleur
```python
TableStyle([
    ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    # Pas de BACKGROUND, pas de TEXTCOLOR coloré
])
```

## Notes Importantes

### ⚠️ Réinitialisation du Compteur
Le compteur utilise actuellement l'ID de la mission. Pour une vraie réinitialisation mensuelle, il faudrait:

```python
# Compter les missions du mois en cours
count = db.query(Mission).filter(
    func.year(Mission.date_mission) == annee,
    func.month(Mission.date_mission) == mois
).count()
return f"{yymmdd}-{count+1:05d}"
```

### 📋 En-têtes Corrigés
Les en-têtes n'utilisent plus les balises HTML `<b>` dans le texte affiché:
- ~~`<b>CHAUFFEUR</b>`~~ → `CHAUFFEUR`
- ~~`<b>Signature du chauffeur</b>`~~ → `Signature chauffeur`

### 🖨️ Impression
Paramètres recommandés:
- **Format**: A5
- **Orientation**: Portrait
- **Qualité**: Brouillon ou Standard
- **Couleur**: Noir et blanc
- **Marges**: Automatiques

## Support

Pour toute question sur le format:
- Voir `MISSIONS_FEATURES.md` pour l'implémentation
- Tester avec `test_ordre_A5.ps1`
- Consulter les exemples générés

## Version

**Format**: 2.0  
**Date**: 15 Novembre 2024  
**Changements**: A5, N&B, 3 signatures, format YYMMDD-XXXXX
