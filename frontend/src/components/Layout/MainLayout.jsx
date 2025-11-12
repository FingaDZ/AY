import { useState } from 'react';
import { Layout, Menu, Dropdown, Avatar, Space } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  UserOutlined,
  CalendarOutlined,
  TeamOutlined,
  CarOutlined,
  DollarOutlined,
  BankOutlined,
  CalculatorOutlined,
  FileTextOutlined,
  SettingOutlined,
  AuditOutlined,
  LogoutOutlined,
  DatabaseOutlined,
} from '@ant-design/icons';
import { useAuth } from '../../contexts/AuthContext';

const { Header, Sider, Content } = Layout;

const menuItems = [
  {
    key: '/',
    icon: <DashboardOutlined />,
    label: 'Tableau de Bord',
  },
  {
    key: '/employes',
    icon: <UserOutlined />,
    label: 'Employés',
  },
  {
    key: '/pointages',
    icon: <CalendarOutlined />,
    label: 'Pointages',
  },
  {
    key: '/clients',
    icon: <TeamOutlined />,
    label: 'Clients',
  },
  {
    key: '/missions',
    icon: <CarOutlined />,
    label: 'Missions',
  },
  {
    key: '/avances',
    icon: <DollarOutlined />,
    label: 'Avances',
  },
  {
    key: '/credits',
    icon: <BankOutlined />,
    label: 'Crédits',
  },
  {
    key: '/salaires',
    icon: <CalculatorOutlined />,
    label: 'Calcul Salaires',
  },
  {
    key: '/parametres',
    icon: <SettingOutlined />,
    label: 'Paramètres',
  },
  {
    key: '/database-config',
    icon: <DatabaseOutlined />,
    label: 'Base de Données',
  },
  {
    key: '/utilisateurs',
    icon: <UserOutlined />,
    label: 'Utilisateurs',
  },
  {
    key: '/logs',
    icon: <AuditOutlined />,
    label: 'Logs',
  },
];

function MainLayout({ children }) {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout, isAdmin } = useAuth();

  const handleMenuClick = ({ key }) => {
    navigate(key);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const userMenuItems = [
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Déconnexion',
      onClick: handleLogout,
    },
  ];

  // Filtrer les menus selon le rôle
  const filteredMenuItems = menuItems.filter(item => {
    // Les utilisateurs normaux n'ont accès qu'aux missions
    if (!isAdmin() && !['/missions', '/'].includes(item.key)) {
      return false;
    }
    return true;
  });

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed}>
        <div style={{ 
          height: 64, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          color: 'white',
          fontSize: collapsed ? 16 : 20,
          fontWeight: 'bold',
        }}>
          {collapsed ? 'AY' : 'AY HR'}
        </div>
        <Menu
          theme="dark"
          selectedKeys={[location.pathname]}
          mode="inline"
          items={filteredMenuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      <Layout>
        <Header style={{ 
          padding: '0 24px', 
          background: '#fff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}>
          <h1 style={{ margin: 0, fontSize: 24 }}>
            Gestion des Ressources Humaines
          </h1>
          <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
            <Space style={{ cursor: 'pointer' }}>
              <Avatar icon={<UserOutlined />} />
              <span>{user?.nom} {user?.prenom}</span>
              <span style={{ fontSize: 12, color: '#888' }}>({user?.role})</span>
            </Space>
          </Dropdown>
        </Header>
        <Content style={{ margin: '24px 16px', padding: 24, background: '#fff' }}>
          {children}
        </Content>
      </Layout>
    </Layout>
  );
}

export default MainLayout;
