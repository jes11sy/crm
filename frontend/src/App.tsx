import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation, useNavigate, Navigate } from 'react-router-dom';
import { Layout, Menu, ConfigProvider, Button, Spin, Progress } from 'antd';
import { antdTheme, antdDarkTheme } from './utils/designSystem';
import {
  HomeOutlined,
  UserOutlined,
  TeamOutlined,
  EnvironmentOutlined,
  ProfileOutlined,
  FileTextOutlined,
  TransactionOutlined,
  SettingOutlined,
  CloudDownloadOutlined,
  SwapOutlined,
  BulbOutlined,
  BulbFilled
} from '@ant-design/icons';
import './App.css';
import useAuth from './hooks/useAuth';
import { usePreload } from './hooks/usePreload';
import { User } from './types/entities';

// Lazy loading для оптимизации размера бандла
const HomePage = lazy(() => import('./pages/HomePage'));
const GorodPage = lazy(() => import('./pages/GorodPage'));
const RKPage = lazy(() => import('./pages/RKPage'));
const MasterPage = lazy(() => import('./pages/MasterPage'));
const TipZayavkiPage = lazy(() => import('./pages/TipZayavkiPage'));
const ZayavkiPage = lazy(() => import('./pages/ZayavkiPage'));
const EditZayavkaPage = lazy(() => import('./pages/EditZayavkaPage'));
const PolzovateliPage = lazy(() => import('./pages/PolzovateliPage'));
const RoliPage = lazy(() => import('./pages/RoliPage'));
const TranzakciiPage = lazy(() => import('./pages/TranzakciiPage'));
const TipTranzakciiPage = lazy(() => import('./pages/TipTranzakciiPage'));
const VkhodyashchieZayavkiPage = lazy(() => import('./pages/VkhodyashchieZayavkiPage'));
const EditVkhodyashchayaZayavkaPage = lazy(() => import('./pages/EditVkhodyashchayaZayavkaPage'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const LogoutPage = lazy(() => import('./pages/LogoutPage'));
const KCStatsPage = lazy(() => import('./pages/KCStatsPage'));
const AvitoReportPage = lazy(() => import('./pages/AvitoReportPage'));
const CityReportPage = lazy(() => import('./pages/CityReportPage'));
const MasterReportPage = lazy(() => import('./pages/MasterReportPage'));
const KassaPage = lazy(() => import('./pages/KassaPage'));
const MangoImportPage = lazy(() => import('./pages/MangoImportPage'));
const MangoEmailPage = lazy(() => import('./pages/MangoEmailPage'));
const DirectorPayoutsPage = lazy(() => import('./pages/DirectorPayoutsPage'));
const MasterDashboard = lazy(() => import('./pages/master/MasterDashboard'));

const { Sider, Content } = Layout;

const menuItems = [
  {
    key: '/',
    icon: <HomeOutlined />,
    label: 'Главная',
  },
  {
    key: '/gorod',
    icon: <EnvironmentOutlined />,
    label: 'Города',
  },
  {
    key: '/rk',
    icon: <ProfileOutlined />,
    label: 'РК',
  },
  {
    key: '/master',
    icon: <TeamOutlined />,
    label: 'Мастера',
  },
  {
    key: '/tipzayavki',
    icon: <FileTextOutlined />,
    label: 'Типы заявок',
  },
  {
    key: '/zayavki',
    icon: <FileTextOutlined />,
    label: 'Заявки',
  },
  {
    key: '/vkhodyashchie-zayavki',
    icon: <FileTextOutlined />,
    label: 'Входящие заявки',
  },
  {
    key: '/mango-import',
    icon: <CloudDownloadOutlined />,
    label: 'Импорт Mango',
  },
  {
    key: '/mango-email',
    icon: <CloudDownloadOutlined />,
    label: 'Почта Mango',
  },
  {
    key: '/kc-stats',
    icon: <UserOutlined />,
    label: 'Статистика КЦ',
  },
  {
    key: '/polzovateli',
    icon: <UserOutlined />,
    label: 'Пользователи',
  },
  {
    key: '/roli',
    icon: <SettingOutlined />,
    label: 'Роли',
  },
  {
    key: '/tranzakcii',
    icon: <TransactionOutlined />,
    label: 'Транзакции',
  },
  {
    key: '/tiptranzakcii',
    icon: <TransactionOutlined />,
    label: 'Типы транзакций',
  },
  {
    key: '/avito-report',
    icon: <FileTextOutlined />,
    label: 'Отчет Авито',
  },
  {
    key: '/city-report',
    icon: <ProfileOutlined />,
    label: 'Отчет Города',
  },
  {
    key: '/master-report',
    icon: <TeamOutlined />,
    label: 'Отчет по Мастерам',
  },
  {
    key: '/kassa',
    icon: <TransactionOutlined />,
    label: 'Касса',
  },
];

// Используем единую дизайн-систему

function AppSidebar() {
  const location = useLocation();
  const [collapsed, setCollapsed] = React.useState(false);
  const navigate = useNavigate();
  const { user, loading } = useAuth();

  // Явно указываем тип user
  const typedUser = user as User | null;

  let filteredMenuItems = menuItems;
  if (typedUser && typedUser.role === 'callcentre') {
    filteredMenuItems = menuItems.filter(item =>
      item.key === '/zayavki' || item.key === '/vkhodyashchie-zayavki' || item.key === '/kc-stats'
    );
  }
  if (typedUser && typedUser.role === 'avitolog') {
    filteredMenuItems = menuItems.filter(item => item.key === '/avito-report');
  }
  if (typedUser && typedUser.role === 'director') {
    filteredMenuItems = menuItems.filter(item =>
      item.key === '/zayavki' || item.key === '/master' || item.key === '/tranzakcii' ||
      item.key === '/city-report' || item.key === '/master-report' || item.key === '/kassa'
    );
    filteredMenuItems.push({
      key: '/payouts',
      icon: <SwapOutlined />,
      label: 'Переводы',
    });
  }

  return (
    <Sider 
      collapsible 
      collapsed={collapsed} 
      onCollapse={setCollapsed}
      theme="light"
      style={{
        boxShadow: '2px 0 8px rgba(0,0,0,0.1)',
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
      }}
    >
      <div style={{ 
        height: 64, 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        borderBottom: '1px solid #f0f0f0',
        margin: '0 16px'
      }}>
        <h2 style={{ 
          color: '#1890ff', 
          margin: 0, 
          fontSize: collapsed ? 16 : 20,
          fontWeight: 'bold'
        }}>
          {collapsed ? 'CRM' : 'CRM Система'}
        </h2>
      </div>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={filteredMenuItems}
          style={{ borderRight: 0, flex: 1 }}
          onClick={({ key }) => navigate(key)}
        />
        <div style={{ margin: 16, marginTop: 'auto' }}>
          <Button type="primary" block onClick={() => navigate('/logout')}>
            Выйти
          </Button>
          {!loading && typedUser && (
            <div style={{ marginTop: 12, textAlign: 'center', color: '#888', fontSize: 14 }}>
              <div>В системе: <b>{typedUser.name}</b></div>
              <div>Роль: <b>{typedUser.role || '—'}</b></div>
            </div>
          )}
        </div>
      </div>
    </Sider>
  );
}

function ThemeToggle({ theme, setTheme }: { theme: 'light' | 'dark', setTheme: (t: 'light' | 'dark') => void }) {
  return (
    <Button
      type="text"
      icon={theme === 'dark' ? <BulbFilled /> : <BulbOutlined />}
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
      style={{ fontSize: 20 }}
      aria-label="Переключить тему"
    >
      {theme === 'dark' ? 'Тёмная' : 'Светлая'}
    </Button>
  );
}

// Типизация для ProtectedRoute
interface ProtectedRouteProps {
  children: React.ReactNode;
}

function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuth, loading, user } = useAuth();
  const location = useLocation();
  const typedUser = user as User | null;
  if (loading) return <div style={{display:'flex',justifyContent:'center',alignItems:'center',height:'80vh'}}><Spin size="large" /></div>;
  if (!isAuth) return <Navigate to="/login" state={{ from: location }} replace />;
  if (typedUser && typedUser.role === 'callcentre') {
    const allowed = ['/zayavki', '/vkhodyashchie-zayavki', '/kc-stats'];
    if (!allowed.some(path => location.pathname.startsWith(path))) {
      return <Navigate to="/zayavki" replace />;
    }
  }
  if (typedUser && typedUser.role === 'avitolog') {
    if (!location.pathname.startsWith('/avito-report')) {
      return <Navigate to="/avito-report" replace />;
    }
  }
  if (typedUser && typedUser.role === 'director') {
    const allowed = ['/zayavki', '/master', '/tranzakcii', '/city-report', '/master-report', '/kassa', '/payouts'];
    if (!allowed.some(path => location.pathname.startsWith(path))) {
      return <Navigate to="/zayavki" replace />;
    }
  }
  if (typedUser && typedUser.role === 'master') {
    return (
      <Suspense fallback={<div style={{display:'flex',justifyContent:'center',alignItems:'center',height:'80vh'}}><Spin size="large" /></div>}>
        <Routes>
          <Route path="/master-dashboard/*" element={<MasterDashboard />} />
          <Route path="*" element={<Navigate to="/master-dashboard" replace />} />
        </Routes>
      </Suspense>
    );
  }
  return <>{children}</>;
}

// Улучшенный компонент загрузки
const LoadingSpinner: React.FC = () => (
  <div style={{
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    height: '50vh',
    gap: '16px'
  }}>
    <Spin size="large" />
    <div style={{ textAlign: 'center' }}>
      <h3>Загрузка...</h3>
      <p>Пожалуйста, подождите</p>
      <Progress percent={75} status="active" style={{ width: 200 }} />
    </div>
  </div>
);

function AppLayout() {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) return <div style={{display:'flex',justifyContent:'center',alignItems:'center',height:'80vh'}}><Spin size="large" /></div>;

  // Только мастер — отдельный роутинг
  if (user && user.role === 'master') {
    return (
      <Suspense fallback={<div style={{display:'flex',justifyContent:'center',alignItems:'center',height:'80vh'}}><Spin size="large" /></div>}>
        <Routes>
          <Route path="/master-dashboard/*" element={<MasterDashboard />} />
          <Route path="*" element={<Navigate to="/master-dashboard/profile" replace />} />
        </Routes>
      </Suspense>
    );
  }

  // Для не-мастеров: если пытаются попасть на /master-dashboard — редирект на главную
  if (location.pathname.startsWith('/master-dashboard')) {
    return <Navigate to="/" replace />;
  }

  // Sidebar и CRM-Layout для остальных
  const showSidebar = location.pathname !== '/login' && location.pathname !== '/master-dashboard';

  return (
    <ConfigProvider theme={antdTheme}>
      <Layout style={{ minHeight: '100vh' }}>
        {showSidebar && <AppSidebar />}
        <Layout>
          <Content style={{ margin: '24px 16px 0' }}>
            <Suspense fallback={<LoadingSpinner />}>
              <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/logout" element={<LogoutPage />} />
                <Route path="/" element={<ProtectedRoute><HomePage /></ProtectedRoute>} />
                <Route path="/gorod" element={<ProtectedRoute><GorodPage /></ProtectedRoute>} />
                <Route path="/rk" element={<ProtectedRoute><RKPage /></ProtectedRoute>} />
                <Route path="/master" element={<ProtectedRoute><MasterPage /></ProtectedRoute>} />
                <Route path="/tipzayavki" element={<ProtectedRoute><TipZayavkiPage /></ProtectedRoute>} />
                <Route path="/zayavki" element={<ProtectedRoute><ZayavkiPage /></ProtectedRoute>} />
                <Route path="/zayavki/:id" element={<ProtectedRoute><EditZayavkaPage /></ProtectedRoute>} />
                <Route path="/polzovateli" element={<ProtectedRoute><PolzovateliPage /></ProtectedRoute>} />
                <Route path="/roli" element={<ProtectedRoute><RoliPage /></ProtectedRoute>} />
                <Route path="/tranzakcii" element={<ProtectedRoute><TranzakciiPage /></ProtectedRoute>} />
                <Route path="/tiptranzakcii" element={<ProtectedRoute><TipTranzakciiPage /></ProtectedRoute>} />
                <Route path="/vkhodyashchie-zayavki" element={<ProtectedRoute><VkhodyashchieZayavkiPage /></ProtectedRoute>} />
                <Route path="/vkhodyashchie-zayavki/:id" element={<ProtectedRoute><EditVkhodyashchayaZayavkaPage /></ProtectedRoute>} />
                <Route path="/kc-stats" element={<ProtectedRoute><KCStatsPage /></ProtectedRoute>} />
                <Route path="/avito-report" element={<ProtectedRoute><AvitoReportPage /></ProtectedRoute>} />
                <Route path="/city-report" element={<ProtectedRoute><CityReportPage /></ProtectedRoute>} />
                <Route path="/master-report" element={<ProtectedRoute><MasterReportPage /></ProtectedRoute>} />
                <Route path="/kassa" element={<ProtectedRoute><KassaPage /></ProtectedRoute>} />
                <Route path="/mango-import" element={<ProtectedRoute><MangoImportPage /></ProtectedRoute>} />
                <Route path="/mango-email" element={<ProtectedRoute><MangoEmailPage /></ProtectedRoute>} />
                <Route path="/payouts" element={<ProtectedRoute><DirectorPayoutsPage /></ProtectedRoute>} />
              </Routes>
            </Suspense>
          </Content>
        </Layout>
      </Layout>
    </ConfigProvider>
  );
}

export default function App() {
  // Состояние темы: light/dark, сохраняем в localStorage
  const [theme, setTheme] = React.useState<'light' | 'dark'>(() => {
    const saved = localStorage.getItem('theme');
    return saved === 'dark' ? 'dark' : 'light';
  });
  
  // Preload критических страниц
  usePreload();
  
  React.useEffect(() => {
    localStorage.setItem('theme', theme);
    document.body.setAttribute('data-theme', theme);
  }, [theme]);

  return (
    <ConfigProvider theme={theme === 'dark' ? antdDarkTheme : antdTheme}>
      <Router>
        <Layout style={{ minHeight: '100vh' }}>
          {/* Шапка с переключателем темы */}
          <Layout.Header style={{ background: 'none', display: 'flex', justifyContent: 'flex-end', alignItems: 'center', height: 56 }}>
            <ThemeToggle theme={theme} setTheme={setTheme} />
          </Layout.Header>
          {/* Основной контент */}
          <Layout>
            <AppSidebar />
            <Layout style={{ background: 'none' }}>
              <Content style={{ margin: '24px 16px 0', minHeight: 280 }}>
                <Suspense fallback={<LoadingSpinner />}>
                  <Routes>
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/logout" element={<LogoutPage />} />
                    <Route path="/" element={<ProtectedRoute><HomePage /></ProtectedRoute>} />
                    <Route path="/gorod" element={<ProtectedRoute><GorodPage /></ProtectedRoute>} />
                    <Route path="/rk" element={<ProtectedRoute><RKPage /></ProtectedRoute>} />
                    <Route path="/master" element={<ProtectedRoute><MasterPage /></ProtectedRoute>} />
                    <Route path="/tipzayavki" element={<ProtectedRoute><TipZayavkiPage /></ProtectedRoute>} />
                    <Route path="/zayavki" element={<ProtectedRoute><ZayavkiPage /></ProtectedRoute>} />
                    <Route path="/zayavki/:id" element={<ProtectedRoute><EditZayavkaPage /></ProtectedRoute>} />
                    <Route path="/polzovateli" element={<ProtectedRoute><PolzovateliPage /></ProtectedRoute>} />
                    <Route path="/roli" element={<ProtectedRoute><RoliPage /></ProtectedRoute>} />
                    <Route path="/tranzakcii" element={<ProtectedRoute><TranzakciiPage /></ProtectedRoute>} />
                    <Route path="/tiptranzakcii" element={<ProtectedRoute><TipTranzakciiPage /></ProtectedRoute>} />
                    <Route path="/vkhodyashchie-zayavki" element={<ProtectedRoute><VkhodyashchieZayavkiPage /></ProtectedRoute>} />
                    <Route path="/vkhodyashchie-zayavki/:id" element={<ProtectedRoute><EditVkhodyashchayaZayavkaPage /></ProtectedRoute>} />
                    <Route path="/kc-stats" element={<ProtectedRoute><KCStatsPage /></ProtectedRoute>} />
                    <Route path="/avito-report" element={<ProtectedRoute><AvitoReportPage /></ProtectedRoute>} />
                    <Route path="/city-report" element={<ProtectedRoute><CityReportPage /></ProtectedRoute>} />
                    <Route path="/master-report" element={<ProtectedRoute><MasterReportPage /></ProtectedRoute>} />
                    <Route path="/kassa" element={<ProtectedRoute><KassaPage /></ProtectedRoute>} />
                    <Route path="/mango-import" element={<ProtectedRoute><MangoImportPage /></ProtectedRoute>} />
                    <Route path="/mango-email" element={<ProtectedRoute><MangoEmailPage /></ProtectedRoute>} />
                    <Route path="/payouts" element={<ProtectedRoute><DirectorPayoutsPage /></ProtectedRoute>} />
                  </Routes>
                </Suspense>
              </Content>
            </Layout>
          </Layout>
        </Layout>
      </Router>
    </ConfigProvider>
  );
}
