import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_service import (
    generate_workout_plan,
    generate_exercise_recommendations,
    generate_weekly_challenge, 
    analyze_injury_risk
)

async def test_ai_services():
    """Тестируем все AI сервисы"""
    print("🔬 ТЕСТИРУЕМ AI СЕРВИСЫ...\n")
    
    # Тест генерации плана тренировок
    print("1. 📋 ТЕСТ ПЛАНОВ ТРЕНИРОВОК:")
    workout_plan = await generate_workout_plan("Хочу план для похудения для начинающих")
    print(workout_plan[:500] + "...\n")
    
    # Тест рекомендаций при травмах
    print("2. 🏥 ТЕСТ РЕКОМЕНДАЦИЙ ПРИ ТРАВМАХ:")
    recommendations = await generate_exercise_recommendations("Болит спина и колени")
    print(recommendations[:500] + "...\n")
    
    # Тест генерации испытаний
    print("3. 🏆 ТЕСТ ИСПЫТАНИЙ:")
    challenge = await generate_weekly_challenge("силовая тренировка")
    print(challenge[:500] + "...\n")
    
    # Тест анализа рисков
    print("4. ⚠️ ТЕСТ АНАЛИЗА РИСКОВ:")
    risk_analysis = await analyze_injury_risk({"exercises": ["приседания", "становая тяга"]})
    print(risk_analysis[:500] + "...\n")
    
    print("✅ ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!")

if __name__ == "__main__":
    asyncio.run(test_ai_services())