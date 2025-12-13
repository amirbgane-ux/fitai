from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str
    fitness_level: Optional[str] = 'beginner'

class UserCreate(UserBase):
    password: Optional[str] = None  # ← Разрешаем None для OAuth пользователей
    telegram_id: Optional[int] = None
    google_id: Optional[str] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    fitness_level: Optional[str] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class User(UserResponse):
    pass