import os
import json
import requests
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Конфигурация логирования уровня Production
logging.basicConfig(
    filename='ai_errors.log',
    level=logging.ERROR,
    format='%(asctime)s | %(levelname)s | %(message)s'
)

# Инициализация путей и окружения
BASE_DIR: Path = Path(__file__).resolve().parent.parent
env_path: str = os.path.join(BASE_DIR, '.env')
load_dotenv(env_path)


class AIAnalysisEngine:
    """
    Класс для взаимодействия с LLM моделями через OpenRouter API.
    Реализует анализ новостного контента: тональность, категория, суммаризация.
    """

    API_URL: str = "https://openrouter.ai/api/v1/chat/completions"
    MODEL: str = "google/gemini-2.0-flash-001"

    def __init__(self) -> None:
        self.api_key: Optional[str] = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            logging.critical("API Key is missing in environment variables.")

    def get_analysis(self, title: str, content: str) -> Dict[str, Any]:
        """
        Отправляет запрос к нейросети и возвращает структурированный JSON.

        Args:
            title: Заголовок статьи.
            content: Полный текст статьи.

        Returns:
            Dict содержащий ключи 'sentiment', 'category', 'summary'.
        """
        if not self.api_key:
            return self._get_fallback_data(title)

        # Оптимизация контекста (Token management)
        truncated_content: str = content[:750] if content else ""

        headers: Dict[str, str] = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "NewsPulse Engine",
        }

        payload: Dict[str, Any] = {
            "model": self.MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Проанализируй новость.\nЗАГОЛОВОК: {title}\nТЕКСТ: {truncated_content}\n\n"
                        f"Верни ТОЛЬКО JSON с ключами: 'sentiment', 'category', 'summary'. "
                        f"Язык ответа: Русский."
                    )
                }
            ],
            "response_format": {"type": "json_object"}  # Подсказка для модели
        }

        try:
            response = requests.post(self.API_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            raw_content: str = response.json()['choices'][0]['message']['content']

            # Очистка и валидация данных
            clean_json: str = raw_content.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)

        except Exception as e:
            logging.error(f"AI Analysis failed for '{title}': {str(e)}")
            return self._get_fallback_data(title)

    def _get_fallback_data(self, title: str) -> Dict[str, str]:
        """Возвращает безопасный набор данных при сбое API."""
        return {
            "summary": f"Автоматический анализ временно недоступен для: {title[:30]}...",
            "sentiment": "нейтральная",
            "category": "Общее"
        }


# Интерфейс для интеграции с Django моделями
def analyze_article_ai(title: str, content: str) -> Dict[str, Any]:
    engine = AIAnalysisEngine()
    return engine.get_analysis(title, content)