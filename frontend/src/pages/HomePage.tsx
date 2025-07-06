import React, { useState } from 'react';
import { Card, Row, Col, Statistic, Typography } from 'antd';
import {
  UserOutlined,
  TeamOutlined,
  EnvironmentOutlined,
  FileTextOutlined,
  TransactionOutlined,
  SettingOutlined
} from '@ant-design/icons';
import { Link } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import { User } from '../types/entities';

const { Title, Paragraph } = Typography;

const cardStyle: React.CSSProperties = {
  textAlign: 'center',
  cursor: 'pointer',
  transition: 'box-shadow 0.2s',
};

const cardHoverStyle: React.CSSProperties = {
  boxShadow: '0 4px 16px rgba(24,144,255,0.10)',
};

const HomePage: React.FC = () => {
  const { user } = useAuth();
  const [hovered, setHovered] = useState<number | null>(null);
  const [quickHovered, setQuickHovered] = useState<number | null>(null);

  const typedUser = user as User | null;

  if (typedUser && typedUser.role === 'callcentre') {
    return (
      <div style={{ minHeight: '80vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ background: '#fff', padding: 32, borderRadius: 16, boxShadow: '0 4px 24px 0 rgba(24,144,255,0.08)', fontSize: 20, color: '#888', textAlign: 'center' }}>
          Доступно только:<br />
          <b>Заявки</b> и <b>Входящие заявки</b>
        </div>
      </div>
    );
  }

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24, color: '#1890ff' }}>
        Добро пожаловать в CRM Систему
      </Title>
      
      <Paragraph style={{ fontSize: 16, color: '#666', marginBottom: 32 }}>
        Управляйте заявками, мастерами, пользователями и транзакциями в единой системе
      </Paragraph>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={8}>
          <Link to="/zayavki" style={{ textDecoration: 'none' }}>
            <Card hoverable style={{ ...cardStyle, ...(hovered === 0 ? cardHoverStyle : {}) }} onMouseEnter={() => setHovered(0)} onMouseLeave={() => setHovered(null)}>
              <Statistic
                title="Заявки"
                value={0}
                prefix={<FileTextOutlined style={{ color: '#1890ff' }} />}
                valueStyle={{ color: '#1890ff' }}
              />
              <Paragraph style={{ marginTop: 8, color: '#666' }}>
                Управление заявками клиентов
              </Paragraph>
            </Card>
          </Link>
        </Col>
        
        <Col xs={24} sm={12} lg={8}>
          <Link to="/master" style={{ textDecoration: 'none' }}>
            <Card hoverable style={{ ...cardStyle, ...(hovered === 1 ? cardHoverStyle : {}) }} onMouseEnter={() => setHovered(1)} onMouseLeave={() => setHovered(null)}>
              <Statistic
                title="Мастера"
                value={0}
                prefix={<TeamOutlined style={{ color: '#52c41a' }} />}
                valueStyle={{ color: '#52c41a' }}
              />
              <Paragraph style={{ marginTop: 8, color: '#666' }}>
                База мастеров по городам
              </Paragraph>
            </Card>
          </Link>
        </Col>
        
        <Col xs={24} sm={12} lg={8}>
          <Link to="/polzovateli" style={{ textDecoration: 'none' }}>
            <Card hoverable style={{ ...cardStyle, ...(hovered === 2 ? cardHoverStyle : {}) }} onMouseEnter={() => setHovered(2)} onMouseLeave={() => setHovered(null)}>
              <Statistic
                title="Пользователи"
                value={0}
                prefix={<UserOutlined style={{ color: '#722ed1' }} />}
                valueStyle={{ color: '#722ed1' }}
              />
              <Paragraph style={{ marginTop: 8, color: '#666' }}>
                Система пользователей и ролей
              </Paragraph>
            </Card>
          </Link>
        </Col>
        
        <Col xs={24} sm={12} lg={8}>
          <Link to="/gorod" style={{ textDecoration: 'none' }}>
            <Card hoverable style={{ ...cardStyle, ...(hovered === 3 ? cardHoverStyle : {}) }} onMouseEnter={() => setHovered(3)} onMouseLeave={() => setHovered(null)}>
              <Statistic
                title="Города"
                value={0}
                prefix={<EnvironmentOutlined style={{ color: '#fa8c16' }} />}
                valueStyle={{ color: '#fa8c16' }}
              />
              <Paragraph style={{ marginTop: 8, color: '#666' }}>
                География работы
              </Paragraph>
            </Card>
          </Link>
        </Col>
        
        <Col xs={24} sm={12} lg={8}>
          <Link to="/tranzakcii" style={{ textDecoration: 'none' }}>
            <Card hoverable style={{ ...cardStyle, ...(hovered === 4 ? cardHoverStyle : {}) }} onMouseEnter={() => setHovered(4)} onMouseLeave={() => setHovered(null)}>
              <Statistic
                title="Транзакции"
                value={0}
                prefix={<TransactionOutlined style={{ color: '#eb2f96' }} />}
                valueStyle={{ color: '#eb2f96' }}
              />
              <Paragraph style={{ marginTop: 8, color: '#666' }}>
                Финансовые операции
              </Paragraph>
            </Card>
          </Link>
        </Col>
        
        <Col xs={24} sm={12} lg={8}>
          <Link to="/roli" style={{ textDecoration: 'none' }}>
            <Card hoverable style={{ ...cardStyle, ...(hovered === 5 ? cardHoverStyle : {}) }} onMouseEnter={() => setHovered(5)} onMouseLeave={() => setHovered(null)}>
              <Statistic
                title="Роли"
                value={0}
                prefix={<SettingOutlined style={{ color: '#13c2c2' }} />}
                valueStyle={{ color: '#13c2c2' }}
              />
              <Paragraph style={{ marginTop: 8, color: '#666' }}>
                Управление правами доступа
              </Paragraph>
            </Card>
          </Link>
        </Col>
      </Row>

      <Card style={{ marginTop: 32 }}>
        <Title level={4}>Быстрые действия</Title>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={8}>
            <Link to="/zayavki" style={{ textDecoration: 'none' }}>
              <Card size="small" hoverable style={{ ...cardStyle, ...(quickHovered === 0 ? cardHoverStyle : {}) }} onMouseEnter={() => setQuickHovered(0)} onMouseLeave={() => setQuickHovered(null)}>
                <FileTextOutlined style={{ fontSize: 32, color: '#1890ff', marginBottom: 8 }} />
                <div>Создать заявку</div>
              </Card>
            </Link>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Link to="/master" style={{ textDecoration: 'none' }}>
              <Card size="small" hoverable style={{ ...cardStyle, ...(quickHovered === 1 ? cardHoverStyle : {}) }} onMouseEnter={() => setQuickHovered(1)} onMouseLeave={() => setQuickHovered(null)}>
                <TeamOutlined style={{ fontSize: 32, color: '#52c41a', marginBottom: 8 }} />
                <div>Добавить мастера</div>
              </Card>
            </Link>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Link to="/polzovateli" style={{ textDecoration: 'none' }}>
              <Card size="small" hoverable style={{ ...cardStyle, ...(quickHovered === 2 ? cardHoverStyle : {}) }} onMouseEnter={() => setQuickHovered(2)} onMouseLeave={() => setQuickHovered(null)}>
                <UserOutlined style={{ fontSize: 32, color: '#722ed1', marginBottom: 8 }} />
                <div>Управление пользователями</div>
              </Card>
            </Link>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default HomePage; 