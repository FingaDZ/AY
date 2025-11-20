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
  
  // Vérifier si l'employé peut être supprimé
  checkCanDelete: (id) => api.get(`/employes/${id}/check-delete`),
  
  // Supprimer un employé (définitif)
  delete: (id) => api.delete(`/employes/${id}`),
  
  // Désactiver un employé (soft delete)
  deactivate: (id) => api.post(`/employes/${id}/deactivate`),
  
  // Réactiver un employé
  reactivate: (id) => api.post(`/employes/${id}/reactivate`),
  
  // Valider le contrat
  validerContrat: (id) => api.post(`/employes/${id}/valider-contrat`),
  
  // Valider tous les contrats
  validerTousContrats: () => api.post('/employes/valider-tous-contrats'),
  
  // Rapport PDF employés actifs
  getRapportActifs: (annee, mois) => api.get('/employes/rapport-pdf/actifs', { 
    params: { annee, mois }, 
    responseType: 'blob' 
  }),
  
  // Générer attestation de travail (employé actif)
  generateAttestation: (id) => api.get(`/employes/${id}/attestation-travail`, { 
    responseType: 'blob' 
  }),
  
  // Générer certificat de travail (employé inactif/parti)
  generateCertificat: (id) => api.get(`/employes/${id}/certificat-travail`, { 
    responseType: 'blob' 
  }),
  
  // Générer contrat de travail
  generateContrat: (id) => api.get(`/employes/${id}/contrat-travail`, { 
    responseType: 'blob' 
  }),
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
  verrouiller: (id) => api.put(`/pointages/${id}/verrouiller`, { verrouille: true }),
  deverrouiller: (id) => api.put(`/pointages/${id}/verrouiller`, { verrouille: false }),
  copier: (data) => api.post('/pointages/copier', data),
  getEmployesActifs: () => api.get('/pointages/employes-actifs'),
  
  // Rapport PDF pointages mensuels
  getRapportMensuel: (annee, mois) => api.get('/pointages/rapport-pdf/mensuel', {
    params: { annee, mois },
    responseType: 'blob'
  }),
};

export const clientService = {
  getAll: (params = {}) => api.get('/clients/', { params }),
  getById: (id) => api.get(`/clients/${id}`),
  create: (data) => api.post('/clients/', data),
  update: (id, data) => api.put(`/clients/${id}`, data),
  delete: (id) => api.delete(`/clients/${id}`),
  
  // Rapport PDF liste clients
  getRapportListe: () => api.get('/clients/rapport-pdf/liste', { responseType: 'blob' }),
};

export const missionService = {
  getAll: (params = {}) => api.get('/missions/', { params }),
  getById: (id) => api.get(`/missions/${id}`),
  create: (data) => api.post('/missions/', data),
  update: (id, data) => api.put(`/missions/${id}`, data),
  delete: (id) => api.delete(`/missions/${id}`),
  getTotauxChauffeur: (params = {}) => api.get('/missions/totaux-chauffeur', { params }),
  getOrdreMissionPdf: (id) => api.get(`/missions/${id}/ordre-mission/pdf`, { responseType: 'blob' }),
  getRapportPdf: (params = {}) => api.post('/missions/rapport/pdf', null, { params, responseType: 'blob' }),
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
  
  // Rapport PDF avances mensuelles
  getRapportMensuel: (annee, mois) => api.get('/avances/rapport-pdf/mensuel', {
    params: { annee, mois },
    responseType: 'blob'
  }),
};

export const creditService = {
  getAll: (params = {}) => api.get('/credits/', { params }),
  getById: (id) => api.get(`/credits/${id}`),
  create: (data) => api.post('/credits/', data),
  update: (id, data) => api.put(`/credits/${id}`, data),
  delete: (id) => api.delete(`/credits/${id}`),
  getHistorique: (id) => api.get(`/credits/${id}/historique`),
  getEcheancier: (id) => api.get(`/credits/${id}/echeancier`),
  createProrogation: (id, data) => api.post(`/credits/${id}/prorogation`, data),
  enregistrerRetenue: (id, mois, annee) => api.post(`/credits/${id}/retenue`, null, { 
    params: { mois, annee } 
  }),
  getPdf: (params = {}) => api.get('/credits/pdf', { params, responseType: 'blob' }),
};

export const salaireService = {
  calculer: (data) => api.post('/salaires/calculer', data),
  calculerTous: (data) => api.post('/salaires/calculer-tous', data),
  sauvegarderBatch: (annee, mois) => api.post(`/salaires/sauvegarder-batch/${annee}/${mois}`),
  genererBulletins: (data) => api.post('/salaires/bulletins-paie/generer', data, { responseType: 'blob' }),
  genererRapport: (data) => api.post('/salaires/rapport-pdf', data, { responseType: 'blob' }),
  getRapport: (annee, mois) => api.get(`/salaires/rapport/${annee}/${mois}`),
};

export const posteService = {
  getAll: (params = {}) => api.get('/postes/', { params }),
  getById: (id) => api.get(`/postes/${id}`),
  create: (data) => api.post('/postes/', data),
  update: (id, data) => api.put(`/postes/${id}`, data),
  delete: (id) => api.delete(`/postes/${id}`),
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
  getG29Data: (annee) => api.get(`/rapports/g29/${annee}`),
  getG29Pdf: (annee) => api.get(`/rapports/g29/${annee}/pdf`, { responseType: 'blob' }),
};
