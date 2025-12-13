from pydantic import BaseModel
from datetime import datetime

class ExerciseRecommendationBase(BaseModel):
    user_limitations: str
    limitations_type: str

class ExerciseRecommendationCreate(ExerciseRecommendationBase):
    pass
class ExerciseRecommendation(ExerciseRecommendationBase):
    id: int
    user_id: int
    ai_recommended_exercises: str
    created_at: datetime
    
    class Config:
        from_attributes = True