import api from './api';

export const logsService = {
    getLogs: (params) => {
        return api.get('/logs/', { params });
    },
    
    getLogDetail: (logId) => {
        return api.get(`/logs/${logId}`);
    },
    
    getModules: () => {
        return api.get('/logs/modules');
    },
    
    getUsers: () => {
        return api.get('/logs/users');
    },
};

export default logsService;
