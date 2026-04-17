import fitz  # PyMuPDF для подсчета страниц
import time  # Для пауз между запросами
import os

# Импортируем наши готовые инструменты
from step1_reader import get_raw_text_from_pdf
from step2_yandex_cleaner import clean_and_structure_text
from step3_saver import save_chunk_to_folder

# --- НАСТРОЙКИ ---
BOOK_PATH = "./books/Кардиология  национальное руководство.pdf"  # Путь к книге
CHUNK_SIZE = 800  # Размер кусочка текста
OVERLAP = 150  # Нахлест, чтобы не разорвать смысл на стыке чанков


def split_into_chunks(text):
    """Режет длинный текст страницы на удобные чанки."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk_str = text[start:end]
        if len(chunk_str.strip()) > OVERLAP + 50:  # Игнорируем пустые огрызки
            chunks.append(chunk_str)
        elif chunks:
            chunks[-1] += chunk_str

        start += (CHUNK_SIZE - OVERLAP)
    return chunks


def process_book(start_page=0, end_page=None):
    """Главный конвейер: читает, режет, отправляет в нейросеть, сохраняет."""

    # 1. Узнаем, сколько всего страниц в книге
    doc = fitz.open(BOOK_PATH)
    total_pages = len(doc)
    doc.close()

    if end_page is None or end_page > total_pages:
        end_page = total_pages - 1

    print(f"🚀 Запуск конвейера! Обрабатываем страницы с {start_page} по {end_page}...\n")

    # 2. Запускаем цикл по страницам
    for page_num in range(start_page, end_page + 1):
        print(f"--- 📄 Читаем страницу {page_num + 1} ---")

        # Шаг 1: Достаем текст
        raw_text = get_raw_text_from_pdf(BOOK_PATH, page_num)

        if len(raw_text.strip()) < 50:
            print("   (Страница пустая, пропускаем)")
            continue

        # Шаг 1.5: Режем текст на чанки
        chunks = split_into_chunks(raw_text)
        print(f"   ✂️ Страница разделена на {len(chunks)} чанков.")

        # 3. Запускаем цикл по чанкам внутри страницы
        for i, chunk_text in enumerate(chunks):
            print(f"   🧠 Отправляем чанк {i + 1}/{len(chunks)} в YandexGPT...")

            try:
                # Шаг 2: Интеллектуальная очистка
                smart_chunk = clean_and_structure_text(chunk_text)

                # ДОБАВЛЯЕМ ПАСПОРТ: записываем, откуда мы взяли этот текст
                smart_chunk['source_page'] = page_num + 1
                # smart_chunk['chapter'] = current_chapter

                # Шаг 3: Сохранение
                file_name = f"page_{page_num + 1}_chunk_{i + 1}.json"
                save_chunk_to_folder(smart_chunk, file_name)

                # ЗАЩИТА: Спим 2 секунды, чтобы Яндекс не забанил нас за спам
                time.sleep(2)

            except Exception as e:
                # Если нейросеть сбоит (например, интернет моргнул), мы не роняем всю программу!
                print(f"   ❌ Ошибка на странице {page_num + 1}, чанке {i + 1}: {e}")
                print("   Продолжаем работу со следующего чанка...")


if __name__ == "__main__":
    # ⚠️ ВАЖНОЕ ПРАВИЛО ПРОГРАММИСТА:
    # Никогда не запускай цикл сразу на все 180 страниц!
    # Сначала протестируй на 2-3 страницах, чтобы убедиться, что всё идеально.

    # Обрабатываем для теста
    process_book(start_page=23, end_page=23)

    # Когда тест пройдет успешно, закомментируй строку выше
    # и раскомментируй строку ниже (она прогонит всю книгу целиком):
    # process_book()