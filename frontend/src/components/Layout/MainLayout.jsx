import { useState, useEffect } from 'react';
import { Layout, Menu, Dropdown, Avatar, Space, Drawer, Button } from 'antd';
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
  IdcardOutlined,
  MenuOutlined,
} from '@ant-design/icons';
import { useAuth } from '../../contexts/AuthContext';
import parametresService from '../../services/parametres';
import useResponsive from '../../hooks/useResponsive';

const { Header, Sider, Content, Footer } = Layout;

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
    key: '/postes',
    icon: <IdcardOutlined />,
    label: 'Postes',
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
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [companyInitials, setCompanyInitials] = useState('AY');
  const [companyName, setCompanyName] = useState('AY HR');
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout, isAdmin } = useAuth();
  const { isMobile, isTablet } = useResponsive();

  useEffect(() => {
    fetchCompanyInfo();
  }, []);

  const fetchCompanyInfo = async () => {
    try {
      const response = await parametresService.getParametres();
      
      // Vérifier que response existe (le service retourne déjà response.data)
      if (!response) {
        console.warn('Réponse API paramètres vide, utilisation des valeurs par défaut');
        setCompanyName('AY HR');
        setCompanyInitials('AY');
        return;
      }
      
      const params = response;
      
      // Utiliser raison_sociale en priorité, sinon nom_entreprise
      const name = params.raison_sociale || params.nom_entreprise || 'AY HR';
      setCompanyName(name);
      
      // Générer les initiales à partir du nom
      const initials = name
        .split(' ')
        .map(word => word[0])
        .join('')
        .substring(0, 3)
        .toUpperCase();
      
      setCompanyInitials(initials);
    } catch (error) {
      console.error('Erreur lors de la récupération des paramètres:', error);
      // Valeurs par défaut en cas d'erreur
      setCompanyName('AY HR');
      setCompanyInitials('AY');
    }
  };

  const handleMenuClick = ({ key }) => {
    navigate(key);
    if (isMobile) {
      setDrawerVisible(false);
    }
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

  const menuComponent = (
    <Menu
      theme="dark"
      selectedKeys={[location.pathname]}
      mode={isMobile ? "inline" : "inline"}
      items={filteredMenuItems}
      onClick={handleMenuClick}
    />
  );

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* Sidebar pour Desktop/Tablette */}
      {!isMobile && (
        <Sider 
          collapsible={!isTablet} 
          collapsed={collapsed && !isTablet} 
          onCollapse={setCollapsed}
          breakpoint="lg"
          collapsedWidth={isTablet ? 80 : 80}
          width={isTablet ? 200 : 250}
          style={{
            overflow: 'auto',
            height: '100vh',
            position: 'fixed',
            left: 0,
            top: 0,
            bottom: 0,
          }}
        >
          <div style={{ 
            height: 64, 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            color: 'white',
            fontSize: collapsed && !isTablet ? 16 : 20,
            fontWeight: 'bold',
            padding: '0 16px',
          }}>
            {collapsed && !isTablet ? companyInitials : companyName}
          </div>
          {menuComponent}
        </Sider>
      )}

      {/* Drawer pour Mobile */}
      {isMobile && (
        <Drawer
          title={companyName}
          placement="left"
          onClose={() => setDrawerVisible(false)}
          open={drawerVisible}
          bodyStyle={{ padding: 0, backgroundColor: '#001529' }}
          headerStyle={{ backgroundColor: '#001529', color: 'white', borderBottom: '1px solid #002140' }}
          width={280}
          style={{ width: '100%', maxWidth: '280px' }}
          contentWrapperStyle={{ width: '280px', maxWidth: '90vw' }}
        >
          {menuComponent}
        </Drawer>
      )}

      <Layout style={{ 
        marginLeft: isMobile ? 0 : (isTablet ? 200 : (collapsed ? 80 : 250)),
        transition: 'margin-left 0.2s',
        ...(isMobile && {
          width: '100% !important',
          maxWidth: '100vw !important'
        })
      }}>
        <Header style={{ 
          padding: isMobile ? '0 16px' : '0 24px', 
          background: '#fff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          position: 'sticky',
          top: 0,
          zIndex: 1,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            {isMobile && (
              <Button
                type="text"
                icon={<MenuOutlined />}
                onClick={() => setDrawerVisible(true)}
                style={{ fontSize: 20 }}
              />
            )}
            <h1 style={{ margin: 0, fontSize: isMobile ? 16 : 24 }}>
              {isMobile ? 'AY HR' : 'Gestion des Ressources Humaines'}
            </h1>
          </div>
          <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
            <Space style={{ cursor: 'pointer' }}>
              <Avatar icon={<UserOutlined />} />
              {!isMobile && (
                <>
                  <span>{user?.nom} {user?.prenom}</span>
                  <span style={{ fontSize: 12, color: '#888' }}>({user?.role})</span>
                </>
              )}
            </Space>
          </Dropdown>
        </Header>
        <Content style={{ 
          margin: isMobile ? '12px' : '24px 16px', 
          padding: isMobile ? 12 : 24, 
          background: '#fff',
          minHeight: 280,
          ...(isMobile && {
            margin: '12px !important',
            padding: '12px !important',
            width: '100%',
            maxWidth: '100vw',
            overflowX: 'hidden'
          })
        }}>
          {children}
        </Content>
        <Footer style={{ 
          textAlign: 'center', 
          padding: isMobile ? '8px 16px' : '12px 50px',
          color: '#888',
          fontSize: isMobile ? '10px' : '12px'
        }}>
          Powered by AIRBAND
        </Footer>
      </Layout>
    </Layout>
  );
}

export default MainLayout;
