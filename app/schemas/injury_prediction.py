from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class InjuryPredictionBase(BaseModel):
    risk_level: Optional[str] = None
    recommendations: Optional[str] = None
    exercises_analyzed: Optional[str] = Field(default="", description="Описание упражнений для анализа")
    risk_factors: Optional[str] = Field(default="", description="Дополнительные факторы риска")

class InjuryPredictionCreate(InjuryPredictionBase):
    workout_plan_id: Optional[int] = None

class InjuryPredictionResponse(InjuryPredictionBase):
    id: int
    user_id: int
    workout_plan_id: Optional[int]
    workout_plan_name: Optional[str] = None  # Вычисляемое поле, не сохраняется в БД
    ai_risk_prediction: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class InjuryPrediction(InjuryPredictionResponse):
    pass