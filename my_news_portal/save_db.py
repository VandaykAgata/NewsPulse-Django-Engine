import os
import django
import json
import sys

# 1. Помогаем Python найти папки проекта
sys.path.append(os.path.abspath(os.curdir))

# 2. Указываем ПРАВИЛЬНОЕ имя папки с настройками
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewsPaper.settings')

django.setup()

from django.core import serializers
from news.models import Post, Category
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
# Если ты хочешь сохранить и настройки Google (социальные аккаунты):
from allauth.socialaccount.models import SocialApp

print("🚀 Начинаю экспорт данных в UTF-8...")

try:
    with open("db_freeze.json", "w", encoding="utf-8") as f:
        data = []
        # Список моделей для сохранения
        models_to_save = [Post, Category, User, Site, SocialApp]

        for model in models_to_save:
            objects = model.objects.all()
            # Сериализуем объекты каждой модели в JSON
            serialized_data = serializers.serialize("json", objects)
            data.extend(json.loads(serialized_data))

        # Сохраняем всё в один файл с красивыми отступами
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"✅ Успех! Создан файл db_freeze.json.")
    print(f"📦 Сохранено объектов: {len(data)}")
except Exception as e:
    print(f"❌ Произошла ошибка: {e}")