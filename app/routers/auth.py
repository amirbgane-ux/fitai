from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from app.database import get_db
from app.crud import crud_user
from app.schemas import User, UserCreate
from app.security import verify_password, create_access_token
from datetime import datetime, timedelta
import requests
import hashlib
import hmac
import time
from app.config import settings

router = APIRouter()

# ============== ОСНОВНАЯ РЕГИСТРАЦИЯ И ЛОГИН ==============
@router.post("/register", response_model=User)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Регистрация нового пользователя через email/password"""
    existing_user = crud_user.get_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    user = crud_user.create(db, user_data)
    return user

@router.post("/login")
def login_user(
    credentials: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Вход пользователя по email/password"""
    user = crud_user.get_by_email(db, credentials.get('email'))
    if not user or not verify_password(credentials.get('password'), user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль"
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        {"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer", "user": user}

# ============== GOOGLE AUTH ==============
@router.post("/google-auth")
def google_auth(
    token_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Авторизация через Google"""
    id_token = token_data.get('id_token')
    if not id_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID токен обязателен"
        )
    
    google_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
    response = requests.get(google_url)
    
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный Google ID токен"
        )
    
    google_user = response.json()
    google_id = google_user.get('sub')
    email = google_user.get('email')
    username = google_user.get('name', email.split('@')[0])
    
    # Ищем по Google ID
    user = crud_user.get_by_google_id(db, google_id)
    if user:
        token = create_access_token({"sub": str(user.id)})
        return {"access_token": token, "token_type": "bearer", "user": user}
    
    # Ищем по email
    existing_user = crud_user.get_by_email(db, email)
    if existing_user:
        existing_user.google_id = google_id
        db.commit()
        db.refresh(existing_user)
        
        token = create_access_token({"sub": str(existing_user.id)})
        return {"access_token": token, "token_type": "bearer", "user": existing_user}
    
    # Создаем нового
    user_data = UserCreate(
        email=email,
        username=username,
        password=None,  # Пустой пароль для OAuth
        google_id=google_id
    )
    user = crud_user.create(db, user_data)
    
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user": user}

# ============== TELEGRAM AUTH (ВСЕ ВАРИАНТЫ) ==============
@router.post("/telegram-auth")
def telegram_auth(
    auth_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """УНИВЕРСАЛЬНЫЙ обработчик Telegram авторизации"""
    print(f"🔐 TELEGRAM AUTH - Тип: {auth_data.get('auth_type', 'unknown')}")
    
    # Определяем тип авторизации
    auth_type = auth_data.get('auth_type', 'unknown')
    
    if auth_type == 'mock':
        return handle_mock_auth(auth_data, db)
    elif auth_type == 'webapp':
        return handle_webapp_auth(auth_data, db)
    elif auth_type == 'oauth':
        return handle_oauth_auth(auth_data, db)
    else:
        # Автоопределение
        return handle_auto_auth(auth_data, db)

def handle_mock_auth(auth_data: Dict[str, Any], db: Session):
    """Mock авторизация для разработки"""
    print("🧪 Используем mock данные для разработки")
    
    telegram_id = int(auth_data.get('id', 123456789))
    first_name = auth_data.get('first_name', 'Test')
    last_name = auth_data.get('last_name', 'User')
    username = auth_data.get('username', f'user_{telegram_id}')
    
    return create_or_get_user(
        db=db,
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        auth_type='mock'
    )

def handle_webapp_auth(auth_data: Dict[str, Any], db: Session):
    """Telegram Web App (Mini App) авторизация"""
    print("📱 Telegram Web App авторизация")
    
    # Проверяем подпись
    if not verify_webapp_signature(auth_data):
        raise HTTPException(status_code=401, detail="Неверная подпись Web App")
    
    telegram_id = int(auth_data['id'])
    first_name = auth_data.get('first_name', '')
    last_name = auth_data.get('last_name', '')
    username = auth_data.get('username', first_name)
    
    return create_or_get_user(
        db=db,
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        auth_type='webapp'
    )

def handle_oauth_auth(auth_data: Dict[str, Any], db: Session):
    """Telegram OAuth авторизация (через сайт)"""
    print("🌐 Telegram OAuth авторизация")
    
    # Проверяем временную метку (не старше 24 часов)
    auth_date = int(auth_data.get('auth_date', 0))
    if time.time() - auth_date > 86400:
        raise HTTPException(status_code=401, detail="Данные устарели")
    
    telegram_id = int(auth_data['id'])
    first_name = auth_data.get('first_name', '')
    last_name = auth_data.get('last_name', '')
    username = auth_data.get('username', first_name)
    
    return create_or_get_user(
        db=db,
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        auth_type='oauth'
    )

def handle_auto_auth(auth_data: Dict[str, Any], db: Session):
    """Автоматическое определение типа"""
    print("🤖 Автоопределение типа авторизации")
    
    telegram_id = int(auth_data.get('id', 0))
    first_name = auth_data.get('first_name', 'User')
    last_name = auth_data.get('last_name', '')
    username = auth_data.get('username', first_name)
    
    # Если есть hash и bot_token - вероятно WebApp
    if 'hash' in auth_data and settings.TELEGRAM_BOT_TOKEN:
        if verify_webapp_signature(auth_data):
            print("Определен как WebApp")
            auth_type = 'webapp'
        else:
            print("Определен как OAuth (устаревшая подпись)")
            auth_type = 'oauth'
    else:
        print("Определен как mock/упрощенный")
        auth_type = 'mock'
    
    return create_or_get_user(
        db=db,
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        auth_type=auth_type
    )

def create_or_get_user(db: Session, telegram_id: int, username: str, 
                      first_name: str, last_name: str, auth_type: str):
    """Общая логика создания/получения пользователя"""
    
    # Ищем по Telegram ID
    user = crud_user.get_by_telegram_id(db, telegram_id)
    
    if user:
        print(f"✅ Найден существующий пользователь: {user.username}")
        # Обновляем информацию если нужно
        if user.username != username:
            user.username = username
            db.commit()
            db.refresh(user)
    else:
        # Создаем нового пользователя
        email = f"telegram_{telegram_id}@{auth_type}.user"
        full_name = f"{first_name} {last_name}".strip()
        
        # Создаем объект UserCreate
        user_create = UserCreate(
            email=email,
            username=username,
            password=None,  # None разрешено в новой схеме
            telegram_id=telegram_id,
            google_id=None,
            fitness_level='beginner'
        )
        
        try:
            user = crud_user.create(db, user_create)
            print(f"✅ Создан новый Telegram пользователь: {username}")
        except Exception as e:
            print(f"❌ Ошибка создания пользователя: {e}")
            # Если email занят, пробуем другой
            import random
            user_create.email = f"telegram_{telegram_id}_{random.randint(1000,9999)}@{auth_type}.user"
            try:
                user = crud_user.create(db, user_create)
            except Exception as e2:
                print(f"❌ Вторая попытка тоже не удалась: {e2}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Не удалось создать пользователя"
                )
    
    # Генерируем токен
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        {"sub": str(user.id), "auth_type": auth_type},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": full_name,
            "telegram_id": user.telegram_id,
            "auth_method": auth_type
        }
    }

def verify_webapp_signature(data: Dict[str, Any]) -> bool:
    """Проверка подписи Telegram Web App"""
    try:
        bot_token = settings.TELEGRAM_BOT_TOKEN
        if not bot_token:
            print("⚠️ TELEGRAM_BOT_TOKEN не настроен")
            return False
        
        received_hash = data['hash']
        
        # Создаем строку для проверки
        check_data = {k: v for k, v in data.items() if k != 'hash'}
        data_check_string = '\n'.join(
            f"{key}={value}"
            for key, value in sorted(check_data.items())
        )
        
        # Правильный алгоритм для WebApp
        secret_key = hmac.new(
            key=b'WebAppData',
            msg=bot_token.encode(),
            digestmod=hashlib.sha256
        ).digest()
        
        computed_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        result = hmac.compare_digest(computed_hash, received_hash)
        print(f"🔐 Проверка подписи: {'✅ Успешно' if result else '❌ Неверно'}")
        return result
        
    except Exception as e:
        print(f"❌ Ошибка проверки подписи: {e}")
        return False