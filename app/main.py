from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, auth, workout_plans, exercise_recommendations, weekly_challenges, workout_history, injury_predictions
from app.database import engine
from app.models import user, user_anthropometrics, workout_plan, exercise_recommendation, weekly_challenge, workout_history as workout_history_model, injury_prediction, ai_interaction

# Создаем таблицы в БД
user.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Fitness App API", 
    description="API для фитнес-приложения с ИИ",
    version="1.0.0"
)

# ============ ОБНОВЛЕННЫЕ CORS НАСТРОЙКИ ============
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Локальная разработка
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        
        # Telegram Web App через ngrok (ТЕКУЩИЙ ДОМЕН)
        "https://supersagacious-caden-superluxurious.ngrok-free.dev",
        
        # Telegram Web App основной домен
        "https://web.telegram.org",

         # Netlify frontend
        "https://sparkly-choux-12aad6.netlify.app",
        
       
    ],
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Добавьте эту строку!
)
# ===================================================

# Подключаем роутеры
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(workout_plans.router, prefix="/workout-plans", tags=["workout-plans"])
app.include_router(exercise_recommendations.router, prefix="/exercise-recommendations", tags=["exercise-recommendations"])
app.include_router(weekly_challenges.router, prefix="/weekly-challenges", tags=["weekly-challenges"])
app.include_router(workout_history.router, prefix="/workout-history", tags=["workout-history"])
app.include_router(injury_predictions.router, prefix="/injury-predictions", tags=["injury-predictions"])

@app.get("/")
async def root():
    return {"message": "Fitness App API работает!"}

@app.get("/health") 
async def health_check():
    return {"status": "healthy"}