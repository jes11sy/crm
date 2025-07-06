import React, { ReactNode, useState } from 'react';
import { Card, Space, Typography, Button, Table, Modal, Form, Input, Select, message } from 'antd';
import { PlusOutlined, ReloadOutlined } from '@ant-design/icons';
import { designSystem } from '../utils/designSystem';
import { Option } from '../types/entities';

const { Title } = Typography;
const { Option: AntdOption } = Select;

// Типы для PageWithTable
interface PageWithTableProps {
  title: string;
  data: any[];
  columns: any[];
  loading: boolean;
  onRefresh: () => void;
  onAdd?: () => void;
  showAddButton?: boolean;
  showRefreshButton?: boolean;
  addButtonText?: string;
  refreshButtonText?: string;
  pagination?: object;
  [key: string]: any;
}

export const PageWithTable: React.FC<PageWithTableProps> = ({
  title,
  data,
  columns,
  loading,
  onRefresh,
  onAdd,
  showAddButton = true,
  showRefreshButton = true,
  addButtonText = "Добавить",
  refreshButtonText = "Обновить",
  pagination = {},
  ...props
}) => {
  const defaultPagination = {
    showSizeChanger: true,
    showQuickJumper: true,
    showTotal: (total: number, range: [number, number]) => `${range[0]}-${range[1]} из ${total} записей`,
    pageSizeOptions: ['10', '20', '50', '100'],
    defaultPageSize: 20,
    ...pagination,
  };

  return (
    <div style={{ padding: designSystem.spacing.lg }}>
      <Card>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <Title level={2} style={{ margin: 0 }}>{title}</Title>
            <Space>
              {showAddButton && (
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={onAdd}
                >
                  {addButtonText}
                </Button>
              )}
              {showRefreshButton && (
                <Button
                  icon={<ReloadOutlined />}
                  onClick={onRefresh}
                  loading={loading}
                >
                  {refreshButtonText}
                </Button>
              )}
            </Space>
          </div>

          <Table
            columns={columns}
            dataSource={data}
            rowKey="id"
            loading={loading}
            pagination={defaultPagination}
            scroll={{ x: 800 }}
            {...props}
          />
        </Space>
      </Card>
    </div>
  );
};

// Типы для FormModal
interface FormModalProps {
  title: string;
  visible: boolean;
  onOk: () => void;
  onCancel: () => void;
  form: any;
  children: ReactNode;
  okText?: string;
  cancelText?: string;
  confirmLoading?: boolean;
  width?: number;
  [key: string]: any;
}

export const FormModal: React.FC<FormModalProps> = ({
  title,
  visible,
  onOk,
  onCancel,
  form,
  children,
  okText = "Сохранить",
  cancelText = "Отмена",
  confirmLoading = false,
  width = 520,
  ...props
}) => {
  return (
    <Modal
      title={title}
      open={visible}
      onOk={onOk}
      onCancel={onCancel}
      okText={okText}
      cancelText={cancelText}
      confirmLoading={confirmLoading}
      width={width}
      {...props}
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={onOk}
      >
        {children}
      </Form>
    </Modal>
  );
};

// Типы для FormField
interface FormFieldInputProps {
  name: string;
  label: string;
  rules?: any[];
  placeholder?: string;
  [key: string]: any;
}

interface FormFieldSelectProps extends FormFieldInputProps {
  options: Option[];
}

interface FormFieldTextAreaProps extends FormFieldInputProps {
  rows?: number;
}

export const FormField = {
  Input: ({ name, label, rules = [], placeholder, ...props }: FormFieldInputProps) => (
    <Form.Item
      name={name}
      label={label}
      rules={rules}
    >
      <Input placeholder={placeholder} {...props} />
    </Form.Item>
  ),

  Select: ({ name, label, rules = [], placeholder, options = [], ...props }: FormFieldSelectProps) => (
    <Form.Item
      name={name}
      label={label}
      rules={rules}
    >
      <Select placeholder={placeholder} {...props}>
        {options.map(option => (
          <AntdOption key={option.value} value={option.value}>
            {option.label}
          </AntdOption>
        ))}
      </Select>
    </Form.Item>
  ),

  TextArea: ({ name, label, rules = [], placeholder, rows = 4, ...props }: FormFieldTextAreaProps) => (
    <Form.Item
      name={name}
      label={label}
      rules={rules}
    >
      <Input.TextArea placeholder={placeholder} rows={rows} {...props} />
    </Form.Item>
  ),
};

// Исправленные типы для утилит и компонентов
export const formUtils = {
  // Создание правил валидации
  createRules: {
    required: (message: string = 'Это поле обязательно') => ({ required: true, message }),
    min: (min: number, message: string) => ({ min, message }),
    max: (max: number, message: string) => ({ max, message }),
    pattern: (pattern: RegExp, message: string) => ({ pattern, message }),
    email: () => ({ 
      type: 'email', 
      message: 'Введите корректный email' 
    }),
    phone: () => ({ 
      pattern: /^\+?1?\d{9,15}$/, 
      message: 'Номер телефона должен быть в формате: +999999999' 
    }),
  },
  
  // Обработка ошибок API
  handleApiError: (error: any, defaultMessage: string = 'Произошла ошибка') => {
    if (error.response?.data?.error) {
      message.error(error.response.data.error);
    } else if (error.response?.data?.detail) {
      message.error(error.response.data.detail);
    } else {
      message.error(defaultMessage);
    }
  },
  
  // Успешное сообщение
  showSuccess: (messageText: string) => {
    message.success(messageText);
  },
};

// Компонент для отображения статусов
interface StatusTagProps {
  status: string;
  statusConfig?: Record<string, { color: string; text: string }>;
}
export const StatusTag: React.FC<StatusTagProps> = ({ status, statusConfig = {} }) => {
  const defaultConfig: Record<string, { color: string; text: string }> = {
    'pending': { color: 'orange', text: 'Ожидает' },
    'active': { color: 'green', text: 'Активен' },
    'inactive': { color: 'red', text: 'Неактивен' },
    'completed': { color: 'blue', text: 'Завершен' },
    'cancelled': { color: 'red', text: 'Отменен' },
    ...statusConfig,
  };
  const config = defaultConfig[status] || { color: 'default', text: status };
  return (
    <span style={{
      padding: '4px 8px',
      borderRadius: designSystem.borderRadius.base,
      backgroundColor: (designSystem.colors as any)[config.color] || '#f0f0f0',
      color: config.color === 'default' ? designSystem.colors.text.primary : '#fff',
      fontSize: designSystem.typography.fontSize.sm,
      fontWeight: designSystem.typography.fontWeight.medium,
    }}>
      {config.text}
    </span>
  );
};

// Компонент для отображения денежных сумм
interface MoneyDisplayProps {
  amount: number;
  currency?: string;
  colorize?: boolean;
}
export const MoneyDisplay: React.FC<MoneyDisplayProps> = ({ amount, currency = '₽', colorize = true }) => {
  const formattedAmount = amount ? `${amount} ${currency}` : '-';
  const color = colorize && amount ? (amount > 0 ? designSystem.colors.success : designSystem.colors.error) : undefined;
  return (
    <span style={{
      fontWeight: designSystem.typography.fontWeight.medium,
      color: color,
    }}>
      {formattedAmount}
    </span>
  );
};

// Компонент для отображения дат
interface DateDisplayProps {
  date: string;
  format?: string;
}
export const DateDisplay: React.FC<DateDisplayProps> = ({ date, format = 'DD.MM.YYYY' }) => {
  if (!date) return <>-</>;
  const dayjs = require('dayjs');
  return <>{dayjs(date).format(format)}</>;
};

// Хук для работы с API
export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<unknown>(null);
  
  const execute = async (apiCall: () => Promise<any>) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiCall();
      return result;
    } catch (err) {
      setError(err);
      formUtils.handleApiError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };
  
  return { loading, error, execute };
};

const CommonComponents = {
  PageWithTable,
  FormModal,
  FormField,
  formUtils,
  StatusTag,
  MoneyDisplay,
  DateDisplay,
  useApi,
};

export default CommonComponents; 