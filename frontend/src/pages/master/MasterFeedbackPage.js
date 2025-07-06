import React, { useState } from 'react';
import { Typography, Input, Button, message, Card } from 'antd';
import axios from 'axios';

export default function MasterFeedbackPage() {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!text.trim()) {
      message.warning('Введите текст сообщения');
      return;
    }
    setLoading(true);
    try {
      await axios.post('/api/master-feedback/', { text });
      message.success('Сообщение отправлено!');
      setText('');
    } catch (e) {
      message.error('Ошибка при отправке');
    }
    setLoading(false);
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'flex-start', minHeight: '60vh', paddingTop: 40 }}>
      <Card style={{ width: 420, maxWidth: '95vw', borderRadius: 18, boxShadow: '0 4px 24px 0 rgba(24,144,255,0.08)' }}>
        <Typography.Title level={3} style={{ fontWeight: 800, marginBottom: 24, textAlign: 'center' }}>Обратная связь</Typography.Title>
        <form onSubmit={handleSubmit}>
          <Input.TextArea
            value={text}
            onChange={e => setText(e.target.value)}
            rows={6}
            placeholder="Опишите ваш вопрос, проблему или пожелание..."
            style={{ fontSize: 16, marginBottom: 20, borderRadius: 10 }}
            maxLength={1000}
            showCount
          />
          <Button type="primary" htmlType="submit" block size="large" loading={loading} style={{ fontWeight: 700, borderRadius: 10 }}>
            Отправить
          </Button>
        </form>
      </Card>
    </div>
  );
} 