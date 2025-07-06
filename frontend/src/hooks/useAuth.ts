import { useEffect, useState } from 'react';
import axios from 'axios';
import { User } from '../types/entities';

interface AuthState {
  user: User | null;
  loading: boolean;
  isAuth: boolean;
}

interface UseAuthReturn extends AuthState {
  logout: () => void;
}

export default function useAuth(): UseAuthReturn {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [isAuth, setIsAuth] = useState<boolean>(false);

  useEffect(() => {
    let mounted = true;
    axios.get('/api/v1/me/', { withCredentials: true })
      .then((res) => {
        if (mounted) {
          setUser(res.data as User);
          setIsAuth(true);
        }
      })
      .catch(() => {
        if (mounted) {
          setUser(null);
          setIsAuth(false);
        }
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => { mounted = false; };
  }, []);

  const logout = (): void => {
    setUser(null);
    setLoading(false);
    setIsAuth(false);
  };

  return { user, loading, isAuth, logout };
} 