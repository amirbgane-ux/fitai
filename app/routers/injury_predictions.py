# app/routers/injury_predictions.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.crud import crud_injury_prediction, crud_workout_plan
from app.schemas import InjuryPrediction, InjuryPredictionCreate
from app.routers.dependencies import get_current_user
from app.services.ai_service import analyze_injury_risk
import json
import re

router = APIRouter()


def extract_risk_level_from_ai_response(ai_response: str) -> str:
    """
    ТОЧНО извлекает уровень риска из ответа ИИ
    Возвращает: 'high', 'medium', или 'low'
    """
    if not ai_response:
        return "medium"
    
    # Приводим к нижнему регистру для поиска
    text_lower = ai_response.lower()
    
    print("\n" + "="*80)
    print("ИЗВЛЕЧЕНИЕ УРОВНЯ РИСКА ИЗ ОТВЕТА ИИ")
    print("="*80)
    print(f"Первые 500 символов ответа:\n{text_lower[:500]}")
    
    # Вариант 1: Ищем "1. Уровень риска: Высокий" (самый распространенный формат)
    # Ищем различные варианты написания
    patterns = [
        # Формат с цифрами: 1. Уровень риска: Высокий
        (r'1\.\s*[уу]ровень\s+[рp]иска\s*[:\-]\s*(низкий|средний|высокий)', 'цифра+уровень риска'),
        
        # Формат: ### 1. Уровень риска: Высокий
        (r'#+\s*1\.\s*[уу]ровень\s+[рp]иска\s*[:\-]\s*(низкий|средний|высокий)', '###+уровень риска'),
        
        # Формат: Уровень риска: Высокий
        (r'[уу]ровень\s+[рp]иска\s*[:\-]\s*(низкий|средний|высокий)', 'уровень риска:'),
        
        # Формат: Риск: Высокий
        (r'[рp]иск\s*[:\-]\s*(низкий|средний|высокий)', 'риск:'),
        
        # Формат: **Уровень риска:** Высокий
        (r'\*\*[уу]ровень\s+[рp]иска:\*\*\s*(низкий|средний|высокий)', '**уровень риска:**'),
        
        # Просто слово "Высокий" в контексте риска
        (r'(?:риск|опасность|уровень)\s+—\s*(низкий|средний|высокий)', 'риск —'),
        
        # Для английского, если ИИ иногда отвечает на английском
        (r'1\.\s*risk\s+level\s*[:\-]\s*(low|medium|high)', 'risk level'),
        (r'risk\s+level\s*[:\-]\s*(low|medium|high)', 'risk level:'),
    ]
    
    for pattern, pattern_name in patterns:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            risk_word = match.group(1).lower()
            print(f"✓ Найден уровень риска: '{risk_word}' (паттерн: {pattern_name})")
            
            # Русские варианты
            if risk_word in ['низкий', 'low']:
                return 'low'
            elif risk_word in ['средний', 'medium']:
                return 'medium'
            elif risk_word in ['высокий', 'high']:
                return 'high'
    
    # Вариант 2: Поиск ключевых слов в начале ответа
    # Часто ИИ пишет уровень риска в начале раздела
    lines = text_lower.split('\n')
    
    for i, line in enumerate(lines[:10]):  # Проверяем первые 10 строк
        line = line.strip()
        print(f"Строка {i}: {line[:100]}")
        
        # Прямой поиск в строке
        if 'высокий' in line and any(word in line for word in ['риск', 'уровень', 'опасность']):
            print(f"✓ Прямой поиск: найдено 'высокий' в строке {i}")
            return 'high'
        elif 'средний' in line and any(word in line for word in ['риск', 'уровень']):
            print(f"✓ Прямой поиск: найдено 'средний' в строке {i}")
            return 'medium'
        elif 'низкий' in line and any(word in line for word in ['риск', 'уровень']):
            print(f"✓ Прямой поиск: найдено 'низкий' в строке {i}")
            return 'low'
    
    # Вариант 3: Подсчет упоминаний
    high_count = text_lower.count('высокий') + text_lower.count('high')
    medium_count = text_lower.count('средний') + text_lower.count('medium')
    low_count = text_lower.count('низкий') + text_lower.count('low')
    
    print(f"\nПодсчет упоминаний:")
    print(f"  Высокий/high: {high_count}")
    print(f"  Средний/medium: {medium_count}")
    print(f"  Низкий/low: {low_count}")
    
    if high_count > medium_count and high_count > low_count:
        print("✓ По подсчету: ВЫСОКИЙ риск")
        return 'high'
    elif medium_count > high_count and medium_count > low_count:
        print("✓ По подсчету: СРЕДНИЙ риск")
        return 'medium'
    elif low_count > high_count and low_count > medium_count:
        print("✓ По подсчету: НИЗКИЙ риск")
        return 'low'
    
    # Вариант 4: Поиск по ключевым фразам
    if any(phrase in text_lower for phrase in [
        'риск высокий', 'высокий риск', 'опасность высокая',
        'high risk', 'risk is high'
    ]):
        print("✓ По ключевым фразам: ВЫСОКИЙ риск")
        return 'high'
    
    # По умолчанию, если ничего не найдено
    print("⚠ Уровень риска не найден точно, используем СРЕДНИЙ по умолчанию")
    print("="*80)
    return 'medium'


def extract_recommendations_from_ai_response(ai_response: str) -> Optional[str]:
    """Извлекает рекомендации из ответа ИИ"""
    if not ai_response:
        return None
    
    # Ищем разделы с рекомендациями
    lines = ai_response.split('\n')
    recommendations_start = -1
    
    # Ищем начало рекомендаций
    keywords = ['рекомендации:', 'советы:', 'советы по снижению риска:', 
                'рекомендации по снижению риска:', 'что делать:', 'как снизить риск:']
    
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        if any(keyword in line_lower for keyword in keywords):
            recommendations_start = i
            break
    
    # Если нашли начало рекомендаций, извлекаем их
    if recommendations_start != -1:
        recommendations_lines = lines[recommendations_start:]
        # Объединяем следующие строки (до следующего заголовка или конца)
        result_lines = []
        for line in recommendations_lines[1:10]:  # Берем до 10 строк после заголовка
            line_stripped = line.strip()
            if line_stripped and not line_stripped.startswith(('#', '**', '###', '---', '==')):
                result_lines.append(line_stripped)
            elif result_lines and line_stripped.startswith(('#', '**', '###')):  # Новый раздел
                break
        
        if result_lines:
            return '\n'.join(result_lines)
    
    return None


def get_workout_plan_name(db: Session, plan_id: int) -> Optional[str]:
    """Получает название плана тренировки на русском"""
    plan = crud_workout_plan.get_by_id(db, plan_id)
    if not plan:
        return None
    
    # Форматируем название плана на русском
    plan_type_translation = {
        'strength': 'Силовая',
        'cardio': 'Кардио',
        'flexibility': 'Гибкость',
        'hiit': 'ВИИТ',
        'recovery': 'Восстановление'
    }
    plan_type = plan_type_translation.get(plan.plan_type, plan.plan_type)
    return f"{plan_type} - {plan.duration_minutes} мин"


@router.get("/", response_model=List[InjuryPrediction])
def get_injury_predictions(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить историю анализа рисков травм для текущего пользователя"""
    predictions = crud_injury_prediction.get_by_user_id(db, current_user.id, skip, limit)
    
    # Добавляем информацию о плане тренировок к каждому прогнозу
    for prediction in predictions:
        if prediction.workout_plan_id:
            plan_name = get_workout_plan_name(db, prediction.workout_plan_id)
            if plan_name:
                prediction.workout_plan_name = plan_name
    
    return predictions


@router.post("/", response_model=InjuryPrediction)
async def create_injury_prediction(
    prediction_data: InjuryPredictionCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Проанализировать риск травмы для плана тренировок или пользовательских упражнений"""
    
    # Проверяем, что есть хотя бы один источник данных
    if not prediction_data.workout_plan_id and not prediction_data.exercises_analyzed:
        raise HTTPException(
            status_code=400, 
            detail="Укажите либо план тренировки, либо опишите упражнения для анализа"
        )
    
    exercises_to_analyze = {}
    
    # Если указан workout_plan_id - получаем план для анализа
    if prediction_data.workout_plan_id:
        plan = crud_workout_plan.get_by_id(db, prediction_data.workout_plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="План тренировки не найден")
        
        # Проверяем доступ пользователя к плану
        if plan.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Нет доступа к этому плану тренировки")
        
        # Форматируем данные плана для анализа
        if isinstance(plan.ai_generated_plan, str):
            try:
                plan_data = json.loads(plan.ai_generated_plan)
                exercises_to_analyze["plan_exercises"] = plan_data
            except:
                exercises_to_analyze["plan_exercises"] = plan.ai_generated_plan
        else:
            exercises_to_analyze["plan_exercises"] = plan.ai_generated_plan
    
    # Добавляем пользовательские упражнения (если есть)
    if prediction_data.exercises_analyzed:
        exercises_to_analyze["user_exercises"] = prediction_data.exercises_analyzed
    
    # Добавляем факторы риска
    if prediction_data.risk_factors:
        exercises_to_analyze["user_risk_factors"] = prediction_data.risk_factors
    
    try:
        # Анализируем риск с помощью ИИ
        print("\n" + "="*80)
        print("ЗАПРОС К ИИ ДЛЯ АНАЛИЗА РИСКА")
        print("="*80)
        print(f"Данные для анализа: {exercises_to_analyze}")
        
        ai_result = await analyze_injury_risk(exercises_to_analyze)
        
        print("\n" + "="*80)
        print("ОТВЕТ ОТ ИИ")
        print("="*80)
        print(f"Ответ (первые 1000 символов): {ai_result[:1000]}...")
        
        # Извлекаем уровень риска из ответа ИИ
        risk_level = extract_risk_level_from_ai_response(ai_result)
        
        print(f"\nИтоговый уровень риска: {risk_level}")
        
        # Извлекаем рекомендации из ответа ИИ
        recommendations = extract_recommendations_from_ai_response(ai_result)
        
    except Exception as e:
        print(f"Ошибка при анализе ИИ: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка при анализе ИИ: {str(e)}")
    
    # Создаем запись в базе данных
    db_data = {
        "user_id": current_user.id,
        "workout_plan_id": prediction_data.workout_plan_id,
        "exercises_analyzed": prediction_data.exercises_analyzed or "",
        "risk_factors": prediction_data.risk_factors or "",
        "ai_risk_prediction": ai_result,
        "risk_level": risk_level,
        "recommendations": recommendations,
    }
    
    # Создаем прогноз в БД
    db_prediction = crud_injury_prediction.create(db, db_data)
    
    # Добавляем вычисляемое поле workout_plan_name для ответа
    if prediction_data.workout_plan_id:
        plan_name = get_workout_plan_name(db, prediction_data.workout_plan_id)
        if plan_name:
            db_prediction.workout_plan_name = plan_name
    
    return db_prediction


@router.delete("/{prediction_id}")
def delete_injury_prediction(
    prediction_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удалить прогноз риска травмы"""
    prediction = crud_injury_prediction.get_by_id(db, prediction_id)
    if not prediction or prediction.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Прогноз не найден")
    
    success = crud_injury_prediction.delete(db, prediction_id)
    if not success:
        raise HTTPException(status_code=500, detail="Не удалось удалить прогноз")
    
    return {"detail": "Прогноз удален"}