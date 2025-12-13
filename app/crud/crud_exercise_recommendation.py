from sqlalchemy.orm import Session
from app.models.exercise_recommendation import ExerciseRecommendation
from app.schemas.exercise_recommendation import ExerciseRecommendationCreate
from typing import Optional, List

class CRUDExerciseRecommendation:
    def get_by_id(self, db: Session, recommendation_id: int) -> Optional[ExerciseRecommendation]:
        return db.query(ExerciseRecommendation).filter(ExerciseRecommendation.id == recommendation_id).first()
    
    def get_by_user_id(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[ExerciseRecommendation]:
        return db.query(ExerciseRecommendation).filter(ExerciseRecommendation.user_id == user_id).offset(skip).limit(limit).all()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[ExerciseRecommendation]:
        return db.query(ExerciseRecommendation).offset(skip).limit(limit).all()
    
    def create(self, db: Session, recommendation_data:  ExerciseRecommendationCreate) -> ExerciseRecommendation:
        db_recommendation = ExerciseRecommendation(**recommendation_data)
        db.add(db_recommendation)
        db.commit()
        db.refresh(db_recommendation)
        return db_recommendation
    
    def delete(self, db: Session, recommendation_id: int) -> bool:
        db_recommendation = self.get_by_id(db, recommendation_id)
        if db_recommendation:
            db.delete(db_recommendation)
            db.commit()
            return True
        return False
    def delete(self, db: Session, recommendation_id: int) -> bool:
        """Удалить рекомендацию упражнений по ID."""
        db_rec = self.get_by_id(db, recommendation_id)
        if db_rec:
            db.delete(db_rec)
            db.commit()
            return True
        return False

crud_exercise_recommendation = CRUDExerciseRecommendation()