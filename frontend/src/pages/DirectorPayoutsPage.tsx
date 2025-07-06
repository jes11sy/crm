import React, { useEffect, useState, useCallback } from 'react';
import { Table, Tag, Button, Modal, Typography, Select, DatePicker, Space, Descriptions, Spin, message, Popconfirm, Input } from 'antd';
import { EyeOutlined } from '@ant-design/icons';
import axios from 'axios';

interface Master {
  id: number;
  name: string;
}

interface Zayavka {
  master_name?: string;
}

interface Payout {
  id: number;
  zayavka_id: number;
  zayavka: Zayavka;
  created_at: string;
  summa: number;
  status: 'pending' | 'checking' | 'confirmed';
  comment?: string;
  file?: string;
}

interface Filters {
  master: number | null;
  status: string | null;
  date: string | null;
}

const STATUS_COLORS: Record<string, string> = {
  pending: 'orange',
  checking: 'blue',
  confirmed: 'green',
};

const STATUS_LABELS: Record<string, string> = {
  pending: 'Ожидает перевод',
  checking: 'Отправлено на проверку',
  confirmed: 'Подтверждено',
};

const DirectorPayoutsPage: React.FC = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [payouts, setPayouts] = useState<Payout[]>([]);
  const [masters, setMasters] = useState<Master[]>([]);
  const [selected, setSelected] = useState<Payout | null>(null);
  const [modalOpen, setModalOpen] = useState<boolean>(false);
  const [filters, setFilters] = useState<Filters>({ master: null, status: null, date: null });

  useEffect(() => {
    fetchMasters();
    fetchPayouts();
  }, []);

  const fetchMasters = async (): Promise<void> => {
    try {
      const res = await axios.get('/api/master/');
      setMasters(Array.isArray(res.data) ? res.data : []);
    } catch (e) {
      console.error('Ошибка загрузки мастеров:', e);
    }
  };

  const fetchPayouts = async (): Promise<void> => {
    setLoading(true);
    try {
      const params: Record<string, any> = {};
      if (filters.master) params['zayavka__master'] = filters.master;
      if (filters.status) params.status = filters.status;
      // Фильтр по дате можно реализовать через created_at__date
      const res = await axios.get('/api/master-payouts/', { params });
      let data = res.data;
      let payoutsArr = Array.isArray(data) ? data : (Array.isArray(data.results) ? data.results : []);
      setPayouts(payoutsArr);
    } catch (e) {
      message.error('Ошибка загрузки выплат');
    }
    setLoading(false);
  };

  const columns = [
    {
      title: 'Мастер',
      dataIndex: ['zayavka', 'master_name'],
      key: 'master',
      render: (_: any, record: Payout) => record.zayavka && record.zayavka.master_name ? record.zayavka.master_name : '—',
      align: 'center' as const,
    },
    {
      title: 'Номер заказа',
      dataIndex: 'zayavka_id',
      key: 'zayavka_id',
      align: 'center' as const,
    },
    {
      title: 'Дата',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text: string) => text ? new Date(text).toLocaleString() : '',
      align: 'center' as const,
    },
    {
      title: 'Сумма',
      dataIndex: 'summa',
      key: 'summa',
      render: (v: number) => v ? <span style={{ fontWeight: 700, color: '#1890ff', fontSize: 18 }}>{v} ₽</span> : '',
      align: 'center' as const,
    },
    {
      title: 'Статус',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => <Tag color={STATUS_COLORS[status]} style={{ fontSize: 16, padding: '4px 16px', borderRadius: 12 }}>{STATUS_LABELS[status]}</Tag>,
      align: 'center' as const,
    },
    {
      title: '',
      key: 'actions',
      align: 'center' as const,
      render: (_: any, record: Payout) => (
        <Button icon={<EyeOutlined />} onClick={() => { setSelected(record); setModalOpen(true); }} shape="circle" size="large" />
      ),
    },
  ];

  const safeMasters = Array.isArray(masters) ? masters : [];

  const handleConfirm = async (): Promise<void> => {
    if (!selected) return;
    try {
      await axios.patch(`/api/master-payouts/${selected.id}/`, { status: 'confirmed' });
      message.success('Выплата подтверждена');
      setModalOpen(false);
      fetchPayouts();
    } catch (e) {
      message.error('Ошибка при подтверждении');
    }
  };

  const handleReject = async (): Promise<void> => {
    if (!selected) return;
    let reason = '';
    Modal.confirm({
      title: 'Укажите причину отказа',
      content: <Input.TextArea autoSize onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => reason = e.target.value} placeholder="Причина отказа" />,
      okText: 'Отправить',
      cancelText: 'Отмена',
      onOk: async () => {
        if (!reason.trim()) {
          message.error('Укажите причину!');
          return Promise.reject();
        }
        try {
          await axios.patch(`/api/master-payouts/${selected.id}/`, { status: 'pending', comment: reason });
          message.success('Выплата отклонена');
          setModalOpen(false);
          fetchPayouts();
        } catch (e) {
          message.error('Ошибка при отклонении');
        }
      },
    });
  };

  return (
    <div style={{
      width: '100%',
      maxWidth: 1400,
      margin: '40px auto 0 auto',
      padding: '0 24px',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'stretch',
    }}>
      <Typography.Title level={2} style={{
        fontSize: 38,
        fontWeight: 900,
        margin: '0 0 32px 0',
        textAlign: 'left',
        letterSpacing: '-1px',
      }}>Переводы мастеров</Typography.Title>
      <Space style={{ marginBottom: 24 }}>
        <Select
          allowClear
          placeholder="Мастер"
          style={{ minWidth: 180 }}
          value={filters.master}
          onChange={(v: number | null) => setFilters(f => ({ ...f, master: v }))}
          options={safeMasters.map(m => ({ value: m.id, label: m.name }))}
        />
        <Select
          allowClear
          placeholder="Статус"
          style={{ minWidth: 180 }}
          value={filters.status}
          onChange={(v: string | null) => setFilters(f => ({ ...f, status: v }))}
          options={Object.entries(STATUS_LABELS).map(([value, label]) => ({ value, label }))}
        />
        <Button type="primary" onClick={fetchPayouts}>Фильтровать</Button>
      </Space>
      <div style={{
        background: 'rgba(255,255,255,0.97)',
        borderRadius: 20,
        boxShadow: '0 4px 24px 0 rgba(24,144,255,0.08)',
        padding: '32px 0',
        minHeight: 400,
      }}>
        <Table
          columns={columns}
          dataSource={payouts}
          rowKey="id"
          loading={loading}
          pagination={{ showSizeChanger: true, showQuickJumper: true }}
          style={{ background: 'transparent' }}
        />
      </div>
      <Modal
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        title={<span style={{ fontWeight: 800, fontSize: 26 }}>Выплата по заказу №{selected?.zayavka_id}</span>}
        footer={selected && (
          <Space style={{ justifyContent: 'flex-end', width: '100%' }}>
            <Button type="primary" onClick={handleConfirm} disabled={selected.status === 'confirmed'}>Подтвердить</Button>
            <Button danger onClick={handleReject} disabled={selected.status === 'pending'}>Отказать</Button>
          </Space>
        )}
        width={500}
        bodyStyle={{ padding: 32 }}
        style={{ borderRadius: 20 }}
      >
        {selected ? (
          <div>
            <Descriptions column={1} bordered size="middle" labelStyle={{ fontWeight: 700, fontSize: 18 }} contentStyle={{ fontSize: 18 }}>
              <Descriptions.Item label="Мастер">{selected.zayavka && selected.zayavka.master_name}</Descriptions.Item>
              <Descriptions.Item label="Сумма"><span style={{ fontWeight: 700, color: '#1890ff', fontSize: 20 }}>{selected.summa} ₽</span></Descriptions.Item>
              <Descriptions.Item label="Статус">
                <Tag color={STATUS_COLORS[selected.status]} style={{ fontSize: 16, padding: '4px 16px', borderRadius: 12 }}>{STATUS_LABELS[selected.status]}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Дата">{selected.created_at ? new Date(selected.created_at).toLocaleString() : ''}</Descriptions.Item>
            </Descriptions>
            {selected.file && (
              <div style={{ marginTop: 32 }}>
                <a href={selected.file} target="_blank" rel="noopener noreferrer" style={{ fontSize: 18 }}>Скачать чек</a>
              </div>
            )}
          </div>
        ) : <Spin />}
      </Modal>
    </div>
  );
};

export default DirectorPayoutsPage; 