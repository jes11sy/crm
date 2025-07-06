import React, { useState, useEffect } from 'react';
import useAuth from '../hooks/useAuth';
import { apiUtils, getMangoAudioFiles } from '../utils/api';
import './MangoImportPage.css';

interface ImportHistoryItem {
  status: string;
  created_at: string;
  date_from: string;
  date_to: string;
  message: string;
  calls_imported?: number;
  recordings_downloaded?: number;
}

interface ImportStatus {
  success: boolean;
  message: string;
  data?: any;
}

interface Settings {
  api_key: string;
  api_salt: string;
  date_from: string;
  date_to: string;
  auto_import_enabled: boolean;
}

interface MangoAudioFile {
  name: string;
  size: number;
  modified: number;
}

const MangoImportPage: React.FC = () => {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [importStatus, setImportStatus] = useState<ImportStatus | null>(null);
  const [importHistory, setImportHistory] = useState([] as ImportHistoryItem[]);
  const [settings, setSettings] = useState<Settings>({
    api_key: 'l3t9b6nv42egkl98ojrtr6mg5z96e917',
    api_salt: 'xt81kobtimc6n7u1k8w9dt026up77qq8',
    date_from: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    date_to: new Date().toISOString().split('T')[0],
    auto_import_enabled: false
  });
  const [audioFiles, setAudioFiles] = useState([] as MangoAudioFile[]);
  const [audioLoading, setAudioLoading] = useState(false);
  const [audioError, setAudioError] = useState<string | null>(null);

  useEffect(() => {
    loadImportHistory();
  }, []);

  useEffect(() => {
    loadAudioFiles();
  }, []);

  const loadImportHistory = async (): Promise<void> => {
    try {
      const response = await apiUtils.get('/mango/import-history/');
      if (response.data.success) {
        setImportHistory(response.data.data);
      }
    } catch (error) {
      console.error('Ошибка загрузки истории:', error);
    }
  };

  const loadAudioFiles = async (): Promise<void> => {
    setAudioLoading(true);
    setAudioError(null);
    try {
      const res = await getMangoAudioFiles();
      setAudioFiles(res.files || []);
    } catch (e) {
      setAudioError('Ошибка загрузки аудиофайлов');
    } finally {
      setAudioLoading(false);
    }
  };

  const handleImport = async (dryRun = false): Promise<void> => {
    setIsLoading(true);
    setImportStatus(null);
    try {
      const response = await apiUtils.post('/mango/import/', {
        api_key: settings.api_key,
        api_salt: settings.api_salt,
        date_from: settings.date_from,
        date_to: settings.date_to,
        dry_run: dryRun
      });
      setImportStatus({
        success: response.data.success,
        message: response.data.message,
        data: response.data.data
      });
      if (response.data.success) {
        loadImportHistory();
      }
    } catch (error: any) {
      setImportStatus({
        success: false,
        message: error.response?.data?.message || error.message || 'Ошибка импорта'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleTestConnection = async (): Promise<void> => {
    setIsLoading(true);
    try {
      const response = await apiUtils.post('/mango/test-connection/', {
        api_key: settings.api_key,
        api_salt: settings.api_salt
      });
      setImportStatus({
        success: response.data.success,
        message: response.data.message
      });
    } catch (error: any) {
      setImportStatus({
        success: false,
        message: error.response?.data?.message || error.message || 'Ошибка тестирования соединения'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString('ru-RU');
  };

  const getStatusIcon = (status: string): string => {
    switch (status) {
      case 'success': return '✅';
      case 'error': return '❌';
      case 'running': return '🔄';
      default: return '⏳';
    }
  };

  return (
    <div className="mango-import-page">
      <div className="mango-import-header">
        <h1>🎙️ Импорт аудиозаписей Mango Office</h1>
        <p>Управление автоматическим импортом звонков и аудиозаписей</p>
      </div>
      <div className="mango-import-container">
        {/* Настройки */}
        <div className="settings-section">
          <h2>⚙️ Настройки API</h2>
          <div className="settings-grid">
            <div className="setting-group">
              <label>API Key:</label>
              <input
                type="text"
                value={settings.api_key}
                onChange={e => setSettings({ ...settings, api_key: e.target.value })}
                placeholder="Введите API Key"
              />
            </div>
            <div className="setting-group">
              <label>API Salt:</label>
              <input
                type="text"
                value={settings.api_salt}
                onChange={e => setSettings({ ...settings, api_salt: e.target.value })}
                placeholder="Введите API Salt"
              />
            </div>
            <div className="setting-group">
              <label>Дата начала:</label>
              <input
                type="date"
                value={settings.date_from}
                onChange={e => setSettings({ ...settings, date_from: e.target.value })}
              />
            </div>
            <div className="setting-group">
              <label>Дата окончания:</label>
              <input
                type="date"
                value={settings.date_to}
                onChange={e => setSettings({ ...settings, date_to: e.target.value })}
              />
            </div>
          </div>
        </div>
        {/* Действия */}
        <div className="actions-section">
          <h2>🚀 Действия</h2>
          <div className="action-buttons">
            <button
              className="btn btn-primary"
              onClick={() => handleTestConnection()}
              disabled={isLoading}
            >
              {isLoading ? '🔄 Тестирование...' : '🔍 Тест соединения'}
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => handleImport(true)}
              disabled={isLoading}
            >
              {isLoading ? '🔄 Тестовый импорт...' : '🧪 Тестовый импорт'}
            </button>
            <button
              className="btn btn-success"
              onClick={() => handleImport(false)}
              disabled={isLoading}
            >
              {isLoading ? '🔄 Импорт...' : '📥 Запустить импорт'}
            </button>
          </div>
        </div>
        {/* Статус */}
        {importStatus && (
          <div className={`status-section ${importStatus.success ? 'success' : 'error'}`}>
            <h2>📊 Статус операции</h2>
            <div className="status-message">
              <span className="status-icon">
                {importStatus.success ? '✅' : '❌'}
              </span>
              <span className="status-text">{importStatus.message}</span>
            </div>
            {importStatus.data && (
              <div className="status-details">
                <pre>{JSON.stringify(importStatus.data, null, 2)}</pre>
              </div>
            )}
          </div>
        )}
        {/* История импорта */}
        <div className="history-section">
          <h2>📋 История импорта</h2>
          <div className="history-list">
            {importHistory.length === 0 ? (
              <p className="no-data">История импорта пуста</p>
            ) : (
              importHistory.map((item, index) => (
                <div key={index} className="history-item">
                  <div className="history-header">
                    <span className="history-status">
                      {getStatusIcon(item.status)}
                    </span>
                    <span className="history-date">
                      {formatDate(item.created_at)}
                    </span>
                  </div>
                  <div className="history-details">
                    <p><strong>Период:</strong> {item.date_from} - {item.date_to}</p>
                    <p><strong>Результат:</strong> {item.message}</p>
                    {item.calls_imported && (
                      <p><strong>Импортировано звонков:</strong> {item.calls_imported}</p>
                    )}
                    {item.recordings_downloaded && (
                      <p><strong>Скачано записей:</strong> {item.recordings_downloaded}</p>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
        {/* Инструкции */}
        <div className="instructions-section">
          <h2>📖 Инструкции</h2>
          <div className="instructions-content">
            <h3>Как настроить автоматический импорт:</h3>
            <ol>
              <li>Проверьте правильность API ключей</li>
              <li>Выполните тест соединения</li>
              <li>Запустите тестовый импорт</li>
              <li>При успешном тесте запустите реальный импорт</li>
              <li>Настройте автоматический запуск через планировщик Windows</li>
            </ol>
            <h3>Команда для автоматического запуска:</h3>
            <code>python auto_import_mango.py</code>
            <h3>Логи импорта:</h3>
            <p>Логи сохраняются в файле: <code>logs/auto_import_mango.log</code></p>
          </div>
        </div>
        {/* Список аудиофайлов Mango Office */}
        <div className="audio-files-section">
          <h2>🎧 Скачанные аудиозаписи Mango Office</h2>
          {audioLoading && <div>Загрузка...</div>}
          {audioError && <div className="error">{audioError}</div>}
          {!audioLoading && !audioError && (
            <table className="audio-files-table">
              <thead>
                <tr>
                  <th>Имя файла</th>
                  <th>Размер</th>
                  <th>Дата</th>
                </tr>
              </thead>
              <tbody>
                {audioFiles.length === 0 && (
                  <tr><td colSpan={3}>Нет файлов</td></tr>
                )}
                {audioFiles.map(f => (
                  <tr key={f.name}>
                    <td>{f.name}</td>
                    <td>{(f.size/1024).toFixed(1)} КБ</td>
                    <td>{new Date(f.modified*1000).toLocaleString('ru-RU')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};

export default MangoImportPage; 