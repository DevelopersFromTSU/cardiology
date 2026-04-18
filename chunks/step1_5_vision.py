import base64
import requests
import os
from dotenv import load_dotenv

load_dotenv()


def describe_image_logic(image_bytes):
    """
    Отправляет изображение в мультимодальную модель Qwen через OpenAI-совместимый эндпоинт.
    """
    folder_id = os.getenv("FOLDER_ID")
    api_key = os.getenv("API_KEY")

    # Кодируем байты изображения в Base64
    encoded_image = base64.b64encode(image_bytes).decode('utf-8')

    # OpenAI-совместимый эндпоинт Яндекса
    url = "https://llm.api.cloud.yandex.net/v1/chat/completions"

    headers = {
        "Authorization": f"Api-Key {api_key}",
        "x-folder-id": folder_id
    }

    payload = {
        "model": f"gpt://{folder_id}/qwen3.5-35b-a3b-fp8/latest",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Ты — профессиональный медицинский оцифровщик. Твоя задача — перевести изображение (инфографику или таблицу) в текст с ПРЕДЕЛЬНОЙ точностью.\n\n"
                            "СТРОГИЕ ПРАВИЛА:\n"
                            "1. ФОРМАТ ТАБЛИЦ: Если на картинке таблица, используй формат Markdown (| столбец |). Если ячейки объединены, дублируй значение для каждой строки. "
                            "Если таблица слишком сложная — разложи её на список четких фактов по шаблону: '[Категория/Возраст] + [Диагноз] = [Целевое значение]'.\n"
                            "2. СОХРАНЕНИЕ ТЕРМИНОВ: Категорически запрещено менять формулировки.Например: ДМАД или СМАД"
                            "3. ЦИФРЫ: Переноси диапазоны давления целиком (например, 140–159/90–99). Не пропускай второе число и не округляй.\n"
                            "4. ВЕРТИКАЛЬНЫЙ ТЕКСТ: Обязательно прочитай текст на полях (боковой или перевернутый) и включи его как заголовок в начало ответа.\n"
                            "5. БЕЗ ОПИСАНИЙ: Не пиши 'на картинке показано'. Сразу выдавай медицинскую информацию.\n"
                            "6. ТОЧНОСТЬ: Не объединяй разные диагнозы (например, СД и ХБП) в одну строку, если в таблице у них разные показатели."

                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.2
    }

    try:
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            print(f"   ⚠️ Ошибка Vision API (Статус {response.status_code}): {response.text}")
            return f"[Ошибка анализа изображения: {response.status_code}]"

    except Exception as e:
        print(f"   ⚠️ Критическая ошибка в Vision-модуле: {e}")
        return f"[Контекст изображения недоступен: {e}]"