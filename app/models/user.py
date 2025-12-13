from sqlalchemy import Column, Integer, String, BigInteger, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=True)
    google_id = Column(String(255), unique=True, index=True, nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False) 
    fitness_level = Column(String(20), default='beginner')
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Связи с другими таблицами
    anthropometrics = relationship("UserAnthropometrics", back_populates="user", cascade="all, delete-orphan", uselist=False)
    workout_plans = relationship("WorkoutPlan", back_populates="user")
    exercise_recommendations = relationship("ExerciseRecommendation", back_populates="user")
    weekly_challenges = relationship("WeeklyChallenge", back_populates="user")
    workout_history = relationship("WorkoutHistory", back_populates="user")
    injury_predictions = relationship("InjuryPrediction", back_populates="user")
    ai_interactions = relationship("AIInteraction", back_populates="user")