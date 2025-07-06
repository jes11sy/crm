#!/bin/bash

# === Параметры подключения ===
REMOTE_USER="root"
REMOTE_HOST="5.129.204.52"
REMOTE_PASS="uh@312C4.tMSmQ"
REMOTE_DIR="/root/crm_deploy"

# === Проверка наличия sshpass ===
if ! command -v sshpass &> /dev/null; then
  echo "Устанавливаю sshpass..."
  sudo apt-get update && sudo apt-get install -y sshpass
fi

# === Копирование проекта на сервер ===
echo "Копирую проект на сервер..."
sshpass -p "$REMOTE_PASS" scp -r ../* $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR

# === Установка Docker и Docker Compose на сервере ===
echo "Устанавливаю Docker и Docker Compose на сервере..."
sshpass -p "$REMOTE_PASS" ssh -o StrictHostKeyChecking=no $REMOTE_USER@$REMOTE_HOST "\
  apt-get update && \
  apt-get install -y docker.io docker-compose && \
  systemctl enable --now docker && \
  cd $REMOTE_DIR && \
  docker-compose -f docker-compose-production.yml --env-file env.production up -d \
"

echo "\n=== Перенос и запуск CRM завершён! ==="
echo "Проверьте сайт по адресу: http://$REMOTE_HOST или по вашему домену."
echo "Если нужен SSL — настройте домен и выполните скрипт получения сертификата на сервере." 