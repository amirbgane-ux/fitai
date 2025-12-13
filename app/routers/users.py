# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import crud_user, crud_anthropometrics
from app.schemas import User, UserCreate, UserUpdate, Anthropometrics, AnthropometricsCreate, AnthropometricsUpdate
# --- ИЗМЕНЕНО: Импорт правильной зависимости ---
from app.routers.dependencies import get_current_user
# --- /ИЗМЕНЕНО ---
from app.models.user_anthropometrics import UserAnthropometrics

router = APIRouter()

# 📋 ПОЛЬЗОВАТЕЛИ

@router.get("/me", response_model=User)
def get_current_user_profile(
    # --- ИЗМЕНЕНО: Используем правильную зависимость ---
    current_user: User = Depends(get_current_user)
    # --- /ИЗМЕНЕНО ---
):
    """Получить данные текущего пользователя"""
    return current_user

@router.put("/me", response_model=User)
def update_current_user(
    user_data: UserUpdate,
    # --- ИЗМЕНЕНО: Используем правильную зависимость ---
    current_user: User = Depends(get_current_user),
    # --- /ИЗМЕНЕНО ---
    db: Session = Depends(get_db)
):
    """Обновить данные текущего пользователя"""
    updated_user = crud_user.update(db, current_user.id, user_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return updated_user

# 📏 АНТРОПОМЕТРИЯ

@router.get("/me/anthropometrics", response_model=Anthropometrics)
def get_user_anthropometrics(
    # --- ИЗМЕНЕНО: Используем правильную зависимость ---
    current_user: User = Depends(get_current_user),
    # --- /ИЗМЕНЕНО ---
    db: Session = Depends(get_db)
):
    """Получить антропометрические данные пользователя"""
    anthropometrics = crud_anthropometrics.get_by_user_id(db, current_user.id)
    if not anthropometrics:
        raise HTTPException(status_code=404, detail="Антропометрические данные не найдены")
    return anthropometrics

@router.post("/me/anthropometrics", response_model=Anthropometrics)
def create_anthropometrics(
    anthropometrics_data: AnthropometricsCreate,
    # --- ИЗМЕНЕНО: Используем правильную зависимость ---
    current_user: User = Depends(get_current_user),
    # --- /ИЗМЕНЕНО ---
    db: Session = Depends(get_db)
):
    """Создать антропометрические данные"""
    # Проверяем есть ли уже антропометрия у пользователя
    existing = crud_anthropometrics.get_by_user_id(db, current_user.id)
    
    if existing:
        # Если есть - обновляем существующую запись
        return crud_anthropometrics.update(db, existing.id, anthropometrics_data)
    else:
        # Создаем новую запись напрямую в базу
        data_dict = {
            "height_cm": anthropometrics_data.height_cm,
            "weight_kg": anthropometrics_data.weight_kg,
            "age": anthropometrics_data.age,
            "gender": anthropometrics_data.gender,
            "user_id": current_user.id
        }
        db_anthropometrics = UserAnthropometrics(**data_dict)
        db.add(db_anthropometrics)
        db.commit()
        db.refresh(db_anthropometrics)
        return db_anthropometrics

@router.put("/me/anthropometrics", response_model=Anthropometrics)
def update_user_anthropometrics(
    anthropometrics_data: AnthropometricsUpdate,
    # --- ИЗМЕНЕНО: Используем правильную зависимость ---
    current_user: User = Depends(get_current_user),
    # --- /ИЗМЕНЕНО ---
    db: Session = Depends(get_db)
):
    """Обновить антропометрические данные"""
    # Получаем существующую запись
    existing = crud_anthropometrics.get_by_user_id(db, current_user.id)
    if not existing:
        raise HTTPException(status_code=404, detail="Антропометрические данные не найдены")
    
    # Обновляем данные
    updated = crud_anthropometrics.update(db, existing.id, anthropometrics_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Ошибка при обновлении данных")
    return updated