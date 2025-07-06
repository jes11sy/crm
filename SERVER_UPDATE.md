# 🚀 Обновление CRM на сервере Ubuntu

## ⚡ Быстрое обновление (рекомендуется)

```bash
# 1. Перейти в папку проекта
cd /путь/к/crm

# 2. Сделать скрипт исполняемым
chmod +x update.sh

# 3. Запустить автоматическое обновление
./update.sh
```

## 🔧 Ручное обновление

```bash
# 1. Остановить сервисы
docker-compose down

# 2. Обновить код с GitHub
git pull origin main

# 3. Пересобрать и запустить
docker-compose up -d --build

# 4. Проверить статус
docker-compose ps
```

## 📋 Что делает скрипт update.sh

✅ Проверяет наличие Docker и Git  
✅ Останавливает все сервисы  
✅ Обновляет код с GitHub  
✅ Пересобирает контейнеры  
✅ Применяет миграции  
✅ Проверяет статус сервисов  
✅ Очищает неиспользуемые ресурсы  

## 🆘 Если что-то пошло не так

```bash
# Проверить логи
docker-compose logs -f

# Проверить статус контейнеров
docker-compose ps

# Перезапустить конкретный сервис
docker-compose restart api-gateway

# Полная пересборка
docker-compose down
docker-compose up -d --build --force-recreate
```

## 📞 Поддержка

- **GitHub**: https://github.com/jes11sy/crm
- **Домен**: https://crm.lead-schem.ru
- **Документация**: UPDATE_GUIDE.md 