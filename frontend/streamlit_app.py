"""
Streamlit UI for AutoOtvet
"""
import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="AutoOtvet - AI помощник для отзывов",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.title("🤖 AutoOtvet")
    st.markdown("---")
    
    page = st.radio(
        "Навигация",
        [
            "🏠 Главная",
            "🔑 API Ключи",
            "🤖 Настройка AI",
            "⚙️ Правила ответов",
            "📊 Статистика",
            "💬 История отзывов"
        ]
    )
    
    st.markdown("---")
    st.caption("v0.1.0-alpha")

# Main content area
if page == "🏠 Главная":
    st.markdown('<p class="main-header">Добро пожаловать в AutoOtvet!</p>', unsafe_allow_html=True)
    
    st.write("""
    **AutoOtvet** — это опенсорс решение для автоматических ответов на отзывы на маркетплейсах 
    с поддержкой множества AI провайдеров.
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("🛒 **Маркетплейсы**\n\nWildberries, Ozon")
    
    with col2:
        st.success("🤖 **AI Провайдеры**\n\nOpenAI, Claude, Gemini, GigaChat, YandexGPT, Perplexity")
    
    with col3:
        st.warning("🔒 **Безопасность**\n\nВсе ключи хранятся локально")
    
    st.markdown("---")
    
    st.subheader("Быстрый старт")
    
    st.markdown("""
    1. **Подключите маркетплейсы** — добавьте API ключи Wildberries/Ozon
    2. **Настройте AI** — выберите провайдера и добавьте API ключ
    3. **Создайте правила** — настройте фильтры и параметры ответов
    4. **Запустите обработку** — система начнет автоматически отвечать на отзывы
    """)
    
    st.markdown("---")
    
    # API Health Check
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            st.success("✅ Backend подключен и работает")
        else:
            st.error("❌ Backend недоступен")
    except:
        st.error("❌ Не удалось подключиться к backend. Убедитесь, что сервер запущен.")

elif page == "🔑 API Ключи":
    st.header("Подключение маркетплейсов")
    
    st.info("💡 Все API ключи шифруются и хранятся только на вашем устройстве")
    
    # Wildberries
    with st.expander("🛒 Wildberries", expanded=True):
        st.markdown("""
        **Как получить API ключ:**
        1. Перейдите в [Личный кабинет продавца](https://seller.wildberries.ru/)
        2. Настройки → Доступ к API
        3. Создайте новый токен с правами на чтение/запись отзывов
        """)
        
        wb_api_key = st.text_input(
            "API Key Wildberries",
            type="password",
            help="Токен из личного кабинета WB"
        )
        wb_shop_name = st.text_input("Название магазина", placeholder="Мой магазин")
        
        if st.button("💾 Сохранить Wildberries", key="save_wb"):
            if wb_api_key and wb_shop_name:
                st.markdown('<div class="success-box">✅ Wildberries подключен успешно!</div>', unsafe_allow_html=True)
                # TODO: Save to backend
            else:
                st.error("Заполните все поля")
    
    # Ozon
    with st.expander("🟣 Ozon"):
        st.markdown("""
        **Как получить API ключи:**
        1. Перейдите в [Seller Ozon](https://seller.ozon.ru/)
        2. Настройки → API ключи
        3. Создайте новый ключ
        """)
        
        ozon_client_id = st.text_input("Client ID", type="password")
        ozon_api_key = st.text_input("API Key", type="password")
        ozon_shop_name = st.text_input("Название магазина", placeholder="Мой магазин на Ozon", key="ozon_shop")
        
        if st.button("💾 Сохранить Ozon", key="save_ozon"):
            if ozon_client_id and ozon_api_key:
                st.markdown('<div class="success-box">✅ Ozon подключен успешно!</div>', unsafe_allow_html=True)
                # TODO: Save to backend
            else:
                st.error("Заполните все поля")

elif page == "🤖 Настройка AI":
    st.header("Выбор AI провайдера")
    
    provider = st.selectbox(
        "Провайдер",
        [
            "GigaChat (Сбер) — 160₽/1M токенов",
            "YandexGPT Lite — 200₽/1M токенов",
            "OpenAI GPT-4o-mini — $0.15/1M токенов",
            "Claude Haiku — $0.25/1M токенов",
            "Gemini Flash — $0.075/1M токенов",
            "Perplexity Sonar — $0.2/1M токенов"
        ]
    )
    
    provider_key = provider.split()[0].lower()
    
    # API Key input
    api_key = st.text_input(
        f"API Key для {provider.split()[0]}",
        type="password",
        help="Ключ провайдера"
    )
    
    # Additional fields for specific providers
    if "gigachat" in provider_key:
        credentials = st.text_input("Credentials (опционально)", type="password")
    elif "yandex" in provider_key:
        folder_id = st.text_input("Folder ID")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        temperature = st.slider(
            "Креативность (Temperature)",
            0.0, 1.0, 0.7, 0.1,
            help="Выше = более креативные ответы"
        )
    
    with col2:
        max_tokens = st.number_input(
            "Макс. токенов",
            50, 500, 200, 10,
            help="Максимальная длина ответа"
        )
    
    st.markdown("---")
    
    # Test generation
    st.subheader("Тест генерации")
    
    test_review = st.text_area(
        "Тестовый отзыв",
        placeholder="Отличный товар, спасибо!",
        height=100
    )
    test_rating = st.slider("Рейтинг", 1, 5, 5)
    
    if st.button("🧪 Сгенерировать ответ"):
        if test_review:
            with st.spinner("Генерирую ответ..."):
                # TODO: Call backend API
                st.success("**Сгенерированный ответ:**")
                st.info("Спасибо за отличный отзыв! 😊 Рады, что вам понравилось. Будем рады видеть снова!")
        else:
            st.error("Введите тестовый отзыв")

elif page == "⚙️ Правила ответов":
    st.header("Настройка правил автоматизации")
    
    rule_name = st.text_input("Название правила", placeholder="Основные правила")
    
    st.subheader("Фильтры по рейтингу")
    rating_range = st.slider(
        "Отвечать на отзывы с рейтингом",
        1, 5, (4, 5),
        help="Выберите диапазон рейтингов"
    )
    
    st.subheader("Фильтры по содержанию")
    
    keywords_include = st.text_input(
        "Отвечать только если есть слова (через запятую)",
        placeholder="спасибо, отлично, качество",
        help="Оставьте пустым для отключения фильтра"
    )
    
    keywords_exclude = st.text_input(
        "НЕ отвечать если есть слова (через запятую)",
        placeholder="брак, возврат, жалоба"
    )
    
    st.subheader("Модерация")
    
    auto_send = st.checkbox(
        "Автоматическая отправка ответов (без модерации)",
        value=False,
        help="Если выключено, ответы будут отправляться в Telegram для утверждения"
    )
    
    if not auto_send:
        st.info("💬 Ответы будут отправляться в Telegram для утверждения перед публикацией")
        tg_token = st.text_input("Telegram Bot Token", type="password")
        tg_chat_id = st.text_input("Ваш Telegram Chat ID")
    
    st.subheader("Кастомный промпт")
    
    custom_prompt = st.text_area(
        "Дополнительные инструкции для AI",
        placeholder="""Например:
- Всегда благодари за покупку
- Предлагай скидку 10% на следующий заказ
- Указывай контакты поддержки: support@example.com""",
        height=150
    )
    
    tone = st.select_slider(
        "Тон ответов",
        options=["Формальный", "Дружелюбный", "Извиняющийся"],
        value="Дружелюбный"
    )
    
    if st.button("💾 Сохранить правила"):
        if rule_name:
            st.success("✅ Правила сохранены успешно!")
            # TODO: Save to backend
        else:
            st.error("Введите название правила")

elif page == "📊 Статистика":
    st.header("Статистика работы")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Отзывов обработано", "0", "0")
    
    with col2:
        st.metric("Средний рейтинг", "0.0", "0.0")
    
    with col3:
        st.metric("Затраты на AI", "₽0", "₽0")
    
    with col4:
        st.metric("Авто-ответы", "0%", "0%")
    
    st.info("📊 Статистика появится после обработки первых отзывов")

elif page == "💬 История отзывов":
    st.header("История обработанных отзывов")
    
    st.info("📝 Отзывы появятся после подключения маркетплейсов и настройки правил")
    
    # TODO: Display reviews table
