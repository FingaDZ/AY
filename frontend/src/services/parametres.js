import api from './api';

const parametresService = {
  // Récupérer les paramètres de l'entreprise
  getParametres: async () => {
    const response = await api.get('/parametres/');
    return response.data;
  },

  // Mettre à jour les paramètres de l'entreprise
  updateParametres: async (data) => {
    const response = await api.put('/parametres/', data);
    return response.data;
  },
};

export default parametresService;
