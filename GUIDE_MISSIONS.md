# Guide Rapide - Gestion des Missions

## Interface Utilisateur

### Page Missions
```
┌─────────────────────────────────────────────────────────────────┐
│  Ordres de Mission                 Tarif/km: 3.00 DA             │
│                                    [Rapport PDF] [+Nouvelle]     │
├─────────────────────────────────────────────────────────────────┤
│  Filtres:                                                        │
│  [Date début - Date fin] [Chauffeur▼] [Client▼]                │
│  [Filtrer] [Réinitialiser]                                      │
├─────────────────────────────────────────────────────────────────┤
│  Totaux par Chauffeur:                                          │
│  Chauffeur      │ Missions │ Distance │ Primes                  │
│  Test TEST      │    2     │  77.5 km │ 232.5 DA               │
├─────────────────────────────────────────────────────────────────┤
│  Liste des Missions:                                             │
│  Date    │ Chauffeur │ Client │ Distance │ Prime │ Actions      │
│  01/11   │ Test TEST │ Client │  40 km   │ 120DA │ [✏️][🗑️][🖨️] │
└─────────────────────────────────────────────────────────────────┘
```

## Scénarios d'Utilisation

### 1. Créer une Nouvelle Mission
1. Cliquer sur **[+ Nouvelle Mission]**
2. Remplir le formulaire:
   - Date: (pré-remplie avec aujourd'hui)
   - Chauffeur: Sélectionner dans la liste
   - Client: Sélectionner (affiche distance et tarif)
3. Cliquer sur **[Créer]**
4. ✅ Mission créée avec calcul automatique de la prime

### 2. Modifier une Mission Existante
1. Trouver la mission dans le tableau
2. Cliquer sur **[✏️ Modifier]**
3. Modifier les champs dans le formulaire
4. Cliquer sur **[Modifier]**
5. ✅ Mission mise à jour, prime recalculée

### 3. Supprimer une Mission
1. Trouver la mission dans le tableau
2. Cliquer sur **[🗑️ Supprimer]**
3. Confirmer dans le popup
4. ✅ Mission supprimée

### 4. Filtrer les Missions

#### Par Période
```
[📅 01/11/2024 - 30/11/2024] [Filtrer]
→ Affiche toutes les missions de novembre
```

#### Par Chauffeur
```
[Chauffeur▼: Ahmed BENALI] [Filtrer]
→ Affiche uniquement les missions d'Ahmed
```

#### Par Client
```
[Client▼: Sonatrach] [Filtrer]
→ Affiche uniquement les missions vers Sonatrach
```

#### Combiné
```
[📅 01/11 - 30/11] [Ahmed BENALI▼] [Sonatrach▼] [Filtrer]
→ Missions d'Ahmed vers Sonatrach en novembre
→ Les totaux se mettent à jour automatiquement
```

### 5. Télécharger un Ordre de Mission

**Pour un chauffeur:**
1. Trouver la mission
2. Cliquer sur **[🖨️ Ordre]**
3. Le PDF se télécharge automatiquement
4. Ouvrir le PDF

**Contenu du PDF:**
```
┌─────────────────────────────┐
│    ORDRE DE MISSION         │
│                             │
│ Ordre N°: 00001             │
│ Date: 15/11/2024            │
│                             │
│ ┌─────────────────────────┐ │
│ │ CHAUFFEUR               │ │
│ │ Nom: Ahmed BENALI       │ │
│ └─────────────────────────┘ │
│                             │
│ ┌─────────────────────────┐ │
│ │ DÉTAILS DE LA MISSION   │ │
│ │ Destination: Sonatrach  │ │
│ │ Distance: 80.00 km      │ │
│ │ Prime: 400.00 DA        │ │
│ └─────────────────────────┘ │
│                             │
│ Signature chauffeur: ___    │
│ Signature responsable: ___  │
└─────────────────────────────┘
```

### 6. Télécharger le Rapport des Missions

**Pour une période:**
1. Sélectionner les filtres (période, chauffeur, etc.)
2. Cliquer sur **[🖨️ Rapport PDF]** dans l'en-tête
3. Le PDF se télécharge

**Contenu du Rapport:**
```
┌────────────────────────────────────────────────┐
│        RAPPORT DES MISSIONS                    │
│                                                │
│ Généré le: 15/11/2024 14:30                   │
│ Période: du 01/11/2024 au 30/11/2024          │
│                                                │
│ ┌────────────────────────────────────────────┐ │
│ │ Date│Chauffeur│Client│Distance│Prime      │ │
│ ├────────────────────────────────────────────┤ │
│ │01/11│Ahmed B. │Sontr.│ 80 km  │ 400 DA   │ │
│ │02/11│Karim M. │TotalE│ 45 km  │ 225 DA   │ │
│ │03/11│Ahmed B. │Sontr.│ 80 km  │ 400 DA   │ │
│ ├────────────────────────────────────────────┤ │
│ │TOTAL│         │      │205 km  │1025 DA   │ │
│ └────────────────────────────────────────────┘ │
│                                                │
│ Nombre total de missions: 3                    │
└────────────────────────────────────────────────┘
```

## Cas d'Usage Pratiques

### Cas 1: Rapport Mensuel pour la Comptabilité
```
Objectif: Obtenir toutes les missions de novembre pour la paie

1. [📅 01/11/2024 - 30/11/2024]
2. [Filtrer]
3. Vérifier les totaux par chauffeur
4. [🖨️ Rapport PDF]
5. → Fichier pour la comptabilité
```

### Cas 2: Ordre de Mission Quotidien
```
Objectif: Créer et imprimer l'ordre pour aujourd'hui

1. [+ Nouvelle Mission]
2. Date: (déjà aujourd'hui)
3. Chauffeur: Ahmed BENALI
4. Client: Sonatrach
5. [Créer]
6. [🖨️ Ordre] → Donner au chauffeur
```

### Cas 3: Vérification des Missions d'un Chauffeur
```
Objectif: Voir toutes les missions d'un chauffeur ce mois

1. [Chauffeur▼: Ahmed BENALI]
2. [📅 01/11/2024 - 30/11/2024]
3. [Filtrer]
4. Voir dans "Totaux":
   - Nombre de missions
   - Distance totale
   - Primes totales
```

### Cas 4: Correction d'une Erreur
```
Objectif: Modifier un client incorrect

1. Trouver la mission
2. [✏️ Modifier]
3. Changer le client
4. [Modifier]
5. → Prime recalculée automatiquement
```

## Raccourcis et Astuces

### 💡 Astuces
- La date est pré-remplie avec aujourd'hui
- La distance et le tarif du client sont affichés dans le sélecteur
- La prime est calculée automatiquement
- Les filtres sont cumulatifs
- Cliquer "Réinitialiser" efface tous les filtres
- Les totaux se mettent à jour avec les filtres

### ⚠️ Points d'Attention
- Confirmation requise avant suppression
- Modifier une mission recalcule la prime
- Les PDFs utilisent le format DD/MM/YYYY
- Le rapport inclut TOUTES les missions filtrées

### 📊 Interprétation des Totaux
```
Chauffeur: Ahmed BENALI
Missions: 15
Distance: 1200 km
Primes: 6000 DA

→ Signifie: 15 ordres de mission ce mois
→ Total parcouru: 1200 km
→ À payer: 6000 DA en primes
```

## Dépannage

### Problème: Le bouton "Rapport PDF" n'apparaît pas
**Solution**: Il faut au moins une mission dans la liste

### Problème: Les totaux sont à 0
**Solution**: Vérifier les filtres, peut-être trop restrictifs

### Problème: Le PDF ne se télécharge pas
**Solution**: 
1. Vérifier que le backend est démarré
2. Vérifier la console du navigateur
3. Réessayer

### Problème: La prime ne se met pas à jour
**Solution**: 
1. Vérifier que le client a un tarif_km
2. Modifier le client pour définir le tarif

## Intégration avec les Autres Modules

### Avec Employés
- Les chauffeurs sont filtrés automatiquement (poste: "Chauffeur")
- Seuls les employés actifs apparaissent

### Avec Clients
- Distance et tarif_km viennent de la fiche client
- Prime = distance × tarif_km

### Avec Salaires
- Les primes mensuelles sont disponibles via l'API
- Endpoint: `/api/missions/primes-mensuelles?annee=2024&mois=11`

## Support

Pour toute question ou problème:
1. Consulter MISSIONS_FEATURES.md pour les détails techniques
2. Vérifier TROUBLESHOOTING.md
3. Contacter l'administrateur système
