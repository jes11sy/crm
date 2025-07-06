#!/bin/bash

# Скрипт настройки домена для CRM системы
# Использование: ./setup_domain.sh yourdomain.com

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Проверка аргументов
if [ $# -eq 0 ]; then
    error "Необходимо указать домен!"
    echo "Использование: $0 yourdomain.com"
    exit 1
fi

DOMAIN=$1
SUBDOMAIN="crm"
FULL_DOMAIN="${SUBDOMAIN}.${DOMAIN}"

log "Начинаем настройку домена: $FULL_DOMAIN"

# Проверка наличия необходимых файлов
if [ ! -f "docker-compose-production.yml" ]; then
    error "Файл docker-compose-production.yml не найден!"
    exit 1
fi

if [ ! -f "nginx-production.conf" ]; then
    error "Файл nginx-production.conf не найден!"
    exit 1
fi

# Создание директорий
log "Создание необходимых директорий..."
mkdir -p ssl_certs
mkdir -p certbot_webroot
mkdir -p logs

# Обновление конфигурационных файлов
log "Обновление конфигурационных файлов..."

# Обновление nginx конфигурации
sed -i "s/crm\.yourdomain\.com/$FULL_DOMAIN/g" nginx-production.conf
sed -i "s/www\.crm\.yourdomain\.com/www.$FULL_DOMAIN/g" nginx-production.conf

# Обновление docker-compose
sed -i "s/crm\.yourdomain\.com/$FULL_DOMAIN/g" docker-compose-production.yml
sed -i "s/www\.crm\.yourdomain\.com/www.$FULL_DOMAIN/g" docker-compose-production.yml

# Создание .env файла для production
log "Создание .env файла для production..."
cat > .env.production << EOF
# Database settings
DB_NAME=crm_production
DB_USER=crm_user
DB_PASSWORD=$(openssl rand -base64 32)

# Django settings
SECRET_KEY=$(openssl rand -base64 64)
DEBUG=False

# Domain settings
DOMAIN=$FULL_DOMAIN
ALLOWED_HOSTS=$FULL_DOMAIN,www.$FULL_DOMAIN

# SSL settings
SSL_EMAIL=admin@$DOMAIN

# Redis settings
REDIS_URL=redis://redis:6379/0

# Email settings (настройте под ваши нужды)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Mango Office settings (если используется)
MANGO_OFFICE_API_KEY=your-mango-api-key
MANGO_OFFICE_API_URL=https://app.mango-office.ru/vpbx/

# Telegram settings (если используется)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id
EOF

log ".env.production файл создан"

# Создание скрипта для получения SSL сертификатов
log "Создание скрипта для SSL сертификатов..."
cat > scripts/get_ssl_cert.sh << 'EOF'
#!/bin/bash

DOMAIN=$1
SUBDOMAIN="crm"
FULL_DOMAIN="${SUBDOMAIN}.${DOMAIN}"

echo "Получение SSL сертификатов для $FULL_DOMAIN..."

# Остановка nginx для освобождения порта 80
docker-compose -f docker-compose-production.yml stop nginx

# Получение сертификатов
docker-compose -f docker-compose-production.yml --profile ssl-setup run --rm certbot

# Запуск nginx
docker-compose -f docker-compose-production.yml up -d nginx

echo "SSL сертификаты получены!"
EOF

chmod +x scripts/get_ssl_cert.sh

# Создание скрипта для обновления SSL сертификатов
log "Создание скрипта для обновления SSL сертификатов..."
cat > scripts/renew_ssl.sh << 'EOF'
#!/bin/bash

DOMAIN=$1
SUBDOMAIN="crm"
FULL_DOMAIN="${SUBDOMAIN}.${DOMAIN}"

echo "Обновление SSL сертификатов для $FULL_DOMAIN..."

# Обновление сертификатов
docker-compose -f docker-compose-production.yml run --rm certbot renew

# Перезагрузка nginx
docker-compose -f docker-compose-production.yml restart nginx

echo "SSL сертификаты обновлены!"
EOF

chmod +x scripts/renew_ssl.sh

# Создание crontab для автоматического обновления SSL
log "Настройка автоматического обновления SSL сертификатов..."
(crontab -l 2>/dev/null; echo "0 12 * * * cd $(pwd) && ./scripts/renew_ssl.sh $DOMAIN") | crontab -

# Создание скрипта для мониторинга
log "Создание скрипта мониторинга..."
cat > scripts/monitor.sh << 'EOF'
#!/bin/bash

DOMAIN=$1
SUBDOMAIN="crm"
FULL_DOMAIN="${SUBDOMAIN}.${DOMAIN}"

echo "Мониторинг системы CRM..."

# Проверка доступности сайта
if curl -f -s "https://$FULL_DOMAIN/health" > /dev/null; then
    echo "✅ Сайт доступен"
else
    echo "❌ Сайт недоступен"
    # Здесь можно добавить отправку уведомления
fi

# Проверка SSL сертификата
if openssl s_client -connect $FULL_DOMAIN:443 -servername $FULL_DOMAIN < /dev/null 2>/dev/null | openssl x509 -noout -dates | grep -q "notAfter"; then
    echo "✅ SSL сертификат действителен"
else
    echo "❌ Проблемы с SSL сертификатом"
fi

# Проверка использования диска
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "⚠️  Высокое использование диска: ${DISK_USAGE}%"
else
    echo "✅ Использование диска в норме: ${DISK_USAGE}%"
fi

# Проверка памяти
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.2f", $3/$2 * 100.0)}')
if (( $(echo "$MEMORY_USAGE > 80" | bc -l) )); then
    echo "⚠️  Высокое использование памяти: ${MEMORY_USAGE}%"
else
    echo "✅ Использование памяти в норме: ${MEMORY_USAGE}%"
fi
EOF

chmod +x scripts/monitor.sh

# Создание инструкции по настройке DNS
log "Создание инструкции по настройке DNS..."
cat > DNS_SETUP.md << EOF
# Настройка DNS для домена $FULL_DOMAIN

## Необходимые DNS записи:

### A записи:
- \`$SUBDOMAIN.$DOMAIN\` → IP адрес вашего сервера
- \`www.$SUBDOMAIN.$DOMAIN\` → IP адрес вашего сервера

### CNAME записи (опционально):
- \`www.$SUBDOMAIN.$DOMAIN\` → \`$SUBDOMAIN.$DOMAIN\`

## Пример для популярных регистраторов:

### Cloudflare:
1. Добавьте домен в Cloudflare
2. Создайте A запись: \`$SUBDOMAIN\` → IP сервера
3. Включите SSL/TLS в режиме "Full (strict)"

### REG.RU:
1. Войдите в панель управления
2. Перейдите в "DNS записи"
3. Добавьте A запись: \`$SUBDOMAIN\` → IP сервера

### Namecheap:
1. Войдите в аккаунт
2. Перейдите в "Domain List" → "Manage"
3. В разделе "Advanced DNS" добавьте A запись: \`$SUBDOMAIN\` → IP сервера

## Проверка настройки:
\`\`\`bash
# Проверка DNS записи
nslookup $FULL_DOMAIN

# Проверка доступности
curl -I http://$FULL_DOMAIN
\`\`\`

## Важные замечания:
- DNS изменения могут распространяться до 24 часов
- Убедитесь, что порты 80 и 443 открыты на сервере
- Проверьте настройки файрвола
EOF

# Создание скрипта для проверки готовности
log "Создание скрипта проверки готовности..."
cat > scripts/check_readiness.sh << 'EOF'
#!/bin/bash

DOMAIN=$1
SUBDOMAIN="crm"
FULL_DOMAIN="${SUBDOMAIN}.${DOMAIN}"

echo "Проверка готовности системы..."

# Проверка DNS
echo "Проверка DNS записи..."
if nslookup $FULL_DOMAIN > /dev/null 2>&1; then
    echo "✅ DNS запись настроена"
else
    echo "❌ DNS запись не найдена"
    echo "Настройте A запись: $SUBDOMAIN → IP вашего сервера"
fi

# Проверка портов
echo "Проверка портов..."
if nc -z localhost 80; then
    echo "✅ Порт 80 открыт"
else
    echo "❌ Порт 80 закрыт"
fi

if nc -z localhost 443; then
    echo "✅ Порт 443 открыт"
else
    echo "❌ Порт 443 закрыт"
fi

# Проверка Docker
echo "Проверка Docker..."
if docker info > /dev/null 2>&1; then
    echo "✅ Docker работает"
else
    echo "❌ Docker не запущен"
fi

# Проверка файлов
echo "Проверка конфигурационных файлов..."
if [ -f "docker-compose-production.yml" ]; then
    echo "✅ docker-compose-production.yml найден"
else
    echo "❌ docker-compose-production.yml не найден"
fi

if [ -f "nginx-production.conf" ]; then
    echo "✅ nginx-production.conf найден"
else
    echo "❌ nginx-production.conf не найден"
fi

if [ -f ".env.production" ]; then
    echo "✅ .env.production найден"
else
    echo "❌ .env.production не найден"
fi

echo ""
echo "Для запуска системы выполните:"
echo "docker-compose -f docker-compose-production.yml --env-file .env.production up -d"
echo ""
echo "Для получения SSL сертификатов выполните:"
echo "./scripts/get_ssl_cert.sh $DOMAIN"
EOF

chmod +x scripts/check_readiness.sh

# Создание финальной инструкции
log "Создание финальной инструкции..."
cat > DEPLOYMENT_GUIDE.md << EOF
# Руководство по развертыванию CRM системы на домене $FULL_DOMAIN

## Шаги для развертывания:

### 1. Подготовка сервера
- Убедитесь, что у вас есть VPS/сервер с Ubuntu 20.04+
- Установите Docker и Docker Compose
- Откройте порты 80 и 443

### 2. Настройка DNS
Следуйте инструкции в файле \`DNS_SETUP.md\`

### 3. Загрузка проекта
\`\`\`bash
git clone <your-repo-url>
cd crm-system
\`\`\`

### 4. Настройка домена
\`\`\`bash
./scripts/setup_domain.sh $DOMAIN
\`\`\`

### 5. Проверка готовности
\`\`\`bash
./scripts/check_readiness.sh $DOMAIN
\`\`\`

### 6. Запуск системы
\`\`\`bash
docker-compose -f docker-compose-production.yml --env-file .env.production up -d
\`\`\`

### 7. Получение SSL сертификатов
\`\`\`bash
./scripts/get_ssl_cert.sh $DOMAIN
\`\`\`

### 8. Проверка работы
Откройте в браузере: https://$FULL_DOMAIN

## Полезные команды:

### Просмотр логов:
\`\`\`bash
docker-compose -f docker-compose-production.yml logs -f
\`\`\`

### Остановка системы:
\`\`\`bash
docker-compose -f docker-compose-production.yml down
\`\`\`

### Обновление системы:
\`\`\`bash
git pull
docker-compose -f docker-compose-production.yml build
docker-compose -f docker-compose-production.yml up -d
\`\`\`

### Мониторинг:
\`\`\`bash
./scripts/monitor.sh $DOMAIN
\`\`\`

## Контакты поддержки:
- Email: support@$DOMAIN
- Документация: https://$FULL_DOMAIN/docs
EOF

log "Настройка домена завершена!"
echo ""
info "Следующие шаги:"
echo "1. Настройте DNS записи (см. DNS_SETUP.md)"
echo "2. Проверьте готовность: ./scripts/check_readiness.sh $DOMAIN"
echo "3. Запустите систему: docker-compose -f docker-compose-production.yml --env-file .env.production up -d"
echo "4. Получите SSL сертификаты: ./scripts/get_ssl_cert.sh $DOMAIN"
echo ""
info "Документация создана в файле DEPLOYMENT_GUIDE.md" 