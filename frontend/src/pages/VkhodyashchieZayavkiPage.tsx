import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Table, Button, Modal, Form, Input, Select, message, Space, Card, Tag, Typography, Tooltip } from 'antd';
import type { ColumnType } from 'antd/es/table';
import { PlusOutlined, EditOutlined, DeleteOutlined, EyeOutlined, SearchOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';
import { useNavigate } from 'react-router-dom';
dayjs.extend(utc);
dayjs.extend(timezone);

const { Title } = Typography;

interface Zayavka {
  id: number;
  rk_name?: string;
  gorod_name?: string;
  phone_client: string;
  phone_atc?: string;
  tip_zayavki_name?: string;
  client_name: string;
  address: string;
  meeting_date?: string;
  tip_techniki?: string;
  problema?: string;
  status?: string;
  kc_name?: string;
  comment_kc?: string;
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

interface Master {
  id: number;
  name: string;
}

const ALL_STATUSES = [
  'Звонит',
  'ТНО',
  'Перезвонить',
  'Отказ',
  'Ожидает',
  'Ожидает Принятия',
  'Принял',
  'В пути',
  'В работе',
  'Модерн',
  'Готово',
  'НеЗаказ',
];

const VkhodyashchieZayavkiPage: React.FC = () => {
  const navigate = useNavigate();
  const [zayavki, setZayavki] = useState<Zayavka[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [goroda, setGoroda] = useState<Gorod[]>([]);
  const [rkList, setRkList] = useState<RK[]>([]);
  const [tipy, setTipy] = useState<TipZayavki[]>([]);
  const [masters, setMasters] = useState<Master[]>([]);
  const [allMasters, setAllMasters] = useState<Master[]>([]);
  const [searchText, setSearchText] = useState<string>('');
  const [searchedColumn, setSearchedColumn] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('INCOMING');
  const [allZayavki, setAllZayavki] = useState<Zayavka[]>([]);

  // Только статусы для входящих заявок
  const INCOMING_STATUSES = [
    'Звонит',
    'ТНО',
    'Перезвонить',
    'Отказ',
  ];

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
      setAllZayavki(Array.isArray(zayavkiRes.data) ? zayavkiRes.data : (zayavkiRes.data.results || []));
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

  useEffect(() => {
    if (statusFilter === 'INCOMING') {
      setZayavki(allZayavki.filter(z => INCOMING_STATUSES.includes(z.status || '')));
    } else if (statusFilter === 'ALL') {
      setZayavki(allZayavki);
    } else {
      setZayavki(allZayavki.filter(z => z.status === statusFilter));
    }
  }, [statusFilter, allZayavki, INCOMING_STATUSES]);

  const handleDelete = async (id: number): Promise<void> => {
    try {
      await axios.delete(`/api/zayavki/${id}/`);
      message.success('Заявка удалена');
      loadData();
    } catch (error) {
      message.error('Ошибка удаления');
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'Звонит': return 'blue';
      case 'ТНО': return 'orange';
      case 'Перезвонить': return 'purple';
      case 'Отказ': return 'red';
      case 'Ожидает': return 'gold';
      default: return 'default';
    }
  };

  const columns: ColumnType<Zayavka>[] = [
    { 
      title: 'ID', 
      dataIndex: 'id', 
      key: 'id', 
      width: 60 
    },
    { 
      title: 'РК', 
      dataIndex: 'rk_name', 
      key: 'rk_name', 
      render: (text: string) => text || 'Не указан'
    },
    { 
      title: 'Город', 
      dataIndex: 'gorod_name', 
      key: 'gorod_name', 
      render: (text: string) => text || 'Не указан'
    },
    { 
      title: 'Номер телефона клиента', 
      dataIndex: 'phone_client', 
      key: 'phone_client', 
      render: (text: string) => text || 'Не указан'
    },
    { 
      title: 'Номер телефона ATC', 
      dataIndex: 'phone_atc', 
      key: 'phone_atc', 
      render: (text: string) => text || 'Не указан'
    },
    { 
      title: 'Тип заявки', 
      dataIndex: 'tip_zayavki_name', 
      key: 'tip_zayavki_name', 
      render: (text: string) => text || 'Не указан'
    },
    { 
      title: 'Имя клиента', 
      dataIndex: 'client_name', 
      key: 'client_name', 
      render: (text: string) => text || 'Не указан'
    },
    { 
      title: 'Адрес', 
      dataIndex: 'address', 
      key: 'address', 
      render: (text: string) => text || 'Не указан'
    },
    { 
      title: 'Дата встречи', 
      dataIndex: 'meeting_date', 
      key: 'meeting_date', 
      render: (text: string) => { 
        if (!text) return 'Не указана'; 
        const d = dayjs(text); 
        if (!d.isValid()) return `НЕВЕРНЫЙ ФОРМАТ: ${text}`; 
        return d.format('DD.MM.YYYY HH:mm'); 
      }
    },
    { 
      title: 'Тип техники', 
      dataIndex: 'tip_techniki', 
      key: 'tip_techniki', 
      render: (text: string) => text || 'Не указан'
    },
    { 
      title: 'Проблема', 
      dataIndex: 'problema', 
      key: 'problema', 
      render: (text: string) => text || 'Не указана'
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
      filters: INCOMING_STATUSES.map(s => ({ text: s, value: s })), 
      onFilter: (value: boolean | React.Key, record: Zayavka) => record.status === value 
    },
    { 
      title: 'Имя КЦ', 
      dataIndex: 'kc_name', 
      key: 'kc_name', 
      render: (text: string) => text || 'Не указано'
    },
    { 
      title: 'Комментарий КЦ', 
      dataIndex: 'comment_kc', 
      key: 'comment_kc', 
      render: (text: string) => text || 'Нет комментария'
    },
    { 
      title: 'Действия', 
      key: 'actions', 
      width: 200, 
      render: (_: any, record: Zayavka) => (
        <Space>
          <Tooltip title="Редактировать">
            <Button 
              type="default" 
              size="small" 
              icon={<EditOutlined />} 
              onClick={() => navigate(`/vkhodyashchie-zayavki/${record.id}`)} 
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
                  title: 'Удалить заявку?', 
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
      ) 
    },
  ];

  return (
    <div>
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <Title level={3} style={{ margin: 0 }}>Входящие заявки</Title>
          <div style={{ display: 'flex', gap: 16 }}>
            <Select
              value={statusFilter}
              style={{ width: 220 }}
              onChange={setStatusFilter}
              options={[
                { value: 'INCOMING', label: 'Входящие статусы' },
                { value: 'ALL', label: 'Все статусы' },
                ...ALL_STATUSES.map(status => ({ value: status, label: status }))
              ]}
            />
          </div>
        </div>
        <Table
          columns={columns}
          dataSource={zayavki}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `${range[0]}-${range[1]} из ${total} заявок`,
          }}
          scroll={{ x: 1200 }}
        />
      </Card>
    </div>
  );
};

export default VkhodyashchieZayavkiPage; 