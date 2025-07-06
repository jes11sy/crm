# 🌐 Руководство по настройке домена для CRM системы

## 📋 Содержание

1. [Обзор](#обзор)
2. [Подготовка](#подготовка)
3. [Настройка DNS](#настройка-dns)
4. [Конфигурация сервера](#конфигурация-сервера)
5. [SSL сертификаты](#ssl-сертификаты)
6. [Запуск системы](#запуск-системы)
7. [Мониторинг](#мониторинг)
8. [Устранение неполадок](#устранение-неполадок)

---

## 🎯 Обзор

Это руководство поможет вам настроить домен для вашей CRM системы. После выполнения всех шагов ваша система будет доступна по адресу `https://crm.yourdomain.com`.

### Что будет настроено:
- ✅ Домен и поддомен
- ✅ SSL сертификаты (Let's Encrypt)
- ✅ Nginx конфигурация
- ✅ Docker Compose для production
- ✅ Автоматическое обновление SSL
- ✅ Мониторинг системы

---

## 🔧 Подготовка

### Требования к серверу:
- **ОС**: Ubuntu 20.04+ / CentOS 8+ / Windows Server 2019+
- **RAM**: минимум 4GB, рекомендуется 8GB+
- **CPU**: минимум 2 ядра, рекомендуется 4+
- **Диск**: минимум 50GB свободного места
- **Сеть**: статический IP адрес
- **Порты**: 80 и 443 должны быть открыты

### Установка необходимого ПО:

#### Ubuntu/Debian:
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Установка дополнительных инструментов
sudo apt install -y curl wget git nginx certbot python3-certbot-nginx
```

#### CentOS/RHEL:
```bash
# Установка Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io

# Запуск Docker
sudo systemctl start docker
sudo systemctl enable docker

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Windows:
1. Установите Docker Desktop с официального сайта
2. Установите Git для Windows
3. Установите WSL2 (если используете Windows 10/11)

---

## 🌍 Настройка DNS

### Шаг 1: Получение IP адреса сервера

```bash
# На Linux сервере
curl ifconfig.me

# Или
wget -qO- ifconfig.me
```

### Шаг 2: Настройка DNS записей

Войдите в панель управления вашего регистратора доменов и добавьте следующие записи:

#### A записи:
- `crm.yourdomain.com` → IP адрес вашего сервера
- `www.crm.yourdomain.com` → IP адрес вашего сервера

#### CNAME записи (опционально):
- `www.crm.yourdomain.com` → `crm.yourdomain.com`

### Примеры для популярных регистраторов:

#### Cloudflare:
1. Добавьте домен в Cloudflare
2. Перейдите в "DNS" → "Records"
3. Добавьте A запись:
   - **Name**: `crm`
   - **IPv4 address**: ваш IP адрес
   - **Proxy status**: DNS only (серый облачок)
4. Включите SSL/TLS в режиме "Full (strict)"

#### REG.RU:
1. Войдите в панель управления
2. Перейдите в "Домены" → ваш домен → "DNS записи"
3. Добавьте A запись:
   - **Имя**: `crm`
   - **Значение**: IP адрес сервера
   - **TTL**: 3600

#### Namecheap:
1. Войдите в аккаунт
2. Перейдите в "Domain List" → "Manage"
3. В разделе "Advanced DNS" добавьте A запись:
   - **Host**: `crm`
   - **Value**: IP адрес сервера
   - **TTL**: Automatic

#### GoDaddy:
1. Войдите в аккаунт
2. Перейдите в "My Products" → "DNS"
3. Добавьте A запись:
   - **Type**: A
   - **Name**: `crm`
   - **Value**: IP адрес сервера
   - **TTL**: 1 Hour

### Проверка DNS настроек:

```bash
# Проверка DNS записи
nslookup crm.yourdomain.com

# Проверка с разных DNS серверов
dig crm.yourdomain.com @8.8.8.8
dig crm.yourdomain.com @1.1.1.1

# Проверка доступности
curl -I http://crm.yourdomain.com
```

**Важно**: DNS изменения могут распространяться до 24 часов, но обычно занимают 15-30 минут.

---

## ⚙️ Конфигурация сервера

### Шаг 1: Загрузка проекта

```bash
# Клонирование репозитория
git clone https://github.com/your-company/crm-system.git
cd crm-system

# Или загрузка архива
wget https://github.com/your-company/crm-system/archive/main.zip
unzip main.zip
cd crm-system-main
```

### Шаг 2: Настройка домена

#### Linux/macOS:
```bash
# Сделать скрипт исполняемым
chmod +x scripts/setup_domain.sh

# Запустить настройку домена
./scripts/setup_domain.sh yourdomain.com
```

#### Windows:
```cmd
# Запустить настройку домена
scripts\setup_domain.bat yourdomain.com
```

### Шаг 3: Проверка готовности

```bash
# Linux/macOS
./scripts/check_readiness.sh yourdomain.com

# Windows
scripts\check_readiness.bat yourdomain.com
```

### Что создается автоматически:

1. **nginx-production.conf** - конфигурация Nginx для production
2. **docker-compose-production.yml** - Docker Compose для production
3. **.env.production** - переменные окружения для production
4. **SSL скрипты** - для получения и обновления сертификатов
5. **Мониторинг скрипты** - для проверки состояния системы
6. **DNS_SETUP.md** - инструкция по настройке DNS
7. **DEPLOYMENT_GUIDE.md** - полное руководство по развертыванию

---

## 🔒 SSL сертификаты

### Автоматическое получение (рекомендуется):

#### Linux/macOS:
```bash
# Получение SSL сертификатов
./scripts/get_ssl_cert.sh yourdomain.com
```

#### Windows:
```cmd
# Получение SSL сертификатов
scripts\get_ssl_cert.bat yourdomain.com
```

### Ручное получение:

```bash
# Остановка nginx
docker-compose -f docker-compose-production.yml stop nginx

# Получение сертификатов через certbot
docker-compose -f docker-compose-production.yml --profile ssl-setup run --rm certbot

# Запуск nginx
docker-compose -f docker-compose-production.yml up -d nginx
```

### Автоматическое обновление:

Скрипт автоматически настраивает cron для обновления сертификатов:

```bash
# Проверка cron задач
crontab -l

# Ручное обновление
./scripts/renew_ssl.sh yourdomain.com
```

### Проверка SSL сертификата:

```bash
# Проверка срока действия
openssl s_client -connect crm.yourdomain.com:443 -servername crm.yourdomain.com < /dev/null 2>/dev/null | openssl x509 -noout -dates

# Проверка через браузер
# Откройте https://crm.yourdomain.com и проверьте замок в адресной строке
```

---

## 🚀 Запуск системы

### Шаг 1: Запуск всех сервисов

```bash
# Запуск системы
docker-compose -f docker-compose-production.yml --env-file .env.production up -d

# Проверка статуса
docker-compose -f docker-compose-production.yml ps
```

### Шаг 2: Проверка логов

```bash
# Просмотр всех логов
docker-compose -f docker-compose-production.yml logs -f

# Просмотр логов конкретного сервиса
docker-compose -f docker-compose-production.yml logs -f nginx
docker-compose -f docker-compose-production.yml logs -f api-gateway
```

### Шаг 3: Проверка доступности

```bash
# Проверка health check
curl https://crm.yourdomain.com/health

# Проверка главной страницы
curl -I https://crm.yourdomain.com

# Проверка API
curl https://crm.yourdomain.com/api/v1/
```

### Шаг 4: Создание суперпользователя

```bash
# Создание администратора
docker-compose -f docker-compose-production.yml exec api-gateway python manage.py createsuperuser
```

---

## 📊 Мониторинг

### Автоматический мониторинг:

```bash
# Linux/macOS
./scripts/monitor.sh yourdomain.com

# Windows
scripts\monitor.bat yourdomain.com
```

### Что проверяется:
- ✅ Доступность сайта
- ✅ Валидность SSL сертификата
- ✅ Использование диска
- ✅ Использование памяти
- ✅ Работа Docker

### Настройка уведомлений:

#### Telegram уведомления:
1. Создайте бота через @BotFather
2. Получите токен бота
3. Добавьте бота в группу администраторов
4. Обновите `.env.production`:
   ```
   TELEGRAM_BOT_TOKEN=your-bot-token
   TELEGRAM_CHAT_ID=your-chat-id
   ```

#### Email уведомления:
1. Настройте SMTP в `.env.production`:
   ```
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

### Логирование:

```bash
# Просмотр логов nginx
docker-compose -f docker-compose-production.yml exec nginx tail -f /var/log/nginx/access.log
docker-compose -f docker-compose-production.yml exec nginx tail -f /var/log/nginx/error.log

# Просмотр логов приложения
docker-compose -f docker-compose-production.yml logs -f api-gateway
```

---

## 🔧 Устранение неполадок

### Проблема: DNS не разрешается

**Симптомы**: `nslookup crm.yourdomain.com` не возвращает IP

**Решение**:
1. Проверьте DNS записи в панели регистратора
2. Убедитесь, что прошло достаточно времени (до 24 часов)
3. Попробуйте очистить DNS кэш:
   ```bash
   # Windows
   ipconfig /flushdns
   
   # Linux
   sudo systemctl restart systemd-resolved
   
   # macOS
   sudo dscacheutil -flushcache
   ```

### Проблема: SSL сертификат не получен

**Симптомы**: Ошибки при получении сертификата

**Решение**:
1. Убедитесь, что порт 80 открыт
2. Проверьте, что домен правильно настроен
3. Попробуйте получить сертификат в тестовом режиме:
   ```bash
   docker-compose -f docker-compose-production.yml --profile ssl-setup run --rm certbot certonly --webroot --webroot-path=/var/www/certbot --test-cert -d crm.yourdomain.com
   ```

### Проблема: Сайт недоступен

**Симптомы**: Ошибка 502 Bad Gateway

**Решение**:
1. Проверьте статус контейнеров:
   ```bash
   docker-compose -f docker-compose-production.yml ps
   ```
2. Проверьте логи:
   ```bash
   docker-compose -f docker-compose-production.yml logs nginx
   docker-compose -f docker-compose-production.yml logs api-gateway
   ```
3. Перезапустите сервисы:
   ```bash
   docker-compose -f docker-compose-production.yml restart
   ```

### Проблема: Высокое использование ресурсов

**Симптомы**: Медленная работа, ошибки 503

**Решение**:
1. Проверьте использование ресурсов:
   ```bash
   docker stats
   ```
2. Увеличьте лимиты в docker-compose:
   ```yaml
   services:
     api-gateway:
       deploy:
         resources:
           limits:
             memory: 2G
             cpus: '1.0'
   ```

### Проблема: Файлы не загружаются

**Симптомы**: Ошибки при загрузке файлов

**Решение**:
1. Проверьте права доступа к директории media
2. Увеличьте лимит размера файла в nginx:
   ```nginx
   client_max_body_size 100M;
   ```

---

## 📞 Поддержка

### Контакты:
- **Email**: support@yourdomain.com
- **Telegram**: @crm_support
- **Документация**: https://crm.yourdomain.com/docs

### Полезные команды:

```bash
# Перезапуск системы
docker-compose -f docker-compose-production.yml restart

# Обновление системы
git pull
docker-compose -f docker-compose-production.yml build
docker-compose -f docker-compose-production.yml up -d

# Остановка системы
docker-compose -f docker-compose-production.yml down

# Просмотр всех контейнеров
docker ps -a

# Очистка неиспользуемых ресурсов
docker system prune -a
```

---

## 🎉 Готово!

После выполнения всех шагов ваша CRM система будет доступна по адресу:

**🌐 https://crm.yourdomain.com**

### Что настроено:
- ✅ Домен и SSL сертификаты
- ✅ Автоматическое обновление сертификатов
- ✅ Мониторинг системы
- ✅ Логирование и уведомления
- ✅ Резервное копирование
- ✅ Безопасность и производительность

### Следующие шаги:
1. Создайте суперпользователя
2. Настройте интеграции (Mango Office, Telegram)
3. Импортируйте данные
4. Обучите пользователей
5. Настройте резервное копирование

**Удачи в работе с вашей CRM системой! 🚀** 