from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.crud import crud_workout_plan, crud_workout_history
from app.schemas import WorkoutPlan, WorkoutPlanResponse, WorkoutHistoryCreate
from app.schemas.workout_plan import WorkoutPlanCreateRequest
from app.routers.dependencies import get_current_user
from app.services.ai_service import generate_workout_plan

router = APIRouter()

@router.get("/", response_model=List[WorkoutPlan])
def get_user_workout_plans(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить все планы тренировок пользователя"""
    return crud_workout_plan.get_by_user_id(db, current_user.id, skip, limit)

@router.get("/{plan_id}", response_model=WorkoutPlan)
def get_workout_plan(
    plan_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить конкретный план тренировок"""
    plan = crud_workout_plan.get_by_id(db, plan_id)
    if not plan or plan.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="План тренировок не найден")
    return plan

@router.post("/", response_model=WorkoutPlanResponse)
async def create_workout_plan(
    plan_data: WorkoutPlanCreateRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создать новый план тренировок с помощью ИИ"""
    ai_plan = await generate_workout_plan(
        plan_data.user_request,
        plan_data.plan_type,
        plan_data.difficulty,
        plan_data.duration_minutes
    )
    
    plan_data_dict = {
        "user_request": plan_data.user_request,
        "plan_type": plan_data.plan_type,
        "difficulty": plan_data.difficulty,
        "duration_minutes": plan_data.duration_minutes,
        "user_id": current_user.id,
        "ai_generated_plan": ai_plan
    }
    
    return crud_workout_plan.create(db, plan_data_dict)

@router.post("/{plan_id}/complete")
def mark_plan_completed(
    plan_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отметить план тренировок как выполненный и создать запись в истории"""
    plan = crud_workout_plan.get_by_id(db, plan_id)
    if not plan or plan.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="План тренировок не найден")
    
    # Обновляем статус выполнения плана
    updated_plan = crud_workout_plan.mark_completed(db, plan_id)
    if not updated_plan:
        raise HTTPException(status_code=500, detail="Не удалось обновить статус плана")

    # Создаем запись в истории с полным планом
    history_data = WorkoutHistoryCreate(
        plan_id=plan_id,
        user_id=current_user.id,
        exercises_completed={
            "plan_id": plan_id,
            "plan_type": plan.plan_type,
            "difficulty": plan.difficulty,
            "duration_minutes": plan.duration_minutes,
            "full_plan": plan.ai_generated_plan,
            "user_request": plan.user_request,
            "created_at": plan.created_at.isoformat() if plan.created_at else None
        },
        session_duration=plan.duration_minutes or 30,
        perceived_exertion=None,
        user_feedback=None,
        notes=None
    )

    # Создаем запись в истории
    history_entry = crud_workout_history.create(db, history_data)

    if not history_entry:
        print(f"Предупреждение: Не удалось создать запись в истории для плана {plan_id}")

    return {
        "is_completed": updated_plan.is_completed,
        "history_entry": history_entry
    }

@router.delete("/{plan_id}")
def delete_workout_plan(
    plan_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удалить план тренировок"""
    plan = crud_workout_plan.get_by_id(db, plan_id)
    if not plan or plan.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="План тренировок не найден")
    
    success = crud_workout_plan.delete(db, plan_id)
    if not success:
        raise HTTPException(status_code=500, detail="Не удалось удалить план")
    
    return {"detail": "План тренировок удалён"}