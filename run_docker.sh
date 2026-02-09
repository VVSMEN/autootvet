#!/bin/bash

echo "🐳 Запуск AutoOtvet через Docker..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Файл .env не найден. Копирую из .env.example..."
    cp .env.example .env
    echo "⚠️  Отредактируйте .env файл и добавьте API ключи"
    exit 1
fi

# Build and start containers
echo "🔨 Сборка и запуск контейнеров..."
docker-compose up --build -d

echo ""
echo "✅ AutoOtvet запущен!"
echo ""
echo "🌐 Frontend: http://localhost:8501"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Для просмотра логов: docker-compose logs -f"
echo "Для остановки: docker-compose down"
echo ""
