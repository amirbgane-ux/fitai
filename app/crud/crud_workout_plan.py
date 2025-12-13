from sqlalchemy.orm import Session
from app.models.workout_plan import WorkoutPlan

from typing import Optional, List

class CRUDWorkoutPlan:
    def get_by_id(self, db: Session, plan_id: int) -> Optional[WorkoutPlan]:
        return db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id).first()
    
    def get_by_user_id(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[WorkoutPlan]:
        return db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).offset(skip).limit(limit).all()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[WorkoutPlan]:
        return db.query(WorkoutPlan).offset(skip).limit(limit).all()
    
    def create(self, db: Session, plan_data) -> WorkoutPlan:
        # Обрабатываем и словарь, и Pydantic модель
        if isinstance(plan_data, dict):
            db_plan = WorkoutPlan(**plan_data)
        else:
            db_plan = WorkoutPlan(**plan_data.model_dump())
        
        db.add(db_plan)
        db.commit()
        db.refresh(db_plan)
        return db_plan
    
    def mark_completed(self, db: Session, plan_id: int) -> Optional[WorkoutPlan]:
        db_plan = self.get_by_id(db, plan_id)
        if db_plan:
            db_plan.is_completed = True
            db.commit()
            db.refresh(db_plan)
        return db_plan
    
    def delete(self, db: Session, plan_id: int) -> bool:
        db_plan = self.get_by_id(db, plan_id)
        if db_plan:
            db.delete(db_plan)
            db.commit()
            return True
        return False

crud_workout_plan = CRUDWorkoutPlan()