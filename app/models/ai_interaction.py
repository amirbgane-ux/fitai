from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class AIInteraction(Base):
    __tablename__ = "ai_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    interaction_type = Column(String(50), nullable=False)
    user_input = Column(Text, nullable=False)
    ai_prompt = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    model_used = Column(String(100), nullable=False)
    tokens_used = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User")