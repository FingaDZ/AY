# Endpoints Archivés - Import Attendance

> **Note** : Ces endpoints ont été remplacés par le système Preview Import unifié.  
> Conservés ici pour référence et réutilisation future si nécessaire.

## Endpoints Supprimés

### 1. Import Direct (`/import-file`)

**Méthode** : `POST`  
**Route** : `/api/attendance-integration/import-file`

**Fonctionnalité** :
- Upload fichier Excel
- Import direct sans prévisualisation
- Retourne résumé (imported, errors, conflicts)

**Code Backend** :
```python
@router.post("/import-file", response_model=AttendanceImportSummary)
async def import_attendance_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(400, "Format non supporté")
    
    content = await file.read()
    import_service = ImportService()
    attendance_service = AttendanceService(db)
    
    logs = import_service.parse_excel(content)
    summary = attendance_service.process_attendance_logs(logs)
    return summary
```

**Frontend Service** :
```javascript
importFile: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return axios.post(`${API_URL}/import-file`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    });
}
```

---

### 2. Import API (`/import-logs`)

**Méthode** : `POST`  
**Route** : `/api/attendance-integration/import-logs`

**Fonctionnalité** :
- Import depuis API Attendance externe
- Spécifier période (start_date, end_date)
- Optionnel : filtrer par employee_id

**Code Backend** :
```python
@router.post("/import-logs", response_model=AttendanceImportSummary)
def import_attendance_logs(
    request: AttendanceImportRequest,
    db: Session = Depends(get_db)
):
    service = AttendanceService(db)
    summary = service.import_attendance_logs(
        start_date=request.start_date,
        end_date=request.end_date,
        employee_id=request.employee_id
    )
    return AttendanceImportSummary(**summary)
```

**Frontend Service** :
```javascript
importLogs: (startDate, endDate, employeeId = null) => {
    return axios.post(`${API_URL}/import-logs`, {
        start_date: startDate,
        end_date: endDate,
        employee_id: employeeId
    });
}
```

---

### 3. Gestion Conflits (`/conflicts/*`)

**Routes** :
- `GET /api/attendance-integration/conflicts` - Liste conflits
- `POST /api/attendance-integration/conflicts/{id}/resolve` - Résoudre
- `DELETE /api/attendance-integration/conflicts/{id}` - Supprimer

**Fonctionnalité** :
- Afficher conflits d'import (pointage existant vs nouveau)
- Résolution manuelle : garder HR ou utiliser Attendance
- Suppression conflit

**Code Backend** :
```python
@router.get("/conflicts", response_model=List[AttendanceImportConflictResponse])
def list_conflicts(
    status: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(100),
    db: Session = Depends(get_db)
):
    query = db.query(AttendanceImportConflict)
    if status:
        conflict_status = ConflictStatus(status)
        query = query.filter(AttendanceImportConflict.status == conflict_status)
    
    conflicts = query.order_by(AttendanceImportConflict.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for conflict in conflicts:
        conflict_dict = AttendanceImportConflictResponse.model_validate(conflict).model_dump()
        if conflict.employe:
            conflict_dict['employee_name'] = f"{conflict.employe.nom} {conflict.employe.prenom}"
            conflict_dict['employee_poste'] = conflict.employe.poste_travail
        result.append(AttendanceImportConflictResponse(**conflict_dict))
    
    return result

@router.post("/conflicts/{conflict_id}/resolve")
def resolve_conflict(
    conflict_id: int,
    resolution: ConflictResolution,
    db: Session = Depends(get_db)
):
    service = AttendanceService(db)
    success = service.resolve_conflict(
        conflict_id=conflict_id,
        resolution=resolution.resolution,
        resolved_by=resolution.resolved_by
    )
    if not success:
        raise HTTPException(404, "Conflit non trouvé")
    return {"message": "Conflit résolu"}
```

**Frontend Service** :
```javascript
getConflicts: (status = null, params = {}) => {
    const queryParams = { ...params };
    if (status) queryParams.status = status;
    return axios.get(`${API_URL}/conflicts`, { params: queryParams });
},

resolveConflict: (conflictId, resolution, resolvedBy) => {
    return axios.post(`${API_URL}/conflicts/${conflictId}/resolve`, {
        resolution,
        resolved_by: resolvedBy
    });
},

deleteConflict: (conflictId) => {
    return axios.delete(`${API_URL}/conflicts/${conflictId}`);
}
```

---

## Pages Frontend Supprimées

### ImportAttendance.jsx

**Fonctionnalité** :
- Upload fichier Excel
- Import API avec dates
- Affichage résumé import

**Remplacé par** : `ImportPreview.jsx` (avec preview avant import)

---

### AttendanceConflicts.jsx

**Fonctionnalité** :
- Liste des conflits d'import
- Résolution manuelle (garder HR / utiliser Attendance)
- Filtrage par statut

**Remplacé par** : Gestion intégrée dans `ImportPreview.jsx`

---

## Réutilisation Future

Si besoin de réactiver ces fonctionnalités :

1. **Import Direct** : Ajouter bouton dans Preview Import qui appelle `/import-confirm` sans preview
2. **Conflits** : Intégrer dans tableau Preview avec actions inline
3. **Import API** : Créer endpoint `/import-preview-api` similaire à `/import-preview`

## Date d'Archivage

29 novembre 2025 - Version 2.1.0 → 2.2.0
