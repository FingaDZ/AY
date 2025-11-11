import api from './api';

export const employeService = {
  // Lister tous les employés
  getAll: (params = {}) => api.get('/employes/', { params }),
  
  // Obtenir un employé par ID
  getById: (id) => api.get(`/employes/${id}`),
  
  // Créer un employé
  create: (data) => api.post('/employes/', data),
  
  // Mettre à jour un employé
  update: (id, data) => api.put(`/employes/${id}`, data),
  
  // Supprimer un employé
  delete: (id) => api.delete(`/employes/${id}`),
  
  // Valider le contrat
  validerContrat: (id) => api.post(`/employes/${id}/valider-contrat`),
  
  // Valider tous les contrats
  validerTousContrats: () => api.post('/employes/valider-tous-contrats'),
};

export const pointageService = {
  getAll: (params = {}) => api.get('/pointages/', { params }),
  getById: (id) => api.get(`/pointages/${id}`),
  create: (data) => api.post('/pointages/', data),
  update: (id, data) => {
    // Convertir les clés jour_XX en format Dict[int, int] pour l'API
    const jours = {};
    for (const [key, value] of Object.entries(data)) {
      if (key.startsWith('jour_')) {
        const jourNum = parseInt(key.replace('jour_', ''));
        jours[jourNum] = value;
      }
    }
    return api.put(`/pointages/${id}`, { jours });
  },
  verrouiller: (id) => api.post(`/pointages/${id}/verrouiller`),
  copier: (data) => api.post('/pointages/copier', data),
  getEmployesActifs: () => api.get('/pointages/employes-actifs'),
};

export const clientService = {
  getAll: (params = {}) => api.get('/clients/', { params }),
  getById: (id) => api.get(`/clients/${id}`),
  create: (data) => api.post('/clients/', data),
  update: (id, data) => api.put(`/clients/${id}`, data),
  delete: (id) => api.delete(`/clients/${id}`),
};

export const missionService = {
  getAll: (params = {}) => api.get('/missions/', { params }),
  getById: (id) => api.get(`/missions/${id}`),
  create: (data) => api.post('/missions/', data),
  delete: (id) => api.delete(`/missions/${id}`),
  getPrimesMensuelles: (params) => api.get('/missions/primes-mensuelles', { params }),
  getTarifKm: () => api.get('/missions/parametres/tarif-km'),
  updateTarifKm: (tarif) => api.put('/missions/parametres/tarif-km', null, { params: { nouveau_tarif: tarif } }),
};

export const avanceService = {
  getAll: (params = {}) => api.get('/avances/', { params }),
  getById: (id) => api.get(`/avances/${id}`),
  create: (data) => api.post('/avances/', data),
  update: (id, data) => api.put(`/avances/${id}`, data),
  delete: (id) => api.delete(`/avances/${id}`),
  getTotalMensuel: (params) => api.get('/avances/total-mensuel', { params }),
};

export const creditService = {
  getAll: (params = {}) => api.get('/credits/', { params }),
  getById: (id) => api.get(`/credits/${id}`),
  create: (data) => api.post('/credits/', data),
  update: (id, data) => api.put(`/credits/${id}`, data),
  delete: (id) => api.delete(`/credits/${id}`),
  getHistorique: (id) => api.get(`/credits/${id}/historique`),
  createProrogation: (id, data) => api.post(`/credits/${id}/prorogation`, data),
};

export const salaireService = {
  calculer: (data) => api.post('/salaires/calculer', data),
  calculerTous: (data) => api.post('/salaires/calculer-tous', data),
  getRapport: (annee, mois) => api.get(`/salaires/rapport/${annee}/${mois}`),
};

export const rapportService = {
  getPointagesPdf: (params) => api.get('/rapports/pointages/pdf', { 
    params, 
    responseType: 'blob' 
  }),
  getPointagesExcel: (params) => api.get('/rapports/pointages/excel', { 
    params, 
    responseType: 'blob' 
  }),
  getSalairesPdf: (params) => api.get('/rapports/salaires/pdf', { 
    params, 
    responseType: 'blob' 
  }),
  getSalairesExcel: (params) => api.get('/rapports/salaires/excel', { 
    params, 
    responseType: 'blob' 
  }),
};
