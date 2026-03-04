import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("OPENROUTER_API_KEY")

if key:
    print(f"✅ Ключ найден! Он начинается на: {key[:10]}...")
else:
    print("❌ ОШИБКА: Ключ не найден. Проверь файл .env!")