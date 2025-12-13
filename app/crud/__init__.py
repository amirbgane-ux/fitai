from app.crud.crud_user import crud_user
from app.crud.crud_anthropometrics import crud_anthropometrics
from app.crud.crud_workout_plan import crud_workout_plan
from app.crud.crud_exercise_recommendation import crud_exercise_recommendation
from app.crud.crud_weekly_challenge import crud_weekly_challenge
from app.crud.crud_workout_history import crud_workout_history
from app.crud.crud_injury_prediction import crud_injury_prediction
from app.crud.crud_ai_interaction import crud_ai_interaction

__all__ = [
    "crud_user",
    "crud_anthropometrics", 
    "crud_workout_plan",
    "crud_exercise_recommendation",
    "crud_weekly_challenge",
    "crud_workout_history",
    "crud_injury_prediction",
    "crud_ai_interaction"
]