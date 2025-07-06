# 🚨 Исправление проблем на сервере

## Проблемы:
1. **Zayavki Service** - отсутствует модуль `django_filters`
2. **PostgreSQL** - ошибка с пользователем `crm_user`
3. **API Gateway** - дублирование namespace

## Решение:

### 1. Обновите проект с GitHub:
```bash
git pull origin main
```

### 2. Исправьте проблемы:
```bash
# Сделайте скрипт исполняемым
chmod +x fix_issues.sh

# Запустите исправления
./fix_issues.sh
```

### 3. Проверьте результат:
```bash
# Статус сервисов
docker-compose ps

# Логи
docker-compose logs -f
```

### 4. Если проблемы остались:
```bash
# Полная пересборка
chmod +x update.sh
./update.sh
```

## Ожидаемый результат:
- ✅ Все сервисы в статусе "Up"
- ✅ Нет ошибок в логах
- ✅ Доступ по адресу: http://crm.lead-schem.ru

## Проверка работоспособности:
```bash
# Проверка API Gateway
curl http://localhost:8000/api/v1/health/

# Проверка User Service
curl http://localhost:8001/api/v1/users/

# Проверка Zayavki Service
curl http://localhost:8002/api/v1/zayavki/

# Проверка Finance Service
curl http://localhost:8003/api/v1/finance/
``` 