from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class WeeklyChallenge(Base):
    __tablename__ = "weekly_challenges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ai_generated_challenge = Column(Text, nullable=False)
    week_number = Column(Integer, nullable=False)
    challenge_type = Column(String(50), nullable=False)
    target_metrics = Column(JSONB)
    completed = Column(Boolean, default=False)
    completed_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Связи
    user = relationship("User", back_populates="weekly_challenges")