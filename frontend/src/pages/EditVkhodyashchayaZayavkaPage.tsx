import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Form, Input, Select, Button, Card, Row, Col, Spin, message, Typography, DatePicker, Tabs } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import dayjs, { Dayjs } from 'dayjs';
import useAuth from '../hooks/useAuth';
import { User } from '../types/entities';
import ZayavkaFiles from '../components/ZayavkaFiles';

const { Title } = Typography;

interface Zayavka {
  id: number;
  gorod: number;
  tip_zayavki: number;
  phone_client: string;
  client_name: string;
  address: string;
  meeting_date?: string;
  rk: number;
  status?: string;
  tip_techniki?: string;
  problema?: string;
  phone_atc?: string;
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

interface FormValues {
  gorod: number;
  tip_zayavki: number;
  phone_client: string;
  client_name: string;
  address: string;
  meeting_date?: Dayjs | string;
  rk: number;
  status: string;
  tip_techniki: string;
  problema: string;
  phone_atc?: string;
  kc_name?: string;
  comment_kc?: string;
}

const INCOMING_STATUSES = [
  'Звонит',
  'ТНО',
  'Перезвонить',
  'Отказ',
  'Ожидает',
];

const EditVkhodyashchayaZayavkaPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [form] = Form.useForm<FormValues>();
  const [zayavka, setZayavka] = useState<Zayavka | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [goroda, setGoroda] = useState<Gorod[]>([]);
  const [rkList, setRkList] = useState<RK[]>([]);
  const [tipy, setTipy] = useState<TipZayavki[]>([]);
  const { user } = useAuth();
  const typedUser = user as User | null;

  useEffect(() => {
    setLoading(true);
    axios.get(`/api/zayavki/${id}/`)
      .then(res => {
        setZayavka(res.data);
        const data: FormValues = { ...res.data };
        if (data.meeting_date && typeof data.meeting_date === 'string') {
          const d = dayjs(data.meeting_date);
          data.meeting_date = d.isValid() ? d : undefined;
        } else {
          data.meeting_date = undefined;
        }
        if ((!data.kc_name || data.kc_name === '') && typedUser && typedUser.name) {
          data.kc_name = typedUser.name;
        }
        form.setFieldsValue(data);
        setLoading(false);
      })
      .catch(() => {
        message.error('Заявка не найдена');
        setLoading(false);
      });
    axios.get('/api/gorod/').then(res => {
      const data = Array.isArray(res.data) ? res.data : (res.data.results || []);
      setGoroda(data);
    });
    axios.get('/api/rk/').then(res => {
      const data = Array.isArray(res.data) ? res.data : (res.data.results || []);
      setRkList(data);
    });
    axios.get('/api/tipzayavki/').then(res => {
      const data = Array.isArray(res.data) ? res.data : (res.data.results || []);
      setTipy(data);
    });
  }, [id, typedUser, form]);

  const handleSave = (values: FormValues): void => {
    const sendValues = { ...values };
    if (sendValues.meeting_date && typeof sendValues.meeting_date !== 'string') {
      sendValues.meeting_date = sendValues.meeting_date.format('YYYY-MM-DDTHH:mm:ss');
    }
    setSaving(true);
    axios.put(`/api/zayavki/${id}/`, sendValues)
      .then(() => {
        setSaving(false);
        message.success('Сохранено!');
        navigate('/vkhodyashchie-zayavki');
      })
      .catch(() => {
        message.error('Ошибка при сохранении');
        setSaving(false);
      });
  };

  if (loading || !zayavka) return <div style={{display:'flex',justifyContent:'center',alignItems:'center',height:'80vh'}}><Spin size="large" /></div>;

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
        <Tabs defaultActiveKey="1" size="large" style={{ marginBottom: 0 }}>
          <Tabs.TabPane tab="Заявка" key="1">
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: 24, gap: 12 }}>
              <EditOutlined style={{ fontSize: 28, color: '#1890ff' }} />
              <Title level={3} style={{ margin: 0, color: '#1890ff', fontWeight: 800 }}>
                Редактирование входящей заявки #{id}
              </Title>
            </div>
            <Form
              form={form}
              layout="vertical"
              onFinish={handleSave}
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
                    <Input placeholder="Телефон клиента" />
                  </Form.Item>
                  <Form.Item name="client_name" label="Клиент" rules={[{required:true,message:'Введите имя клиента'}]}>
                    <Input placeholder="Имя клиента" />
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
                  <Form.Item name="status" label="Статус" rules={[{required:true,message:'Выберите статус'}]}>
                    <Select placeholder="Выберите статус">
                      {INCOMING_STATUSES.map(opt => <Select.Option key={opt} value={opt}>{opt}</Select.Option>)}
                    </Select>
                  </Form.Item>
                  <Form.Item name="tip_techniki" label="Тип техники" rules={[{required:true,message:'Введите тип техники'}]}>
                    <Input placeholder="Тип техники" />
                  </Form.Item>
                  <Form.Item name="problema" label="Проблема" rules={[{required:true,message:'Опишите проблему'}]}>
                    <Input placeholder="Проблема" />
                  </Form.Item>
                  <Form.Item name="phone_atc" label="Телефон ATC">
                    <Input placeholder="Телефон ATC" />
                  </Form.Item>
                  <Form.Item name="kc_name" label="Имя КЦ">
                    <Input placeholder="Имя КЦ" />
                  </Form.Item>
                  <Form.Item name="comment_kc" label="Комментарий КЦ">
                    <Input placeholder="Комментарий КЦ" />
                  </Form.Item>
                </Col>
              </Row>
              <Form.Item>
                <Button type="primary" htmlType="submit" block loading={saving}>Сохранить</Button>
              </Form.Item>
            </Form>
          </Tabs.TabPane>
          <Tabs.TabPane tab="Вложения" key="2">
            <ZayavkaFiles zayavkaId={id ? parseInt(id) : 0} canEdit={true} />
          </Tabs.TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default EditVkhodyashchayaZayavkaPage; 