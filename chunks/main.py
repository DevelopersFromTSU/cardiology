import fitz  # PyMuPDF для подсчета страниц
import time  # Для пауз между запросами
import os
import re

# Импортируем наши готовые инструменты
from step1_reader import get_raw_text_from_pdf
from step2_yandex_cleaner import clean_and_structure_text
from step3_saver import save_chunk_to_folder

# --- НАСТРОЙКИ ---
BOOK_PATH = "./books/Артериальная гипертония 2024 РКО.pdf"  # Путь к книге

def process_book(start_page=0, end_page=None):
    """Главный конвейер: читает страницу целиком и отправляет в нейросеть."""

    doc = fitz.open(BOOK_PATH)
    total_pages = len(doc)
    doc.close()

    if end_page is None or end_page > total_pages:
        end_page = total_pages - 1

    print(f"🚀 Запуск конвейера! Обрабатываем страницы с {start_page} по {end_page}...\n")

    for page_num in range(start_page, end_page + 1):
        print(f"--- 📄 Страница {page_num + 1} ---")

        # Шаг 1: Достаем текст страницы ЦЕЛИКОМ
        # Шаг 1: Достаем текст страницы ЦЕЛИКОМ
        # Шаг 1: Достаем текст страницы ЦЕЛИКОМ
        raw_text = get_raw_text_from_pdf(BOOK_PATH, page_num)

        # --- УМНАЯ ОБРЕЗКА ХВОСТОВ (С ПРЕДОХРАНИТЕЛЕМ) ---
        match = re.search(r'[А-Я][а-я]{2,}', raw_text)
        if match:
            tail = raw_text[:match.start()]

            # ПРЕДОХРАНИТЕЛЬ:
            # Удаляем хвост ТОЛЬКО если он короче 300 символов И в нем нет маркеров списка (•)
            if len(tail) < 300 and "•" not in tail:
                raw_text = raw_text[match.start():]
            else:
                print("   ⚠️ Обнаружен длинный текст или список без заглавных букв. Обрезка отменена.")
        # ------------------------------------

        print(f"   🧠 Отправляем страницу целиком в YandexGPT...")

        # --- УНИЧТОЖЕНИЕ ФАНТОМНЫХ ТОЧЕК (УСИЛЕННОЕ) ---
        # Убираем точку перед союзами, даже если там есть лишние пробелы/переносы
        raw_text = re.sub(r'\s*\.\s+(и/или|и|а|но)\b', r' \1', raw_text)

        # Жестко удаляем точку сразу после двойных скобок (ваш случай)
        raw_text = re.sub(r'\)\)\.\s*', ')) ', raw_text)
        # ---------------------------------------------------

        try:
            # Шаг 2: Интеллектуальная очистка
            smart_page = clean_and_structure_text(raw_text)

            # Добавляем номер страницы для истории
            smart_page['source_page'] = page_num + 1

            # Шаг 3: Сохранение (один файл на одну страницу)
            file_name = f"page_{page_num + 1}.json"
            save_chunk_to_folder(smart_page, file_name)

            print(f"   ✅ Сохранено: {file_name}")

            # Пауза, чтобы не превысить лимиты API (1 запрос на страницу — это безопасно)
            time.sleep(1)

        except Exception as e:
            print(f"   ❌ Ошибка на странице {page_num + 1}: {e}")

if __name__ == "__main__":
    # Запускаем, например, для первых 10 страниц
    process_book(start_page=8, end_page=9)