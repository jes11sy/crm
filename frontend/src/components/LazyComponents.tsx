import React, { lazy, Suspense } from 'react';
import { Spin, Skeleton } from 'antd';

// Lazy loading для крупных компонентов
const PageWithTable = lazy(() => import('./CommonComponents').then(module => ({ default: module.PageWithTable })));
const FormModal = lazy(() => import('./CommonComponents').then(module => ({ default: module.FormModal })));
const ZayavkaFiles = lazy(() => import('./ZayavkaFiles'));

// Улучшенный fallback компонент
const LoadingFallback: React.FC<{ type?: 'spinner' | 'skeleton' }> = ({ type = 'spinner' }) => {
  if (type === 'skeleton') {
    return (
      <div style={{ padding: 16 }}>
        <Skeleton active paragraph={{ rows: 4 }} />
      </div>
    );
  }
  
  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '200px' 
    }}>
      <Spin size="large" />
    </div>
  );
};

// Обёртка для lazy компонентов с fallback
export const LazyPageWithTable: React.FC<any> = (props) => (
  <Suspense fallback={<LoadingFallback type="skeleton" />}>
    <PageWithTable {...props} />
  </Suspense>
);

export const LazyFormModal: React.FC<any> = (props) => (
  <Suspense fallback={<LoadingFallback />}>
    <FormModal {...props} />
  </Suspense>
);

export const LazyZayavkaFiles: React.FC<any> = (props) => (
  <Suspense fallback={<LoadingFallback />}>
    <ZayavkaFiles {...props} />
  </Suspense>
);

// Универсальная обёртка для любых lazy компонентов
export const withLazyLoading = <P extends object>(
  Component: React.ComponentType<P>,
  fallbackType: 'spinner' | 'skeleton' = 'spinner'
) => {
  const LazyComponent = lazy(() => Promise.resolve({ default: Component }));
  
  return (props: P) => (
    <Suspense fallback={<LoadingFallback type={fallbackType} />}>
      <LazyComponent {...props} />
    </Suspense>
  );
}; 