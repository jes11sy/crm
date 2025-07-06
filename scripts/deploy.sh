#!/bin/bash

# Скрипт автоматического развертывания CRM системы
# Использование: ./deploy.sh [staging|production]

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функции для логирования
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка аргументов
if [ $# -eq 0 ]; then
    log_error "Укажите окружение: staging или production"
    echo "Использование: $0 [staging|production]"
    exit 1
fi

ENVIRONMENT=$1

# Проверка окружения
if [ "$ENVIRONMENT" != "staging" ] && [ "$ENVIRONMENT" != "production" ]; then
    log_error "Неверное окружение. Используйте staging или production"
    exit 1
fi

log_info "Начинаем развертывание в окружении: $ENVIRONMENT"

# Функция проверки зависимостей
check_dependencies() {
    log_info "Проверяем зависимости..."
    
    # Проверка Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker не установлен"
        exit 1
    fi
    
    # Проверка Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose не установлен"
        exit 1
    fi
    
    # Проверка git
    if ! command -v git &> /dev/null; then
        log_error "Git не установлен"
        exit 1
    fi
    
    log_info "Все зависимости установлены"
}

# Функция создания резервной копии
create_backup() {
    log_info "Создаем резервную копию базы данных..."
    
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Резервная копия PostgreSQL
    docker-compose exec -T postgres pg_dump -U crm_user crm > "$BACKUP_DIR/database.sql"
    
    # Резервная копия файлов
    tar -czf "$BACKUP_DIR/files.tar.gz" media/ logs/
    
    log_info "Резервная копия создана: $BACKUP_DIR"
}

# Функция обновления кода
update_code() {
    log_info "Обновляем код из репозитория..."
    
    # Получаем последние изменения
    git fetch origin
    git reset --hard origin/main
    
    # Обновляем зависимости
    log_info "Обновляем зависимости..."
    pip install -r requirements.txt
    
    cd frontend
    npm install
    cd ..
}

# Функция сборки образов
build_images() {
    log_info "Собираем Docker образы..."
    
    # Сборка бэкенда
    docker build -f Dockerfile.backend -t crm-backend:latest .
    
    # Сборка фронтенда
    docker build -f frontend/Dockerfile -t crm-frontend:latest ./frontend
    
    log_info "Образы собраны успешно"
}

# Функция применения миграций
run_migrations() {
    log_info "Применяем миграции базы данных..."
    
    docker-compose exec -T django python manage.py migrate
    
    log_info "Миграции применены"
}

# Функция сбора статических файлов
collect_static() {
    log_info "Собираем статические файлы..."
    
    docker-compose exec -T django python manage.py collectstatic --noinput
    
    log_info "Статические файлы собраны"
}

# Функция проверки здоровья
health_check() {
    log_info "Проверяем здоровье системы..."
    
    # Проверка API
    for i in {1..30}; do
        if curl -f http://localhost:8000/api/health/ > /dev/null 2>&1; then
            log_info "API работает корректно"
            break
        fi
        
        if [ $i -eq 30 ]; then
            log_error "API не отвечает после 30 попыток"
            exit 1
        fi
        
        log_warn "API не отвечает, попытка $i/30"
        sleep 2
    done
    
    # Проверка фронтенда
    for i in {1..30}; do
        if curl -f http://localhost:3000 > /dev/null 2>&1; then
            log_info "Фронтенд работает корректно"
            break
        fi
        
        if [ $i -eq 30 ]; then
            log_error "Фронтенд не отвечает после 30 попыток"
            exit 1
        fi
        
        log_warn "Фронтенд не отвечает, попытка $i/30"
        sleep 2
    done
}

# Функция отправки уведомлений
send_notifications() {
    log_info "Отправляем уведомления..."
    
    # Здесь можно добавить отправку уведомлений в Slack, Telegram и т.д.
    echo "Развертывание в $ENVIRONMENT завершено успешно" > /tmp/deployment_status.txt
    
    log_info "Уведомления отправлены"
}

# Функция отката
rollback() {
    log_error "Произошла ошибка, выполняем откат..."
    
    # Останавливаем новые контейнеры
    docker-compose down
    
    # Восстанавливаем предыдущую версию
    git reset --hard HEAD~1
    
    # Запускаем предыдущую версию
    docker-compose up -d
    
    log_warn "Откат выполнен"
    exit 1
}

# Основная логика развертывания
main() {
    # Устанавливаем обработчик ошибок
    trap rollback ERR
    
    check_dependencies
    create_backup
    update_code
    build_images
    
    # Останавливаем текущие контейнеры
    log_info "Останавливаем текущие контейнеры..."
    docker-compose down
    
    # Запускаем новые контейнеры
    log_info "Запускаем новые контейнеры..."
    docker-compose up -d
    
    # Ждем запуска контейнеров
    sleep 10
    
    run_migrations
    collect_static
    health_check
    send_notifications
    
    log_info "Развертывание завершено успешно!"
}

# Запуск основной функции
main 