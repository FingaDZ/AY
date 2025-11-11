import { useState } from 'react';
import { Layout, Menu } from 'antd';
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
} from '@ant-design/icons';

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
    key: '/rapports',
    icon: <FileTextOutlined />,
    label: 'Rapports',
  },
];

function MainLayout({ children }) {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const handleMenuClick = ({ key }) => {
    navigate(key);
  };

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
          items={menuItems}
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
        </Header>
        <Content style={{ margin: '24px 16px', padding: 24, background: '#fff' }}>
          {children}
        </Content>
      </Layout>
    </Layout>
  );
}

export default MainLayout;
