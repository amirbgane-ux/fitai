# app/services/ai_service.py
import os
import httpx
from typing import Dict, Any
import json
import logging
from datetime import datetime, date
from app.config import settings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_service.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.daily_usage = 0.0
        self.daily_budget_rub = 100.0  # Дневной лимит 100 рублей
        self.last_reset_date = date.today()

        # Список моделей для фолбэка
        self.model_list = [
            "amazon/nova-2-lite-v1:free",
            "deepseek/deepseek-chat-v3.1",
            "qwen/qwen3-235b-a22b-thinking-2507",
            "deepseek/deepseek-chat-v3-0324",
            "nex-agi/deepseek-v3.1-nex-n1:free",
            
        ]
        
    def _check_and_reset_daily_usage(self):
        """Проверяет и сбрасывает дневной счетчик если сменилась дата"""
        today = date.today()
        if today != self.last_reset_date:
            logger.info(f"Сброс дневного использования. Было: {self.daily_usage} руб.")
            self.daily_usage = 0.0
            self.last_reset_date = today
    
    def _calculate_estimated_cost(self, prompt: str, response: str = "") -> float:
        """
        Расчет примерной стоимости запроса
        """
        # Упрощенный расчет для демо-целей
        input_chars = len(prompt)
        output_chars = len(response) if response else 1000
        
        # Примерная оценка: 1 токен ≈ 2 символа на русском
        input_tokens = input_chars / 2
        output_tokens = output_chars / 2
        
        # Условная стоимость (для бесплатных моделей можно поставить 0.0)
        input_cost = (input_tokens / 1_000_000) * 0.14
        output_cost = (output_tokens / 1_000_000) * 0.28
        
        total_cost_usd = input_cost + output_cost
        
        # Конвертация в рубли
        exchange_rate = 90.0
        total_cost_rub = total_cost_usd * exchange_rate
        
        return total_cost_rub
    
    async def _make_ai_request(self, prompt: str, max_tokens: int = 4000) -> str:
        """
        Базовый метод для запросов к OpenRouter API с контролем бюджета и фолбэком
        """
        # Проверяем и сбрасываем дневной счетчик если нужно
        self._check_and_reset_daily_usage()
        
        # Если API ключ не установлен - возвращаем демо-данные
        if not self.api_key:
            logger.warning("OpenRouter API ключ не установлен, используем демо-режим")
            return self._get_demo_response(prompt)
        
        # Проверяем дневной лимит
        estimated_cost = self._calculate_estimated_cost(prompt)
        if self.daily_usage + estimated_cost > self.daily_budget_rub:
            logger.warning(f"Дневной лимит превышен. Использовано: {self.daily_usage:.4f} руб., Лимит: {self.daily_budget_rub} руб.")
            return "Дневной лимит запросов исчерпан. Попробуйте завтра или обратитесь к администратору."

        # Цикл по списку моделей
        for model_name in self.model_list:
            try:
                logger.info(f"Попытка запроса к модели: {model_name}")
                response_content = await self._make_single_request(prompt, max_tokens, model_name)
                
                # Если запрос удался, возвращаем результат
                actual_cost = self._calculate_estimated_cost(prompt, response_content)
                self.daily_usage += actual_cost
                logger.info(
                    f"Успешный ответ от модели {model_name}. "
                    f"Условная стоимость: {actual_cost:.4f} руб., "
                    f"дневной итог: {self.daily_usage:.4f} руб."
                )
                return response_content

            except httpx.TimeoutException:
                logger.warning(f"Таймаут запроса к модели {model_name}")
                continue
            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code
                if status_code == 429 or 500 <= status_code < 600:
                    logger.warning(f"HTTP ошибка от модели {model_name}: {status_code}")
                    continue
                else:
                    logger.warning(f"HTTP ошибка от модели {model_name}: {status_code}")
                    continue
            except Exception as e:
                logger.warning(f"Ошибка при запросе к модели {model_name}: {e}")
                continue

        # Если все модели не сработали
        logger.error("Все попытки запросов к моделям OpenRouter не увенчались успехом. Используем демо-режим.")
        return self._get_demo_response(prompt)
    
    async def _make_single_request(self, prompt: str, max_tokens: int, model_name: str) -> str:
        """Выполняет один запрос к указанной модели."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "FitAI App"
        }

        data = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }

        async with httpx.AsyncClient() as client:
            logger.info(f"Отправка запроса к OpenRouter API. Модель: {model_name}. Длина промпта: {len(prompt)} символов")
            response = await client.post(self.base_url, headers=headers, json=data, timeout=30.0)
            response.raise_for_status()
            result = response.json()

            usage = result.get('usage', {})
            prompt_tokens = usage.get('prompt_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)
            total_tokens = usage.get('total_tokens', 0)

            logger.info(
                f"OpenRouter API (модель {model_name}): использовано токенов - {total_tokens} "
                f"(вход: {prompt_tokens}, выход: {completion_tokens})"
            )

            return result["choices"][0]["message"]["content"]

    def get_usage_statistics(self) -> Dict[str, Any]:
        """Возвращает статистику использования"""
        return {
            "daily_usage_rub": round(self.daily_usage, 4),
            "daily_budget_rub": self.daily_budget_rub,
            "remaining_budget_rub": round(self.daily_budget_rub - self.daily_usage, 4),
            "last_reset_date": self.last_reset_date.isoformat(),
            "percentage_used": round((self.daily_usage / self.daily_budget_rub) * 100, 2)
        }
    
    def set_daily_budget(self, budget_rub: float):
        """Установка дневного бюджета"""
        self.daily_budget_rub = budget_rub
        logger.info(f"Установлен дневной бюджет: {budget_rub} руб.")
    
    def _get_demo_response(self, prompt: str) -> str:
        """
        Демо-ответы когда нет API ключа или при ошибках
        """
        prompt_lower = prompt.lower()
        
        # Проверяем, что это запрос на генерацию челленджа
        if any(phrase in prompt_lower for phrase in [
            "челлендж", "испытание", "challenge", "недельное", "выносливость",
            "сила", "техника", "consistency", "недельный"
        ]):
            logger.info("Использован демо-режим: генерация челленджа")
            return self._get_demo_challenge(prompt)
        elif any(phrase in prompt_lower for phrase in [
            "анализ риска травм", "анализ риска", "риск травм", 
            "травмоопасность", "опасность травм"
        ]):
            logger.info("Использован демо-режим: анализ риска травм")
            return self._get_demo_injury_prediction(prompt)
        elif any(word in prompt_lower for word in ["травм", "болит", "травма", "ограничен"]):
            logger.info("Использован демо-режим: рекомендации при травмах")
            return self._get_demo_recommendations(prompt)
        elif "план тренировок" in prompt_lower or "workout" in prompt_lower:
            logger.info("Использован демо-режим: план тренировок")
            return self._get_demo_workout_plan(prompt)
        else:
            logger.info("Использован демо-режим: общий ответ")
            return "Я - ИИ помощник для фитнеса. Задайте вопрос о тренировках, питании или здоровье."

    def _get_demo_workout_plan(self, prompt: str) -> str:
        """Демо-план тренировок"""
        return """ПЛАН ТРЕНИРОВКИ ДЛЯ НАЧИНАЮЩИХ..."""

    def _get_demo_recommendations(self, prompt: str) -> str:
        """Демо-рекомендации при травмах"""
        return """РЕКОМЕНДАЦИИ ПРИ ТРАВМАХ СПИНЫ И КОЛЕНЕЙ..."""

    def _get_demo_challenge(self, prompt: str) -> str:
        """Демо-испытание с учетом метрик из промпта"""
        # Извлекаем метрики из промпта для демо-ответа
        target_reps = "100"
        target_sets = "5"
        target_duration = "30"
        
        # Пытаемся извлечь из промпта
        if "target_reps" in prompt.lower():
            # Простая логика извлечения
            import re
            reps_match = re.search(r'target_reps[^\d]*(\d+)', prompt)
            if reps_match:
                target_reps = reps_match.group(1)
        
        if "target_sets" in prompt.lower():
            sets_match = re.search(r'target_sets[^\d]*(\d+)', prompt)
            if sets_match:
                target_sets = sets_match.group(1)
        
        if "target_duration" in prompt.lower():
            duration_match = re.search(r'target_duration[^\d]*(\d+)', prompt)
            if duration_match:
                target_duration = duration_match.group(1)
        
        return f"""
НЕДЕЛЬНОЕ ИСПЫТАНИЕ: "СИЛА ВОЛИ"

ЦЕЛЬ: Выполнить {target_reps} повторений за {target_sets} подходов, суммарно {target_duration} минут тренировок в неделю

ПЛАН НА НЕДЕЛЮ:
Понедельник: {int(int(target_reps)/7)} повторений, {target_sets} подхода
Вторник: {int(int(target_reps)/7)} повторений, {target_sets} подхода
Среда: {int(int(target_reps)/7)} повторений, {target_sets} подхода
Четверг: {int(int(target_reps)/7)} повторений, {target_sets} подхода
Пятница: {int(int(target_reps)/7)} повторений, {target_sets} подхода
Суббота: {int(int(target_reps)/7)} повторений, {target_sets} подхода
Воскресенье: {int(int(target_reps)/7)} повторений, {target_sets} подхода

Ежедневная тренировка по {int(int(target_duration)/7)} минут

КАК ВЫПОЛНЯТЬ:
- Разбейте на подходы: {target_sets} подхода по {int(int(target_reps)/(7*int(target_sets)))} повторений
- Отдыхайте между подходами 60-90 секунд
- Следите за техникой

ЦЕЛЕВЫЕ МЕТРИКИ:
- Повторения: {target_reps} в неделю
- Подходы: {target_sets} в день
- Длительность: {target_duration} минут в неделю

НАГРАДА: Улучшение силы на 15%

СОВЕТ: Выполняйте в удобное время
"""

    def _get_demo_injury_prediction(self, prompt: str) -> str:
        """Демо-прогноз травм"""
        return """АНАЛИЗ РИСКА ТРАВМ..."""

# Создаем экземпляр сервиса
ai_service = AIService()

async def generate_workout_plan(
    user_request: str,
    plan_type: str,
    difficulty: str,
    duration_minutes: int
) -> str:
    """Генерация плана тренировок"""
    prompt = f"""
    Ты - профессиональный фитнес-тренер. Создай подробный план тренировки.

    ЗАПРОС ПОЛЬЗОВАТЕЛЯ: {user_request}

    ТИП ТРЕНИРОВКИ: {plan_type}
    СЛОЖНОСТЬ: {difficulty}
    ДЛИТЕЛЬНОСТЬ: {duration_minutes} минут

    Структура плана:
    1. Разминка (упражнения и время)
    2. Основная часть (упражнения, подходы, повторения, техника)
    3. Заминка (растяжка)
    4. Рекомендации (частота, питание, восстановление)

    Учитывай тип тренировки, сложность и длительность при составлении плана.
    Будь конкретен и мотивирующ.
    
    ВАЖНОЕ ОГРАНИЧЕНИЕ: НЕ используй таблицы, символы звездочек (*), маркдаун или другие форматирования. 
    Используй только обычный текст с нумерованными и буквенными списками.
    """
    return await ai_service._make_ai_request(prompt)

async def generate_exercise_recommendations(combined_request: str) -> str:
    """Генерация рекомендаций при ограничениях"""
    prompt = f"""
    Ты - спортивный врач. Пользователь сообщает о следующих ограничениях: {combined_request}
    
    Предоставь:
    1. Безопасные упражнения (с объяснением почему они безопасны)
    2. Упражнения которых следует избегать (и почему)
    3. Общие рекомендации по тренировкам
    4. Советы по восстановлению и профилактике
    
    Будь профессиональным и заботливым.
    
    ВАЖНОЕ ОГРАНИЧЕНИЕ: НЕ используй таблицы, символы звездочек (*), маркдаун или другие форматирования. 
    Используй только обычный текст с нумерованными и буквенными списками.
    """
    return await ai_service._make_ai_request(prompt)

# async def generate_weekly_challenge(challenge_type: str, target_metrics: dict = None) -> str:
#     """Генерация недельного испытания"""
#     # Формируем строку с целями для промпта
#     metrics_str = ""
#     if target_metrics:
#         parts = []
#         if target_metrics.get('target_reps'):
#             parts.append(f"Цель по повторениям: {target_metrics['target_reps']}")
#         if target_metrics.get('target_sets'):
#             parts.append(f"Цель по подходам: {target_metrics['target_sets']}")
#         if target_metrics.get('target_duration'):
#             parts.append(f"Цель по длительности (мин): {target_metrics['target_duration']}")
#         if parts:
#             metrics_str = " " + ", ".join(parts) + "."

#     prompt = f"""
#     Ты - мотивационный фитнес-коуч. Создай увлекательное недельное испытание.

#     ТИП ИСПЫТАНИЯ: {challenge_type}
#     {metrics_str}

#     ВАЖНО: Ты ОБЯЗАН использовать эти цели в своем ответе. Не игнорируй их!
#     Включи в свой план конкретные цифры: количество повторений, подходов и минут тренировки, соответствующие целям пользователя.

#     Структура испытания:
#     1. Название и цель
#     2. План на каждый день недели (с указанием количества повторений, подходов и времени)
#     3. Советы по выполнению
#     4. Ожидаемые результаты

#     Сделай испытание достижимым но challenging.
    
#     ВАЖНОЕ ОГРАНИЧЕНИЕ: НЕ используй таблицы, символы звездочек (*), маркдаун или другие форматирования. 
#     Используй только обычный текст с нумерованными и буквенными списками для структуры.
#     """
#     return await ai_service._make_ai_request(prompt)
async def generate_weekly_challenge(challenge_type: str, target_metrics: dict = None) -> str:
    """Генерация недельного испытания"""
    # Формируем строку с целями для промпта
    metrics_str = ""
    if target_metrics:
        parts = []
        if target_metrics.get('target_reps'):
            parts.append(f"Цель по повторениям: {target_metrics['target_reps']}")
        if target_metrics.get('target_sets'):
            parts.append(f"Цель по подходам: {target_metrics['target_sets']}")
        if target_metrics.get('target_duration'):
            parts.append(f"Цель по длительности (мин): {target_metrics['target_duration']}")
        if parts:
            metrics_str = " " + ", ".join(parts) + "."

    prompt = f"""
    Ты - мотивационный фитнес-коуч. Создай увлекательное недельное испытание.

    ТИП ИСПЫТАНИЯ: {challenge_type}
    {metrics_str}

    ВАЖНО: Ты ОБЯЗАН использовать эти цели в своем ответе. Не игнорируй их!
    Включи в свой план конкретные цифры: количество повторений, подходов и минут тренировки, соответствующие целям пользователя.

    Структура испытания:
    1. Название и цель
    2. План на каждый день недели (с указанием количества повторений, подходов и времени)
    3. Советы по выполнению
    4. Ожидаемые результаты

    Сделай испытание достижимым но challenging.
    """
    return await ai_service._make_ai_request(prompt)


async def analyze_injury_risk(exercises_data: Dict[str, Any]) -> str:
    """Анализ риска травмы"""
    description_parts = []
    if "plan_exercises" in exercises_data:
        description_parts.append(f"План тренировок: {exercises_data['plan_exercises']}")
    if "user_exercises" in exercises_data:  # Исправлено с user_description на user_exercises
        description_parts.append(f"Описание упражнений от пользователя: {exercises_data['user_exercises']}")
    if "user_risk_factors" in exercises_data:
        description_parts.append(f"Факторы риска от пользователя: {exercises_data['user_risk_factors']}")

    full_description = "\n".join(description_parts)

    prompt = f"""
    Ты - спортивный врач и специалист по фитнесу. Проанализируй риск травмы на основе предоставленных данных.

    ДАННЫЕ ДЛЯ АНАЛИЗА:
    {full_description}

    СТРОГО ВОЗВРАЩАЙ ОТВЕТ В СЛЕДУЮЩЕМ ФОРМАТЕ:

    1. Уровень риска: [ВСТАВЬТЕ ЗДЕСЬ: Низкий/Средний/Высокий]
    Объяснение уровня риска в 1-2 предложениях.

    2. Основные факторы риска
    - Фактор 1
    - Фактор 2
    - Фактор 3

    3. Рекомендации по снижению риска
    - Рекомендация 1
    - Рекомендация 2
    - Рекомендация 3

    4. Альтернативные безопасные упражнения
    - Упражнение 1 и почему оно безопаснее
    - Упражнение 2 и почему оно безопаснее

    ВАЖНО: 
    1. Первой строкой после заголовка "1. Уровень риска:" ДОЛЖНО БЫТЬ только одно слово: "Низкий", "Средний" или "Высокий"
    2. НЕ используй символы решетки (#), звездочки (*), таблицы или маркдаун-форматирование
    3. Используй только обычные цифры с точками для нумерации и дефисы для списков
    4. Будь конкретным и профессиональным
    5. Учитывай факторы риска пользователя
    """
    return await ai_service._make_ai_request(prompt)

async def get_ai_usage_stats() -> Dict[str, Any]:
    """Получение статистики использования AI"""
    return ai_service.get_usage_statistics()

async def set_ai_budget(budget_rub: float):
    """Установка дневного бюджета для AI"""
    ai_service.set_daily_budget(budget_rub)