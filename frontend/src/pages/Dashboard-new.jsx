import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Users, 
  Briefcase, 
  Clock, 
  DollarSign, 
  CreditCard, 
  Car 
} from 'lucide-react';
import { 
  employeService, 
  clientService, 
  pointageService,
  avanceService,
  creditService,
  missionService 
} from '../services';

function Dashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    employes: 0,
    clients: 0,
    pointages: 0,
    avances: 0,
    credits: 0,
    missions: 0,
  });

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const [employes, clients, pointages, avances, credits, missions] = await Promise.all([
        employeService.getAll(),
        clientService.getAll(),
        pointageService.getAll(),
        avanceService.getAll(),
        creditService.getAll(),
        missionService.getAll(),
      ]);

      setStats({
        employes: employes.data.total || employes.data.length || 0,
        clients: clients.data.total || clients.data.length || 0,
        pointages: pointages.data.total || pointages.data.length || 0,
        avances: avances.data.total || avances.data.length || 0,
        credits: credits.data.total || credits.data.length || 0,
        missions: missions.data.total || missions.data.length || 0,
      });
    } catch (error) {
      console.error('Erreur chargement stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const cards = [
    { title: 'Employés', value: stats.employes, icon: Users, color: 'blue', link: '/employes' },
    { title: 'Clients', value: stats.clients, icon: Briefcase, color: 'green', link: '/clients' },
    { title: 'Pointages', value: stats.pointages, icon: Clock, color: 'orange', link: '/pointages' },
    { title: 'Avances', value: stats.avances, icon: DollarSign, color: 'red', link: '/avances' },
    { title: 'Crédits', value: stats.credits, icon: CreditCard, color: 'purple', link: '/credits' },
    { title: 'Missions', value: stats.missions, icon: Car, color: 'indigo', link: '/missions' },
  ];

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Dashboard</h1>
          <p className="text-gray-500 mt-1">Vue d'ensemble du système AY HR</p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {cards.map((card) => {
          const Icon = card.icon;
          return (
            <div
              key={card.title}
              onClick={() => navigate(card.link)}
              className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 cursor-pointer hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-gray-500 text-sm font-medium">{card.title}</h3>
                <Icon className={`text-${card.color}-500 w-6 h-6`} />
              </div>
              <p className="text-3xl font-bold text-gray-800">{card.value}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default Dashboard;
