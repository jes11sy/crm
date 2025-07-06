import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Table, Card, Select } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import dayjs, { Dayjs } from 'dayjs';
import isoWeek from 'dayjs/plugin/isoWeek';
import isBetween from 'dayjs/plugin/isBetween';
dayjs.extend(isoWeek);
dayjs.extend(isBetween);

const AVITO_STATUSES = [
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

const PERIODS = [
  { value: 'all', label: 'Все время' },
  { value: 'month', label: 'Месяц' },
  { value: 'week', label: 'Неделя' },
  { value: 'day', label: 'День' },
];

type PeriodKey = 'all' | 'month' | 'week' | 'day';

interface Zayavka {
  id: number;
  gorod_name?: string;
  client_name?: string;
  phone_client?: string;
  status: string;
  chistymi?: number;
  meeting_date?: string;
  rk_name?: string;
}

interface StatsRow {
  gorod: string;
  count: number;
  oborot: number;
}

const AvitoReportPage: React.FC = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [zayavki, setZayavki] = useState<Zayavka[]>([]);
  const [period, setPeriod] = useState<PeriodKey>('all');

  useEffect(() => {
    setLoading(true);
    axios.get('/api/zayavki/')
      .then(res => {
        const data: Zayavka[] = Array.isArray(res.data) ? res.data : (res.data.results || []);
        setZayavki(data);
      })
      .finally(() => setLoading(false));
  }, []);

  // Фильтрация по периоду
  const now = dayjs();
  let dateFilter: (z: Zayavka) => boolean = () => true;
  if (period === 'month') {
    const start = now.startOf('month');
    const end = now.endOf('month');
    dateFilter = z => z.meeting_date ? dayjs(z.meeting_date).isBetween(start, end, null, '[]') : false;
  } else if (period === 'week') {
    const start = now.startOf('isoWeek');
    const end = now.endOf('isoWeek');
    dateFilter = z => z.meeting_date ? dayjs(z.meeting_date).isBetween(start, end, null, '[]') : false;
  } else if (period === 'day') {
    const start = now.startOf('day');
    const end = now.endOf('day');
    dateFilter = z => z.meeting_date ? dayjs(z.meeting_date).isBetween(start, end, null, '[]') : false;
  }

  // Фильтруем заявки по РК Авито, статусу и периоду
  const avitoZayavki = zayavki.filter(z => z.rk_name === 'Авито' && AVITO_STATUSES.includes(z.status) && dateFilter(z));

  // Группируем по городу
  const statsByGorod: Record<string, { count: number; oborot: number }> = {};
  avitoZayavki.forEach(z => {
    const gorod = z.gorod_name || 'Без города';
    if (!statsByGorod[gorod]) {
      statsByGorod[gorod] = { count: 0, oborot: 0 };
    }
    statsByGorod[gorod].count += 1;
    statsByGorod[gorod].oborot += Number(z.chistymi) || 0;
  });
  const statsRows: StatsRow[] = Object.entries(statsByGorod).map(([gorod, data]) => ({
    gorod,
    count: data.count,
    oborot: data.oborot,
  }));

  const columns: ColumnsType<StatsRow> = [
    { title: 'Город', dataIndex: 'gorod', key: 'gorod' },
    { title: 'Кол-во заказов', dataIndex: 'count', key: 'count' },
    { title: 'Оборот (чистыми)', dataIndex: 'oborot', key: 'oborot', render: (v: number) => v.toLocaleString() + ' ₽' },
  ];

  const tableColumns: ColumnsType<Zayavka> = [
    { title: 'ID', dataIndex: 'id', key: 'id' },
    { title: 'Город', dataIndex: 'gorod_name', key: 'gorod_name' },
    { title: 'Клиент', dataIndex: 'client_name', key: 'client_name' },
    { title: 'Телефон', dataIndex: 'phone_client', key: 'phone_client' },
    { title: 'Статус', dataIndex: 'status', key: 'status' },
    { title: 'Сумма (чистыми)', dataIndex: 'chistymi', key: 'chistymi', render: (v?: number) => v ? v + ' ₽' : '' },
    { title: 'Дата', dataIndex: 'meeting_date', key: 'meeting_date', render: (v?: string) => v ? v.slice(0, 10) : '' },
  ];

  return (
    <div style={{ minHeight: '80vh', padding: 24 }}>
      <Card style={{ maxWidth: 700, margin: '0 auto 32px auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
          <div style={{ fontSize: 22, color: '#1890ff', fontWeight: 700 }}>Отчет Авито</div>
          <Select
            value={period}
            onChange={setPeriod}
            options={PERIODS}
            style={{ width: 180 }}
          />
        </div>
        <Table
          columns={columns}
          dataSource={statsRows}
          pagination={false}
          rowKey="gorod"
          size="middle"
        />
      </Card>
      <Card style={{ maxWidth: 1200, margin: '0 auto' }}>
        <div style={{ fontSize: 18, color: '#1890ff', fontWeight: 600, marginBottom: 16 }}>Заявки по РК Авито</div>
        <Table
          columns={tableColumns}
          dataSource={avitoZayavki}
          loading={loading}
          rowKey="id"
          size="small"
        />
      </Card>
    </div>
  );
};

export default AvitoReportPage; 