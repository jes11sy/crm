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
  BankOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const { Title } = Typography;

interface RK {
  id: number;
  rk_name: string;
}

interface RKFormValues {
  rk_name: string;
}

interface ApiResponse<T> {
  results?: T[];
}

export default function RKPage(): React.JSX.Element {
  const [rkList, setRkList] = useState<RK[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [modalVisible, setModalVisible] = useState<boolean>(false);
  const [editingRK, setEditingRK] = useState<RK | null>(null);
  const [form] = Form.useForm<RKFormValues>();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async (): Promise<void> => {
    try {
      const response = await axios.get<RK[] | ApiResponse<RK>>('/api/rk/');
      setRkList(Array.isArray(response.data) ? response.data : (response.data.results || []));
      setLoading(false);
    } catch (error) {
      message.error('Ошибка загрузки данных');
      setLoading(false);
    }
  };

  const handleAdd = (): void => {
    setEditingRK(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: RK): void => {
    setEditingRK(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = async (id: number): Promise<void> => {
    try {
      await axios.delete(`/api/rk/${id}/`);
      message.success('РК удален');
      loadData();
    } catch (error) {
      message.error('Ошибка удаления');
    }
  };

  const handleSubmit = async (values: RKFormValues): Promise<void> => {
    try {
      if (editingRK) {
        await axios.put(`/api/rk/${editingRK.id}/`, values);
        message.success('РК обновлен');
      } else {
        await axios.post('/api/rk/', values);
        message.success('РК создан');
      }
      setModalVisible(false);
      loadData();
    } catch (error) {
      message.error('Ошибка сохранения');
    }
  };

  const columns: ColumnsType<RK> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: 'Название РК',
      dataIndex: 'rk_name',
      key: 'rk_name',
      render: (text: string) => text || 'Не указано',
    },
    {
      title: 'Действия',
      key: 'actions',
      width: 150,
      render: (_: unknown, record: RK) => (
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
                  title: 'Удалить РК?',
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
            РК
          </Title>
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
            onClick={handleAdd}
            size="large"
          >
            Добавить РК
          </Button>
        </div>

        <Table<RK>
          columns={columns}
          dataSource={rkList}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total: number, range: [number, number]) => `${range[0]}-${range[1]} из ${total} РК`,
          }}
        />
      </Card>

      <Modal
        title={editingRK ? 'Редактировать РК' : 'Добавить РК'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={400}
      >
        <Form<RKFormValues>
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item name="rk_name" label="Название РК" rules={[{ required: true, message: 'Введите название РК' }]}>
            <Input placeholder="Название РК" prefix={<BankOutlined />} />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingRK ? 'Обновить' : 'Создать'}
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