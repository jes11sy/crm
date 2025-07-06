# Руководство по развертыванию CRM системы на домене crm.lead-schem.ru

## Шаги для развертывания:

### 1. Подготовка сервера
- Убедитесь, что у вас есть VPS/сервер с Ubuntu 20.04+
- Установите Docker и Docker Compose
- Откройте порты 80 и 443

### 2. Настройка DNS
Следуйте инструкции в файле `DNS_SETUP.md`

### 3. Загрузка проекта
```bash
git clone <your-repo-url>
cd crm-system
```

### 4. Настройка домена
```bash
scripts\setup_domain.bat lead-schem.ru
```

### 5. Проверка готовности
```bash
scripts\check_readiness.bat lead-schem.ru
```

### 6. Запуск системы
```bash
docker-compose -f docker-compose-production.yml --env-file .env.production up -d
```

### 7. Получение SSL сертификатов
```bash
scripts\get_ssl_cert.bat lead-schem.ru
```

### 8. Проверка работы
Откройте в браузере: https://crm.lead-schem.ru

## Полезные команды:

### Просмотр логов:
```bash
docker-compose -f docker-compose-production.yml logs -f
```

### Остановка системы:
```bash
docker-compose -f docker-compose-production.yml down
```

### Обновление системы:
```bash
git pull
docker-compose -f docker-compose-production.yml build
docker-compose -f docker-compose-production.yml up -d
```

### Мониторинг:
```bash
scripts\monitor.bat lead-schem.ru
```

## Контакты поддержки:
- Email: support@lead-schem.ru
- Документация: https://crm.lead-schem.ru/docs
