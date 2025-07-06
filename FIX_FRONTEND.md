# 🔧 Исправление Frontend CRM

## Проблема
Frontend не отображается, показывается только API Gateway страница.

## Решение

### 1. Перезапуск с frontend
```bash
# На сервере выполните:
chmod +x restart_with_frontend.sh
./restart_with_frontend.sh
```

### 2. Проверка статуса
```bash
docker-compose ps
```

### 3. Проверка логов frontend
```bash
docker-compose logs frontend
```

### 4. Проверка логов nginx
```bash
docker-compose logs nginx
```

## Что было исправлено:

1. **nginx.conf** - добавлен upstream для frontend и правильное проксирование
2. **docker-compose.yml** - добавлен frontend сервис
3. **frontend/Dockerfile** - изменен для development сервера
4. **restart_with_frontend.sh** - скрипт для перезапуска

## После исправления:
- Frontend: http://crm.lead-schem.ru/
- API: http://crm.lead-schem.ru/api/
- Swagger: http://crm.lead-schem.ru/swagger/

## Если проблемы остаются:
1. Проверьте, что порт 3000 не занят
2. Убедитесь, что все файлы frontend присутствуют
3. Проверьте логи на ошибки 