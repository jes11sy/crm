import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Table, 
  Button, 
  Modal, 
  Form, 
  Input, 
  Select, 
  message, 
  Space, 
  Card, 
  Typography,
  Tooltip
} from 'antd';
import type { ColumnType } from 'antd/es/table';
import { 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined,
  UserOutlined
} from '@ant-design/icons';
import useAuth from '../hooks/useAuth';
import { User } from '../types/entities';

const { Title } = Typography;

interface Master {
  id: number;
  name: string;
  gorod: number;
  gorod_id?: number;
  gorod_name?: string;
  login?: string;
  phone?: string;
  is_active?: boolean;
  note?: string;
}

interface Gorod {
  id: number;
  name: string;
}

interface FormValues {
  name: string;
  gorod: number;
  login: string;
  phone: string;
  is_active: boolean;
  note: string;
}

const MasterPage: React.FC = () => {
  const [masters, setMasters] = useState<Master[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [modalVisible, setModalVisible] = useState<boolean>(false);
  const [editingMaster, setEditingMaster] = useState<Master | null>(null);
  const [form] = Form.useForm<FormValues>();
  const [goroda, setGoroda] = useState<Gorod[]>([]);
  const { user } = useAuth();
  const typedUser = user as User | null;

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async (): Promise<void> => {
    try {
      const [mastersRes, gorodaRes] = await Promise.all([
        axios.get('/api/master/'),
        axios.get('/api/gorod/')
      ]);
      
      setMasters(Array.isArray(mastersRes.data) ? mastersRes.data : (mastersRes.data.results || []));
      setGoroda(Array.isArray(gorodaRes.data) ? gorodaRes.data : (gorodaRes.data.results || []));
      setLoading(false);
    } catch (error) {
      message.error('Ошибка загрузки данных');
      setLoading(false);
    }
  };

  const handleAdd = (): void => {
    setEditingMaster(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: Master): void => {
    setEditingMaster(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = async (id: number): Promise<void> => {
    try {
      await axios.delete(`/api/master/${id}/`);
      message.success('Мастер удален');
      loadData();
    } catch (error) {
      message.error('Ошибка удаления');
    }
  };

  const handleSubmit = async (values: FormValues): Promise<void> => {
    try {
      if (editingMaster) {
        await axios.put(`/api/master/${editingMaster.id}/`, values);
        message.success('Мастер обновлен');
      } else {
        await axios.post('/api/master/', values);
        message.success('Мастер создан');
      }
      setModalVisible(false);
      loadData();
    } catch (error) {
      message.error('Ошибка сохранения');
    }
  };

  const generateLoginPassword = (): void => {
    const login = `master_${Math.random().toString(36).substr(2, 6)}`;
    form.setFieldsValue({ login });
    message.success('Логин сгенерирован');
  };

  // Фильтрация мастеров по городу для director
  let filteredMasters = masters;
  if (typedUser && typedUser.role === 'director') {
    filteredMasters = masters.filter(m => String(m.gorod) === String(typedUser.gorod_id) || String(m.gorod_id) === String(typedUser.gorod_id));
  }

  const columns: ColumnType<Master>[] = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: 'Имя',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => text || 'Не указано',
    },
    {
      title: 'Город',
      dataIndex: 'gorod_name',
      key: 'gorod_name',
      render: (text: string) => text || 'Не указан',
      filters: goroda.map(g => ({ text: g.name, value: g.name })),
      onFilter: (value: boolean | React.Key, record: Master) => record.gorod_name === value,
    },
    {
      title: 'Логин',
      dataIndex: 'login',
      key: 'login',
      render: (text: string) => text || 'Не указан',
    },
    {
      title: 'Телефон',
      dataIndex: 'phone',
      key: 'phone',
      render: (text: string) => text || 'Не указан',
    },
    {
      title: 'Статус',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (value: boolean) => value ? 'Работает' : 'Не работает',
    },
    {
      title: 'Примечание',
      dataIndex: 'note',
      key: 'note',
      render: (text: string) => text || '—',
    },
    {
      title: 'Действия',
      key: 'actions',
      width: 150,
      render: (_: any, record: Master) => (
        <Space>
          <Tooltip title="Редактировать">
            <Button 
              type="default" 
              size="small" 
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
            />
          </Tooltip>
          <Tooltip title="Удалить">
            <Button 
              type="default" 
              size="small" 
              danger
              icon={<DeleteOutlined />}
              onClick={() => {
                Modal.confirm({
                  title: 'Удалить мастера?',
                  content: 'Это действие нельзя отменить.',
                  okText: 'Удалить',
                  okType: 'danger',
                  cancelText: 'Отмена',
                  onOk: () => handleDelete(record.id),
                });
              }}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <Title level={3} style={{ margin: 0 }}>
            Мастера
          </Title>
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
            onClick={handleAdd}
            size="large"
          >
            Добавить мастера
          </Button>
        </div>
        <Table
          columns={columns}
          dataSource={filteredMasters}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `${range[0]}-${range[1]} из ${total} мастеров`,
          }}
        />
      </Card>

      <Modal
        title={editingMaster ? 'Редактировать мастера' : 'Добавить мастера'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item name="name" label="Имя" rules={[{ required: true, message: 'Введите имя' }]}>
            <Input placeholder="Имя мастера" />
          </Form.Item>

          <Form.Item name="gorod" label="Город" rules={[{ required: true, message: 'Выберите город' }]}>
            <Select placeholder="Выберите город" showSearch optionFilterProp="children">
              {goroda.map(g => (
                <Select.Option key={g.id} value={g.id}>{g.name}</Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item name="login" label="Логин" rules={[{ required: true, message: 'Введите логин' }]}>
            <Input placeholder="Логин" />
          </Form.Item>

          <Form.Item name="phone" label="Телефон" rules={[{ required: true, message: 'Введите телефон' }]}>
            <Input placeholder="Телефон" />
          </Form.Item>

          <Form.Item name="is_active" label="Статус" valuePropName="checked">
            <Select placeholder="Выберите статус">
              <Select.Option value={true}>Работает</Select.Option>
              <Select.Option value={false}>Не работает</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item name="note" label="Примечание">
            <Input.TextArea rows={3} placeholder="Примечание" />
          </Form.Item>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 24 }}>
            <Button onClick={generateLoginPassword} icon={<UserOutlined />}>
              Сгенерировать логин/пароль
            </Button>
            <Space>
              <Button onClick={() => setModalVisible(false)}>
                Отмена
              </Button>
              <Button type="primary" htmlType="submit">
                {editingMaster ? 'Обновить' : 'Создать'}
              </Button>
            </Space>
          </div>
        </Form>
      </Modal>
    </div>
  );
};

export default MasterPage; 