from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class WorkoutHistory(Base):
    __tablename__ = "workout_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("workout_plans.id"))
    exercises_completed = Column(JSONB, nullable=False)
    session_duration = Column(Integer, nullable=False)
    perceived_exertion = Column(Integer)
    user_feedback = Column(Text)
    notes = Column(Text)
    completed_at = Column(TIMESTAMP, server_default=func.now())

    # Связи
    user = relationship("User", back_populates="workout_history")
    workout_plan = relationship("WorkoutPlan", back_populates="workout_history")