# app/schemas/workout_plan.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WorkoutPlanBase(BaseModel):
    user_request: str
    plan_type: str
    difficulty: Optional[str] = None
    duration_minutes: Optional[int] = None

# --- ИСПРАВЛЕНО ---
# Создайте отдельную схему для создания, без user_id и ai_generated_plan
class WorkoutPlanCreateRequest(BaseModel):  # Новое имя, чтобы было понятно назначение
    user_request: str
    plan_type: str
    difficulty: Optional[str] = None
    duration_minutes: Optional[int] = None
    # user_id и ai_generated_plan будут добавлены на бэкенде
# --- /ИСПРАВЛЕНО ---

class WorkoutPlanResponse(WorkoutPlanBase):
    id: int
    user_id: int
    ai_generated_plan: str
    is_completed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class WorkoutPlan(WorkoutPlanResponse):
    pass