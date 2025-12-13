from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    if not password:  # Добавляем проверку на пустой пароль
        return ""  # Для OAuth пользователей
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    if not hashed_password:  # Если хеш пустой
        return False  # Нельзя войти по паролю для OAuth пользователей
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(dict: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Создание JWT токена"""
    to_encode = dict.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def decode_access_token(token: str) -> int | None:
    """
    Декодирует JWT токен и возвращает user_id (sub).
    Возвращает None, если токен недействителен.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
        return int(user_id)
    except jwt.PyJWTError:
        return None

# Дополнительные утилиты
def is_oauth_user(hashed_password: str) -> bool:
    """Проверяет является ли пользователь OAuth (без пароля)"""
    return not bool(hashed_password)  # True если пароль пустой

def validate_user_password(user_password_hash: str, input_password: str) -> bool:
    """Валидация пароля пользователя с учетом OAuth"""
    if is_oauth_user(user_password_hash):
        return False  # OAuth пользователи не могут входить по паролю
    return verify_password(input_password, user_password_hash)