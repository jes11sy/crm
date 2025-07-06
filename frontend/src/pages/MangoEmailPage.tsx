import React, { useState, useEffect } from 'react';
import useAuth from '../hooks/useAuth';
import api from '../utils/api';
import './MangoEmailPage.css';

interface FormData {
  email: string;
  password: string;
  imap_server: string;
  imap_port: number;
  download_dir: string;
  dry_run: boolean;
}

interface ServerInfo {
  server: string;
  port: number;
  note: string;
}

interface ServerInfoResponse {
  supported_imap_servers: Record<string, ServerInfo>;
}

interface ProcessingResult {
  success: boolean;
  message?: string;
  error?: string;
  output?: string;
}

const MangoEmailPage: React.FC = () => {
  const { user, isAuth } = useAuth();
  const [formData, setFormData] = useState<FormData>({
    email: '',
    password: '',
    imap_server: 'imap.gmail.com',
    imap_port: 993,
    download_dir: 'media/audio',
    dry_run: true
  });
  const [serverInfo, setServerInfo] = useState<ServerInfoResponse | null>(null);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [result, setResult] = useState<ProcessingResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadServerInfo();
  }, []);

  const loadServerInfo = async (): Promise<void> => {
    try {
      const response = await api.get<ServerInfoResponse>('/mango/email-processing/');
      setServerInfo(response.data);
    } catch (err) {
      console.error('Ошибка при загрузке информации о серверах:', err);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleServerChange = (e: React.ChangeEvent<HTMLSelectElement>): void => {
    const selectedServer = e.target.value;
    const server = serverInfo?.supported_imap_servers[selectedServer];
    
    if (server) {
      setFormData(prev => ({
        ...prev,
        imap_server: server.server,
        imap_port: server.port
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    setIsProcessing(true);
    setResult(null);
    setError(null);

    try {
      const response = await api.post<ProcessingResult>('/mango/email-processing/', formData);
      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Произошла ошибка при обработке писем');
    } finally {
      setIsProcessing(false);
    }
  };

  const formatOutput = (output: string): React.JSX.Element[] => {
    if (!output) return [];
    return output.split('\n').map((line, index) => (
      <div key={index} className="output-line">
        {line}
      </div>
    ));
  };

  if (!isAuth) {
    return <div className="mango-email-page">Необходима авторизация</div>;
  }

  return (
    <div className="mango-email-page">
      <div className="mango-email-container">
        <h1>Обработка писем с записями Mango Office</h1>
        
        <div className="info-section">
          <h3>Информация</h3>
          <p>
            Эта функция позволяет автоматически обрабатывать письма с аудиозаписями звонков, 
            отправляемые Mango Office на указанный email адрес.
          </p>
          <p>
            <strong>Как настроить:</strong>
          </p>
          <ol>
            <li>В настройках Mango Office включите отправку записей на email</li>
            <li>Укажите email адрес и пароль для доступа к почте</li>
            <li>Выберите IMAP сервер вашего почтового провайдера</li>
            <li>Запустите обработку писем</li>
          </ol>
        </div>

        <form onSubmit={handleSubmit} className="email-form">
          <div className="form-group">
            <label htmlFor="email">Email адрес:</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              required
              placeholder="example@gmail.com"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Пароль:</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              required
              placeholder="Пароль от email"
            />
            <small>
              Для Gmail используйте пароль приложения, а не обычный пароль
            </small>
          </div>

          <div className="form-group">
            <label htmlFor="server_select">Почтовый сервер:</label>
            <select
              id="server_select"
              onChange={handleServerChange}
              value={Object.keys(serverInfo?.supported_imap_servers || {}).find(
                key => serverInfo?.supported_imap_servers[key]?.server === formData.imap_server
              ) || 'custom'}
            >
              <option value="custom">Выберите сервер...</option>
              {serverInfo?.supported_imap_servers && 
                Object.entries(serverInfo.supported_imap_servers).map(([key, server]) => (
                  <option key={key} value={key}>
                    {key.toUpperCase()} ({server.server}:{server.port})
                  </option>
                ))
              }
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="imap_server">IMAP сервер:</label>
            <input
              type="text"
              id="imap_server"
              name="imap_server"
              value={formData.imap_server}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="imap_port">IMAP порт:</label>
            <input
              type="number"
              id="imap_port"
              name="imap_port"
              value={formData.imap_port}
              onChange={handleInputChange}
              required
              min="1"
              max="65535"
            />
          </div>

          <div className="form-group">
            <label htmlFor="download_dir">Папка для сохранения:</label>
            <input
              type="text"
              id="download_dir"
              name="download_dir"
              value={formData.download_dir}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="form-group checkbox-group">
            <label>
              <input
                type="checkbox"
                name="dry_run"
                checked={formData.dry_run}
                onChange={handleInputChange}
              />
              Режим тестирования (не сохранять файлы)
            </label>
          </div>

          <div className="server-notes">
            {serverInfo?.supported_imap_servers && 
              Object.entries(serverInfo.supported_imap_servers).map(([key, server]) => (
                <div key={key} className="server-note">
                  <strong>{key.toUpperCase()}:</strong> {server.note}
                </div>
              ))
            }
          </div>

          <button 
            type="submit" 
            className="submit-btn"
            disabled={isProcessing}
          >
            {isProcessing ? 'Обработка...' : 'Запустить обработку писем'}
          </button>
        </form>

        {error && (
          <div className="error-message">
            <h3>Ошибка:</h3>
            <p>{error}</p>
          </div>
        )}

        {result && (
          <div className="result-section">
            <h3>Результат обработки:</h3>
            {result.success ? (
              <div className="success-message">
                <p>{result.message}</p>
                {result.output && (
                  <div className="output-container">
                    <h4>Вывод команды:</h4>
                    <div className="output-content">
                      {formatOutput(result.output)}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="error-message">
                <p>{result.error}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MangoEmailPage; 