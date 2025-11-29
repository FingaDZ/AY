import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import EmployesList from './pages/Employes/EmployesList';
import EmployeForm from './pages/Employes/EmployeForm';
import PostesList from './pages/Postes/PostesList';
import GrillePointage from './pages/Pointages/GrillePointage';
import ClientsList from './pages/Clients/ClientsList';
import MissionsList from './pages/Missions/MissionsList';
import AvancesList from './pages/Avances/AvancesList';
import CreditsList from './pages/Credits/CreditsList';
import CongesList from './pages/Conges/CongesList';
import SalaireCalcul from './pages/Salaires/SalaireCalcul';
import ParametresPage from './pages/Parametres/ParametresPage';
import DatabaseConfigPage from './pages/DatabaseConfig/DatabaseConfigPage';
import UtilisateursPage from './pages/Utilisateurs/UtilisateursPage';
import LogsPage from './pages/Logs/LogsPage';
import LoginPage from './pages/Login/LoginPage';
import ImportPreview from './pages/Pointages/ImportPreview';
import IncompleteLogsList from './pages/IncompleteLogs/IncompleteLogsList';

// Composant pour protéger les routes
function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="flex justify-center items-center h-screen">
      <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-500"></div>
    </div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/*" element={
        <ProtectedRoute>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />

              {/* Employés */}
              <Route path="/employes" element={<EmployesList />} />
              <Route path="/employes/nouveau" element={<EmployeForm />} />
              <Route path="/employes/:id" element={<EmployeForm />} />

              {/* Postes de Travail */}
              <Route path="/postes" element={<PostesList />} />

              {/* Pointages */}
              <Route path="/pointages" element={<GrillePointage />} />
              <Route path="/pointages/import-preview" element={<ImportPreview />} />
              <Route path="/incomplete-logs" element={<IncompleteLogsList />} />

              {/* Clients */}
              <Route path="/clients" element={<ClientsList />} />

              {/* Missions */}
              <Route path="/missions" element={<MissionsList />} />

              {/* Avances */}
              <Route path="/avances" element={<AvancesList />} />

              {/* Crédits */}
              <Route path="/credits" element={<CreditsList />} />

              {/* Congés */}
              <Route path="/conges" element={<CongesList />} />

              {/* Salaires */}
              <Route path="/salaires" element={<SalaireCalcul />} />

              {/* Paramètres */}
              <Route path="/parametres" element={<ParametresPage />} />

              {/* Configuration Base de Données */}
              <Route path="/database-config" element={<DatabaseConfigPage />} />

              {/* Utilisateurs */}
              <Route path="/utilisateurs" element={<UtilisateursPage />} />

              {/* Logs */}
              <Route path="/logs" element={<LogsPage />} />

              {/* Redirect */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Layout>
        </ProtectedRoute>
      } />
    </Routes>
  );
}

function App() {
  return (
    <Router
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true
      }}
    >
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </Router>
  );
}

export default App;
