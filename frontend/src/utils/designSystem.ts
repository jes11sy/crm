import { theme } from 'antd';

// Единая дизайн-система на основе Ant Design
export const designSystem = {
  // Цветовая палитра
  colors: {
    primary: '#1890ff',
    success: '#52c41a',
    warning: '#faad14',
    error: '#ff4d4f',
    info: '#1890ff',
    
    // Нейтральные цвета
    text: {
      primary: 'rgba(0, 0, 0, 0.88)',
      secondary: 'rgba(0, 0, 0, 0.65)',
      tertiary: 'rgba(0, 0, 0, 0.45)',
      disabled: 'rgba(0, 0, 0, 0.25)',
    },
    
    background: {
      primary: '#ffffff',
      secondary: '#fafafa',
      tertiary: '#f5f5f5',
    },
    
    border: {
      primary: '#d9d9d9',
      secondary: '#f0f0f0',
    }
  },
  
  // Типографика
  typography: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif',
    fontSize: {
      xs: '12px',
      sm: '14px',
      base: '16px',
      lg: '18px',
      xl: '20px',
      '2xl': '24px',
      '3xl': '30px',
      '4xl': '36px',
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: {
      tight: 1.25,
      normal: 1.5,
      relaxed: 1.75,
    }
  },
  
  // Отступы и размеры
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px',
    '2xl': '48px',
    '3xl': '64px',
  },
  
  // Радиусы скругления
  borderRadius: {
    sm: '2px',
    base: '6px',
    lg: '8px',
    xl: '12px',
    full: '9999px',
  },
  
  // Тени
  boxShadow: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    base: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  },
  
  // Анимации
  transition: {
    fast: '0.15s ease-in-out',
    base: '0.2s ease-in-out',
    slow: '0.3s ease-in-out',
  }
};

// Конфигурация темы Ant Design
export const antdTheme = {
  algorithm: theme.defaultAlgorithm,
  token: {
    // Цвета
    colorPrimary: designSystem.colors.primary,
    colorSuccess: designSystem.colors.success,
    colorWarning: designSystem.colors.warning,
    colorError: designSystem.colors.error,
    colorInfo: designSystem.colors.info,
    
    // Типографика
    fontFamily: designSystem.typography.fontFamily,
    fontSize: 14,
    
    // Радиусы
    borderRadius: 6,
    
    // Отступы
    padding: 16,
    margin: 16,
    
    // Компоненты
    controlHeight: 32,
    controlHeightLG: 40,
    controlHeightSM: 24,
  },
  components: {
    // Настройки для конкретных компонентов
    Button: {
      borderRadius: 6,
      controlHeight: 32,
    },
    Input: {
      borderRadius: 6,
      controlHeight: 32,
    },
    Select: {
      borderRadius: 6,
      controlHeight: 32,
    },
    Table: {
      borderRadius: 6,
      headerBg: designSystem.colors.background.secondary,
      headerColor: designSystem.colors.text.primary,
    },
    Modal: {
      borderRadius: 8,
    },
    Card: {
      borderRadius: 8,
    },
  },
};

// Конфигурация темной темы Ant Design
export const antdDarkTheme = {
  algorithm: theme.darkAlgorithm,
  token: {
    colorPrimary: '#1677ff',
    colorBgBase: '#141414',
    colorTextBase: '#f0f2f5',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#ff4d4f',
    colorInfo: '#1677ff',
    fontFamily: designSystem.typography.fontFamily,
    fontSize: 14,
    borderRadius: 6,
    padding: 16,
    margin: 16,
    controlHeight: 32,
    controlHeightLG: 40,
    controlHeightSM: 24,
  },
  components: {
    Button: {
      borderRadius: 6,
      controlHeight: 32,
    },
    Input: {
      borderRadius: 6,
      controlHeight: 32,
    },
    Select: {
      borderRadius: 6,
      controlHeight: 32,
    },
    Table: {
      borderRadius: 6,
      headerBg: '#1f1f1f',
      headerColor: '#f0f2f5',
    },
    Modal: {
      borderRadius: 8,
    },
    Card: {
      borderRadius: 8,
    },
  },
};

// Утилиты для стилизации
export const styleUtils = {
  // Создание стилей для компонентов
  createComponentStyles: (componentName: string, customStyles: Record<string, any> = {}) => ({
    ...designSystem,
    ...customStyles,
  }),
  
  // Создание стилей для состояний
  createStateStyles: (baseStyles: Record<string, any>, states: Record<string, any> = {}) => ({
    ...baseStyles,
    ...states,
  }),
  
  // Создание стилей для размеров
  createSizeStyles: (sizes: Record<string, any> = {}) => ({
    small: { ...sizes.small },
    default: { ...sizes.default },
    large: { ...sizes.large },
  }),
};

// Константы для часто используемых значений
export const constants = {
  // Размеры экранов
  breakpoints: {
    xs: 480,
    sm: 576,
    md: 768,
    lg: 992,
    xl: 1200,
    xxl: 1600,
  },
  
  // Z-index слои
  zIndex: {
    dropdown: 1050,
    sticky: 1020,
    fixed: 1030,
    modalBackdrop: 1040,
    modal: 1050,
    popover: 1060,
    tooltip: 1070,
  },
  
  // Максимальные значения
  maxWidth: {
    sm: '540px',
    md: '720px',
    lg: '960px',
    xl: '1140px',
    xxl: '1320px',
  },
};

export default designSystem; 