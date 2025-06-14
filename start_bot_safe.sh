#!/bin/bash
echo "🚀 Запуск Crypto Lead Bot..."

# Переходим в директорию проекта
cd /root/projects/crypto-lead-bot-production

# Активируем виртуальное окружение
source venv/bin/activate

# Останавливаем старые процессы
echo "⏹️  Останавливаем старые процессы..."
pkill -f "python run.py"
sleep 2

# Запускаем бота
echo "▶️  Запускаем бота..."
python run.py
