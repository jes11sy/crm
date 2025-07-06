import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Typography, Spin, Button, Tag, Form, InputNumber, message, Tabs, Space, Modal, Input } from 'antd';
import axios from 'axios';
import ZayavkaFiles from '../components/ZayavkaFiles';
import useAuth from '../hooks/useAuth';
import { User } from '../types/entities';

const { Title } = Typography;
const API_FILES_URL = '/api/zayavka-files/';

interface Zayavka {
  id: number;
  client_name: string;
  phone_client: string;
  address: string;
  meeting_date?: string;
  tip_zayavki_name?: string;
  problema?: string;
  status?: string;
  itog?: number;
  rashod?: number;
  chistymi?: number;
  sdacha_mastera?: number;
  master?: number;
  comment_master?: string;
}

interface CalculatedValues {
  chistymi: number | null;
  sdacha_mastera: number | null;
}

interface FormValues {
  itog: number;
  rashod: number;
}

interface ModalState {
  visible: boolean;
  type: string;
  values: Record<string, any>;
}

const ZayavkaMasterDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const typedUser = user as User | null;
  const [zayavka, setZayavka] = useState<Zayavka | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [form] = Form.useForm<FormValues>();
  const [calculatedValues, setCalculatedValues] = useState<CalculatedValues>({
    chistymi: null,
    sdacha_mastera: null
  });
  const [modal, setModal] = useState<ModalState>({ visible: false, type: '', values: {} });
  const [modalLoading, setModalLoading] = useState<boolean>(false);

  useEffect(() => {
    setLoading(true);
    axios.get(`/api/zayavki/${id}/`)
      .then(res => {
        setZayavka(res.data);
        form.setFieldsValue({
          itog: res.data.itog,
          rashod: res.data.rashod,
        });
        calculateValues(res.data.itog, res.data.rashod);
      })
      .finally(() => setLoading(false));
  }, [id, form]);

  const calculateValues = (itog: number | null | undefined, rashod: number | null | undefined): void => {
    if (itog !== null && itog !== undefined && rashod !== null && rashod !== undefined) {
      const chistymi = itog - rashod;
      const sdacha_mastera = chistymi * 0.5;
      setCalculatedValues({
        chistymi: chistymi >= 0 ? chistymi : 0,
        sdacha_mastera: chistymi >= 0 ? sdacha_mastera : 0
      });
    } else {
      setCalculatedValues({
        chistymi: null,
        sdacha_mastera: null
      });
    }
  };

  useEffect(() => {
    const itog = form.getFieldValue('itog');
    const rashod = form.getFieldValue('rashod');
    calculateValues(itog, rashod);
  }, [form.getFieldValue('itog'), form.getFieldValue('rashod')]);

  const handleStatusChange = async (newStatus: string): Promise<void> => {
    setSaving(true);
    const updateData: Partial<Zayavka> = { status: newStatus };
    
    // Если отказался - очищаем поле мастера
    if (newStatus === 'Ожидает') {
      updateData.master = undefined;
    }
    
    try {
      const response = await axios.patch(`/api/zayavki/${id}/`, updateData);
      setZayavka(response.data);
      message.success('Статус обновлен!');
    } catch (error) {
      message.error('Ошибка при обновлении статуса');
    } finally {
      setSaving(false);
    }
  };

  const handleSave = async (values: FormValues): Promise<void> => {
    setSaving(true);
    try {
      // Проверка на чек расхода
      if (values.rashod > 0) {
        const res = await axios.get(`${API_FILES_URL}?zayavka=${id}`);
        const files = Array.isArray(res.data) ? res.data : res.data.results || [];
        const hasChek = files.some((f: any) => f.type === 'chek');
        if (!hasChek) {
          message.error('Пожалуйста, прикрепите чек расхода!');
          setSaving(false);
          return;
        }
      }
      const dataToSend = {
        ...values,
        chistymi: calculatedValues.chistymi,
        sdacha_mastera: calculatedValues.sdacha_mastera,
        status: 'Готово',
        master: zayavka?.master || (typedUser && typedUser.id),
      };
      await axios.patch(`/api/zayavki/${id}/`, dataToSend);
      const res = await axios.get(`/api/zayavki/${id}/`);
      setZayavka(res.data);
      message.success('Заявка проведена!');
    } catch {
      message.error('Ошибка при проведении');
    } finally {
      setSaving(false);
    }
  };

  // Универсальный обработчик для статусов с комментарием
  const handleStatusWithComment = async (status: string, commentFields: Record<string, any>): Promise<void> => {
    setModalLoading(true);
    try {
      let comment = '';
      if (status === 'Модерн') {
        comment = `Предоплата: ${commentFields.predoplata}; Сроки: ${commentFields.sroki}`;
      } else {
        comment = commentFields.comment;
      }
      const dataToSend: Partial<Zayavka> = {
        status,
        comment_master: comment,
      };
      if (status === 'Отказ') {
        dataToSend.itog = 0;
        dataToSend.rashod = 0;
        dataToSend.chistymi = 0;
        dataToSend.sdacha_mastera = 0;
      }
      await axios.patch(`/api/zayavki/${id}/`, dataToSend);
      if (zayavka) {
        setZayavka({ ...zayavka, ...dataToSend });
      }
      setModal({ visible: false, type: '', values: {} });
      message.success('Статус обновлен!');
    } catch {
      message.error('Ошибка при обновлении статуса');
    } finally {
      setModalLoading(false);
    }
  };

  if (loading) return <Spin style={{ margin: 40 }} />;
  if (!zayavka) return <div style={{ margin: 40 }}>Заявка не найдена</div>;

  // После получения zayavka:
  const isFinalized = zayavka.status === 'Готово' || zayavka.status === 'Отказ' || zayavka.status === 'НеЗаказ';
  const isModern = zayavka.status === 'Модерн';

  // Функция для отображения описания заявки
  const renderZayavkaInfo = () => (
    <div>
      <Title level={4}>Заявка №{zayavka.id}</Title>
      <div style={{ marginBottom: 12 }}><b>Клиент:</b> {zayavka.client_name}</div>
      <div style={{ marginBottom: 12 }}><b>Телефон:</b> {zayavka.phone_client}</div>
      <div style={{ marginBottom: 12 }}><b>Адрес:</b> {zayavka.address}</div>
      <div style={{ marginBottom: 12 }}><b>Дата встречи:</b> {zayavka.meeting_date ? new Date(zayavka.meeting_date).toLocaleString() : '—'}</div>
      <div style={{ marginBottom: 12 }}><b>Тип заявки:</b> {zayavka.tip_zayavki_name || '—'}</div>
      <div style={{ marginBottom: 12 }}><b>Проблема:</b> {zayavka.problema}</div>
      <div style={{ marginBottom: 12 }}><b>Статус:</b> <Tag color={zayavka.status === 'Готово' ? 'green' : 'blue'}>{zayavka.status}</Tag></div>
      {zayavka.status === 'Готово' && (
        <div style={{ marginTop: 24, marginBottom: 8, padding: 16, background: '#f6ffed', borderRadius: 8, border: '1px solid #b7eb8f' }}>
          <div><b>Итог:</b> {zayavka.itog !== null ? `${zayavka.itog} ₽` : '—'}</div>
          <div><b>Расход:</b> {zayavka.rashod !== null ? `${zayavka.rashod} ₽` : '—'}</div>
          <div><b>Чистыми:</b> {zayavka.chistymi !== null ? `${zayavka.chistymi} ₽` : '—'}</div>
          <div><b>Сдача мастера (50%):</b> {zayavka.sdacha_mastera !== null ? `${zayavka.sdacha_mastera} ₽` : '—'}</div>
        </div>
      )}
    </div>
  );

  // Функция для отображения кнопок в зависимости от статуса
  const renderActionButtons = () => {
    if (isFinalized) return null;
    if (isModern) {
      return (
        <Space>
          <Button type="primary" htmlType="submit" loading={saving} style={{background:'#52c41a', borderColor:'#52c41a'}}>Готово</Button>
          <Button danger loading={saving} onClick={() => setModal({ visible: true, type: 'otkaz', values: {} })}>Отказ</Button>
        </Space>
      );
    }
    return (
      <Space>
        <Button type="primary" htmlType="submit" loading={saving} style={{background:'#52c41a', borderColor:'#52c41a'}}>Готово</Button>
        <Button loading={saving} style={{background:'#faad14', borderColor:'#faad14', color:'#fff'}} onClick={() => setModal({ visible: true, type: 'modern', values: {} })}>Модерн</Button>
        <Button danger loading={saving} onClick={() => setModal({ visible: true, type: 'otkaz', values: {} })}>Отказ</Button>
        <Button danger loading={saving} onClick={() => setModal({ visible: true, type: 'nezakaz', values: {} })}>НеЗаказ</Button>
      </Space>
    );
  };

  return (
    <div style={{ maxWidth: 700, margin: '40px auto' }}>
      <Card bordered>
        <Tabs defaultActiveKey="1" size="large">
          <Tabs.TabPane tab="Заявка" key="1">
            {renderZayavkaInfo()}
            {!isFinalized && (
              <Form form={form} onFinish={handleSave} layout="vertical" style={{ marginTop: 24 }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                  <Form.Item name="itog" label="Итог" rules={[{ required: true, message: 'Введите итог' }]}>
                    <InputNumber placeholder="Итог" style={{ width: '100%' }} />
                  </Form.Item>
                  <Form.Item name="rashod" label="Расход" rules={[{ required: true, message: 'Введите расход' }]}>
                    <InputNumber placeholder="Расход" style={{ width: '100%' }} />
                  </Form.Item>
                </div>
                <div style={{ marginTop: 16, padding: 16, background: '#f0f0f0', borderRadius: 8 }}>
                  <div><b>Чистыми:</b> {calculatedValues.chistymi !== null ? `${calculatedValues.chistymi} ₽` : '—'}</div>
                  <div><b>Сдача мастера (50%):</b> {calculatedValues.sdacha_mastera !== null ? `${calculatedValues.sdacha_mastera} ₽` : '—'}</div>
                </div>
                <Form.Item style={{ marginTop: 24 }}>
                  {renderActionButtons()}
                </Form.Item>
              </Form>
            )}
          </Tabs.TabPane>
          <Tabs.TabPane tab="Вложения" key="2">
            <ZayavkaFiles zayavkaId={id ? parseInt(id) : 0} canEdit={true} />
          </Tabs.TabPane>
        </Tabs>
      </Card>

      {/* Модальные окна для статусов */}
      <Modal
        title={modal.type === 'modern' ? 'Модерн' : modal.type === 'otkaz' ? 'Отказ' : 'НеЗаказ'}
        open={modal.visible}
        onCancel={() => setModal({ visible: false, type: '', values: {} })}
        footer={null}
      >
        {modal.type === 'modern' && (
          <Form onFinish={(values) => handleStatusWithComment('Модерн', values)}>
            <Form.Item name="predoplata" label="Предоплата" rules={[{ required: true, message: 'Введите предоплату' }]}>
              <Input placeholder="Предоплата" />
            </Form.Item>
            <Form.Item name="sroki" label="Сроки" rules={[{ required: true, message: 'Введите сроки' }]}>
              <Input placeholder="Сроки" />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={modalLoading} block>
                Подтвердить
              </Button>
            </Form.Item>
          </Form>
        )}
        {(modal.type === 'otkaz' || modal.type === 'nezakaz') && (
          <Form onFinish={(values) => handleStatusWithComment(modal.type === 'otkaz' ? 'Отказ' : 'НеЗаказ', values)}>
            <Form.Item name="comment" label="Комментарий" rules={[{ required: true, message: 'Введите комментарий' }]}>
              <Input.TextArea rows={4} placeholder="Комментарий" />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={modalLoading} block>
                Подтвердить
              </Button>
            </Form.Item>
          </Form>
        )}
      </Modal>
    </div>
  );
};

export default ZayavkaMasterDetailPage; 