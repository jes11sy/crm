import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface LoginResponse {
  success: boolean;
  role?: string;
  error?: string;
}

const LoginPage: React.FC = () => {
  const [login, setLogin] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const loginRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      const res = await fetch('/api/v1/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ login, password }),
      });
      
      const data: LoginResponse = await res.json();
      
      if (data.success) {
        setLoading(false);
        window.location.replace(data.role === 'master' ? '/master-dashboard/profile' : '/');
      } else {
        setError(data.error || 'Ошибка авторизации');
        setLoading(false);
      }
    } catch {
      setError('Ошибка сети');
      setLoading(false);
    }
  };

  useEffect(() => {
    if (loginRef.current) {
      loginRef.current.focus();
    }
  }, []);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #e0e7ff 0%, #f8fafc 100%)' }}>
      <div style={{ position: 'relative', width: 370, maxWidth: '95vw', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        {/* <img src={logologin} alt="Логотип" style={{ width: 300, height: 300, objectFit: 'contain', borderRadius: 32, marginBottom: -56, zIndex: 2, boxShadow: 'none', background: 'none' }} /> */}
        <form
          onSubmit={handleSubmit}
          style={{
            minWidth: 280,
            maxWidth: 370,
            width: '100%',
            borderRadius: 18,
            boxShadow: '0 8px 32px 0 rgba(24,144,255,0.12)',
            padding: '38px 24px 24px 24px',
            background: '#fff',
            display: 'flex',
            flexDirection: 'column',
            gap: 20,
            marginTop: 0,
          }}
        >
          <h2 style={{ textAlign: 'center', marginBottom: 12, color: '#1890ff', fontWeight: 700, fontSize: 22, letterSpacing: 0.5 }}>Вход в систему</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <label style={{ fontWeight: 500, color: '#333' }}>Логин</label>
            <div style={{ position: 'relative' }}>
              <span style={{ position: 'absolute', left: 10, top: 10, color: '#bfbfbf', fontSize: 18 }}>
                <svg width="1em" height="1em" viewBox="0 0 24 24" fill="none"><path d="M12 12c2.7 0 8 1.34 8 4v2H4v-2c0-2.66 5.3-4 8-4Zm0-2a4 4 0 1 1 0-8 4 4 0 0 1 0 8Z" fill="#bfbfbf"/></svg>
              </span>
              <input
                ref={loginRef}
                type="text"
                value={login}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setLogin(e.target.value)}
                required
                style={{
                  width: '100%',
                  padding: '10px 10px 10px 38px',
                  border: error ? '1px solid #ff4d4f' : '1px solid #d9d9d9',
                  borderRadius: 8,
                  fontSize: 16,
                  outline: 'none',
                  transition: 'border 0.2s',
                  background: error ? '#fff1f0' : '#fff',
                }}
                placeholder="Введите логин"
                autoComplete="username"
              />
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <label style={{ fontWeight: 500, color: '#333' }}>Пароль</label>
            <div style={{ position: 'relative' }}>
              <span style={{ position: 'absolute', left: 10, top: 10, color: '#bfbfbf', fontSize: 18 }}>
                <svg width="1em" height="1em" viewBox="0 0 24 24" fill="none"><path d="M12 17a5 5 0 0 0 5-5V9a5 5 0 1 0-10 0v3a5 5 0 0 0 5 5Zm0 2c-3.31 0-10 1.66-10 5v2h20v-2c0-3.34-6.69-5-10-5Z" fill="#bfbfbf"/></svg>
              </span>
              <input
                type="password"
                value={password}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
                required
                style={{
                  width: '100%',
                  padding: '10px 10px 10px 38px',
                  border: error ? '1px solid #ff4d4f' : '1px solid #d9d9d9',
                  borderRadius: 8,
                  fontSize: 16,
                  outline: 'none',
                  transition: 'border 0.2s',
                  background: error ? '#fff1f0' : '#fff',
                }}
                placeholder="Введите пароль"
                autoComplete="current-password"
              />
            </div>
          </div>
          <button
            type="submit"
            disabled={loading}
            style={{
              background: '#1890ff',
              color: '#fff',
              border: 'none',
              borderRadius: 8,
              padding: '12px 0',
              fontSize: 16,
              fontWeight: 700,
              cursor: loading ? 'not-allowed' : 'pointer',
              boxShadow: loading ? 'none' : '0 2px 8px rgba(24,144,255,0.10)',
              opacity: loading ? 0.7 : 1,
              transition: 'all 0.2s',
              marginTop: 8,
            }}
          >
            {loading ? 'Входим...' : 'Войти'}
          </button>
          {error && <div style={{ color: '#ff4d4f', textAlign: 'center', marginTop: 8 }}>{error}</div>}
        </form>
      </div>
    </div>
  );
};

export default LoginPage; 