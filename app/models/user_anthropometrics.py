from sqlalchemy import Column, Integer, String, Numeric, TIMESTAMP, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class UserAnthropometrics(Base):
    __tablename__ = "user_anthropometrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    height_cm = Column(Integer, nullable=False)
    weight_kg = Column(Numeric(5, 2), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)
    injuries = Column(Text)
    fitness_goals = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Обратная связь
    user = relationship("User", back_populates="anthropometrics")