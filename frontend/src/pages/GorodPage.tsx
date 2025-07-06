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
  EnvironmentOutlined
} from '@ant-design/icons';

const { Title } = Typography;

interface Gorod {
  id: number;
  name: string;
}

export default function GorodPage(): React.JSX.Element {
  const [goroda, setGoroda] = useState<Gorod[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [modalVisible, setModalVisible] = useState<boolean>(false);
  const [editingGorod, setEditingGorod] = useState<Gorod | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async (): Promise<void> => {
    try {
      const response = await axios.get('/api/gorod/');
      const data: Gorod[] = Array.isArray(response.data) ? response.data : (response.data.results || []);
      setGoroda(data);
      setLoading(false);
    } catch (error) {
      message.error('Ошибка загрузки данных');
      setLoading(false);
    }
  };

  const handleAdd = (): void => {
    setEditingGorod(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: Gorod): void => {
    setEditingGorod(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = async (id: number): Promise<void> => {
    try {
      await axios.delete(`/api/gorod/${id}/`);
      message.success('Город удален');
      loadData();
    } catch (error) {
      message.error('Ошибка удаления');
    }
  };

  const handleSubmit = async (values: { name: string }): Promise<void> => {
    try {
      if (editingGorod) {
        await axios.put(`/api/gorod/${editingGorod.id}/`, values);
        message.success('Город обновлен');
      } else {
        await axios.post('/api/gorod/', values);
        message.success('Город создан');
      }
      setModalVisible(false);
      loadData();
    } catch (error) {
      message.error('Ошибка сохранения');
    }
  };

  const columns = [
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
      render: (_: any, record: Gorod) => (
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
                  title: 'Удалить город?',
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
            Города
          </Title>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleAdd}
            size="large"
          >
            Добавить город
          </Button>
        </div>

        <Table
          columns={columns}
          dataSource={goroda}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total: number, range: [number, number]) => `${range[0]}-${range[1]} из ${total} городов`,
          }}
        />
      </Card>

      <Modal
        title={editingGorod ? 'Редактировать город' : 'Добавить город'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={400}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item name="name" label="Название" rules={[{ required: true, message: 'Введите название города' }]}> 
            <Input placeholder="Название города" prefix={<EnvironmentOutlined />} />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingGorod ? 'Обновить' : 'Создать'}
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