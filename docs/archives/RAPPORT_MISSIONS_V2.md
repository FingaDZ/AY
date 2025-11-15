# Rapport des Missions v2.0 - Nouveau Format

## ✅ Modifications Appliquées

### 1. En-tête Optimisé (même style que Ordre de Mission v2.1)

**Avant:**
```
RAPPORT DES MISSIONS
(centré, seul)

Généré le: 11/11/2025 14:30
Période: du 01/01/2024 au 31/12/2025
```

**Après:**
```
RAPPORT DES MISSIONS          Total: 2 mission(s)
(gauche)                      (droite - même ligne)

Généré le: 11/11/2025 14:30
(juste en dessous du titre)

Période: du 01/01/2024 au 31/12/2025
```

### 2. Format et Marges

**Avant:**
- Format: A4
- Marges: 2cm haut/bas
- Largeur disponible: ~17cm

**Après:**
- Format: A4 (comme demandé)
- Marges: 1cm partout (comme ordre de mission)
- Largeur disponible: 19cm (21cm - 2cm marges)

### 3. Tableau Optimisé

**Largeurs de colonnes dynamiques:**

| Colonne | Avant | Après | Utilisation |
|---------|-------|-------|-------------|
| Date | 2.5cm | 2.5cm | ✓ Inchangé |
| Chauffeur | 4cm | 5cm | ⬆️ +25% |
| Client | 4cm | 5cm | ⬆️ +25% |
| Distance | 2.5cm | 3.25cm | ⬆️ +30% |
| Prime | 2.5cm | 3.25cm | ⬆️ +30% |
| **TOTAL** | **15.5cm** | **19cm** | **+23%** |

### 4. Style Noir et Blanc

**Avant:**
- En-tête: Bleu (#1890ff) avec texte blanc
- Lignes paires: Bleu clair (lightblue)
- Total: Gris clair

**Après:**
- En-tête: Gris clair avec texte noir
- Lignes paires: ~~Pas d'alternance de couleur~~
- Total: Gris clair (identique)
- **Tout en noir et blanc** (comme ordre de mission)

### 5. Padding Augmenté

**Avant:**
```python
('PADDING', (0, 0), (-1, -1), 6),
```

**Après:**
```python
('PADDING', (0, 0), (-1, -1), 6),
('LEFTPADDING', (0, 0), (-1, -1), 8),
('RIGHTPADDING', (0, 0), (-1, -1), 8),
```

Évite le chevauchement du texte (comme ordre de mission).

## 📋 Nouveau Format Complet

```
┌─────────────────────────────────────────────────────────┐  A4
│ RAPPORT DES MISSIONS              Total: 2 mission(s)   │  ← Même ligne
│                                                          │
│ Généré le: 11/11/2025 14:30                             │  ← Juste en dessous
│ Période: du 01/01/2024 au 31/12/2025                    │
│                                                          │
│ ┌──────┬────────────┬────────────┬──────────┬─────────┐ │
│ │ Date │ Chauffeur  │   Client   │ Distance │  Prime  │ │
│ │      │            │            │   (km)   │  (DA)   │ │
│ ├──────┼────────────┼────────────┼──────────┼─────────┤ │
│ │11/11 │ Ahmed      │ Ali        │    80.00 │  400.00 │ │
│ │      │ BENALI     │ MEZIANE    │          │         │ │
│ ├──────┼────────────┼────────────┼──────────┼─────────┤ │
│ │12/11 │ Mohamed    │ Fatima     │   120.00 │  600.00 │ │
│ │      │ SAID       │ BOUZID     │          │         │ │
│ ├──────┼────────────┼────────────┼──────────┼─────────┤ │
│ │TOTAL │            │            │   200.00 │ 1000.00 │ │
│ └──────┴────────────┴────────────┴──────────┴─────────┘ │
└─────────────────────────────────────────────────────────┘
```

## 🔍 Détails Techniques

### En-tête (Tableau 2 colonnes)
```python
header_data = [
    ['RAPPORT DES MISSIONS', f'Total: {len(missions)} mission(s)']
]

header_table = Table(header_data, colWidths=[13*cm, 6*cm])
# 13cm pour le titre + 6cm pour le total = 19cm (largeur disponible)
```

**Styles:**
- Titre: Helvetica-Bold, 14pt, aligné à gauche, noir
- Total: Helvetica-Bold, 10pt, aligné à droite, noir

### Tableau Principal (5 colonnes)
```python
col_widths = [2.5*cm, 5*cm, 5*cm, 3.25*cm, 3.25*cm]
# Total: 19cm (utilise toute la largeur disponible)
```

**Calcul:**
- A4 largeur: 21cm
- Marges (gauche + droite): 1cm + 1cm = 2cm
- Disponible: 21cm - 2cm = 19cm
- Répartition:
  - Date: 2.5cm (13%)
  - Chauffeur: 5cm (26%)
  - Client: 5cm (26%)
  - Distance: 3.25cm (17%)
  - Prime: 3.25cm (17%)

### Alignement des Colonnes
```python
('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Date centrée
('ALIGN', (1, 1), (2, -2), 'LEFT'),    # Noms à gauche
('ALIGN', (3, 1), (4, -2), 'RIGHT'),   # Chiffres à droite
```

### Padding Optimisé
```python
('PADDING', (0, 0), (-1, -1), 6),      # Padding général
('LEFTPADDING', (0, 0), (-1, -1), 8),  # Marge intérieure gauche
('RIGHTPADDING', (0, 0), (-1, -1), 8), # Marge intérieure droite
```

Évite le chevauchement même avec noms longs.

## 📊 Comparaison v1.0 vs v2.0

| Élément | v1.0 | v2.0 |
|---------|------|------|
| **Format** | A4 | A4 |
| **Marges** | 2cm haut/bas | 1cm partout |
| **Largeur utilisée** | 15.5cm (73%) | 19cm (90%) |
| **En-tête** | 2 lignes | 1 ligne |
| **Position total** | Bas (résumé) | Titre (même ligne) |
| **Couleur en-tête** | Bleu (#1890ff) | Gris clair (N&B) |
| **Couleur lignes** | Alternance bleu | ~~Pas d'alternance~~ |
| **Col Chauffeur** | 4cm | 5cm (+25%) |
| **Col Client** | 4cm | 5cm (+25%) |
| **Col Distance** | 2.5cm | 3.25cm (+30%) |
| **Col Prime** | 2.5cm | 3.25cm (+30%) |
| **Padding** | 6pt | 6pt + 8pt L/R |
| **Taille exemple** | ~2500 bytes | ~2226 bytes |

## ✅ Avantages

### Plus d'espace
- **+3.5cm de largeur** utilisable (15.5cm → 19cm)
- **Colonnes plus larges** pour noms longs
- **Moins de risque** de chevauchement

### Cohérence visuelle
- **Même style** que ordre de mission v2.1
- **Marges identiques** (1cm)
- **Noir et blanc** uniforme
- **En-tête similaire** (titre + info sur même ligne)

### Lisibilité
- **Total visible** immédiatement (en-tête)
- **Date/période** bien placées
- **Colonnes équilibrées** (26% / 26% / 17% / 17%)
- **Chiffres alignés** à droite (facile à lire)

### Professionnalisme
- **Format A4 standard** pour impression
- **Noir et blanc** économique
- **Layout épuré** sans couleurs distrayantes
- **Padding augmenté** pour confort visuel

## 🎯 Cas d'Usage

### 1. Rapport Mensuel
```python
POST /api/missions/rapport/pdf
{
  "date_debut": "2025-11-01",
  "date_fin": "2025-11-30"
}
```

### 2. Rapport par Chauffeur
```python
POST /api/missions/rapport/pdf
{
  "chauffeur_id": 1,
  "date_debut": "2025-01-01",
  "date_fin": "2025-12-31"
}
```

### 3. Rapport par Client
```python
POST /api/missions/rapport/pdf
{
  "client_id": 2,
  "date_debut": "2025-01-01",
  "date_fin": "2025-12-31"
}
```

### 4. Rapport Complet
```python
POST /api/missions/rapport/pdf
{
  "date_debut": "2024-01-01",
  "date_fin": "2025-12-31"
}
```

## 🧪 Test

```powershell
# Générer un rapport de test
$body = @{ 
  date_debut = "2024-01-01"
  date_fin = "2025-12-31" 
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "http://localhost:8000/api/missions/rapport/pdf" `
  -Method Post `
  -Body $body `
  -ContentType "application/json" `
  -OutFile "test_rapport_missions_v2.pdf"

# Ouvrir le PDF
Start-Process "test_rapport_missions_v2.pdf"
```

**Résultat:**
```
✓ PDF généré: test_rapport_missions_v2.pdf (2226 bytes)
✓ Format A4, noir et blanc
✓ En-tête optimisé avec total
✓ Colonnes dynamiques (19cm largeur)
✓ Padding augmenté, pas de chevauchement
```

## 📝 Notes

### Ligne TOTAL
La ligne de total est en **gras** et sur **fond gris clair** pour la distinguer.

```python
# Ligne de totaux
data.append([
    'TOTAL',
    '',
    '',
    f"{total_distance:.2f}",
    f"{total_primes:.2f}"
])

# Style
('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
```

### Sans alternance de couleur
Contrairement à la v1.0, la v2.0 ne fait **plus d'alternance bleu clair/blanc** pour les lignes.

**Raison:** Cohérence avec l'ordre de mission (noir et blanc uniquement).

**Si vous voulez réactiver l'alternance gris clair:**
```python
# Ajouter après le TableStyle:
for i in range(1, len(data) - 1):
    if i % 2 == 0:
        style_list.append(
            ('BACKGROUND', (0, i), (-1, i), colors.lightgrey)
        )
```

### Format A4 vs A5
- **Ordre de mission**: A5 (148×210mm) - Document individuel compact
- **Rapport missions**: A4 (210×297mm) - Liste avec plusieurs lignes

### Nombre de missions affiché
Le nombre total de missions s'affiche maintenant dans l'**en-tête** (même ligne que le titre), pas en bas comme avant.

**Avantage:** Visible immédiatement sans scroller.

## 🎯 Résultat

✅ **Format**: A4 (210×297mm)  
✅ **Marges**: 1cm partout (comme ordre de mission)  
✅ **En-tête**: Titre + Total sur même ligne  
✅ **Date**: Juste en dessous du titre  
✅ **Tableau**: 5 colonnes dynamiques (19cm largeur)  
✅ **Style**: Noir et blanc (pas de couleurs)  
✅ **Padding**: Augmenté (8pt L/R) pour éviter chevauchement  
✅ **Total**: Ligne en gras avec fond gris clair  

**Fichier de test**: `test_rapport_missions_v2.pdf`

Format cohérent avec l'ordre de mission v2.1, prêt pour production ! 🎊
