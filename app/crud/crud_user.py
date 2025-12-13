from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.security import get_password_hash
from typing import Optional, List

class CRUDUser:
    def get_by_id(self, db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    def get_by_google_id(self, db: Session, google_id: str) -> Optional[User]:
        return db.query(User).filter(User.google_id == google_id).first()
    
    def get_by_telegram_id(self, db: Session, telegram_id: int) -> Optional[User]:
        return db.query(User).filter(User.telegram_id == telegram_id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()
    
    def create(self, db: Session, user_data: UserCreate) -> User:
        # Хешируем пароль если он есть
        hashed_password = ""
        if user_data.password:
            hashed_password = get_password_hash(user_data.password)
        
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            password=hashed_password,
            telegram_id=user_data.telegram_id,
            google_id=user_data.google_id,
            fitness_level=user_data.fitness_level
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def update(self, db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
        db_user = self.get_by_id(db, user_id)
        if db_user:
            update_data = user_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_user, field, value)
            db.commit()
            db.refresh(db_user)
        return db_user
    
    def delete(self, db: Session, user_id: int) -> bool:
        db_user = self.get_by_id(db, user_id)
        if db_user:
            db.delete(db_user)
            db.commit()
            return True
        return False

crud_user = CRUDUser()