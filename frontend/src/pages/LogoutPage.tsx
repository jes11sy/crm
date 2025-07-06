import { useEffect } from 'react';
import { message } from 'antd';
import axios from 'axios';
import useAuth from '../hooks/useAuth';

const LogoutPage: React.FC = () => {
  const { logout } = useAuth();
  
  useEffect(() => {
    axios.post('/api/v1/logout/', {}, { withCredentials: true })
      .then(() => {
        logout();
        message.success('Вы вышли из системы');
        window.location.replace('/login');
      })
      .catch(() => {
        logout();
        message.error('Ошибка при выходе');
        window.location.replace('/login');
      });
  }, [logout]);
  
  return null;
};

export default LogoutPage; 