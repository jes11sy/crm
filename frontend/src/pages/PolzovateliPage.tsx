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
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  UserOutlined
} from '@ant-design/icons';

const { Title } = Typography;

interface Polzovatel {
  id: number;
  name: string;
  login: string;
  rol: number;
  rol_name: string;
  gorod: number;
  gorod_name: string;
  note?: string;
}

interface Rol {
  id: number;
  name: string;
}

interface Gorod {
  id: number;
  name: string;
}

interface PolzovatelForm {
  name: string;
  rol: number;
  gorod?: number;
  login: string;
  password: string;
}

export default function PolzovateliPage(): React.JSX.Element {
  const [polzovateli, setPolzovateli] = useState<Polzovatel[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [modalVisible, setModalVisible] = useState<boolean>(false);
  const [editingPolzovatel, setEditingPolzovatel] = useState<Polzovatel | null>(null);
  const [form] = Form.useForm();
  const [roli, setRoli] = useState<Rol[]>([]);
  const [goroda, setGoroda] = useState<Gorod[]>([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async (): Promise<void> => {
    try {
      const [polzovateliRes, roliRes, gorodaRes] = await Promise.all([
        axios.get('/api/polzovateli/'),
        axios.get('/api/roli/'),
        axios.get('/api/gorod/')
      ]);
      setPolzovateli(Array.isArray(polzovateliRes.data) ? polzovateliRes.data : (polzovateliRes.data.results || []));
      setRoli(Array.isArray(roliRes.data) ? roliRes.data : (roliRes.data.results || []));
      setGoroda(Array.isArray(gorodaRes.data) ? gorodaRes.data : (gorodaRes.data.results || []));
      setLoading(false);
    } catch (error) {
      message.error('Ошибка загрузки данных');
      setLoading(false);
    }
  };

  const handleAdd = (): void => {
    setEditingPolzovatel(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: Polzovatel): void => {
    setEditingPolzovatel(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = async (id: number): Promise<void> => {
    try {
      await axios.delete(`/api/polzovateli/${id}/`);
      message.success('Пользователь удален');
      loadData();
    } catch (error) {
      message.error('Ошибка удаления');
    }
  };

  const handleSubmit = async (values: PolzovatelForm): Promise<void> => {
    try {
      if (editingPolzovatel) {
        await axios.put(`/api/polzovateli/${editingPolzovatel.id}/`, values);
        message.success('Пользователь обновлен');
      } else {
        await axios.post('/api/polzovateli/', values);
        message.success('Пользователь создан');
      }
      setModalVisible(false);
      loadData();
    } catch (error) {
      message.error('Ошибка сохранения');
    }
  };

  const generateLoginPassword = (): void => {
    const login = `user_${Math.random().toString(36).substr(2, 6)}`;
    const password = Math.random().toString(36).substr(2, 8);
    form.setFieldsValue({ login, password });
    message.success('Логин и пароль сгенерированы');
  };

  const columns = [
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
      title: 'Логин',
      dataIndex: 'login',
      key: 'login',
      render: (text: string) => text || 'Не указан',
    },
    {
      title: 'Роль',
      dataIndex: 'rol_name',
      key: 'rol_name',
      render: (text: string) => text || 'Не указана',
    },
    {
      title: 'Город',
      dataIndex: 'gorod_name',
      key: 'gorod_name',
      render: (text: string) => text || 'Не указан',
    },
    {
      title: 'Примечание',
      dataIndex: 'note',
      key: 'note',
      render: (text: string) => text || '',
    },
    {
      title: 'Действия',
      key: 'actions',
      width: 150,
      render: (_: any, record: Polzovatel) => (
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
                  title: 'Удалить пользователя?',
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
            Пользователи
          </Title>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleAdd}
            size="large"
          >
            Добавить пользователя
          </Button>
        </div>

        <Table
          columns={columns}
          dataSource={polzovateli}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total: number, range: [number, number]) => `${range[0]}-${range[1]} из ${total} пользователей`,
          }}
        />
      </Card>

      <Modal
        title={editingPolzovatel ? 'Редактировать пользователя' : 'Добавить пользователя'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={500}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item name="name" label="Имя" rules={[{ required: true, message: 'Введите имя' }]}> 
            <Input placeholder="Имя пользователя" prefix={<UserOutlined />} />
          </Form.Item>

          <Form.Item name="rol" label="Роль" rules={[{ required: true, message: 'Выберите роль' }]}> 
            <Select placeholder="Выберите роль" showSearch optionFilterProp="children">
              {roli.map(rol => (
                <Select.Option key={rol.id} value={rol.id}>{rol.name}</Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item name="gorod" label="Город">
            <Select placeholder="Выберите город" showSearch optionFilterProp="children">
              {goroda.map(gorod => (
                <Select.Option key={gorod.id} value={gorod.id}>{gorod.name}</Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item name="login" label="Логин" rules={[{ required: true, message: 'Введите логин' }]}> 
            <Input placeholder="Логин" />
          </Form.Item>

          <Form.Item name="password" label="Пароль" rules={[{ required: true, message: 'Введите пароль' }]}> 
            <Input.Password placeholder="Пароль" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="default" onClick={generateLoginPassword}>
                Сгенерировать логин/пароль
              </Button>
            </Space>
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingPolzovatel ? 'Обновить' : 'Создать'}
              </Button>
              <Button onClick={() => setModalVisible(false)}>
                Отмена
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
} 