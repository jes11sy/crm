import React, { useEffect, useState } from 'react';
import axios from 'axios';
import useAuth from '../hooks/useAuth';
import { Card, Statistic, Row, Col, Spin, Button, Space } from 'antd';
import { CheckCircleTwoTone, DollarTwoTone, FundTwoTone, TrophyTwoTone } from '@ant-design/icons';
import dayjs, { Dayjs } from 'dayjs';
import isBetween from 'dayjs/plugin/isBetween';
dayjs.extend(isBetween);

const PERIODS = [
  { key: 'month', label: 'Месяц' },
  { key: 'week', label: 'Неделя' },
  { key: 'day', label: 'День' },
];

type PeriodKey = 'month' | 'week' | 'day';

interface Zayavka {
  id: number;
  master: number;
  status: string;
  meeting_date?: string;
  chistymi?: number;
  sdacha_mastera?: number;
}

interface Stats {
  closedCount: number;
  avgCheck: number;
  oborot: number;
  zarplata: number;
}

function getPeriodRange(period: PeriodKey): [Dayjs, Dayjs] {
  const now = dayjs();
  if (period === 'month') {
    return [now.startOf('month'), now.endOf('month')];
  }
  if (period === 'week') {
    return [now.startOf('week'), now.endOf('week')];
  }
  if (period === 'day') {
    return [now.startOf('day'), now.endOf('day')];
  }
  return [now, now];
}

const StatistikaMasterPage: React.FC = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState<boolean>(true);
  const [stats, setStats] = useState<Stats>({
    closedCount: 0,
    avgCheck: 0,
    oborot: 0,
    zarplata: 0,
  });
  const [period, setPeriod] = useState<PeriodKey>('month');

  useEffect(() => {
    if (!user) return;
    setLoading(true);
    axios.get('/api/zayavki/')
      .then(res => {
        const all: Zayavka[] = Array.isArray(res.data) ? res.data : (res.data.results || []);
        const [start, end] = getPeriodRange(period);
        const my = all.filter(z =>
          z.master === user.id &&
          (z.status === 'Готово' || z.status === 'Отказ') &&
          z.meeting_date &&
          dayjs(z.meeting_date).isBetween(start, end, null, '[]')
        );
        const closedCount = my.length;
        const oborot = my.reduce((sum, z) => sum + (Number(z.chistymi) || 0), 0);
        const zarplata = my.reduce((sum, z) => sum + (Number(z.sdacha_mastera) || 0), 0);
        const avgCheck = closedCount > 0 ? oborot / closedCount : 0;
        setStats({ closedCount, avgCheck, oborot, zarplata });
      })
      .finally(() => setLoading(false));
  }, [user, period]);

  if (loading) return <Spin style={{ margin: 40 }} size="large" />;

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
      <h2 style={{
        fontSize: 38,
        fontWeight: 900,
        margin: '0 0 32px 0',
        textAlign: 'left',
        letterSpacing: '-1px',
      }}>Статистика мастера</h2>
      <div style={{ display: 'flex', gap: 24, marginBottom: 32 }}>
        {PERIODS.map(p => (
          <Button
            key={p.key}
            type={period === p.key ? 'primary' : 'default'}
            size="large"
            style={{
              borderRadius: 22,
              minWidth: 120,
              fontWeight: 700,
              fontSize: 20,
              transition: 'all 0.2s',
              boxShadow: period === p.key ? '0 2px 12px #bae7ff' : undefined,
              marginRight: 8,
            }}
            onClick={() => setPeriod(p.key as PeriodKey)}
          >
            {p.label}
          </Button>
        ))}
      </div>
      <div style={{
        display: 'flex',
        gap: 32,
        flexWrap: 'wrap',
        justifyContent: 'flex-start',
        alignItems: 'stretch',
      }}>
        <Card bordered={false} style={{
          minWidth: 260,
          flex: '1 1 300px',
          borderRadius: 20,
          textAlign: 'center',
          background: 'rgba(246,255,237,0.95)',
          boxShadow: '0 4px 24px 0 rgba(24,144,255,0.08)',
          padding: '32px 24px',
          display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center',
        }}>
          <CheckCircleTwoTone twoToneColor="#52c41a" style={{ fontSize: 48, marginBottom: 12 }} />
          <Statistic title={<span style={{ fontSize: 20, color: '#222' }}>Закрытых заявок</span>} value={stats.closedCount} valueStyle={{ fontSize: 36, fontWeight: 900, color: '#222' }} />
        </Card>
        <Card bordered={false} style={{
          minWidth: 260,
          flex: '1 1 300px',
          borderRadius: 20,
          textAlign: 'center',
          background: 'rgba(255,251,230,0.95)',
          boxShadow: '0 4px 24px 0 rgba(24,144,255,0.08)',
          padding: '32px 24px',
          display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center',
        }}>
          <TrophyTwoTone twoToneColor="#faad14" style={{ fontSize: 48, marginBottom: 12 }} />
          <Statistic title={<span style={{ fontSize: 20, color: '#222' }}>Средний чек</span>} value={stats.avgCheck} precision={2} suffix="₽" valueStyle={{ fontSize: 36, fontWeight: 900, color: '#faad14' }} />
        </Card>
        <Card bordered={false} style={{
          minWidth: 260,
          flex: '1 1 300px',
          borderRadius: 20,
          textAlign: 'center',
          background: 'rgba(230,247,255,0.95)',
          boxShadow: '0 4px 24px 0 rgba(24,144,255,0.08)',
          padding: '32px 24px',
          display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center',
        }}>
          <FundTwoTone twoToneColor="#1890ff" style={{ fontSize: 48, marginBottom: 12 }} />
          <Statistic title={<span style={{ fontSize: 20, color: '#222' }}>Оборот</span>} value={stats.oborot} precision={2} suffix="₽" valueStyle={{ fontSize: 36, fontWeight: 900, color: '#1890ff' }} />
        </Card>
        <Card bordered={false} style={{
          minWidth: 260,
          flex: '1 1 300px',
          borderRadius: 20,
          textAlign: 'center',
          background: 'rgba(255,240,246,0.95)',
          boxShadow: '0 4px 24px 0 rgba(24,144,255,0.08)',
          padding: '32px 24px',
          display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center',
        }}>
          <DollarTwoTone twoToneColor="#eb2f96" style={{ fontSize: 48, marginBottom: 12 }} />
          <Statistic title={<span style={{ fontSize: 20, color: '#222' }}>Зарплата</span>} value={stats.zarplata} precision={2} suffix="₽" valueStyle={{ fontSize: 36, fontWeight: 900, color: '#eb2f96' }} />
        </Card>
      </div>
    </div>
  );
};

export default StatistikaMasterPage; 