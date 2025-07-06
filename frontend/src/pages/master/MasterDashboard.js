import React from 'react';
import { Button, Menu, Layout } from 'antd';
import { UserOutlined, FileTextOutlined, BarChartOutlined, MessageOutlined, LogoutOutlined, DollarOutlined } from '@ant-design/icons';
import { useNavigate, Link, Routes, Route, Outlet, useLocation, Navigate } from 'react-router-dom';
import useAuth from '../../hooks/useAuth';
import ZayvkiMasterPage from '../ZayvkiMasterPage';
import StatistikaMasterPage from '../StatistikaMasterPage';
import FinansiMasterPage from '../FinansiMasterPage';
import ZayavkaMasterDetailPage from '../ZayavkaMasterDetailPage';
import LogoutPage from '../LogoutPage';
import MasterFeedbackPage from './MasterFeedbackPage';

const { Sider, Content } = Layout;

const menuItems = [
  { key: '/master-dashboard/profile', icon: <UserOutlined />, label: 'Профиль' },
  { key: '/master-dashboard/zayavki', icon: <FileTextOutlined />, label: 'Заявки' },
  { key: '/master-dashboard/stats', icon: <BarChartOutlined />, label: 'Статистика' },
  { key: '/master-dashboard/finansi', icon: <DollarOutlined />, label: 'Финансы' },
  { key: '/master-dashboard/feedback', icon: <MessageOutlined />, label: 'Обратная связь' },
];

function ProfilePage() {
  const { user } = useAuth();
  return user ? (
    <div style={{ maxWidth: 500 }}>
      <h2>Профиль мастера</h2>
      <div style={{ margin: '24px 0' }}>
        <b>ФИО:</b> {user.name}<br/>
        <b>Дата рождения:</b> {user.birth_date ? new Date(user.birth_date).toLocaleDateString() : '—'}<br/>
        <b>Телефон:</b> {user.phone || '—'}<br/>
        <b>Статус:</b> {user.is_active ? 'Работает' : 'Неактивен'}
      </div>
    </div>
  ) : <div>Нет данных о мастере</div>;
}

export default function MasterDashboard() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, loading } = useAuth();
  const selectedKey = menuItems.find(item => location.pathname.startsWith(item.key))?.key || '/master-dashboard/profile';

  if (!loading && !user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <Layout style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #e0e7ff 0%, #f8fafc 100%)' }}>
      <Sider width={220} style={{ background: '#fff', boxShadow: '2px 0 8px rgba(24,144,255,0.06)' }}>
        <div style={{ height: 64, display: 'flex', alignItems: 'center', justifyContent: 'center', borderBottom: '1px solid #f0f0f0', margin: '0 8px' }}>
          <h2 style={{ color: '#1890ff', margin: 0, fontSize: 20, fontWeight: 'bold' }}>Мастер</h2>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[selectedKey]}
          items={menuItems.map(item => ({ ...item, label: <Link to={item.key}>{item.label}</Link> }))}
          style={{ borderRight: 0, marginTop: 16 }}
        />
        <div style={{ margin: 16, marginTop: 'auto', position: 'absolute', bottom: 24, width: '80%' }}>
          <Button type="primary" icon={<LogoutOutlined />} block onClick={() => navigate('/master-dashboard/logout')}>
            Выйти
          </Button>
        </div>
      </Sider>
      <Content style={{ padding: 48, minHeight: '100vh', background: 'none' }}>
        <Routes>
          <Route path="profile" element={<div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}><div style={{ background: '#fff', borderRadius: 24, boxShadow: '0 8px 32px 0 rgba(24,144,255,0.12)', padding: '48px 36px', minWidth: 340, minHeight: 320, width: 420 }}><ProfilePage /></div></div>} />
          <Route path="zayavki" element={<ZayvkiMasterPage />} />
          <Route path="zayavki/:id" element={<ZayavkaMasterDetailPage />} />
          <Route path="stats" element={<StatistikaMasterPage />} />
          <Route path="finansi" element={<FinansiMasterPage />} />
          <Route path="logout" element={<LogoutPage />} />
          <Route path="feedback" element={<MasterFeedbackPage />} />
          <Route path="*" element={<div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}><div style={{ background: '#fff', borderRadius: 24, boxShadow: '0 8px 32px 0 rgba(24,144,255,0.12)', padding: '48px 36px', minWidth: 340, minHeight: 320, width: 420 }}><ProfilePage /></div></div>} />
        </Routes>
      </Content>
    </Layout>
  );
}

function FeedbackPage() {
  return <div><h2>Обратная связь</h2><p>Здесь можно отправить сообщение или пожелание.</p></div>;
} 