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
import SalaireHistorique from './pages/Salaires/SalaireHistorique';
import ParametresPage from './pages/Parametres/ParametresPage';
import ParametresSalaires from './pages/Parametres/ParametresSalaires';
import DatabaseConfigPage from './pages/DatabaseConfig/DatabaseConfigPage';
import UtilisateursPage from './pages/Utilisateurs/UtilisateursPage';
import LogsPage from './pages/Logs/LogsPage';
import LoginPage from './pages/Login/LoginPage';
import ImportPreview from './pages/Pointages/ImportPreview';
import ProtectedAdminRoute from './components/ProtectedAdminRoute';
<ProtectedAdminRoute>
  <PostesList />
</ProtectedAdminRoute>
              } />

{/* Pointages - ADMIN ONLY */ }
              <Route path="/pointages" element={
                <ProtectedAdminRoute>
                  <GrillePointage />
                </ProtectedAdminRoute>
              } />
              <Route path="/pointages/import-preview" element={
                <ProtectedAdminRoute>
                  <ImportPreview />
                </ProtectedAdminRoute>
              } />

{/* Clients - Accessible à tous */ }
<Route path="/clients" element={<ClientsList />} />


{/* Avances - ADMIN ONLY */ }
<Route path="/avances" element={
  <ProtectedAdminRoute>
    <AvancesList />
  </ProtectedAdminRoute>
} />

{/* Crédits - ADMIN ONLY */ }
<Route path="/credits" element={
  <ProtectedAdminRoute>
    <CreditsList />
  </ProtectedAdminRoute>
} />

{/* Congés - ADMIN ONLY */ }
<Route path="/conges" element={
  <ProtectedAdminRoute>
    <CongesList />
  </ProtectedAdminRoute>
} />

{/* Salaires - ADMIN ONLY */ }
              <Route path="/salaires" element={
                <ProtectedAdminRoute>
                  <SalaireCalcul />
                </ProtectedAdminRoute>
              } />
              <Route path="/salaires/historique" element={
                <ProtectedAdminRoute>
                  <SalaireHistorique />
                </ProtectedAdminRoute>
              } />

{/* Paramètres - ADMIN ONLY */ }
              <Route path="/parametres" element={
                <ProtectedAdminRoute>
                  <ParametresPage />
                </ProtectedAdminRoute>
              } />
              <Route path="/parametres/salaires" element={
                <ProtectedAdminRoute>
                  <ParametresSalaires />
                </ProtectedAdminRoute>
              } />

{/* Configuration Base de Données - ADMIN ONLY */ }
<Route path="/database-config" element={
  <ProtectedAdminRoute>
    <DatabaseConfigPage />
  </ProtectedAdminRoute>
} />

{/* Utilisateurs - ADMIN ONLY */ }
<Route path="/utilisateurs" element={
  <ProtectedAdminRoute>
    <UtilisateursPage />
  </ProtectedAdminRoute>
} />

{/* Logs - ADMIN ONLY */ }
<Route path="/logs" element={
  <ProtectedAdminRoute>
    <LogsPage />
  </ProtectedAdminRoute>
} />

{/* Redirect */ }
<Route path="*" element={<Navigate to="/" replace />} />
            </Routes >
          </Layout >
        </ProtectedRoute >
      } />
    </Routes >
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
