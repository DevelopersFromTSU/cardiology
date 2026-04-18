import fitz  # PyMuPDF
import time
import os
import re
from utils import force_expand_abbreviations
import hashlib

# Импортируем инструменты
from step1_reader import get_raw_text_from_pdf
from step2_yandex_cleaner import clean_and_structure_text
from step3_saver import save_chunk_to_folder
from step1_5_vision import describe_image_logic

# --- НАСТРОЙКИ ---
BOOK_PATH = "./books/Артериальная гипертония 2024 РКО.pdf"


def process_book(start_page=0, end_page=None):
    """Конвейер: сначала Визуальные данные (картинки, таблицы), затем Текст."""

    if not os.path.exists(BOOK_PATH):
        print(f"❌ Файл не найден: {BOOK_PATH}")
        return

    doc = fitz.open(BOOK_PATH)
    total_pages = len(doc)

    if end_page is None or end_page >= total_pages:
        end_page = total_pages - 1

    print(f"🚀 Запуск структурированного конвейера! Страницы: {start_page + 1} - {end_page + 1}\n")

    for page_num in range(start_page, end_page + 1):
        print(f"--- 📄 Страница {page_num + 1} ---")
        page = doc[page_num]

        # --- БЛОК 1: ИЗОБРАЖЕНИЯ (Схемы, графики) ---
        image_context = ""
        image_list = page.get_images(full=True)

        if image_list:
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                width, height = base_image["width"], base_image["height"]

                if width < 150 or height < 150:
                    continue

                print(f"   📸 Анализ изображения ({width}x{height})...")
                desc = describe_image_logic(image_bytes)

                # Защита от пустых ответов или ошибок
                if not desc or "ПРОПУСК" in desc or "Ошибка" in desc:
                    continue

                image_context += f"### ВИЗУАЛЬНЫЙ МАТЕРИАЛ:\n{desc}\n\n"

        # --- БЛОК 2: ТАБЛИЦЫ (Через Vision-скриншоты) ---
        table_context = ""
        tabs_finder = page.find_tables()
        tabs = tabs_finder.tables

        if tabs:
            print(f"   📊 Найдено таблиц: {len(tabs)}. Делаем снимки...")
            for i, table in enumerate(tabs):
                bbox = table.bbox
                pix = page.get_pixmap(clip=bbox, matrix=fitz.Matrix(3, 3))
                image_bytes = pix.tobytes("png")

                print(f"   🔍 Анализируем таблицу {i + 1} через Vision...")
                table_desc = describe_image_logic(image_bytes)
                table_context += f"### ТАБЛИЦА {i + 1} (ДАННЫЕ):\n{table_desc}\n\n"

        # --- БЛОК 3: ОСНОВНОЙ ТЕКСТ (Текстовый слой PDF) ---
        raw_text = get_raw_text_from_pdf(BOOK_PATH, page_num)

        # --- СБОРКА ПАКЕТА: Картинка -> Таблица -> Текст ---
        # Такой порядок помогает YandexGPT в step2 лучше понимать,
        # к каким данным относится последующий текст.
        full_payload = ""
        if image_context:
            full_payload += f"{image_context}"
        if table_context:
            full_payload += f"{table_context}"

        full_payload += f"### ОСНОВНОЙ ТЕКСТ СТРАНИЦЫ:\n{raw_text}"

        # 3. Препроцессинг (расшифровка аббревиатур)
        full_payload = re.sub(r'\)\)\.\s*', ')) ', full_payload)
        processed_text = force_expand_abbreviations(full_payload)

        try:
            print(f"   🧠 Интеллектуальная сборка страницы...")
            # Здесь YandexGPT склеивает всё в один структурированный JSON
            smart_page = clean_and_structure_text(processed_text)

            # 5. Сохранение
            file_name = f"page_{page_num + 1}.json"
            save_chunk_to_folder(smart_page, file_name)
            print(f"   ✅ Страница {page_num + 1} успешно сохранена.")

        except Exception as e:
            print(f"   ❌ Ошибка на этапе очистки: {e}")

    print(f"\n🏁 Обработка завершена!")


if __name__ == "__main__":
    # Тест страницы 188
    process_book(start_page=187, end_page=187)