import React, { useEffect, useState } from 'react';
import axios from 'axios';
import useAuth from '../hooks/useAuth';

const PRINYATYE_STATUSES = [
  'Ожидает',
  'Ожидает Принятия',
  'Принял',
  'В пути',
  'В работе',
  'Готово',
  'Отказ',
  'Модерн',
  'НеЗаказ',
];

interface Zayavka {
  id: number;
  status: string;
  kc_name?: string;
  rk_name?: string;
}

interface User {
  id: number;
  name: string;
  [key: string]: any;
}

const KCStatsPage: React.FC = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [zayavki, setZayavki] = useState<Zayavka[]>([]);
  const { user } = useAuth() as { user: User | null };

  useEffect(() => {
    setLoading(true);
    axios.get('/api/zayavki/')
      .then(res => {
        const data: Zayavka[] = Array.isArray(res.data) ? res.data : (res.data.results || []);
        setZayavki(data);
      })
      .finally(() => setLoading(false));
  }, []);

  const callsCount = zayavki.length;
  const prinyatyeCount = zayavki.filter(z => PRINYATYE_STATUSES.includes(z.status)).length;
  const myAvitoCount = user ? zayavki.filter(z => PRINYATYE_STATUSES.includes(z.status) && z.kc_name === user.name && z.rk_name === 'Авито').length : 0;
  const myListCount = user ? zayavki.filter(z => PRINYATYE_STATUSES.includes(z.status) && z.kc_name === user.name && z.rk_name === 'Лист').length : 0;

  return (
    <div style={{ minHeight: '80vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ background: '#fff', padding: 32, borderRadius: 16, boxShadow: '0 4px 24px 0 rgba(24,144,255,0.08)', minWidth: 400 }}>
        <div style={{ fontSize: 22, color: '#1890ff', fontWeight: 700, marginBottom: 24 }}>Статистика КЦ</div>
        {loading ? (
          <div style={{ textAlign: 'center', color: '#888' }}>Загрузка...</div>
        ) : (
          <div style={{ display: 'flex', gap: 32, justifyContent: 'center' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 16, color: '#888' }}>Кол-во звонков</div>
              <div style={{ fontSize: 32, fontWeight: 700, color: '#1890ff' }}>{callsCount}</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 16, color: '#888' }}>Кол-во принятых</div>
              <div style={{ fontSize: 32, fontWeight: 700, color: '#52c41a' }}>{prinyatyeCount}</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 16, color: '#888' }}>Ваши заявки (РК Авито)</div>
              <div style={{ fontSize: 32, fontWeight: 700, color: '#faad14' }}>{myAvitoCount}</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 16, color: '#888' }}>Ваши заявки (РК Лист)</div>
              <div style={{ fontSize: 32, fontWeight: 700, color: '#faad14' }}>{myListCount}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default KCStatsPage; 