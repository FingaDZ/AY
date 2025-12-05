import api from './api';

const BASE_URL = '/parametres-salaires';

export const parametresSalaireService = {
    // Récupérer les paramètres actuels
    getParametres: () => {
        return api.get(BASE_URL);
    },

    // Mettre à jour les paramètres
    updateParametres: (params) => {
        return api.put(BASE_URL, params);
    },

    // Récupérer le barème IRG
    getIRGBareme: (actifOnly = true) => {
        return api.get(`${BASE_URL}/irg-bareme`, {
            params: { actif_only: actifOnly }
        });
    },

    // Créer une tranche IRG
    createIRGTranche: (tranche) => {
        return api.post(`${BASE_URL}/irg-bareme`, tranche);
    },

    // Supprimer une tranche IRG
    deleteIRGTranche: (trancheId) => {
        return api.delete(`${BASE_URL}/irg-bareme/${trancheId}`);
    },

    // Désactiver tout le barème actif
    desactiverBareme: () => {
        return api.post(`${BASE_URL}/irg-bareme/desactiver-tout`);
    },

    // Reports en attente
    getReports: (params = {}) => {
        return api.get(`${BASE_URL}/reports`, { params });
    },

    // Créer un report manuel
    createReport: (report) => {
        return api.post(`${BASE_URL}/reports`, report);
    },
};

export default parametresSalaireService;
