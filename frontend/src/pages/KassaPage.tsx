import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Card, Typography, Table, Tabs, Button, Modal, Form, Input, InputNumber, DatePicker, message, Select } from 'antd';
import dayjs, { Dayjs } from 'dayjs';
import useAuth from '../hooks/useAuth';

const { Title } = Typography;

interface Tranzakciya {
  id: number;
  date: string;
  summa: number | string;
  note?: string;
  tip_tranzakcii_name: string;
  gorod: number;
}

interface TipTranzakcii {
  id: number;
  name: string;
}

interface TranzakciyaForm {
  date: Dayjs;
  summa: number;
  tip_tranzakcii: number;
  comment?: string;
}

export default function KassaPage(): React.JSX.Element {
  const { user } = useAuth();
  const [loading, setLoading] = useState<boolean>(true);
  const [tranzakcii, setTranzakcii] = useState<Tranzakciya[]>([]);
  const [tipy, setTipy] = useState<TipTranzakcii[]>([]);
  const [modalOpen, setModalOpen] = useState<boolean>(false);
  const [modalType, setModalType] = useState<'приход' | 'расход'>('приход');
  const [form] = Form.useForm();

  useEffect(() => {
    loadData();
    axios.get('/api/tiptranzakcii/').then(res => {
      const data: TipTranzakcii[] = Array.isArray(res.data) ? res.data : (res.data.results || []);
      setTipy(data);
    });
  }, []);

  const loadData = (): void => {
    setLoading(true);
    axios.get('/api/tranzakcii/')
      .then(res => {
        const data: Tranzakciya[] = Array.isArray(res.data) ? res.data : (res.data.results || []);
        setTranzakcii(data);
      })
      .finally(() => setLoading(false));
  };

  // Фильтрация по типу и городу
  let prihod = tranzakcii.filter(t => t.tip_tranzakcii_name === 'Приход');
  let rashod = tranzakcii.filter(t => t.tip_tranzakcii_name === 'Расход');
  if (user && (user.role === 'director' || user.role === 'admin')) {
    prihod = prihod.filter(t => String(t.gorod) === String(user.gorod_id));
    rashod = rashod.filter(t => String(t.gorod) === String(user.gorod_id));
  }

  const prihodColumns = [
    { title: 'Дата', dataIndex: 'date', key: 'date', render: (v: string) => v ? dayjs(v).format('DD.MM.YYYY') : '' },
    { title: 'Сумма', dataIndex: 'summa', key: 'summa', render: (v: number | string) => v ? v + ' ₽' : '' },
    { title: 'Комментарий', dataIndex: 'note', key: 'note' },
  ];
  const rashodColumns = [
    { title: 'Дата', dataIndex: 'date', key: 'date', render: (v: string) => v ? dayjs(v).format('DD.MM.YYYY') : '' },
    { title: 'Сумма', dataIndex: 'summa', key: 'summa', render: (v: number | string) => v ? v + ' ₽' : '' },
    { title: 'Комментарий', dataIndex: 'note', key: 'note' },
  ];

  // Баланс
  const prihodSum = prihod.reduce((acc, t) => acc + (Number(t.summa) || 0), 0);
  const rashodSum = rashod.reduce((acc, t) => acc + (Number(t.summa) || 0), 0);
  const balance = prihodSum - rashodSum;

  const openAddModal = (type: 'приход' | 'расход'): void => {
    setModalType(type);
    setModalOpen(true);
    form.resetFields();
    form.setFieldsValue({ date: dayjs() });
  };

  const handleAdd = async (): Promise<void> => {
    try {
      const values = await form.validateFields();
      console.log('user:', user);
      console.log('gorod:', user?.gorod_id);
      await axios.post('/api/tranzakcii/', {
        ...values,
        summa: values.summa,
        gorod: user?.gorod_id,
        tip_tranzakcii: values.tip_tranzakcii,
        operation: modalType,
        date: values.date.format('YYYY-MM-DD'),
      });
      message.success('Транзакция добавлена');
      setModalOpen(false);
      loadData();
    } catch (e: any) {
      message.error(e?.response?.data?.detail || 'Ошибка добавления');
      console.error(e);
    }
  };

  return (
    <Card style={{ maxWidth: 900, margin: '0 auto' }}>
      <Title level={3} style={{ marginBottom: 24 }}>Касса</Title>
      <Tabs
        defaultActiveKey="prihod"
        items={[
          {
            key: 'prihod',
            label: 'Приход',
            children: <>
              <Button type="primary" style={{ marginBottom: 16 }} onClick={() => openAddModal('приход')}>Добавить</Button>
              <Table columns={prihodColumns} dataSource={prihod} loading={loading} rowKey="id" pagination={false} />
            </>,
          },
          {
            key: 'rashod',
            label: 'Расход',
            children: <>
              <Button type="primary" style={{ marginBottom: 16 }} onClick={() => openAddModal('расход')}>Добавить</Button>
              <Table columns={rashodColumns} dataSource={rashod} loading={loading} rowKey="id" pagination={false} />
            </>,
          },
          {
            key: 'balance',
            label: 'Баланс',
            children: (
              <div style={{ padding: 32, textAlign: 'center', fontSize: 24 }}>
                <div>Приход: <b>{prihodSum} ₽</b></div>
                <div>Расход: <b>{rashodSum} ₽</b></div>
                <div style={{ marginTop: 16, fontSize: 32 }}>Баланс: <b>{balance} ₽</b></div>
              </div>
            ),
          },
        ]}
      />
      <Modal
        open={modalOpen}
        title={modalType === 'приход' ? 'Добавить приход' : 'Добавить расход'}
        onCancel={() => setModalOpen(false)}
        onOk={handleAdd}
        okText="Сохранить"
        cancelText="Отмена"
      >
        <Form form={form} layout="vertical">
          <Form.Item name="date" label="Дата" rules={[{ required: true, message: 'Выберите дату' }]}> 
            <DatePicker format="YYYY-MM-DD" style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="summa" label="Сумма" rules={[{ required: true, message: 'Введите сумму' }]}> 
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="tip_tranzakcii" label="Тип транзакции" rules={[{ required: true, message: 'Выберите тип транзакции' }]}> 
            <Select placeholder="Выберите тип">
              {tipy.map(t => (
                <Select.Option key={t.id} value={t.id}>{t.name}</Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="comment" label="Комментарий">
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
} 