import requests
import json
import asyncio
import aiohttp

BASE_URL = "http://127.0.0.1:8000"

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"🔹 {message}")

async def test_basic_endpoints():
    print_info("ТЕСТИРУЕМ БАЗОВЫЕ ENDPOINTS...")
    
    try:
        # Тест главной страницы
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print_success(f"GET / - {response.json()}")
        else:
            print_error(f"GET / - Status: {response.status_code}")
        
        # Тест health check
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print_success(f"GET /health - {response.json()}")
        else:
            print_error(f"GET /health - Status: {response.status_code}")
            
    except Exception as e:
        print_error(f"Basic endpoints: {e}")

async def test_user_endpoints():
    print_info("\n👤 ТЕСТИРУЕМ ПОЛЬЗОВАТЕЛЬСКИЕ ENDPOINTS...")
    
    try:
        # Регистрация пользователя
        user_data = {
            "email": "test_user@example.com",
            "username": "testuser",
            "fitness_level": "beginner"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        if response.status_code == 200:
            user = response.json()
            print_success(f"POST /auth/register - Создан пользователь: {user['username']}")
        else:
            print_error(f"POST /auth/register - Status: {response.status_code}, Error: {response.text}")
        
        # Получение профиля
        response = requests.get(f"{BASE_URL}/users/me")
        if response.status_code == 200:
            user = response.json()
            print_success(f"GET /users/me - Получен профиль: {user['username']}")
        else:
            print_error(f"GET /users/me - Status: {response.status_code}")
            
    except Exception as e:
        print_error(f"User endpoints: {e}")

async def test_workout_plan_endpoints():
    print_info("\n💪 ТЕСТИРУЕМ ПЛАНЫ ТРЕНИРОВОК...")
    
    try:
        # Создание плана тренировок
        plan_data = {
            "user_request": "Хочу план тренировок для похудения для начинающих",
            "plan_type": "cardio",
            "difficulty": "easy",
            "duration_minutes": 30
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{BASE_URL}/workout-plans/", json=plan_data) as response:
                if response.status == 200:
                    result = await response.json()
                    print_success(f"POST /workout-plans/ - Создан план: {result['plan_type']}")
                    print_info(f"   ИИ ответ: {result['ai_generated_plan'][:100]}...")
                    
                    # Получение всех планов
                    async with session.get(f"{BASE_URL}/workout-plans/") as get_response:
                        if get_response.status == 200:
                            plans = await get_response.json()
                            print_success(f"GET /workout-plans/ - Найдено планов: {len(plans)}")
                        else:
                            print_error(f"GET /workout-plans/ - Status: {get_response.status}")
                            
                else:
                    error_text = await response.text()
                    print_error(f"POST /workout-plans/ - Status: {response.status}, Error: {error_text}")
                    
    except Exception as e:
        print_error(f"Workout plan endpoints: {e}")

async def test_exercise_recommendations():
    print_info("\n🏥 ТЕСТИРУЕМ РЕКОМЕНДАЦИИ ПРИ ТРАВМАХ...")
    
    try:
        recommendation_data = {
            "user_limitations": "Болит спина и колени, нужно безопасные упражнения",
            "limitations_type": "back_pain"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{BASE_URL}/exercise-recommendations/", json=recommendation_data) as response:
                if response.status == 200:
                    result = await response.json()
                    print_success(f"POST /exercise-recommendations/ - Получены рекомендации: {result['limitations_type']}")
                    print_info(f"   ИИ ответ: {result['ai_recommended_exercises'][:100]}...")
                    
                    # Получение всех рекомендаций
                    async with session.get(f"{BASE_URL}/exercise-recommendations/") as get_response:
                        if get_response.status == 200:
                            recommendations = await get_response.json()
                            print_success(f"GET /exercise-recommendations/ - Найдено рекомендаций: {len(recommendations)}")
                        else:
                            print_error(f"GET /exercise-recommendations/ - Status: {get_response.status}")
                            
                else:
                    error_text = await response.text()
                    print_error(f"POST /exercise-recommendations/ - Status: {response.status}, Error: {error_text}")
                    
    except Exception as e:
        print_error(f"Exercise recommendations: {e}")

async def test_weekly_challenges():
    print_info("\n🏆 ТЕСТИРУЕМ НЕДЕЛЬНЫЕ ИСПЫТАНИЯ...")
    
    try:
        challenge_data = {
            "week_number": 1,
            "challenge_type": "strength",
            "target_metrics": {"target_reps": 100, "target_sets": 5}
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{BASE_URL}/weekly-challenges/", json=challenge_data) as response:
                if response.status == 200:
                    result = await response.json()
                    print_success(f"POST /weekly-challenges/ - Создано испытание: {result['challenge_type']}")
                    print_info(f"   ИИ ответ: {result['ai_generated_challenge'][:100]}...")
                    
                    # Получение всех испытаний
                    async with session.get(f"{BASE_URL}/weekly-challenges/") as get_response:
                        if get_response.status == 200:
                            challenges = await get_response.json()
                            print_success(f"GET /weekly-challenges/ - Найдено испытаний: {len(challenges)}")
                        else:
                            print_error(f"GET /weekly-challenges/ - Status: {get_response.status}")
                            
                else:
                    error_text = await response.text()
                    print_error(f"POST /weekly-challenges/ - Status: {response.status}, Error: {error_text}")
                    
    except Exception as e:
        print_error(f"Weekly challenges: {e}")

async def test_workout_history():
    print_info("\n📊 ТЕСТИРУЕМ ИСТОРИЮ ТРЕНИРОВОК...")
    
    try:
        history_data = {
            "plan_id": 1,
            "exercises_completed": {
                "pushups": {"sets": 3, "reps": 15, "completed": True},
                "squats": {"sets": 3, "reps": 12, "completed": True}
            },
            "session_duration": 45,
            "perceived_exertion": 7,
            "user_feedback": "Хорошая тренировка!",
            "notes": "Чувствовал усталость в конце"
        }
        
        response = requests.post(f"{BASE_URL}/workout-history/", json=history_data)
        if response.status_code == 200:
            result = response.json()
            print_success(f"POST /workout-history/ - Добавлена запись тренировки")
            print_info(f"   Длительность: {result['session_duration']} мин")
            
            # Получение истории
            response = requests.get(f"{BASE_URL}/workout-history/")
            if response.status_code == 200:
                history = response.json()
                print_success(f"GET /workout-history/ - Найдено записей: {len(history)}")
            else:
                print_error(f"GET /workout-history/ - Status: {response.status_code}")
                
        else:
            print_error(f"POST /workout-history/ - Status: {response.status_code}, Error: {response.text}")
            
    except Exception as e:
        print_error(f"Workout history: {e}")

async def test_injury_predictions():
    print_info("\n⚠️ ТЕСТИРУЕМ ПРОГНОЗ ТРАВМ...")
    
    try:
        prediction_data = {
            "workout_plan_id": 1,
            "exercises_analyzed": {
                "exercises": ["приседания", "становая тяга", "жим лежа"],
                "intensity": "high",
                "frequency": "3 times per week"
            },
            "risk_factors": {"overload": True, "recovery": "insufficient"}
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{BASE_URL}/injury-predictions/", json=prediction_data) as response:
                if response.status == 200:
                    result = await response.json()
                    print_success(f"POST /injury-predictions/ - Получен прогноз")
                    print_info(f"   Уровень риска: {result.get('risk_level', 'N/A')}")
                    print_info(f"   ИИ ответ: {result['ai_risk_prediction'][:100]}...")
                    
                    # Получение всех прогнозов
                    async with session.get(f"{BASE_URL}/injury-predictions/") as get_response:
                        if get_response.status == 200:
                            predictions = await get_response.json()
                            print_success(f"GET /injury-predictions/ - Найдено прогнозов: {len(predictions)}")
                        else:
                            print_error(f"GET /injury-predictions/ - Status: {get_response.status}")
                            
                else:
                    error_text = await response.text()
                    print_error(f"POST /injury-predictions/ - Status: {response.status}, Error: {error_text}")
                    
    except Exception as e:
        print_error(f"Injury predictions: {e}")

async def run_all_tests():
    print("🎯 ЗАПУСКАЕМ ПОЛНОЕ ТЕСТИРОВАНИЕ API...")
    print("=" * 50)
    
    await test_basic_endpoints()
    await test_user_endpoints()
    await test_workout_plan_endpoints()
    await test_exercise_recommendations()
    await test_weekly_challenges()
    await test_workout_history()
    await test_injury_predictions()
    
    print("\n" + "=" * 50)
    print("🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")

if __name__ == "__main__":
    asyncio.run(run_all_tests())