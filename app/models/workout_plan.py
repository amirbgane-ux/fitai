from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_request = Column(Text, nullable=False)
    ai_generated_plan = Column(Text, nullable=False)
    plan_type = Column(String(50), nullable=False)
    difficulty = Column(String(20))
    duration_minutes = Column(Integer)
    is_completed = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Связи
    user = relationship("User", back_populates="workout_plans")
    workout_history = relationship("WorkoutHistory", back_populates="workout_plan")
    injury_predictions = relationship("InjuryPrediction", back_populates="workout_plan")