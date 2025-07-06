import React, { useState, useEffect, useRef } from 'react';
import { Table, Tag, Typography, Input, Space, Tooltip } from 'antd';
import { EyeOutlined, SearchOutlined } from '@ant-design/icons';
import type { ColumnType } from 'antd/es/table';
import type { InputRef } from 'antd';
import axios from 'axios';
import useAuth from '../hooks/useAuth';
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';

dayjs.extend(utc);
dayjs.extend(timezone);

const { Title } = Typography;

interface Zayavka {
  id: number;
  client_name: string;
  phone_client: string;
  address: string;
  meeting_date: string;
  status: string;
  problema: string;
  chistymi: number;
  master: number;
}

interface ZayavkaResponse {
  results?: Zayavka[];
}

export default function ZayvkiMasterPage(): React.JSX.Element {
  const [zayavki, setZayavki] = useState<Zayavka[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const searchInput = useRef<InputRef>(null);
  const { user } = useAuth();

  useEffect(() => {
    if (!user) return;
    axios.get<Zayavka[] | ZayavkaResponse>('/api/zayavki/')
      .then(res => {
        const all = Array.isArray(res.data) ? res.data : (res.data.results || []);
        setZayavki(all.filter(z => z.master === user.id));
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [user]);

  const getStatusColor = (status: string): string => {
    switch ((status || '').trim()) {
      case 'Ожидает': return 'orange';
      case 'В работе': return 'blue';
      case 'Готово': return 'green';
      case 'Отказ': return 'red';
      default: return 'default';
    }
  };

  const getColumnSearchProps = (dataIndex: keyof Zayavka, placeholder?: string) => ({
    filterDropdown: ({ setSelectedKeys, selectedKeys, confirm, clearFilters }: any) => (
      <div style={{ padding: 8 }}>
        <Input
          ref={searchInput}
          placeholder={placeholder || `Поиск`}
          value={selectedKeys[0]}
          onChange={e => setSelectedKeys(e.target.value ? [e.target.value] : [])}
          onPressEnter={() => handleSearch(selectedKeys, confirm)}
          style={{ marginBottom: 8, display: 'block' }}
        />
        <Space>
          <button type="button" className="ant-btn ant-btn-primary" onClick={() => handleSearch(selectedKeys, confirm)} style={{ width: 90 }}>
            <SearchOutlined /> Поиск
          </button>
          <button type="button" className="ant-btn" onClick={() => handleReset(clearFilters)} style={{ width: 90 }}>
            Сбросить
          </button>
        </Space>
      </div>
    ),
    filterIcon: (filtered: boolean) => <SearchOutlined style={{ color: filtered ? '#1890ff' : undefined }} />,
    onFilter: (value: React.Key | boolean, record: Zayavka) =>
      record[dataIndex]
        ? record[dataIndex].toString().toLowerCase().includes(value.toString().toLowerCase())
        : false,
    onFilterDropdownOpenChange: (visible: boolean) => {
      if (visible) {
        setTimeout(() => searchInput.current?.select(), 100);
      }
    },
  });

  const handleSearch = (selectedKeys: React.Key[], confirm: () => void): void => {
    confirm();
  };

  const handleReset = (clearFilters: () => void): void => {
    clearFilters();
  };

  const columns: ColumnType<Zayavka>[] = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
    { title: 'Клиент', dataIndex: 'client_name', key: 'client_name', ...getColumnSearchProps('client_name', 'Поиск по клиенту') },
    { title: 'Телефон', dataIndex: 'phone_client', key: 'phone_client', ...getColumnSearchProps('phone_client', 'Поиск по телефону') },
    { title: 'Адрес', dataIndex: 'address', key: 'address', ...getColumnSearchProps('address', 'Поиск по адресу') },
    { 
      title: 'Дата', 
      dataIndex: 'meeting_date', 
      key: 'meeting_date', 
      render: (text: string) => text ? dayjs(text).format('DD.MM.YYYY HH:mm') : '—', 
      ...getColumnSearchProps('meeting_date', 'Поиск по дате') 
    },
    { 
      title: 'Статус', 
      dataIndex: 'status', 
      key: 'status', 
      render: (status: string) => <Tag color={getStatusColor(status)}>{status}</Tag>, 
      filters: [
        { text: 'Модерн', value: 'Модерн' },
        { text: 'Готово', value: 'Готово' },
        { text: 'Отказ', value: 'Отказ' },
      ], 
      onFilter: (value: React.Key | boolean, record: Zayavka) => record.status === value 
    },
    { title: 'Проблема', dataIndex: 'problema', key: 'problema', ...getColumnSearchProps('problema', 'Поиск по проблеме') },
    { title: 'Итог', dataIndex: 'chistymi', key: 'chistymi', render: (chistymi: number) => chistymi ? `${chistymi} ₽` : '—' },
    { 
      title: 'Действия', 
      key: 'actions', 
      width: 100, 
      render: (_: any, record: Zayavka) => (
        <Space>
          <Tooltip title="Просмотр">
            <button type="button" className="ant-btn ant-btn-primary ant-btn-sm" onClick={() => window.open(`/master-dashboard/zayavki/${record.id}`, '_blank')}>
              <EyeOutlined />
            </button>
          </Tooltip>
        </Space>
      ) 
    },
  ];

  return (
    <div style={{ padding: 32 }}>
      <Title level={3} style={{ margin: '0 0 16px 0' }}>Мои заявки</Title>
      <Table
        columns={columns}
        dataSource={zayavki}
        rowKey="id"
        loading={loading}
        pagination={{ showSizeChanger: true, showQuickJumper: true, showTotal: (total: number, range: [number, number]) => `${range[0]}-${range[1]} из ${total} заявок` }}
        scroll={{ x: 1200 }}
        style={{ width: '100%' }}
      />
    </div>
  );
} 