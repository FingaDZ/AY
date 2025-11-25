# Intégration Système de Pointage (Attendance)

Ce document détaille la stratégie d'intégration entre **AY HR System** (Gestion RH) et **Attendance System** (Pointage Facial).

## 1. Architecture

*   **HR System (Maître)** : `192.168.20.53` (Gère les employés, postes, congés, paie).
*   **Attendance System (Esclave)** : `192.168.20.56` (Gère la reconnaissance faciale et les logs de pointage).

## 2. Stratégie de Données

### A. Synchronisation des Employés (HR -> Attendance)
Le flux de données est unidirectionnel pour les informations de base. HR System est la source de vérité.

*   **Fréquence** : À la création/modification d'un employé dans HR.
*   **Données** :
    *   `name` : Nom complet (ex: "GHELLAM ABDERREZZAQ").
    *   `department` : Poste de travail (ex: "Développeur").
    *   `pin` : Année de naissance (ex: "1990").
*   **Photos** :
    *   *Actuellement* : HR System ne gère pas les photos.
    *   *Action Requise* : L'administrateur doit uploader les photos manuellement sur l'interface Attendance (`http://192.168.20.56:3000`) après la création automatique de l'employé, OU nous devons ajouter la gestion des photos dans HR System.

### B. Récupération des Pointages (Attendance -> HR)
HR System récupère les logs de pointage pour calculer les heures travaillées.

*   **Fréquence** : Tâche planifiée (Cron) ou Action Manuelle ("Importer Pointages").
*   **Données** :
    *   `employee_name` : Pour la correspondance.
    *   `timestamp` : Date et heure du pointage.
    *   `type` : `ENTRY` ou `EXIT`.
    *   `worked_minutes` : Durée calculée par Attendance (si disponible).

## 3. Spécifications API (Attendance System)

### Créer un Employé
*   **Endpoint** : `POST http://192.168.20.56:8000/api/employees/`
*   **Payload (Multipart/Form-Data)** :
    *   `name`: string
    *   `department`: string
    *   `pin`: string
    *   `file1`...`file6`: (Optionnel si créé sans photos, mais requis pour la reconnaissance)

### Mettre à jour un Employé
*   **Endpoint** : `PUT http://192.168.20.56:8000/api/employees/{id}`
*   **Payload** : Idem création.

### Récupérer les Pointages
*   **Endpoint** : `GET http://192.168.20.56:8000/api/attendance/`
*   **Query Params** :
    *   `start_date`: ISO Format (ex: `2025-11-25T00:00:00`)
    *   `end_date`: ISO Format
    *   `limit`: int (ex: 1000)

## 4. Plan d'Implémentation Future

1.  **Service de Synchro (Backend HR)** :
    *   Créer `services/attendance_sync.py`.
    *   Fonction `sync_employee_to_attendance(employee)` appelée après `create_employee` et `update_employee`.
    *   Fonction `fetch_attendance_logs(date)` pour remplir la table `pointages` de HR.

2.  **Interface Utilisateur (Frontend HR)** :
    *   Bouton "Synchroniser avec Attendance" dans la liste des employés.
    *   Bouton "Importer Pointages" dans la grille de pointage.

3.  **Gestion des Photos** :
    *   Ajouter le champ photo dans HR System pour automatiser complètement l'envoi vers Attendance.
