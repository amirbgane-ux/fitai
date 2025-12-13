from app.models.user import User
from app.models.user_anthropometrics import UserAnthropometrics
from app.models.workout_plan import WorkoutPlan
from app.models.exercise_recommendation import ExerciseRecommendation
from app.models.weekly_challenge import WeeklyChallenge
from app.models.workout_history import WorkoutHistory
from app.models.injury_prediction import InjuryPrediction
from app.models.ai_interaction import AIInteraction

__all__ = [
    "User",
    "UserAnthropometrics", 
    "WorkoutPlan",
    "ExerciseRecommendation",
    "WeeklyChallenge",
    "WorkoutHistory",
    "InjuryPrediction",
    "AIInteraction"
]