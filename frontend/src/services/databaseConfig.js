import api from './api';

const databaseConfigService = {
  // Récupérer la configuration active
  getConfig: async () => {
    const response = await api.get('/database-config/');
    return response.data;
  },

  // Créer ou mettre à jour la configuration
  createOrUpdate: async (data) => {
    const response = await api.post('/database-config/', data);
    return response.data;
  },

  // Mettre à jour une configuration existante
  update: async (id, data) => {
    const response = await api.put(`/database-config/${id}`, data);
    return response.data;
  },

  // Tester une connexion
  testConnection: async (data) => {
    const response = await api.post('/database-config/test', data);
    return response.data;
  },

  // Récupérer l'historique
  getHistory: async () => {
    const response = await api.get('/database-config/history');
    return response.data;
  },
};

export default databaseConfigService;
