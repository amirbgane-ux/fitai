from app.schemas.user import User, UserCreate, UserUpdate, UserResponse
from app.schemas.anthropometrics import Anthropometrics, AnthropometricsCreate, AnthropometricsUpdate
from app.schemas.workout_plan import WorkoutPlan, WorkoutPlanCreateRequest, WorkoutPlanResponse # <-- Заменили WorkoutPlanCreate на WorkoutPlanCreateRequest
from app.schemas.exercise_recommendation import ExerciseRecommendation, ExerciseRecommendationCreate
from app.schemas.weekly_challenge import WeeklyChallenge, WeeklyChallengeCreate, WeeklyChallengeUpdate
from app.schemas.workout_history import WorkoutHistory, WorkoutHistoryCreate
from app.schemas.injury_prediction import InjuryPrediction, InjuryPredictionCreate
from app.schemas.ai_interaction import AIInteraction, AIInteractionCreate

__all__ = [
    "User", "UserCreate", "UserUpdate", "UserResponse",  # <-- Добавь UserUpdate, если его не было
    "Anthropometrics", "AnthropometricsCreate", "AnthropometricsUpdate",
    "WorkoutPlan", "WorkoutPlanCreateRequest", "WorkoutPlanResponse", # <-- Заменили WorkoutPlanCreate на WorkoutPlanCreateRequest
    "ExerciseRecommendation", "ExerciseRecommendationCreate",
    "WeeklyChallenge", "WeeklyChallengeCreate", "WeeklyChallengeUpdate",
    "WorkoutHistory", "WorkoutHistoryCreate",
    "InjuryPrediction", "InjuryPredictionCreate",
    "AIInteraction", "AIInteractionCreate"
]