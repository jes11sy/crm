import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Table, 
  Button, 
  Modal, 
  Form, 
  Input, 
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
  SafetyCertificateOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const { Title } = Typography;

interface Rol {
  id: number;
  name: string;
}

interface RolFormValues {
  name: string;
}

interface ApiResponse<T> {
  results?: T[];
}

export default function RoliPage(): React.JSX.Element {
  const [roli, setRoli] = useState<Rol[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [modalVisible, setModalVisible] = useState<boolean>(false);
  const [editingRol, setEditingRol] = useState<Rol | null>(null);
  const [form] = Form.useForm<RolFormValues>();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async (): Promise<void> => {
    try {
      const response = await axios.get<Rol[] | ApiResponse<Rol>>('/api/roli/');
      setRoli(Array.isArray(response.data) ? response.data : (response.data.results || []));
      setLoading(false);
    } catch (error) {
      message.error('Ошибка загрузки данных');
      setLoading(false);
    }
  };

  const handleAdd = (): void => {
    setEditingRol(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: Rol): void => {
    setEditingRol(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = async (id: number): Promise<void> => {
    try {
      await axios.delete(`/api/roli/${id}/`);
      message.success('Роль удалена');
      loadData();
    } catch (error) {
      message.error('Ошибка удаления');
    }
  };

  const handleSubmit = async (values: RolFormValues): Promise<void> => {
    try {
      if (editingRol) {
        await axios.put(`/api/roli/${editingRol.id}/`, values);
        message.success('Роль обновлена');
      } else {
        await axios.post('/api/roli/', values);
        message.success('Роль создана');
      }
      setModalVisible(false);
      loadData();
    } catch (error) {
      message.error('Ошибка сохранения');
    }
  };

  const columns: ColumnsType<Rol> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: 'Название',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => text || 'Не указано',
    },
    {
      title: 'Действия',
      key: 'actions',
      width: 150,
      render: (_: unknown, record: Rol) => (
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
                  title: 'Удалить роль?',
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
            Роли
          </Title>
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
            onClick={handleAdd}
            size="large"
          >
            Добавить роль
          </Button>
        </div>

        <Table<Rol>
          columns={columns}
          dataSource={roli}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total: number, range: [number, number]) => `${range[0]}-${range[1]} из ${total} ролей`,
          }}
        />
      </Card>

      <Modal
        title={editingRol ? 'Редактировать роль' : 'Добавить роль'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={400}
      >
        <Form<RolFormValues>
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item name="name" label="Название" rules={[{ required: true, message: 'Введите название роли' }]}>
            <Input placeholder="Название роли" prefix={<SafetyCertificateOutlined />} />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingRol ? 'Обновить' : 'Создать'}
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