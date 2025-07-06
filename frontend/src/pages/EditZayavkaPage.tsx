import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Form, Input, Select, Button, Card, Row, Col, Spin, message, Typography, Alert, DatePicker } from 'antd';
import { PhoneOutlined, UserOutlined, DollarOutlined, EditOutlined } from '@ant-design/icons';
import dayjs, { Dayjs } from 'dayjs';
import ZayavkaFiles from '../components/ZayavkaFiles';

const { Title } = Typography;

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
  itog?: number;
  rashod?: number;
  chistymi?: number;
  sdacha_mastera?: number;
  status?: string;
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
  itog?: number;
  rashod?: number;
}

const statusOptions = [
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

const EditZayavkaPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [form] = Form.useForm<FormValues>();
  const [zayavka, setZayavka] = useState<Zayavka | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [masters, setMasters] = useState<Master[]>([]);
  const [allMasters, setAllMasters] = useState<Master[]>([]);
  const [goroda, setGoroda] = useState<Gorod[]>([]);
  const [rkList, setRkList] = useState<RK[]>([]);
  const [tipy, setTipy] = useState<TipZayavki[]>([]);
  const [chistymi, setChistymi] = useState<number | null>(null);
  const [sdachaMastera, setSdachaMastera] = useState<number | null>(null);

  useEffect(() => {
    if (!id) return;
    
    setLoading(true);
    axios.get(`/api/zayavki/${id}/`)
      .then((res) => {
        const data = res.data as Zayavka;
        setZayavka(data);
        const formData: FormValues = { ...data };
        if (data.meeting_date) {
          const d = dayjs(data.meeting_date);
          formData.meeting_date = d.isValid() ? d : undefined;
        } else {
          formData.meeting_date = undefined;
        }
        form.setFieldsValue(formData);
        setLoading(false);
      })
      .catch(() => {
        message.error('Заявка не найдена');
        setLoading(false);
      });
      
    axios.get('/api/master/').then((res) => {
      const data = Array.isArray(res.data) ? res.data : (res.data.results || []);
      setAllMasters(data);
    });
    
    axios.get('/api/gorod/').then((res) => {
      const data = Array.isArray(res.data) ? res.data : (res.data.results || []);
      setGoroda(data);
    });
    
    axios.get('/api/rk/').then((res) => {
      const data = Array.isArray(res.data) ? res.data : (res.data.results || []);
      setRkList(data);
    });
    
    axios.get('/api/tipzayavki/').then((res) => {
      const data = Array.isArray(res.data) ? res.data : (res.data.results || []);
      setTipy(data);
    });
  }, [id, form]);

  useEffect(() => {
    if (zayavka && allMasters.length) {
      const gorodId = form.getFieldValue('gorod') || zayavka.gorod || zayavka.gorod_id;
      setMasters(allMasters.filter(m => m.gorod === gorodId || (m.gorod && typeof m.gorod === 'object' && m.gorod.id === gorodId)));
    }
    if (zayavka) {
      const itog = parseFloat(String(zayavka.itog || 0));
      const rashod = parseFloat(String(zayavka.rashod || 0));
      if (!isNaN(itog) && !isNaN(rashod)) {
        const ch = itog - rashod;
        setChistymi(ch);
        setSdachaMastera(ch * 0.5);
      }
    }
  }, [zayavka, allMasters, form]);

  const handleValuesChange = (changed: Partial<FormValues>, all: FormValues): void => {
    if (changed.gorod) {
      setMasters(allMasters.filter(m => m.gorod === changed.gorod || (m.gorod && typeof m.gorod === 'object' && m.gorod.id === changed.gorod)));
      form.setFieldsValue({ master: undefined });
    }
    const itog = parseFloat(String(all.itog || 0));
    const rashod = parseFloat(String(all.rashod || 0));
    if (all.master && !isNaN(itog) && !isNaN(rashod)) {
      const ch = itog - rashod;
      setChistymi(ch);
      setSdachaMastera(ch * 0.5);
    } else {
      setChistymi(null);
      setSdachaMastera(null);
    }
  };

  const handleSave = (values: FormValues): void => {
    const sendValues = { ...values };
    if (sendValues.meeting_date && typeof sendValues.meeting_date !== 'string') {
      sendValues.meeting_date = sendValues.meeting_date.format('YYYY-MM-DDTHH:mm:ss');
    }
    const itog = parseFloat(String(sendValues.itog || 0));
    const rashod = parseFloat(String(sendValues.rashod || 0));
    let ch: number | null = null;
    let sdacha: number | null = null;
    if (sendValues.master && !isNaN(itog) && !isNaN(rashod)) {
      ch = itog - rashod;
      sdacha = ch * 0.5;
    }
    setSaving(true);
    axios.put(`/api/zayavki/${id}/`, {
      ...sendValues,
      chistymi: ch,
      sdacha_mastera: sdacha,
    })
      .then(() => {
        setSaving(false);
        message.success('Сохранено!');
        navigate('/zayavki');
      })
      .catch(() => {
        message.error('Ошибка при сохранении');
        setSaving(false);
      });
  };

  if (loading || !zayavka) {
    return (
      <div style={{display:'flex',justifyContent:'center',alignItems:'center',height:'80vh'}}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #e0e7ff 0%, #f8fafc 100%)' }}>
      <Card
        style={{
          minWidth: 400,
          maxWidth: 700,
          width: '100%',
          borderRadius: 16,
          boxShadow: '0 8px 32px 0 rgba(24,144,255,0.10)',
          padding: 32,
        }}
        bodyStyle={{ padding: 0 }}
      >
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: 24, gap: 12 }}>
          <EditOutlined style={{ fontSize: 28, color: '#1890ff' }} />
          <Title level={3} style={{ margin: 0, color: '#1890ff', fontWeight: 800 }}>
            Редактирование заявки #{id}
          </Title>
        </div>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSave}
          onValuesChange={handleValuesChange}
          style={{ width: '100%' }}
        >
          <Row gutter={24}>
            <Col xs={24} sm={12}>
              <Form.Item name="gorod" label="Город" rules={[{required:true,message:'Выберите город'}]}>
                <Select placeholder="Выберите город" allowClear showSearch optionFilterProp="children">
                  {goroda.map(g => <Select.Option key={g.id} value={g.id}>{g.name}</Select.Option>)}
                </Select>
              </Form.Item>
              <Form.Item name="tip_zayavki" label="Тип заявки" rules={[{required:true,message:'Выберите тип'}]}>
                <Select placeholder="Выберите тип заявки" allowClear showSearch optionFilterProp="children">
                  {tipy.map(t => <Select.Option key={t.id} value={t.id}>{t.name}</Select.Option>)}
                </Select>
              </Form.Item>
              <Form.Item name="phone_client" label="Телефон" rules={[{required:true,message:'Введите телефон'}]}>
                <Input prefix={<PhoneOutlined />} placeholder="Телефон клиента" />
              </Form.Item>
              <Form.Item name="client_name" label="Клиент" rules={[{required:true,message:'Введите имя клиента'}]}>
                <Input prefix={<UserOutlined />} placeholder="Имя клиента" />
              </Form.Item>
              <Form.Item name="address" label="Адрес" rules={[{required:true,message:'Введите адрес'}]}>
                <Input placeholder="Адрес" />
              </Form.Item>
              <Form.Item name="meeting_date" label="Дата встречи" rules={[{required:true,message:'Выберите дату встречи'}]}>
                <DatePicker showTime format="YYYY-MM-DD HH:mm" style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item name="rk" label="РК" rules={[{required:true,message:'Выберите РК'}]}>
                <Select placeholder="Выберите РК" allowClear showSearch optionFilterProp="children">
                  {rkList.map(rk => <Select.Option key={rk.id} value={rk.id}>{rk.rk_name}</Select.Option>)}
                </Select>
              </Form.Item>
              <Form.Item name="master" label="Мастер" rules={[{required:true,message:'Выберите мастера'}]}>
                <Select placeholder="Выберите мастера" allowClear showSearch optionFilterProp="children">
                  {masters.map(m => <Select.Option key={m.id} value={m.id}>{m.name}</Select.Option>)}
                </Select>
              </Form.Item>
              <Form.Item name="itog" label="Итог">
                <Input prefix={<DollarOutlined />} placeholder="Итоговая сумма" type="number" />
              </Form.Item>
              <Form.Item name="rashod" label="Расход">
                <Input prefix={<DollarOutlined />} placeholder="Расходы" type="number" />
              </Form.Item>
              {chistymi !== null && (
                <Alert
                  message={`Чистыми: ${chistymi} ₽`}
                  type="info"
                  showIcon
                  style={{ marginBottom: 16 }}
                />
              )}
              {sdachaMastera !== null && (
                <Alert
                  message={`Сдача мастеру: ${sdachaMastera} ₽`}
                  type="success"
                  showIcon
                  style={{ marginBottom: 16 }}
                />
              )}
            </Col>
          </Row>
          <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end', marginTop: 24 }}>
            <Button onClick={() => navigate('/zayavki')}>
              Отмена
            </Button>
            <Button type="primary" htmlType="submit" loading={saving}>
              Сохранить
            </Button>
          </div>
        </Form>
      </Card>
      {zayavka && (
        <ZayavkaFiles zayavkaId={zayavka.id} canEdit={true} canEditAudio={true} />
      )}
    </div>
  );
};

export default EditZayavkaPage; 