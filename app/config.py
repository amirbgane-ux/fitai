from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    OPENROUTER_API_KEY: Optional[str] = None
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_BOT_USERNAME: Optional[str] = None  # ← ДОБАВЛЕНО
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# Добавьте для отладки
print(f"=== CONFIG LOADED ===")
print(f"Database URL: {settings.DATABASE_URL[:30]}...")
print(f"Telegram Token: {settings.TELEGRAM_BOT_TOKEN[:10] if settings.TELEGRAM_BOT_TOKEN else 'NOT SET'}")
print(f"Telegram Username: {settings.TELEGRAM_BOT_USERNAME}")
print(f"=====================")