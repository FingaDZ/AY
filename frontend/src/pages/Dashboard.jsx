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
import Card from '../components/Card';
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
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Dashboard</h1>
          <p className="text-gray-500 mt-1">Vue d'ensemble du système AY HR <span className="text-xs ml-2 px-2 py-1 bg-blue-100 text-blue-600 rounded-full">v3.5.3</span></p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {cards.map((card) => {
          const Icon = card.icon;
          const colorMap = {
            blue: 'text-blue-500',
            green: 'text-green-500',
            orange: 'text-orange-500',
            red: 'text-red-500',
            purple: 'text-purple-500',
            indigo: 'text-indigo-500',
          };
          return (
            <div
              key={card.title}
              onClick={() => navigate(card.link)}
              className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 cursor-pointer hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-gray-500 text-sm font-medium">{card.title}</h3>
                <Icon className={`${colorMap[card.color]} w-6 h-6`} />
              </div>
              <p className="text-3xl font-bold text-gray-800">{card.value}</p>
            </div>
          );
        })}
      </div>

      <Card title="Actions Rapides">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div
            onClick={() => navigate('/employes/nouveau')}
            className="p-6 border border-gray-200 rounded-lg text-center cursor-pointer hover:bg-gray-50 transition-colors"
          >
            <Users className="w-8 h-8 mx-auto mb-2 text-blue-500" />
            <p className="font-medium text-gray-800">Nouvel Employé</p>
          </div>
          <div
            onClick={() => navigate('/pointages')}
            className="p-6 border border-gray-200 rounded-lg text-center cursor-pointer hover:bg-gray-50 transition-colors"
          >
            <Clock className="w-8 h-8 mx-auto mb-2 text-orange-500" />
            <p className="font-medium text-gray-800">Gestion Pointages</p>
          </div>
          <div
            onClick={() => navigate('/salaires')}
            className="p-6 border border-gray-200 rounded-lg text-center cursor-pointer hover:bg-gray-50 transition-colors"
          >
            <DollarSign className="w-8 h-8 mx-auto mb-2 text-green-500" />
            <p className="font-medium text-gray-800">Calculer Salaires</p>
          </div>
        </div>
      </Card>
    </div>
  );
}

export default Dashboard;
