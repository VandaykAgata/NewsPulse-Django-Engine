import os
import json
import requests
import logging
from pathlib import Path
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(filename='ai_errors.log', level=logging.ERROR, format='%(asctime)s %(levelname)s %(message)s')

# УМНЫЙ ПУТЬ:
# 1. Path(__file__) — это сам ai_logic.py
# 2. .parent — это папка news/
# 3. .parent — это папка my_news_portal/ (где и лежит .env)
BASE_DIR = Path(__file__).resolve().parent.parent

# Загружаем .env, указывая точный путь
env_path = os.path.join(BASE_DIR, '.env')
load_dotenv(env_path)

api_key = os.getenv("OPENROUTER_API_KEY")

# Проверка в консоли
if not api_key:
    print(f"❌ ОШИБКА: Ключ не найден по пути: {env_path}")
else:
    print(f"✅ Ключ успешно загружен из: {env_path}")
    print(f"✅ Начало ключа: {api_key[:10]}...")


def analyze_article_ai(title, content):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Agata News Portal",
    }

    # Ограничиваем текст статьи, чтобы не превысить лимиты (вдруг там целая книга)
    # 2000 символов более чем достаточно для анализа
    text_to_analyze = content[:700] if content else "Нет текста"

    data = {
        "model": "google/gemini-2.0-flash-001",
        "messages": [
            {
                "role": "user",
                "content": (
                    f"Проанализируй новость и верни JSON.\n"
                    f"ЗАГОЛОВОК: {title}\n"
                    f"ТЕКСТ: {text_to_analyze}\n\n"
                    f"ОТВЕТЬ ТОЛЬКО В ФОРМАТЕ JSON: "
                    f"{{\"sentiment\": \"тональность\", \"category\": \"категория\", \"summary\": \"краткое резюме на русском\"}}"
                )
            }
        ],
    }

    try:
        print(f"--- Отправка на анализ (ждем до 30 сек): {title[:20]}... ---")
        # Увеличиваем таймаут до 30
        response = requests.post(url, headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            res_json = response.json()
            ai_text = res_json['choices'][0]['message']['content']

            # Чистим ответ от возможных спецсимволов Markdown
            clean_json = ai_text.replace("```json", "").replace("```", "").strip()
            print(f"+++ ПОЛУЧЕН ОТВЕТ: {clean_json}")

            return json.loads(clean_json)
        else:
            # Если статус не 200, мы увидим причину в консоли
            print(f"❌ Ошибка API: {response.status_code}, Ответ: {response.text}")

    except Exception as e:
        print(f"❌ Ошибка в процессе: {e}")

    # Если мы тут — значит сработал План Б
    return {
        "summary": f"Анализ для: {title[:25]}...",
        "sentiment": "нейтральная",
        "category": "Общее"
    }