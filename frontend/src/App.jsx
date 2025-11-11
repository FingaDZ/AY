import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from 'antd';
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

function App() {
  return (
    <Router>
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
          
          {/* Redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </MainLayout>
    </Router>
  );
}

export default App;
