import axios from 'axios';

// Logique dynamique pour l'URL de l'API:
// 1. Si on est sur le port 3000 (Accès direct IP locale), on tape sur le port 8000
// 2. Sinon (Accès via Domaine/Proxy), on utilise le chemin relatif /api (le proxy doit gérer)
const isLocalPort3000 = window.location.port === '3000';
const API_BASE_URL = isLocalPort3000
  ? `${window.location.protocol}//${window.location.hostname}:8000/api`
  : '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token d'authentification
api.interceptors.request.use(
  (config) => {
    const user = localStorage.getItem('user');
    if (user) {
      try {
        const userData = JSON.parse(user);
        config.headers.Authorization = `Bearer ${userData.id}`;
      } catch (e) {
        // Ignorer si parse échoue
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Intercepteur pour gérer les erreurs
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    // Si 401, déconnecter (sauf si déjà sur la page de login)
    if (error.response?.status === 401 && !window.location.pathname.includes('/login')) {
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
