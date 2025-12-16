# Назначение: получение списка бесплатных моделей с сайта OpenRouter.ai
#
import os
import requests
from dotenv import load_dotenv

# загружаем токен из .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# отправляем запрос на OpenRouter
url = "https://openrouter.ai/api/v1/models"
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get(url, headers=headers)
response.raise_for_status() # добавляем проверку на ошибки запроса

# получаем отсортированный список FREE моделей
models = response.json().get("data", [])
free_models = sorted(
    [(m["name"], m["id"], m["context_length"]) for m in models if m["name"].endswith("(free)")]
)

# красиво все выводим в виде таблицы
print(f"{'№':>3} | {'Название модели':45} | {'Код модели':46} | {'Контекст'}")
print("-" * 111)
for i, (name, model_id, context) in enumerate(free_models, 1):
    print(f"{i:3} | {name:45} | {model_id:46} | {context}")