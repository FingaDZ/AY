import api from './api';

const utilisateursService = {
  // Lister tous les utilisateurs
  list: async () => {
    const response = await api.get('/utilisateurs/');
    return response.data;
  },

  // Créer un utilisateur
  create: async (data) => {
    const response = await api.post('/utilisateurs/', data);
    return response.data;
  },

  // Obtenir un utilisateur
  get: async (id) => {
    const response = await api.get(`/utilisateurs/${id}`);
    return response.data;
  },

  // Mettre à jour un utilisateur
  update: async (id, data) => {
    const response = await api.put(`/utilisateurs/${id}`, data);
    return response.data;
  },

  // Supprimer un utilisateur
  delete: async (id) => {
    await api.delete(`/utilisateurs/${id}`);
  },

  // Connexion
  login: async (email, password) => {
    const response = await api.post('/utilisateurs/login', { email, password });
    return response.data;
  },
};

export default utilisateursService;
