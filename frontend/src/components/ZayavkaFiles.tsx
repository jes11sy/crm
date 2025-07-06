import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Card, Button, Upload, message, Row, Col, Typography } from 'antd';
import { UploadOutlined, DeleteOutlined } from '@ant-design/icons';

interface FileType {
  key: string;
  label: string;
  accept: string;
}

interface ZayavkaFile {
  id: number;
  file: string;
  type: string;
  uploaded_by_name?: string;
  uploaded_at: string;
}

interface ZayavkaFilesProps {
  zayavkaId: number;
  canEdit?: boolean;
  canEditAudio?: boolean;
}

const FILE_TYPES: FileType[] = [
  { key: 'bso', label: 'БСО', accept: '.pdf,.jpg,.jpeg,.png' },
  { key: 'chek', label: 'Чек расхода', accept: '.pdf,.jpg,.jpeg,.png' },
  { key: 'audio', label: 'Аудиозапись', accept: '.mp3,.wav,.ogg' },
];

const API_URL = '/api/zayavka-files/';
const { Title } = Typography;

const ZayavkaFiles: React.FC<ZayavkaFilesProps> = ({ zayavkaId, canEdit = true, canEditAudio = true }) => {
  const [files, setFiles] = useState<ZayavkaFile[]>([]);
  const [uploading, setUploading] = useState<boolean>(false);

  useEffect(() => {
    fetchFiles();
    // eslint-disable-next-line
  }, [zayavkaId]);

  const fetchFiles = async (): Promise<void> => {
    try {
      const res = await axios.get(`${API_URL}?zayavka=${zayavkaId}`, { withCredentials: true });
      setFiles(Array.isArray(res.data) ? res.data : res.data.results || []);
    } catch {
      message.error('Ошибка загрузки файлов');
    }
  };

  const handleUpload = async (type: string, file: File): Promise<boolean> => {
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);
    formData.append('zayavka', zayavkaId.toString());
    try {
      await axios.post(API_URL, formData, {
        withCredentials: true,
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      fetchFiles();
      message.success('Файл загружен');
    } catch {
      message.error('Ошибка загрузки файла');
    } finally {
      setUploading(false);
    }
    return false;
  };

  const handleDelete = async (fileId: number): Promise<void> => {
    if (!window.confirm('Удалить файл?')) return;
    setUploading(true);
    try {
      await axios.delete(`${API_URL}${fileId}/`, { withCredentials: true });
      fetchFiles();
      message.success('Файл удалён');
    } catch {
      message.error('Ошибка удаления файла');
    } finally {
      setUploading(false);
    }
  };

  const filesByType = (type: string): ZayavkaFile[] => files.filter(f => f.type === type);

  return (
    <div style={{ marginTop: 32 }}>
      <Title level={4} style={{ marginBottom: 24 }}>Файлы заявки</Title>
      <Row gutter={24}>
        {FILE_TYPES.slice(0, 2).map(ft => (
          <Col xs={24} sm={12} md={8} key={ft.key}>
            <Card
              title={ft.label}
              bordered={false}
              style={{ minHeight: 220, borderRadius: 12, boxShadow: '0 2px 12px #e6f7ff' }}
              bodyStyle={{ padding: 16 }}
            >
              {canEdit && (
                <Upload
                  beforeUpload={(file: File) => handleUpload(ft.key, file)}
                  showUploadList={false}
                  accept={ft.accept}
                  disabled={uploading}
                >
                  <Button icon={<UploadOutlined />} loading={uploading} style={{ marginBottom: 12 }}>
                    Загрузить
                  </Button>
                </Upload>
              )}
              <div>
                {filesByType(ft.key).length === 0 && (
                  <div style={{ color: '#888', marginTop: 8 }}>Нет файлов</div>
                )}
                {filesByType(ft.key).map(f => (
                  <Card
                    key={f.id}
                    style={{
                      marginBottom: 12,
                      border: '1px solid #f0f0f0',
                      borderRadius: 8,
                      background: '#fafcff',
                    }}
                    bodyStyle={{ padding: 10 }}
                  >
                    <a href={f.file} target="_blank" rel="noopener noreferrer" style={{ fontWeight: 500 }}>
                      {f.file.split('/').pop()}
                    </a>
                    <div style={{ fontSize: 12, color: '#666' }}>
                      Загружено: {f.uploaded_by_name || '—'}<br />
                      {new Date(f.uploaded_at).toLocaleString()}
                    </div>
                    {canEdit && (
                      <Button
                        icon={<DeleteOutlined />}
                        danger
                        size="small"
                        style={{ marginTop: 8 }}
                        onClick={() => handleDelete(f.id)}
                        loading={uploading}
                      >
                        Удалить
                      </Button>
                    )}
                  </Card>
                ))}
              </div>
            </Card>
          </Col>
        ))}
      </Row>
      <Row gutter={24} style={{ marginTop: 24 }}>
        <Col xs={24}>
          <Card
            title="Аудиозапись"
            bordered={false}
            style={{ borderRadius: 12, boxShadow: '0 2px 12px #e6f7ff', maxWidth: 600, margin: '0 auto' }}
            bodyStyle={{ padding: 24 }}
          >
            {canEdit && canEditAudio && (
              <Upload
                beforeUpload={(file: File) => handleUpload('audio', file)}
                showUploadList={false}
                accept=".mp3,.wav,.ogg"
                disabled={uploading}
              >
                <Button icon={<UploadOutlined />} loading={uploading} style={{ marginBottom: 12 }}>
                  Загрузить
                </Button>
              </Upload>
            )}
            <div>
              {filesByType('audio').length === 0 && (
                <div style={{ color: '#888', marginTop: 8 }}>Нет файлов</div>
              )}
              {filesByType('audio').map(f => (
                <Card
                  key={f.id}
                  style={{
                    marginBottom: 12,
                    border: '1px solid #f0f0f0',
                    borderRadius: 8,
                    background: '#fafcff',
                  }}
                  bodyStyle={{ padding: 10 }}
                >
                  <a href={f.file} target="_blank" rel="noopener noreferrer" style={{ fontWeight: 500 }}>
                    {f.file.split('/').pop()}
                  </a>
                  <div style={{ margin: '8px 0' }}>
                    <audio src={f.file} controls style={{ width: '100%' }} />
                  </div>
                  <div style={{ fontSize: 12, color: '#666' }}>
                    Загружено: {f.uploaded_by_name || '—'}<br />
                    {new Date(f.uploaded_at).toLocaleString()}
                  </div>
                  {canEdit && canEditAudio && (
                    <Button
                      icon={<DeleteOutlined />}
                      danger
                      size="small"
                      style={{ marginTop: 8 }}
                      onClick={() => handleDelete(f.id)}
                      loading={uploading}
                    >
                      Удалить
                    </Button>
                  )}
                </Card>
              ))}
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default ZayavkaFiles; 