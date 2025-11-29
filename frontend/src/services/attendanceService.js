import axios from 'axios';

const API_URL = '/api/attendance-integration';

const attendanceService = {
    // Sync single employee
    syncEmployee: (employeeId) => {
        return axios.post(`${API_URL}/sync-employee`, { employee_id: employeeId });
    },

    // Sync all employees
    syncAllEmployees: () => {
        return axios.post(`${API_URL}/sync-all-employees`);
    },

    // Get mappings
    getMappings: (params = {}) => {
        return axios.get(`${API_URL}/mappings`, { params });
    },

    // Delete mapping
    deleteMapping: (mappingId) => {
        return axios.delete(`${API_URL}/mappings/${mappingId}`);
    },

    // Import logs
    importLogs: (startDate, endDate, employeeId = null) => {
        return axios.post(`${API_URL}/import-logs`, {
            start_date: startDate,
            end_date: endDate,
            employee_id: employeeId
        });
    },

    // Import file
    importFile: (file) => {
        const formData = new FormData();
        formData.append('file', file);
        return axios.post(`${API_URL}/import-file`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
    },

    // Get conflicts
    getConflicts: (status = null, params = {}) => {
        const queryParams = { ...params };
        if (status) queryParams.status = status;
        return axios.get(`${API_URL}/conflicts`, { params: queryParams });
    },

    // Resolve conflict
    resolveConflict: (conflictId, resolution, resolvedBy) => {
        return axios.post(`${API_URL}/conflicts/${conflictId}/resolve`, {
            resolution,
            resolved_by: resolvedBy
        });
    },

    // Delete conflict
    deleteConflict: (conflictId) => {
        return axios.delete(`${API_URL}/conflicts/${conflictId}`);
    }
};

export default attendanceService;
