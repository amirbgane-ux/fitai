# app/schemas/weekly_challenge.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class WeeklyChallengeBase(BaseModel):
    challenge_type: str
    week_number: int
    target_reps: Optional[int] = None
    target_sets: Optional[int] = None
    target_duration: Optional[int] = None

class WeeklyChallengeCreate(WeeklyChallengeBase):
    pass

class WeeklyChallengeUpdate(BaseModel):
    completed: Optional[bool] = None

class WeeklyChallengeResponse(WeeklyChallengeBase):
    id: int
    user_id: int
    ai_generated_challenge: str
    completed: bool
    completed_at: Optional[datetime] = None
    created_at: datetime
    target_metrics: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# WeeklyChallenge теперь ссылается на WeeklyChallengeResponse
class WeeklyChallenge(WeeklyChallengeResponse):
    pass