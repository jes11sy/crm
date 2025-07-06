import React, { Component, ReactNode, ErrorInfo } from 'react';

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

interface ErrorBoundaryProps {
  children: ReactNode;
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
    
    // Логирование ошибки
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
          padding: '20px',
          textAlign: 'center',
          background: '#f5f5f5'
        }}>
          <h1 style={{ color: '#ff4d4f', marginBottom: '20px' }}>
            Что-то пошло не так
          </h1>
          <p style={{ marginBottom: '20px', color: '#666' }}>
            Произошла непредвиденная ошибка. Попробуйте обновить страницу.
          </p>
          <button
            onClick={() => window.location.reload()}
            style={{
              background: '#1890ff',
              color: 'white',
              border: 'none',
              padding: '10px 20px',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            Обновить страницу
          </button>
          {process.env.NODE_ENV === 'development' && this.state.error && (
            <details style={{ marginTop: '20px', textAlign: 'left' }}>
              <summary>Детали ошибки (только для разработки)</summary>
              <pre style={{ 
                background: '#f0f0f0', 
                padding: '10px', 
                borderRadius: '4px',
                overflow: 'auto',
                maxHeight: '200px'
              }}>
                {this.state.error && this.state.error.toString()}
                <br />
                {this.state.errorInfo?.componentStack}
              </pre>
            </details>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary; 