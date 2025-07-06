import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
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
  Tag,
  Typography,
  Tooltip
} from 'antd';
import type { ColumnType } from 'antd/es/table';
import { 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined,
  EyeOutlined
} from '@ant-design/icons';
import dayjs, { Dayjs } from 'dayjs';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';
import useAuth from '../hooks/useAuth';
import { User } from '../types/entities';

dayjs.extend(utc);
dayjs.extend(timezone);

const { Title } = Typography;
const { TextArea } = Input;

interface Master {
  id: number;
  name: string;
  gorod: number | { id: number };
}

interface Gorod {
  id: number;
  name: string;
}

interface RK {
  id: number;
  rk_name: string;
}

interface TipZayavki {
  id: number;
  name: string;
}

interface Zayavka {
  id: number;
  gorod: number;
  gorod_id?: number;
  tip_zayavki: number;
  phone_client: string;
  client_name: string;
  address: string;
  meeting_date?: string;
  rk: number;
  master: number;
  status?: string;
  problema?: string;
  tip_techniki?: string;
  kc_name?: string;
  created_at?: string;
  updated_at?: string;
}

interface FormValues {
  gorod: number;
  tip_zayavki: number;
  phone_client: string;
  client_name: string;
  address: string;
  meeting_date?: Dayjs | string;
  rk: number;
  master: number;
  status: string;
  problema: string;
  tip_techniki: string;
  kc_name: string;
}

const ZayavkiPage: React.FC = () => {
  const [zayavki, setZayavki] = useState<Zayavka[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [modalVisible, setModalVisible] = useState<boolean>(false);
  const [editingZayavka, setEditingZayavka] = useState<Zayavka | null>(null);
  const [form] = Form.useForm<FormValues>();
  const navigate = useNavigate();
  
  const [goroda, setGoroda] = useState<Gorod[]>([]);
  const [rkList, setRkList] = useState<RK[]>([]);
  const [tipy, setTipy] = useState<TipZayavki[]>([]);
  const [masters, setMasters] = useState<Master[]>([]);
  const [allMasters, setAllMasters] = useState<Master[]>([]);

  const ALLOWED_STATUSES = [
    'Ожидает',
    'Ожидает Принятия',
    'Принял',
    'В пути',
    'В работе',
    'Модерн',
    'Готово',
    'Отказ',
    'НеЗаказ',
  ];

  const { user } = useAuth();
  const typedUser = user as User | null;

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async (): Promise<void> => {
    try {
      const [zayavkiRes, gorodaRes, rkRes, tipyRes, mastersRes] = await Promise.all([
        axios.get('/api/zayavki/'),
        axios.get('/api/gorod/'),
        axios.get('/api/rk/'),
        axios.get('/api/tipzayavki/'),
        axios.get('/api/master/')
      ]);
      
      setZayavki(Array.isArray(zayavkiRes.data) ? zayavkiRes.data : (zayavkiRes.data.results || []));
      setGoroda(Array.isArray(gorodaRes.data) ? gorodaRes.data : (gorodaRes.data.results || []));
      setRkList(Array.isArray(rkRes.data) ? rkRes.data : (rkRes.data.results || []));
      setTipy(Array.isArray(tipyRes.data) ? tipyRes.data : (tipyRes.data.results || []));
      setAllMasters(Array.isArray(mastersRes.data) ? mastersRes.data : (mastersRes.data.results || []));
      setLoading(false);
    } catch (error) {
      message.error('Ошибка загрузки данных');
      setLoading(false);
    }
  };

  const handleAdd = (): void => {
    setEditingZayavka(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: Zayavka): void => {
    setEditingZayavka(record);
    const formData: FormValues = { 
      ...record,
      status: record.status || 'Ожидает',
      problema: record.problema || '',
      tip_techniki: record.tip_techniki || '',
      kc_name: record.kc_name || ''
    };
    if (record.meeting_date) {
      const d = dayjs(record.meeting_date);
      formData.meeting_date = d.isValid() ? d : undefined;
    }
    form.setFieldsValue(formData);
    setModalVisible(true);
  };

  const handleDelete = async (id: number): Promise<void> => {
    try {
      await axios.delete(`/api/zayavki/${id}/`);
      message.success('Заявка удалена');
      loadData();
    } catch (error) {
      message.error('Ошибка удаления');
    }
  };

  const handleSubmit = async (values: FormValues): Promise<void> => {
    try {
      const sendValues = { ...values };
      if (sendValues.meeting_date && typeof sendValues.meeting_date !== 'string') {
        sendValues.meeting_date = sendValues.meeting_date.format('YYYY-MM-DDTHH:mm:ss');
      }
      
      if (editingZayavka) {
        await axios.put(`/api/zayavki/${editingZayavka.id}/`, sendValues);
        message.success('Заявка обновлена');
      } else {
        await axios.post('/api/zayavki/', sendValues);
        message.success('Заявка создана');
      }
      setModalVisible(false);
      loadData();
    } catch (error) {
      message.error('Ошибка сохранения');
    }
  };

  const handleGorodChange = (gorodId: number): void => {
    const filteredMasters = allMasters.filter(m => m.gorod === gorodId || (m.gorod && typeof m.gorod === 'object' && m.gorod.id === gorodId));
    setMasters(filteredMasters);
    form.setFieldsValue({ master: undefined });
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'Ожидает': return 'orange';
      case 'В работе': return 'blue';
      case 'Завершено': return 'green';
      case 'Отказ': return 'red';
      default: return 'default';
    }
  };

  // Фильтрация заявок по статусу и по городу для director
  let filteredZayavki = zayavki.filter(z => ALLOWED_STATUSES.includes((z.status || '').trim()));
  if (typedUser && typedUser.role === 'director') {
    filteredZayavki = filteredZayavki.filter(z => String(z.gorod) === String(typedUser.gorod_id) || String(z.gorod_id) === String(typedUser.gorod_id));
  }

  const columns: ColumnType<Zayavka>[] = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: 'Город',
      dataIndex: 'gorod',
      key: 'gorod',
      render: (gorodId: number) => {
        const gorod = goroda.find(g => g.id === gorodId);
        return gorod ? gorod.name : gorodId;
      },
    },
    {
      title: 'Клиент',
      dataIndex: 'client_name',
      key: 'client_name',
    },
    {
      title: 'Телефон',
      dataIndex: 'phone_client',
      key: 'phone_client',
    },
    {
      title: 'Статус',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>
          {status || 'Не указан'}
        </Tag>
      ),
      filters: ALLOWED_STATUSES.map(status => ({ text: status, value: status })),
      onFilter: (value: boolean | React.Key, record: Zayavka) => record.status === value,
    },
    {
      title: 'Дата встречи',
      dataIndex: 'meeting_date',
      key: 'meeting_date',
      render: (date: string) => date ? dayjs(date).format('DD.MM.YYYY HH:mm') : 'Не указана',
      sorter: (a: Zayavka, b: Zayavka) => {
        if (!a.meeting_date) return 1;
        if (!b.meeting_date) return -1;
        return dayjs(a.meeting_date).unix() - dayjs(b.meeting_date).unix();
      },
    },
    {
      title: 'Действия',
      key: 'actions',
      render: (_: any, record: Zayavka) => (
        <Space>
          <Tooltip title="Просмотр">
            <Button 
              icon={<EyeOutlined />} 
              onClick={() => navigate(`/zayavki/${record.id}`)}
              size="small"
            />
          </Tooltip>
          <Tooltip title="Редактировать">
            <Button 
              icon={<EditOutlined />} 
              onClick={() => handleEdit(record)}
              size="small"
            />
          </Tooltip>
          <Tooltip title="Удалить">
            <Button 
              icon={<DeleteOutlined />} 
              danger
              onClick={() => handleDelete(record.id)}
              size="small"
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <Title level={2} style={{ margin: 0 }}>Заявки</Title>
        <Button 
          type="primary" 
          icon={<PlusOutlined />} 
          onClick={handleAdd}
          size="large"
        >
          Добавить заявку
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          dataSource={filteredZayavki}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `${range[0]}-${range[1]} из ${total} заявок`,
          }}
        />
      </Card>

      <Modal
        title={editingZayavka ? 'Редактировать заявку' : 'Добавить заявку'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={800}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <Form.Item name="gorod" label="Город" rules={[{ required: true, message: 'Выберите город' }]}>
              <Select 
                placeholder="Выберите город" 
                onChange={handleGorodChange}
                showSearch
                optionFilterProp="children"
              >
                {goroda.map(g => (
                  <Select.Option key={g.id} value={g.id}>{g.name}</Select.Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item name="tip_zayavki" label="Тип заявки" rules={[{ required: true, message: 'Выберите тип заявки' }]}>
              <Select placeholder="Выберите тип заявки" showSearch optionFilterProp="children">
                {tipy.map(t => (
                  <Select.Option key={t.id} value={t.id}>{t.name}</Select.Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item name="client_name" label="Имя клиента" rules={[{ required: true, message: 'Введите имя клиента' }]}>
              <Input placeholder="Имя клиента" />
            </Form.Item>

            <Form.Item name="phone_client" label="Телефон клиента" rules={[{ required: true, message: 'Введите телефон' }]}>
              <Input placeholder="Телефон клиента" />
            </Form.Item>

            <Form.Item name="rk" label="РК" rules={[{ required: true, message: 'Выберите РК' }]}>
              <Select placeholder="Выберите РК" showSearch optionFilterProp="children">
                {rkList.map(rk => (
                  <Select.Option key={rk.id} value={rk.id}>{rk.rk_name}</Select.Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item name="master" label="Мастер" rules={[{ required: true, message: 'Выберите мастера' }]}>
              <Select placeholder="Выберите мастера" showSearch optionFilterProp="children">
                {masters.map(m => (
                  <Select.Option key={m.id} value={m.id}>{m.name}</Select.Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item name="status" label="Статус" rules={[{ required: true, message: 'Выберите статус' }]}>
              <Select placeholder="Выберите статус">
                {ALLOWED_STATUSES.map(status => (
                  <Select.Option key={status} value={status}>{status}</Select.Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item name="meeting_date" label="Дата встречи" rules={[{ required: true, message: 'Выберите дату встречи' }]}>
              <Input type="datetime-local" />
            </Form.Item>
          </div>

          <Form.Item name="address" label="Адрес" rules={[{ required: true, message: 'Введите адрес' }]}>
            <Input placeholder="Адрес" />
          </Form.Item>

          <Form.Item name="problema" label="Проблема" rules={[{ required: true, message: 'Опишите проблему' }]}>
            <TextArea rows={3} placeholder="Опишите проблему" />
          </Form.Item>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <Form.Item name="tip_techniki" label="Тип техники" rules={[{ required: true, message: 'Введите тип техники' }]}>
              <Input placeholder="Тип техники" />
            </Form.Item>

            <Form.Item name="kc_name" label="Имя КЦ" rules={[{ required: true, message: 'Введите имя КЦ' }]}>
              <Input placeholder="Имя КЦ" />
            </Form.Item>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '24px' }}>
            <Button onClick={() => setModalVisible(false)}>
              Отмена
            </Button>
            <Button type="primary" htmlType="submit">
              {editingZayavka ? 'Обновить' : 'Создать'}
            </Button>
          </div>
        </Form>
      </Modal>
    </div>
  );
};

export default ZayavkiPage; 