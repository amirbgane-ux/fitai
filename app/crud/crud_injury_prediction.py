from sqlalchemy.orm import Session
from app.models.injury_prediction import InjuryPrediction
from app.schemas.injury_prediction import InjuryPredictionCreate
from typing import Optional, List

class CRUDInjuryPrediction:
    def get_by_id(self, db: Session, prediction_id: int) -> Optional[InjuryPrediction]:
        return db.query(InjuryPrediction).filter(InjuryPrediction.id == prediction_id).first()
    
    def get_by_user_id(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[InjuryPrediction]:
        return db.query(InjuryPrediction).filter(InjuryPrediction.user_id == user_id).offset(skip).limit(limit).all()
    
    def get_by_plan_id(self, db: Session, plan_id: int) -> List[InjuryPrediction]:
        return db.query(InjuryPrediction).filter(InjuryPrediction.workout_plan_id == plan_id).all()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[InjuryPrediction]:
        return db.query(InjuryPrediction).offset(skip).limit(limit).all()
    
    def create(self, db: Session, prediction_data: InjuryPredictionCreate) -> InjuryPrediction:
        db_prediction = InjuryPrediction(**prediction_data)
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)
        return db_prediction
    
    def delete(self, db: Session, prediction_id: int) -> bool:
        db_prediction = self.get_by_id(db, prediction_id)
        if db_prediction:
            db.delete(db_prediction)
            db.commit()
            return True
        return False
    def delete(self, db: Session, prediction_id: int) -> bool:
        """Удалить прогноз риска травмы по ID."""
        db_pred = self.get_by_id(db, prediction_id)
        if db_pred:
            db.delete(db_pred)
            db.commit()
            return True
        return False

crud_injury_prediction = CRUDInjuryPrediction()