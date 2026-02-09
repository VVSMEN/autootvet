#!/bin/bash

echo "🚀 Запуск AutoOtvet локально..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install backend dependencies
echo "📥 Установка зависимостей backend..."
pip install -r backend/requirements.txt > /dev/null 2>&1

# Install frontend dependencies
echo "📥 Установка зависимостей frontend..."
pip install -r frontend/requirements.txt > /dev/null 2>&1

# Create data directory
mkdir -p data/logs

echo ""
echo "✅ Готово к запуску!"
echo ""
echo "Запустите в отдельных терминалах:"
echo "  1. Backend:  cd backend && python main.py"
echo "  2. Frontend: streamlit run frontend/streamlit_app.py"
echo ""
