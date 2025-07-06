import React, { useEffect, useState } from 'react';
import { Table, Tag, Button, Modal, Upload, message, Typography, Spin, Descriptions } from 'antd';
import { UploadOutlined, EyeOutlined } from '@ant-design/icons';
import type { UploadFile } from 'antd/es/upload/interface';
import axios from 'axios';
import useAuth from '../hooks/useAuth';

interface Payout {
  id: number;
  zayavka_id: number;
  created_at: string;
  summa: number;
  status: 'pending' | 'checking' | 'confirmed';
  comment?: string;
  file?: string;
}

interface PayoutResponse {
  results?: Payout[];
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

export default function FinansiMasterPage(): React.JSX.Element {
  const { user } = useAuth();
  const [loading, setLoading] = useState<boolean>(true);
  const [payouts, setPayouts] = useState<Payout[]>([]);
  const [selected, setSelected] = useState<Payout | null>(null);
  const [modalOpen, setModalOpen] = useState<boolean>(false);
  const [uploading, setUploading] = useState<boolean>(false);
  const [fileList, setFileList] = useState<UploadFile[]>([]);

  useEffect(() => {
    fetchPayouts();
    // eslint-disable-next-line
  }, []);

  const fetchPayouts = async (): Promise<void> => {
    setLoading(true);
    try {
      const res = await axios.get<Payout[] | PayoutResponse>('/api/master-payouts/');
      let data = res.data;
      let payoutsArr: Payout[] = Array.isArray(data) ? data : (Array.isArray(data.results) ? data.results : []);
      setPayouts(payoutsArr);
    } catch (e) {
      message.error('Ошибка загрузки выплат');
    }
    setLoading(false);
  };

  const openModal = (record: Payout): void => {
    setSelected(record);
    setModalOpen(true);
    setFileList([]);
  };

  const handleUpload = async (): Promise<void> => {
    if (!fileList.length) {
      message.warning('Прикрепите файл чека!');
      return;
    }
    if (!selected) return;
    
    setUploading(true);
    const formData = new FormData();
    formData.append('file', fileList[0].originFileObj as File);
    formData.append('status', 'checking');
    try {
      await axios.patch(`/api/master-payouts/${selected.id}/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      message.success('Чек отправлен на проверку!');
      setModalOpen(false);
      fetchPayouts();
    } catch (e) {
      message.error('Ошибка отправки чека');
    }
    setUploading(false);
  };

  const columns = [
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
      title: 'Комментарий руководителя',
      dataIndex: 'comment',
      key: 'comment',
      render: (v: string) => v || '—',
      align: 'center' as const,
    },
    {
      title: '',
      key: 'actions',
      align: 'center' as const,
      render: (_: any, record: Payout) => (
        <Button icon={<EyeOutlined />} onClick={() => openModal(record)} shape="circle" size="large" />
      ),
    },
  ];

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
      }}>Финансы</Typography.Title>
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
        footer={null}
        width={500}
        bodyStyle={{ padding: 32 }}
        style={{ borderRadius: 20 }}
      >
        {selected ? (
          <div>
            <Descriptions column={1} bordered size="middle" labelStyle={{ fontWeight: 700, fontSize: 18 }} contentStyle={{ fontSize: 18 }}>
              <Descriptions.Item label="Сумма"><span style={{ fontWeight: 700, color: '#1890ff', fontSize: 20 }}>{selected.summa} ₽</span></Descriptions.Item>
              <Descriptions.Item label="Статус">
                <Tag color={STATUS_COLORS[selected.status]} style={{ fontSize: 16, padding: '4px 16px', borderRadius: 12 }}>{STATUS_LABELS[selected.status]}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Комментарий руководителя">{selected.comment || '—'}</Descriptions.Item>
              <Descriptions.Item label="Дата">{selected.created_at ? new Date(selected.created_at).toLocaleString() : ''}</Descriptions.Item>
            </Descriptions>
            {selected.status === 'pending' && (
              <div style={{ marginTop: 32 }}>
                <Upload
                  beforeUpload={(file: UploadFile) => { setFileList([file]); return false; }}
                  fileList={fileList}
                  onRemove={() => setFileList([])}
                  maxCount={1}
                >
                  <Button icon={<UploadOutlined />}>Прикрепить чек</Button>
                </Upload>
                <Button
                  type="primary"
                  style={{ marginTop: 16, width: '100%', fontSize: 18, height: 48, borderRadius: 12 }}
                  loading={uploading}
                  onClick={handleUpload}
                >
                  Отправить
                </Button>
              </div>
            )}
            {selected.status !== 'pending' && selected.file && (
              <div style={{ marginTop: 32 }}>
                <a href={selected.file} target="_blank" rel="noopener noreferrer" style={{ fontSize: 18 }}>Скачать чек</a>
              </div>
            )}
          </div>
        ) : <Spin />}
      </Modal>
    </div>
  );
} 