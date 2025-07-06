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
  FileTextOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const { Title } = Typography;

interface TipZayavki {
  id: number;
  name: string;
}

interface TipZayavkiFormValues {
  name: string;
}

interface ApiResponse<T> {
  results?: T[];
}

export default function TipZayavkiPage(): React.JSX.Element {
  const [tipy, setTipy] = useState<TipZayavki[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [modalVisible, setModalVisible] = useState<boolean>(false);
  const [editingTip, setEditingTip] = useState<TipZayavki | null>(null);
  const [form] = Form.useForm<TipZayavkiFormValues>();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async (): Promise<void> => {
    try {
      const response = await axios.get<TipZayavki[] | ApiResponse<TipZayavki>>('/api/tipzayavki/');
      setTipy(Array.isArray(response.data) ? response.data : (response.data.results || []));
      setLoading(false);
    } catch (error) {
      message.error('Ошибка загрузки данных');
      setLoading(false);
    }
  };

  const handleAdd = (): void => {
    setEditingTip(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: TipZayavki): void => {
    setEditingTip(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = async (id: number): Promise<void> => {
    try {
      await axios.delete(`/api/tipzayavki/${id}/`);
      message.success('Тип заявки удален');
      loadData();
    } catch (error) {
      message.error('Ошибка удаления');
    }
  };

  const handleSubmit = async (values: TipZayavkiFormValues): Promise<void> => {
    try {
      if (editingTip) {
        await axios.put(`/api/tipzayavki/${editingTip.id}/`, values);
        message.success('Тип заявки обновлен');
      } else {
        await axios.post('/api/tipzayavki/', values);
        message.success('Тип заявки создан');
      }
      setModalVisible(false);
      loadData();
    } catch (error) {
      message.error('Ошибка сохранения');
    }
  };

  const columns: ColumnsType<TipZayavki> = [
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
      render: (_: unknown, record: TipZayavki) => (
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
                  title: 'Удалить тип заявки?',
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
            Типы заявок
          </Title>
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
            onClick={handleAdd}
            size="large"
          >
            Добавить тип
          </Button>
        </div>

        <Table<TipZayavki>
          columns={columns}
          dataSource={tipy}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total: number, range: [number, number]) => `${range[0]}-${range[1]} из ${total} типов`,
          }}
        />
      </Card>

      <Modal
        title={editingTip ? 'Редактировать тип заявки' : 'Добавить тип заявки'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={400}
      >
        <Form<TipZayavkiFormValues>
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item name="name" label="Название" rules={[{ required: true, message: 'Введите название типа' }]}>
            <Input placeholder="Название типа заявки" prefix={<FileTextOutlined />} />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingTip ? 'Обновить' : 'Создать'}
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