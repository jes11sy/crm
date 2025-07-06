#!/bin/bash

# 🚀 Скрипт автоматического обновления CRM
# Автор: AI Assistant
# Версия: 1.0

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для вывода
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Проверка наличия Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker не установлен. Установите Docker и попробуйте снова."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose не установлен. Установите Docker Compose и попробуйте снова."
        exit 1
    fi
    
    log_success "Docker и Docker Compose найдены"
}

# Проверка наличия Git
check_git() {
    if ! command -v git &> /dev/null; then
        log_error "Git не установлен. Установите Git и попробуйте снова."
        exit 1
    fi
    
    log_success "Git найден"
}

# Проверка наличия .env файла
check_env() {
    if [ ! -f ".env" ]; then
        log_warning ".env файл не найден. Создаю из примера..."
        if [ -f "env.example" ]; then
            cp env.example .env
            log_warning "Создан .env файл из env.example. Отредактируйте его перед запуском!"
            exit 1
        else
            log_error "Файл env.example не найден. Создайте .env файл вручную."
            exit 1
        fi
    fi
    
    log_success ".env файл найден"
}

# Остановка сервисов
stop_services() {
    log_info "Остановка сервисов..."
    docker-compose down
    log_success "Сервисы остановлены"
}

# Обновление кода
update_code() {
    log_info "Обновление кода с GitHub..."
    
    # Проверка статуса Git
    if [ -d ".git" ]; then
        # Сохранение текущих изменений (если есть)
        if ! git diff --quiet; then
            log_warning "Обнаружены локальные изменения. Создаю stash..."
            git stash push -m "Auto stash before update $(date)"
        fi
        
        # Обновление кода
        git pull origin main
        log_success "Код обновлен с GitHub"
    else
        log_error "Это не Git репозиторий. Обновите код вручную."
        exit 1
    fi
}

# Пересборка и запуск сервисов
rebuild_services() {
    log_info "Пересборка и запуск сервисов..."
    docker-compose up -d --build
    log_success "Сервисы пересобраны и запущены"
}

# Применение миграций
apply_migrations() {
    log_info "Применение миграций..."
    
    # Ждем запуска сервисов
    sleep 10
    
    # User Service
    if docker-compose ps user-service | grep -q "Up"; then
        log_info "Применение миграций User Service..."
        docker-compose exec -T user-service python manage.py migrate --noinput || log_warning "Ошибка миграций User Service"
    fi
    
    # Zayavki Service
    if docker-compose ps zayavki-service | grep -q "Up"; then
        log_info "Применение миграций Zayavki Service..."
        docker-compose exec -T zayavki-service python manage.py migrate --noinput || log_warning "Ошибка миграций Zayavki Service"
    fi
    
    # Finance Service
    if docker-compose ps finance-service | grep -q "Up"; then
        log_info "Применение миграций Finance Service..."
        docker-compose exec -T finance-service python manage.py migrate --noinput || log_warning "Ошибка миграций Finance Service"
    fi
    
    log_success "Миграции применены"
}

# Проверка статуса сервисов
check_status() {
    log_info "Проверка статуса сервисов..."
    docker-compose ps
    
    # Проверка здоровья сервисов
    log_info "Проверка здоровья сервисов..."
    
    # API Gateway
    if curl -f -s http://localhost:8000/health/ > /dev/null; then
        log_success "API Gateway работает"
    else
        log_warning "API Gateway недоступен"
    fi
    
    # User Service
    if curl -f -s http://localhost:8001/swagger/ > /dev/null; then
        log_success "User Service работает"
    else
        log_warning "User Service недоступен"
    fi
    
    # Zayavki Service
    if curl -f -s http://localhost:8002/swagger/ > /dev/null; then
        log_success "Zayavki Service работает"
    else
        log_warning "Zayavki Service недоступен"
    fi
    
    # Finance Service
    if curl -f -s http://localhost:8003/swagger/ > /dev/null; then
        log_success "Finance Service работает"
    else
        log_warning "Finance Service недоступен"
    fi
}

# Очистка неиспользуемых ресурсов
cleanup() {
    log_info "Очистка неиспользуемых ресурсов..."
    docker system prune -f
    log_success "Очистка завершена"
}

# Основная функция
main() {
    echo "🚀 Начинаем обновление CRM проекта..."
    echo "================================================"
    
    # Проверки
    check_docker
    check_git
    check_env
    
    # Обновление
    stop_services
    update_code
    rebuild_services
    apply_migrations
    check_status
    cleanup
    
    echo "================================================"
    log_success "Обновление завершено успешно!"
    echo ""
    echo "📊 Статус сервисов:"
    docker-compose ps
    echo ""
    echo "📝 Логи сервисов: docker-compose logs -f"
    echo "🌐 Доступ к приложению: https://crm.lead-schem.ru"
}

# Обработка ошибок
trap 'log_error "Произошла ошибка. Проверьте логи выше."; exit 1' ERR

# Запуск основной функции
main "$@" 