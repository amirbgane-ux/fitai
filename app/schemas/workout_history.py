# app/schemas/workout_history.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class WorkoutHistoryBase(BaseModel):
    session_duration: int
    perceived_exertion: Optional[int] = None
    user_feedback: Optional[str] = None
    notes: Optional[str] = None

class WorkoutHistoryCreate(WorkoutHistoryBase):
    plan_id: Optional[int] = None
    exercises_completed: Dict[str, Any]
    # ДОБАВЬТЕ user_id в схему создания
    user_id: int

class WorkoutHistory(WorkoutHistoryBase):
    id: int
    user_id: int
    plan_id: Optional[int] = None
    exercises_completed: Dict[str, Any]
    completed_at: datetime
    
    class Config:
        from_attributes = True