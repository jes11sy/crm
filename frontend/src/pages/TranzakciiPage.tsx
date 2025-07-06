import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { PageWithTable, MoneyDisplay, DateDisplay } from '../components/CommonComponents';
import useAuth from '../hooks/useAuth';
import { User, Tranzakciya } from '../types/entities';

const TranzakciiPage: React.FC = () => {
  const { user } = useAuth();
  const [tranzakcii, setTranzakcii] = useState<Tranzakciya[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchTranzakcii = async () => {
    setLoading(true);
    try {
      const res = await axios.get('/api/tranzakcii/', { withCredentials: true });
      setTranzakcii(Array.isArray(res.data) ? res.data : (res.data.results || []));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTranzakcii();
  }, []);

  const typedUser = user as User | null;
  let filteredTranzakcii = tranzakcii;
  if (typedUser && typedUser.role === 'director') {
    filteredTranzakcii = tranzakcii.filter(t => t.gorod === typedUser.gorod_id);
  }

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: 'Город',
      dataIndex: 'gorod_name',
      key: 'gorod_name',
      render: (text: string, record: Tranzakciya) => text || record.gorod,
    },
    {
      title: 'Тип транзакции',
      dataIndex: 'tip_tranzakcii_name',
      key: 'tip_tranzakcii_name',
      render: (text: string, record: Tranzakciya) => text || record.tip_tranzakcii,
    },
    {
      title: 'Сумма',
      dataIndex: 'summa',
      key: 'summa',
      render: (summa: number) => <MoneyDisplay amount={summa} />,
    },
    {
      title: 'Дата',
      dataIndex: 'date',
      key: 'date',
      render: (date: string) => <DateDisplay date={date} />,
    },
    {
      title: 'Примечание',
      dataIndex: 'note',
      key: 'note',
      ellipsis: true,
    },
  ];

  return (
    <PageWithTable
      title="Транзакции"
      data={filteredTranzakcii}
      columns={columns}
      loading={loading}
      onRefresh={fetchTranzakcii}
      showAddButton={false}
    />
  );
};

export default TranzakciiPage; 