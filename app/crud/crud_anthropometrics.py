from sqlalchemy.orm import Session
from app.models.user_anthropometrics import UserAnthropometrics
from app.schemas.anthropometrics import AnthropometricsCreate, AnthropometricsUpdate
from typing import Optional, List

class CRUDAnthropometrics:
    def get_by_id(self, db: Session, anthropometrics_id: int) -> Optional[UserAnthropometrics]:
        return db.query(UserAnthropometrics).filter(UserAnthropometrics.id == anthropometrics_id).first()
    
    def get_by_user_id(self, db: Session, user_id: int) -> Optional[UserAnthropometrics]:
        return db.query(UserAnthropometrics).filter(UserAnthropometrics.user_id == user_id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[UserAnthropometrics]:
        return db.query(UserAnthropometrics).offset(skip).limit(limit).all()
    
    def create(self, db: Session, anthropometrics_data: AnthropometricsCreate) -> UserAnthropometrics:
        # Проверяем, есть ли уже антропометрия у пользователя
        existing = self.get_by_user_id(db, anthropometrics_data.user_id)
        if existing:
            # Если есть - обновляем существующую
            return self.update(db, existing.id, anthropometrics_data)
        
        db_anthropometrics = UserAnthropometrics(**anthropometrics_data.model_dump())
        db.add(db_anthropometrics)
        db.commit()
        db.refresh(db_anthropometrics)
        return db_anthropometrics
    
    def update(self, db: Session, anthropometrics_id: int, anthropometrics_data: AnthropometricsUpdate) -> Optional[UserAnthropometrics]:
        db_anthropometrics = self.get_by_id(db, anthropometrics_id)
        if db_anthropometrics:
            update_data = anthropometrics_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_anthropometrics, field, value)
            db.commit()
            db.refresh(db_anthropometrics)
        return db_anthropometrics
    
    def update_by_user_id(self, db: Session, user_id: int, anthropometrics_data: AnthropometricsUpdate) -> Optional[UserAnthropometrics]:
        db_anthropometrics = self.get_by_user_id(db, user_id)
        if db_anthropometrics:
            return self.update(db, db_anthropometrics.id, anthropometrics_data)
        return None
    
    def delete(self, db: Session, anthropometrics_id: int) -> bool:
        db_anthropometrics = self.get_by_id(db, anthropometrics_id)
        if db_anthropometrics:
            db.delete(db_anthropometrics)
            db.commit()
            return True
        return False

crud_anthropometrics = CRUDAnthropometrics()