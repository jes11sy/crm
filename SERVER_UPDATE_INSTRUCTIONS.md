# 🔄 Инструкция по обновлению на сервере

## Проблема
Git конфликт с локальными изменениями в nginx.conf

## Решение

### 1. Сохранить текущие изменения (если нужно)
```bash
git stash
```

### 2. Получить обновления
```bash
git pull origin main
```

### 3. Если нужно восстановить изменения
```bash
git stash pop
```

### 4. Альтернативный способ (принудительное обновление)
```bash
# Если локальные изменения не нужны:
git reset --hard HEAD
git pull origin main
```

### 5. Запустить frontend
```bash
chmod +x restart_with_frontend.sh
./restart_with_frontend.sh
```

## Быстрое решение (если локальные изменения не важны):

```bash
# На сервере выполните эти команды по порядку:
git reset --hard HEAD
git pull origin main
chmod +x restart_with_frontend.sh
./restart_with_frontend.sh
```

## Проверка после обновления:
```bash
docker-compose ps
curl http://crm.lead-schem.ru/
```

## Если что-то пошло не так:
```bash
docker-compose logs frontend
docker-compose logs nginx
``` 