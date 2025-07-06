import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Card, Typography, Table, Select } from 'antd';
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

const CLOSED_STATUSES = ['Готово', 'Отказ'];

interface Zayavka {
  id: number;
  status: string;
  meeting_date?: string;
  gorod_name?: string;
  master_name?: string;
  chistymi?: number | string;
  sdacha_mastera?: number | string;
}

interface StatsRow {
  gorod: string;
  master: string;
  count: number;
  avg: number;
  oborot: number;
  zarplata: number;
}

export default function MasterReportPage(): React.JSX.Element {
  const [loading, setLoading] = useState<boolean>(true);
  const [zayavki, setZayavki] = useState<Zayavka[]>([]);
  const [period, setPeriod] = useState<'all' | 'month' | 'week' | 'day'>('all');

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

  // Группировка по мастеру
  const statsByMaster: Record<string, {
    gorod: string;
    master: string;
    count: number;
    sum: number;
    sdacha: number;
  }> = {};
  closedZayavki.forEach(z => {
    const key = (z.gorod_name || 'Без города') + '|' + (z.master_name || 'Без мастера');
    if (!statsByMaster[key]) {
      statsByMaster[key] = {
        gorod: z.gorod_name || 'Без города',
        master: z.master_name || 'Без мастера',
        count: 0,
        sum: 0,
        sdacha: 0,
      };
    }
    statsByMaster[key].count += 1;
    statsByMaster[key].sum += Number(z.chistymi) || 0;
    statsByMaster[key].sdacha += Number(z.sdacha_mastera) || 0;
  });

  const statsRows: StatsRow[] = Object.values(statsByMaster).map(data => ({
    gorod: data.gorod,
    master: data.master,
    count: data.count,
    avg: data.count ? Math.round(data.sum / data.count) : 0,
    oborot: data.sum,
    zarplata: data.sum - data.sdacha,
  }));

  const columns = [
    { title: 'Город', dataIndex: 'gorod', key: 'gorod' },
    { title: 'ФИО мастера', dataIndex: 'master', key: 'master' },
    { title: 'Кол-во закрытых заявок', dataIndex: 'count', key: 'count' },
    { title: 'Средний чек', dataIndex: 'avg', key: 'avg', render: (v: number) => v ? v + ' ₽' : '' },
    { title: 'Оборот', dataIndex: 'oborot', key: 'oborot', render: (v: number) => v ? v + ' ₽' : '' },
    { title: 'Зарплата', dataIndex: 'zarplata', key: 'zarplata', render: (v: number) => v ? v + ' ₽' : '' },
  ];

  return (
    <Card style={{ maxWidth: 1000, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0 }}>Отчет по мастерам</Title>
        <Select
          value={period}
          onChange={setPeriod}
          options={PERIODS}
          style={{ width: 180 }}
        />
      </div>
      <Table columns={columns} dataSource={statsRows} loading={loading} rowKey={row => row.gorod + '|' + row.master} pagination={false} />
    </Card>
  );
} 