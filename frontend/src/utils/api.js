import axios from 'axios';
import { useState } from 'react';

// Базовый URL для API
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Создаем экземпляр axios с базовой конфигурацией
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  withCredentials: true,
});

// Интерцептор для запросов
api.interceptors.request.use(
  (config) => {
    // Добавляем заголовки для логирования
    config.metadata = { startTime: new Date() };
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Интерцептор для ответов
api.interceptors.response.use(
  (response) => {
    // Логируем успешные запросы
    const duration = new Date() - response.config.metadata.startTime;
    console.log(`API ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status} (${duration}ms)`);
    return response;
  },
  (error) => {
    // Обрабатываем различные типы ошибок
    if (error.response) {
      // Сервер ответил с ошибкой
      const { status, data } = error.response;
      
      switch (status) {
        case 401:
          // Неавторизован - перенаправляем на логин
          window.location.href = '/login';
          break;
        case 403:
          console.error('Доступ запрещен:', data);
          break;
        case 404:
          console.error('Ресурс не найден:', data);
          break;
        case 500:
          console.error('Ошибка сервера:', data);
          break;
        default:
          console.error(`HTTP ${status}:`, data);
      }
    } else if (error.request) {
      // Запрос был отправлен, но ответ не получен
      console.error('Нет ответа от сервера:', error.request);
    } else {
      // Ошибка при настройке запроса
      console.error('Ошибка запроса:', error.message);
    }
    
    return Promise.reject(error);
  }
);

// Утилиты для работы с API
export const apiUtils = {
  // GET запрос
  get: (url, config = {}) => api.get(url, config),
  
  // POST запрос
  post: (url, data = {}, config = {}) => api.post(url, data, config),
  
  // PUT запрос
  put: (url, data = {}, config = {}) => api.put(url, data, config),
  
  // PATCH запрос
  patch: (url, data = {}, config = {}) => api.patch(url, data, config),
  
  // DELETE запрос
  delete: (url, config = {}) => api.delete(url, config),
  
  // Загрузка файла
  upload: (url, file, onProgress = null) => {
    const formData = new FormData();
    formData.append('file', file);
    
    return api.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: onProgress,
    });
  },
  
  // Скачивание файла
  download: (url, filename = 'download') => {
    return api.get(url, {
      responseType: 'blob',
    }).then((response) => {
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    });
  },
};

// Хуки для работы с API
export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const execute = async (apiCall) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiCall();
      return result;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };
  
  return { loading, error, execute };
};

export default api;

export async function getMangoAudioFiles() {
  const res = await fetch('/api/v1/mango-audio-files/');
  if (!res.ok) throw new Error('Ошибка загрузки аудиофайлов');
  return res.json();
} 