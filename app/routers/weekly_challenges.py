# app/routers/weekly_challenges.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.crud import crud_weekly_challenge
from app.schemas import WeeklyChallenge, WeeklyChallengeCreate, WeeklyChallengeUpdate
from app.routers.dependencies import get_current_user
from app.services.ai_service import generate_weekly_challenge

router = APIRouter()

@router.get("/", response_model=List[WeeklyChallenge])
def get_weekly_challenges(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить все недельные испытания пользователя"""
    return crud_weekly_challenge.get_by_user_id(db, current_user.id, skip, limit)

@router.get("/current", response_model=WeeklyChallenge)
def get_current_weekly_challenge(
    week_number: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить текущее недельное испытание"""
    challenge = crud_weekly_challenge.get_current_week(db, current_user.id, week_number)
    if not challenge:
        raise HTTPException(status_code=404, detail="Испытание не найдено")
    return challenge

@router.post("/", response_model=WeeklyChallenge)
async def create_weekly_challenge(
    challenge_data: WeeklyChallengeCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создать новое недельное испытание"""
    # Собираем target_metrics из отдельных полей
    target_metrics = {}
    if challenge_data.target_reps is not None:
        target_metrics['target_reps'] = challenge_data.target_reps
    if challenge_data.target_sets is not None:
        target_metrics['target_sets'] = challenge_data.target_sets
    if challenge_data.target_duration is not None:
        target_metrics['target_duration'] = challenge_data.target_duration

    # Генерируем испытание с помощью ИИ, передавая target_metrics
    ai_challenge = await generate_weekly_challenge(
        challenge_data.challenge_type, 
        target_metrics
    )

    # Создаем словарь для БД
    challenge_dict = {
        "week_number": challenge_data.week_number,
        "challenge_type": challenge_data.challenge_type,
        "target_metrics": target_metrics if target_metrics else None,
        "user_id": current_user.id,
        "ai_generated_challenge": ai_challenge
    }
    
    return crud_weekly_challenge.create(db, challenge_dict)

@router.patch("/{challenge_id}", response_model=WeeklyChallenge)
def update_weekly_challenge(
    challenge_id: int,
    challenge_data: WeeklyChallengeUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновить статус испытания"""
    challenge = crud_weekly_challenge.get_by_id(db, challenge_id)
    if not challenge or challenge.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Испытание не найдено")
    
    return crud_weekly_challenge.update(db, challenge_id, challenge_data)

@router.delete("/{challenge_id}")
def delete_weekly_challenge(
    challenge_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удалить недельный челлендж"""
    challenge = crud_weekly_challenge.get_by_id(db, challenge_id)
    if not challenge or challenge.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Челлендж не найден")
    
    success = crud_weekly_challenge.delete(db, challenge_id)
    if not success:
        raise HTTPException(status_code=500, detail="Не удалось удалить челлендж")
    
    return {"detail": "Челлендж удалён"}

@router.patch("/{challenge_id}/complete", response_model=WeeklyChallenge)
def mark_weekly_challenge_completed(
    challenge_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отметить недельный челлендж как выполненный"""
    challenge = crud_weekly_challenge.get_by_id(db, challenge_id)
    if not challenge or challenge.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Челлендж не найден")
    
    updated_challenge = crud_weekly_challenge.mark_completed(db, challenge_id)
    if not updated_challenge:
         raise HTTPException(status_code=500, detail="Не удалось обновить статус челленджа")
    return updated_challenge