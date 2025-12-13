# app/crud/crud_weekly_challenge.py
from sqlalchemy.orm import Session
from app.models.weekly_challenge import WeeklyChallenge
from sqlalchemy import func
# --- ИЗМЕНЕНО: Убираем WeeklyChallengeCreate из импорта, так как create теперь принимает dict ---
# from app.schemas.weekly_challenge import WeeklyChallengeCreate, WeeklyChallengeUpdate
from app.schemas.weekly_challenge import WeeklyChallengeUpdate # <-- WeeklyChallengeUpdate всё ещё нужен
# --- /ИЗМЕНЕНО ---
from typing import Optional, List

class CRUDWeeklyChallenge:
    def get_by_id(self, db: Session, challenge_id: int) -> Optional[WeeklyChallenge]:
        return db.query(WeeklyChallenge).filter(WeeklyChallenge.id == challenge_id).first()
    
    def get_by_user_id(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[WeeklyChallenge]:
        return db.query(WeeklyChallenge).filter(WeeklyChallenge.user_id == user_id).offset(skip).limit(limit).all()
    
    def get_current_week(self, db: Session, user_id: int, week_number: int) -> Optional[WeeklyChallenge]:
        return db.query(WeeklyChallenge).filter(
            WeeklyChallenge.user_id == user_id,
            WeeklyChallenge.week_number == week_number
        ).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[WeeklyChallenge]:
        return db.query(WeeklyChallenge).offset(skip).limit(limit).all()
    
    # --- ИЗМЕНЕНО: Сигнатура метода create ---
    # Теперь принимает словарь, подготовленный в роутере
    def create(self, db: Session, challenge_dict: dict) -> WeeklyChallenge:
        # challenge_dict уже содержит все необходимые поля, включая target_metrics
        db_challenge = WeeklyChallenge(**challenge_dict)
        db.add(db_challenge)
        db.commit()
        db.refresh(db_challenge)
        return db_challenge
    # --- /ИЗМЕНЕНО ---
    
    def update(self, db: Session, challenge_id: int, challenge_data: WeeklyChallengeUpdate) -> Optional[WeeklyChallenge]:
        db_challenge = self.get_by_id(db, challenge_id)
        if db_challenge:
            update_data = challenge_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_challenge, field, value)
            
            # Если отмечаем как выполненное - ставим текущее время
            if update_data.get('completed') and not db_challenge.completed_at:
                from sqlalchemy import func
                db_challenge.completed_at = func.now()
            
            db.commit()
            db.refresh(db_challenge)
        return db_challenge
    
    def delete(self, db: Session, challenge_id: int) -> bool:
        db_challenge = self.get_by_id(db, challenge_id)
        if db_challenge:
            db.delete(db_challenge)
            db.commit()
            return True
        return False
    def delete(self, db: Session, challenge_id: int) -> bool:
        """Удаляет челлендж по ID. Возвращает True, если удаление прошло успешно."""
        db_challenge = self.get_by_id(db, challenge_id)
        if db_challenge:
            db.delete(db_challenge)
            db.commit()
            return True
        return False
    def mark_completed(self, db: Session, challenge_id: int) -> Optional[WeeklyChallenge]:
        """Отметить челлендж как выполненный."""
        db_challenge = self.get_by_id(db, challenge_id)
        if db_challenge:
            db_challenge.completed = True
            db_challenge.completed_at = func.now() # или datetime.utcnow(), в зависимости от вашей модели
            db.commit()
            db.refresh(db_challenge)
        return db_challenge

crud_weekly_challenge = CRUDWeeklyChallenge()