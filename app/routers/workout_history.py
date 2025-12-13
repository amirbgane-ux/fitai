from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.crud import crud_workout_history
from app.schemas import WorkoutHistory, WorkoutHistoryCreate
from app.routers.dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=List[WorkoutHistory])
def get_workout_history(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить историю тренировок пользователя"""
    return crud_workout_history.get_by_user_id(db, current_user.id, skip, limit)

@router.post("/", response_model=WorkoutHistory)
def create_workout_history(
    history_data: WorkoutHistoryCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Добавить запись о выполненной тренировке"""
    # Проверяем, что user_id совпадает с текущим пользователем
    if history_data.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    return crud_workout_history.create(db, history_data)

@router.delete("/clear")
def clear_workout_history(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Очистить всю историю тренировок пользователя"""
    deleted_count = crud_workout_history.delete_by_user_id(db, current_user.id)
    return {"detail": f"Удалено {deleted_count} записей истории"}