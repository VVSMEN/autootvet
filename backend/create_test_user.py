"""
Create test user for development
"""
import sys
sys.path.insert(0, '.')

from app.db.database import SessionLocal, init_db
from app.db.models import User

# Initialize database
init_db()
db = SessionLocal()

try:
    # Check if user exists
    user = db.query(User).first()
    
    if not user:
        user = User(
            email="admin@autootvet.com",
            telegram_id=None,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✅ Создан тестовый пользователь:")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Telegram ID: {user.telegram_id}")
    else:
        print(f"✅ Пользователь уже существует:")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Telegram ID: {user.telegram_id}")
        
except Exception as e:
    print(f"❌ Ошибка: {e}")
    db.rollback()
finally:
    db.close()
