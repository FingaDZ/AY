import api from './api';

const editionSalaireService = {
    /**
     * Récupère la prévisualisation des salaires pour une période donnée.
     * @param {number} annee 
     * @param {number} mois 
     * @returns {Promise<Array>} Liste des calculs de salaire
     */
    getPreview: async (annee, mois) => {
        try {
            const response = await api.get('/edition-salaires/preview', {
                params: { annee, mois }
            });
            return response.data;
        } catch (error) {
            console.error("Erreur lors du chargement de l'édition des salaires:", error);
            throw error;
        }
    },

    /**
     * Validera l'édition (Futur)
     */
    validateEdition: async (annee, mois, data) => {
        // TODO: Implémenter la sauvegarde
        return Promise.resolve({ success: true });
    }
};

export default editionSalaireService;
