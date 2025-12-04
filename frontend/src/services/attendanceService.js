import api from './api';

const attendanceService = {
    // Sync single employee
    syncEmployee: (employeeId) => {
        return api.post('/attendance-integration/sync-employee', { employee_id: employeeId });
    },

    // Sync all employees
    syncAllEmployees: () => {
        return api.post('/attendance-integration/sync-all-employees');
    },

    // Get mappings
    getMappings: (params = {}) => {
        return api.get('/attendance-integration/mappings', { params });
    },

    // Delete mapping
    deleteMapping: (mappingId) => {
        return api.delete(`/attendance-integration/mappings/${mappingId}`);
    },

    // Import logs
    importLogs: (startDate, endDate, employeeId = null) => {
        return api.post('/attendance-integration/import-logs', {
            start_date: startDate,
            end_date: endDate,
            employee_id: employeeId
        });
    },

    // Import file
    importFile: (file) => {
        const formData = new FormData();
        formData.append('file', file);
        return api.post('/attendance-integration/import-file', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
    },

    // Get conflicts
    getConflicts: (status = null, params = {}) => {
        const queryParams = { ...params };
        if (status) queryParams.status = status;
        return api.get('/attendance-integration/conflicts', { params: queryParams });
    },

    // Resolve conflict
    resolveConflict: (conflictId, resolution, resolvedBy) => {
        return api.post(`/attendance-integration/conflicts/${conflictId}/resolve`, {
            resolution,
            resolved_by: resolvedBy
        });
    },

    // Preview import
    previewImport: (file) => {
        const formData = new FormData();
        formData.append('file', file);
        return api.post('/attendance-integration/import-preview', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
    },

    // Confirm import
    confirmImport: (data) => {
        return api.post('/attendance-integration/import-confirm', data);
    },

    // Delete conflict
    deleteConflict: (conflictId) => {
        return api.delete(`/attendance-integration/conflicts/${conflictId}`);
    }
};

export default attendanceService;
