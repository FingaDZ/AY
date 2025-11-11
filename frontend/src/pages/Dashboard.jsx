import { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Spin, message } from 'antd';
import {
  UserOutlined,
  TeamOutlined,
  CalendarOutlined,
  DollarOutlined,
  BankOutlined,
  CarOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
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
        employes: employes.data.total || 0,
        clients: Array.isArray(clients.data) ? clients.data.length : 0,
        pointages: Array.isArray(pointages.data) ? pointages.data.length : 0,
        avances: Array.isArray(avances.data) ? avances.data.length : 0,
        credits: Array.isArray(credits.data) ? credits.data.length : 0,
        missions: Array.isArray(missions.data) ? missions.data.length : 0,
      });
    } catch (error) {
      message.error('Erreur lors du chargement des statistiques');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const statsCards = [
    {
      title: 'Employés',
      value: stats.employes,
      icon: <UserOutlined style={{ fontSize: 32, color: '#1890ff' }} />,
      color: '#1890ff',
      path: '/employes',
    },
    {
      title: 'Clients',
      value: stats.clients,
      icon: <TeamOutlined style={{ fontSize: 32, color: '#52c41a' }} />,
      color: '#52c41a',
      path: '/clients',
    },
    {
      title: 'Pointages',
      value: stats.pointages,
      icon: <CalendarOutlined style={{ fontSize: 32, color: '#faad14' }} />,
      color: '#faad14',
      path: '/pointages',
    },
    {
      title: 'Missions',
      value: stats.missions,
      icon: <CarOutlined style={{ fontSize: 32, color: '#722ed1' }} />,
      color: '#722ed1',
      path: '/missions',
    },
    {
      title: 'Avances',
      value: stats.avances,
      icon: <DollarOutlined style={{ fontSize: 32, color: '#eb2f96' }} />,
      color: '#eb2f96',
      path: '/avances',
    },
    {
      title: 'Crédits',
      value: stats.credits,
      icon: <BankOutlined style={{ fontSize: 32, color: '#13c2c2' }} />,
      color: '#13c2c2',
      path: '/credits',
    },
  ];

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: 50 }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>Tableau de Bord</h2>
      <Row gutter={[16, 16]}>
        {statsCards.map((stat, index) => (
          <Col xs={24} sm={12} lg={8} key={index}>
            <Card 
              hoverable
              className="stats-card"
              onClick={() => navigate(stat.path)}
              style={{ borderTop: `4px solid ${stat.color}` }}
            >
              <Statistic
                title={stat.title}
                value={stat.value}
                prefix={stat.icon}
                valueStyle={{ color: stat.color }}
              />
            </Card>
          </Col>
        ))}
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col span={24}>
          <Card title="Actions Rapides">
            <Row gutter={16}>
              <Col span={8}>
                <Card
                  hoverable
                  onClick={() => navigate('/employes/nouveau')}
                  style={{ textAlign: 'center' }}
                >
                  <UserOutlined style={{ fontSize: 32, marginBottom: 8 }} />
                  <p>Nouvel Employé</p>
                </Card>
              </Col>
              <Col span={8}>
                <Card
                  hoverable
                  onClick={() => navigate('/pointages/nouveau')}
                  style={{ textAlign: 'center' }}
                >
                  <CalendarOutlined style={{ fontSize: 32, marginBottom: 8 }} />
                  <p>Nouveau Pointage</p>
                </Card>
              </Col>
              <Col span={8}>
                <Card
                  hoverable
                  onClick={() => navigate('/salaires')}
                  style={{ textAlign: 'center' }}
                >
                  <DollarOutlined style={{ fontSize: 32, marginBottom: 8 }} />
                  <p>Calculer Salaires</p>
                </Card>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default Dashboard;
