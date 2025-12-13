from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AnthropometricsBase(BaseModel):
   
    height_cm: int
    weight_kg: float
    age: int
    gender: str
    injuries: Optional[str] = None
    fitness_goals: Optional[str] = None

class AnthropometricsCreate(AnthropometricsBase):
    pass
class AnthropometricsUpdate(BaseModel):
    height_cm: Optional[int] = None
    weight_kg: Optional[float] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    injuries: Optional[str] = None
    fitness_goals: Optional[str] = None

class Anthropometrics(AnthropometricsBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True