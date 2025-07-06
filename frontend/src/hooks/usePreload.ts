import { useEffect } from 'react';

// Список критических страниц для preloading
const criticalPages = [
  () => import('../pages/HomePage'),
  () => import('../pages/LoginPage'),
  () => import('../pages/ZayavkiPage'),
  () => import('../pages/MasterPage'),
];

// Список крупных компонентов для preloading
const criticalComponents = [
  () => import('../components/CommonComponents'),
  () => import('../components/ZayavkaFiles'),
];

export const usePreload = () => {
  useEffect(() => {
    // Preload критических страниц после загрузки основного контента
    const preloadCriticalPages = async () => {
      try {
        await Promise.all([
          ...criticalPages.map(page => page()),
          ...criticalComponents.map(component => component()),
        ]);
        console.log('Критические страницы и компоненты предзагружены');
      } catch (error) {
        console.warn('Ошибка при предзагрузке:', error);
      }
    };

    // Запускаем preloading с небольшой задержкой
    const timer = setTimeout(preloadCriticalPages, 1000);
    
    return () => clearTimeout(timer);
  }, []);
};

// Хук для preloading конкретной страницы
export const usePreloadPage = (pageImport: () => Promise<any>) => {
  useEffect(() => {
    const preloadPage = async () => {
      try {
        await pageImport();
      } catch (error) {
        console.warn('Ошибка при предзагрузке страницы:', error);
      }
    };

    preloadPage();
  }, [pageImport]);
}; 