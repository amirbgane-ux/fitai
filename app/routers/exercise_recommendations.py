# app/routers/exercise_recommendations.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.crud import crud_exercise_recommendation
from app.schemas import ExerciseRecommendation, ExerciseRecommendationCreate
# --- ИЗМЕНЕНО: Импорт правильной зависимости ---
from app.routers.dependencies import get_current_user
# --- /ИЗМЕНЕНО ---
from app.services.ai_service import generate_exercise_recommendations

router = APIRouter()

@router.get("/", response_model=List[ExerciseRecommendation])
def get_exercise_recommendations(
    skip: int = 0,
    limit: int = 100,
    # --- ИЗМЕНЕНО: Используем правильную зависимость ---
    current_user = Depends(get_current_user),
    # --- /ИЗМЕНЕНО ---
    db: Session = Depends(get_db)
):
    """Получить все рекомендации по упражнениям"""
    return crud_exercise_recommendation.get_by_user_id(db, current_user.id, skip, limit)

@router.post("/", response_model=ExerciseRecommendation)
async def create_exercise_recommendation(
    recommendation_data: ExerciseRecommendationCreate,
    # --- ИЗМЕНЕНО: Используем правильную зависимость ---
    current_user = Depends(get_current_user),
    # --- /ИЗМЕНЕНО ---
    db: Session = Depends(get_db)
):
    """Получить рекомендации по упражнениям при ограничениях"""
    # --- ИЗМЕНЕНО: Объединяем ограничения и тип в один запрос для ИИ ---
    # Это позволяет ИИ учитывать тип ограничений при генерации
    combined_request = f"Тип ограничений: {recommendation_data.limitations_type}. Описание: {recommendation_data.user_limitations}"
    # --- /ИЗМЕНЕНО ---

    # Генерируем рекомендации с помощью ИИ, передавая объединённый запрос
    ai_recommendations = await generate_exercise_recommendations(combined_request) # <-- Передаём combined_request
    
    # Создаем словарь для БД
    recommendation_dict = {
        "user_limitations": recommendation_data.user_limitations,
        "limitations_type": recommendation_data.limitations_type, # <-- Сохраняем отдельно
        "user_id": current_user.id,
        "ai_recommended_exercises": ai_recommendations
    }
    
    return crud_exercise_recommendation.create(db, recommendation_dict)
# --- НОВОЕ: Роут для удаления рекомендации ---
@router.delete("/{recommendation_id}")
def delete_exercise_recommendation(
    recommendation_id: int,
    current_user = Depends(get_current_user), # <-- Используем правильную зависимость
    db: Session = Depends(get_db)
):
    """Удалить рекомендацию упражнений"""
    recommendation = crud_exercise_recommendation.get_by_id(db, recommendation_id)
    if not recommendation or recommendation.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Рекомендация не найдена")
    
    success = crud_exercise_recommendation.delete(db, recommendation_id)
    if not success:
        raise HTTPException(status_code=500, detail="Не удалось удалить рекомендацию")
    
    return {"detail": "Рекомендация удалена"}
# --- /НОВОЕ ---