import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Layout, Spin } from 'antd';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import MainLayout from './components/Layout/MainLayout';
import Dashboard from './pages/Dashboard';
import EmployesList from './pages/Employes/EmployesList';
import EmployeForm from './pages/Employes/EmployeForm';
import GrillePointage from './pages/Pointages/GrillePointage';
import ClientsList from './pages/Clients/ClientsList';
import MissionsList from './pages/Missions/MissionsList';
import AvancesList from './pages/Avances/AvancesList';
import CreditsList from './pages/Credits/CreditsList';
import SalaireCalcul from './pages/Salaires/SalaireCalcul';
import Rapports from './pages/Rapports/Rapports';
import RapportsPage from './pages/Rapports/RapportsPage';
import ParametresPage from './pages/Parametres/ParametresPage';
import UtilisateursPage from './pages/Utilisateurs/UtilisateursPage';
import LogsPage from './pages/Logs/LogsPage';
import LoginPage from './pages/Login/LoginPage';

// Composant pour protéger les routes
function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
      <Spin size="large" />
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
          <MainLayout>
            <Routes>
          <Route path="/" element={<Dashboard />} />
          
          {/* Employés */}
          <Route path="/employes" element={<EmployesList />} />
          <Route path="/employes/nouveau" element={<EmployeForm />} />
          <Route path="/employes/:id" element={<EmployeForm />} />
          
          {/* Pointages - Vue grille uniquement */}
          <Route path="/pointages" element={<GrillePointage />} />
          
          {/* Clients */}
          <Route path="/clients" element={<ClientsList />} />
          
          {/* Missions */}
          <Route path="/missions" element={<MissionsList />} />
          
          {/* Avances */}
          <Route path="/avances" element={<AvancesList />} />
          
          {/* Crédits */}
          <Route path="/credits" element={<CreditsList />} />
          
          {/* Salaires */}
          <Route path="/salaires" element={<SalaireCalcul />} />
          
          {/* Rapports */}
          <Route path="/rapports" element={<Rapports />} />
          <Route path="/rapports/centre" element={<RapportsPage />} />
          
          {/* Paramètres */}
          <Route path="/parametres" element={<ParametresPage />} />
          
          {/* Utilisateurs */}
          <Route path="/utilisateurs" element={<UtilisateursPage />} />
          
          {/* Logs */}
          <Route path="/logs" element={<LogsPage />} />
          
              {/* Redirect */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </MainLayout>
        </ProtectedRoute>
      } />
    </Routes>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </Router>
  );
}

export default App;
