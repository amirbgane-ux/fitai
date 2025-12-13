from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class ExerciseRecommendation(Base):
    __tablename__ = "exercise_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_limitations = Column(Text, nullable=False)
    limitations_type = Column(String(100), nullable=False)
    ai_recommended_exercises = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Связи
    user = relationship("User", back_populates="exercise_recommendations")