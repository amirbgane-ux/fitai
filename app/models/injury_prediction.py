from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class InjuryPrediction(Base):
    __tablename__ = "injury_predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workout_plan_id = Column(Integer, ForeignKey("workout_plans.id"))
    exercises_analyzed = Column(JSONB, nullable=False)
    ai_risk_prediction = Column(Text, nullable=False)
    risk_level = Column(String(50))
    risk_factors = Column(JSONB)
    recommendations = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # # Связи
    user = relationship("User", back_populates="injury_predictions")
    workout_plan = relationship("WorkoutPlan", back_populates="injury_predictions")