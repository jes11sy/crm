import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Card, Typography, Table, Select } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import dayjs, { Dayjs } from 'dayjs';
import isoWeek from 'dayjs/plugin/isoWeek';
import isBetween from 'dayjs/plugin/isBetween';
dayjs.extend(isoWeek);
dayjs.extend(isBetween);

const { Title } = Typography;

const PERIODS = [
  { value: 'all', label: 'Все время' },
  { value: 'month', label: 'Месяц' },
  { value: 'week', label: 'Неделя' },
  { value: 'day', label: 'День' },
];

type PeriodKey = 'all' | 'month' | 'week' | 'day';

const CLOSED_STATUSES = ['Готово', 'Отказ'];

interface Zayavka {
  id: number;
  status: string;
  gorod_name?: string;
  chistymi?: number;
  meeting_date?: string;
}

interface StatsRow {
  gorod: string;
  count: number;
  avg: number;
  oborot: number;
}

const CityReportPage: React.FC = () => {
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

  // Только закрытые заявки (Готово/Отказ)
  const closedZayavki = zayavki.filter(z => CLOSED_STATUSES.includes(z.status) && dateFilter(z));

  // Группировка по городу
  const statsByGorod: Record<string, { count: number; sum: number; gotovoSum: number; gotovoCount: number }> = {};
  closedZayavki.forEach(z => {
    const gorod = z.gorod_name || 'Без города';
    if (!statsByGorod[gorod]) {
      statsByGorod[gorod] = { count: 0, sum: 0, gotovoSum: 0, gotovoCount: 0 };
    }
    statsByGorod[gorod].count += 1;
    statsByGorod[gorod].sum += Number(z.chistymi) || 0;
    if (z.status === 'Готово') {
      statsByGorod[gorod].gotovoSum += Number(z.chistymi) || 0;
      statsByGorod[gorod].gotovoCount += 1;
    }
  });

  const statsRows: StatsRow[] = Object.entries(statsByGorod).map(([gorod, data]) => ({
    gorod,
    count: data.count,
    avg: data.count ? Math.round(data.sum / data.count) : 0,
    oborot: data.gotovoSum,
  }));

  const columns: ColumnsType<StatsRow> = [
    { title: 'Город', dataIndex: 'gorod', key: 'gorod' },
    { title: 'Кол-во закрытых заказов', dataIndex: 'count', key: 'count' },
    { title: 'Средний чек', dataIndex: 'avg', key: 'avg', render: (v: number) => v ? v + ' ₽' : '' },
    { title: 'Оборот', dataIndex: 'oborot', key: 'oborot', render: (v: number) => v ? v + ' ₽' : '' },
  ];

  return (
    <Card style={{ maxWidth: 800, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0 }}>Отчет по городу</Title>
        <Select
          value={period}
          onChange={setPeriod}
          options={PERIODS}
          style={{ width: 180 }}
        />
      </div>
      <Table columns={columns} dataSource={statsRows} loading={loading} rowKey="gorod" pagination={false} />
    </Card>
  );
};

export default CityReportPage; 