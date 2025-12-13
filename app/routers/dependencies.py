# app/routers/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import crud_user
from app.security import decode_access_token # <-- Импортируем функцию из security.py

# Создаём схему аутентификации (ожидаем Bearer токен)
oauth2_scheme = HTTPBearer()

def get_current_user(
    token: str = Depends(oauth2_scheme), # <-- Получаем токен через схему
    db: Session = Depends(get_db)
):
    """
    Зависимость для получения текущего пользователя из JWT токена.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Декодируем токен, чтобы получить user_id
    user_id = decode_access_token(token.credentials) # token.credentials содержит сам токен
    
    if user_id is None:
        raise credentials_exception
    
    # Находим пользователя в базе по ID
    user = crud_user.get_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    
    return user

# Упрощенная версия больше не нужна, можно удалить или закомментировать
# def get_current_user_simplified(db: Session = Depends(get_db)):
#     user = crud_user.get_by_id(db, 1)
#     if not user:
#         raise HTTPException(status_code=404, detail="Пользователь не найден")
#     return user