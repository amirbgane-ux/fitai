from sqlalchemy.orm import Session
from app.models.workout_history import WorkoutHistory
from app.schemas.workout_history import WorkoutHistoryCreate
from typing import Optional, List, Union, Dict, Any

class CRUDWorkoutHistory:
    def get_by_id(self, db: Session, history_id: int) -> Optional[WorkoutHistory]:
        return db.query(WorkoutHistory).filter(WorkoutHistory.id == history_id).first()
    
    def get_by_user_id(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[WorkoutHistory]:
        return db.query(WorkoutHistory)\
            .filter(WorkoutHistory.user_id == user_id)\
            .order_by(WorkoutHistory.completed_at.desc())\
            .offset(skip).limit(limit).all()
    
    def get_by_plan_id(self, db: Session, plan_id: int) -> List[WorkoutHistory]:
        return db.query(WorkoutHistory).filter(WorkoutHistory.plan_id == plan_id).all()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[WorkoutHistory]:
        return db.query(WorkoutHistory).offset(skip).limit(limit).all()
    
    def create(self, db: Session, history_data: Union[WorkoutHistoryCreate, Dict[str, Any]]) -> WorkoutHistory:
        # Поддерживаем и словарь, и Pydantic модель
        if isinstance(history_data, dict):
            db_history = WorkoutHistory(**history_data)
        else:
            db_history = WorkoutHistory(**history_data.model_dump())
        
        db.add(db_history)
        db.commit()
        db.refresh(db_history)
        return db_history
    
    def delete(self, db: Session, history_id: int) -> bool:
        db_history = self.get_by_id(db, history_id)
        if db_history:
            db.delete(db_history)
            db.commit()
            return True
        return False
    
    def delete_by_user_id(self, db: Session, user_id: int) -> int:
        """Удаляет все записи истории для указанного пользователя. Возвращает количество удалённых записей."""
        histories = db.query(WorkoutHistory).filter(WorkoutHistory.user_id == user_id).all()
        count = len(histories)
        for history in histories:
            db.delete(history)
        db.commit()
        return count

crud_workout_history = CRUDWorkoutHistory()