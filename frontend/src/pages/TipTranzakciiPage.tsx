import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Form } from 'antd';
import { PageWithTable, FormModal, FormField, formUtils } from '../components/CommonComponents';
import { TipTranzakcii } from '../types/entities';

const TipTranzakciiPage: React.FC = () => {
  const [types, setTypes] = useState<TipTranzakcii[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  const fetchTypes = async () => {
    setLoading(true);
    try {
      const res = await axios.get('/api/tiptranzakcii/', { withCredentials: true });
      setTypes(Array.isArray(res.data) ? res.data : (res.data.results || []));
    } catch (err) {
      console.error(err);
      formUtils.handleApiError(err, 'Ошибка при загрузке типов транзакций');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTypes();
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
      await axios.post('/api/tiptranzakcii/', values, { withCredentials: true });
      formUtils.showSuccess('Тип транзакции успешно добавлен');
      handleCloseModal();
      fetchTypes();
    } catch (err) {
      formUtils.handleApiError(err, 'Ошибка при добавлении типа транзакции');
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
      title: 'Название типа',
      dataIndex: 'name',
      key: 'name',
    },
  ];

  return (
    <>
      <PageWithTable
        title="Типы транзакций"
        data={types}
        columns={columns}
        loading={loading}
        onRefresh={fetchTypes}
        onAdd={handleOpenModal}
        addButtonText="Добавить тип"
      />

      <FormModal
        title="Добавить тип транзакции"
        visible={modalVisible}
        onOk={handleSubmit}
        onCancel={handleCloseModal}
        form={form}
        okText="Добавить"
        confirmLoading={loading}
      >
        <FormField.Input
          name="name"
          label="Название типа"
          placeholder="Введите название типа транзакции"
          rules={[
            formUtils.createRules.required('Пожалуйста, введите название типа'),
            formUtils.createRules.min(2, 'Название должно содержать минимум 2 символа'),
            formUtils.createRules.max(100, 'Название не должно превышать 100 символов'),
          ]}
        />
      </FormModal>
    </>
  );
};

export default TipTranzakciiPage; 