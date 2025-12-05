import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

/**
 * Composant de protection des routes administrateur
 * Redirige vers le dashboard si l'utilisateur n'est pas admin
 */
const ProtectedAdminRoute = ({ children }) => {
    const { user, loading, isAdmin } = useAuth();

    // Affichage pendant le chargement
    if (loading) {
        return (
            <div className="flex justify-center items-center h-screen">
                <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-500"></div>
            </div>
        );
    }

    // Redirection si non connecté
    if (!user) {
        return <Navigate to="/login" replace />;
    }

    // Redirection si non-admin
    if (!isAdmin()) {
        console.warn(`Access denied: User ${user.email} (${user.role}) attempted to access admin route`);
        return <Navigate to="/" replace />;
    }

    // Accès autorisé
    return children;
};

export default ProtectedAdminRoute;
