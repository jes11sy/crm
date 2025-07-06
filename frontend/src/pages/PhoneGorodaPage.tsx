import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Form } from 'antd';
import { PageWithTable, FormModal, FormField, formUtils } from '../components/CommonComponents';
import { Gorod, PhoneGoroda, Option } from '../types/entities';

const PhoneGorodaPage: React.FC = () => {
  const [phones, setPhones] = useState<PhoneGoroda[]>([]);
  const [goroda, setGoroda] = useState<Gorod[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  const fetchData = async () => {
    setLoading(true);
    try {
      const [phonesRes, gorodaRes] = await Promise.all([
        axios.get('/api/phonegoroda/', { withCredentials: true }),
        axios.get('/api/gorod/', { withCredentials: true })
      ]);
      setPhones(Array.isArray(phonesRes.data) ? phonesRes.data : (phonesRes.data.results || []));
      setGoroda(Array.isArray(gorodaRes.data) ? gorodaRes.data : (gorodaRes.data.results || []));
    } catch (err) {
      console.error(err);
      formUtils.handleApiError(err, 'Ошибка при загрузке данных');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleOpenModal = () => {
    setModalVisible(true);
    form.resetFields();
  };

  const handleCloseModal = () => {
    setModalVisible(false);
    form.resetFields();
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      await axios.post('/api/phonegoroda/', values, { withCredentials: true });
      formUtils.showSuccess('Телефон города успешно добавлен');
      handleCloseModal();
      fetchData();
    } catch (err) {
      formUtils.handleApiError(err, 'Ошибка при добавлении телефона');
    }
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: 'Город',
      dataIndex: 'gorod',
      key: 'gorod',
      render: (gorod: number | Gorod) => {
        if (typeof gorod === 'object') {
          return gorod.name;
        }
        const gorodObj = goroda.find((g) => g.id === gorod);
        return gorodObj ? gorodObj.name : gorod;
      },
    },
    {
      title: 'Телефон',
      dataIndex: 'phone',
      key: 'phone',
    },
  ];

  const gorodOptions: Option[] = goroda.map((gorod) => ({
    value: gorod.id,
    label: gorod.name,
  }));

  return (
    <>
      <PageWithTable
        title="Телефоны города"
        data={phones}
        columns={columns}
        loading={loading}
        onRefresh={fetchData}
        onAdd={handleOpenModal}
        addButtonText="Добавить телефон"
      />

      <FormModal
        title="Добавить телефон города"
        visible={modalVisible}
        onOk={handleSubmit}
        onCancel={handleCloseModal}
        form={form}
        okText="Добавить"
        confirmLoading={loading}
      >
        <FormField.Select
          name="gorod"
          label="Город"
          placeholder="Выберите город"
          options={gorodOptions}
          rules={[
            formUtils.createRules.required('Пожалуйста, выберите город'),
          ]}
        />
        <FormField.Input
          name="phone"
          label="Телефон"
          placeholder="Введите номер телефона"
          rules={[
            formUtils.createRules.required('Пожалуйста, введите номер телефона'),
            formUtils.createRules.phone(),
          ]}
        />
      </FormModal>
    </>
  );
};

export default PhoneGorodaPage; 