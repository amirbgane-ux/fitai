from pydantic import BaseModel,  ConfigDict
from typing import Optional
from datetime import datetime

class AIInteractionBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    interaction_type: str
    user_input: str

class AIInteractionCreate(AIInteractionBase):
    
    ai_prompt: str
    model_used: str
    tokens_used: Optional[int] = None

class AIInteraction(AIInteractionBase):
    id: int
    user_id: int
    ai_prompt: str
    ai_response: str
    model_used: str
    tokens_used: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True