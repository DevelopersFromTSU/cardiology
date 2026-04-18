import fitz  # PyMuPDF
import time
import os
import re
from utils import force_expand_abbreviations

# Импортируем инструменты
from step1_reader import get_raw_text_from_pdf
from step2_yandex_cleaner import clean_and_structure_text
from step3_saver import save_chunk_to_folder
from step1_5_vision import describe_image_logic

# --- НАСТРОЙКИ ---
BOOK_PATH = "./books/Артериальная гипертония 2024 РКО.pdf"


def process_book(start_page=0, end_page=None):
    """Конвейер: Текст страницы, затем визуальные данные в конце."""

    if not os.path.exists(BOOK_PATH):
        print(f"❌ Файл не найден: {BOOK_PATH}")
        return

    doc = fitz.open(BOOK_PATH)
    total_pages = len(doc)

    if end_page is None or end_page >= total_pages:
        end_page = total_pages - 1

    print(f"🚀 Запуск конвейера! Порядок: Текст -> Визуал. Страницы: {start_page + 1} - {end_page + 1}\n")

    for page_num in range(start_page, end_page + 1):
        print(f"--- 📄 Страница {page_num + 1} ---")
        page = doc[page_num]

        # --- БЛОК 1: ПОДГОТОВКА ИЗОБРАЖЕНИЙ (Схемы, графики) ---
        image_context = ""
        image_list = page.get_images(full=True)

        # Отбираем самую информативную картинку каждого размера (защита от масок)
        best_images = {}

        if image_list:
            for img in image_list:
                xref = img[0]
                base_image = doc.extract_image(xref)
                w, h = base_image["width"], base_image["height"]
                img_bytes = base_image["image"]

                if w < 150 or h < 150:
                    continue

                size = (w, h)
                # Если такой размер еще не встречался или текущий файл тяжелее (детальнее)
                if size not in best_images or len(img_bytes) > len(best_images[size]):
                    best_images[size] = img_bytes

            for size, img_bytes in best_images.items():
                print(f"   📸 Анализ изображения ({size[0]}x{size[1]})...")
                desc = describe_image_logic(img_bytes)
                if desc and "ПРОПУСК" not in desc:
                    image_context += f"### ВИЗУАЛЬНЫЙ МАТЕРИАЛ (Картинка):\n{desc}\n\n"
                time.sleep(1)

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
                time.sleep(1)

        # --- БЛОК 3: ОСНОВНОЙ ТЕКСТ (Текстовый слой PDF) ---
        raw_text = get_raw_text_from_pdf(BOOK_PATH, page_num)

        # --- СБОРКА ПАКЕТА (МЕНЯЕМ ПОРЯДОК) ---
        # Текст теперь идет первым, а описания картинок и таблиц — дополнением в конце.
        full_payload = f"### ОСНОВНОЙ ТЕКСТ СТРАНИЦЫ:\n{raw_text}\n\n"

        if image_context:
            full_payload += image_context
        if table_context:
            full_payload += table_context

        # Препроцессинг
        full_payload = re.sub(r'\)\)\.\s*', ')) ', full_payload)
        processed_text = force_expand_abbreviations(full_payload)

        try:
            print(f"   🧠 Интеллектуальная сборка страницы...")
            smart_page = clean_and_structure_text(processed_text)

            # Сохранение
            file_name = f"page_{page_num + 1}.json"
            save_chunk_to_folder(smart_page, file_name)
            print(f"   ✅ Страница {page_num + 1} успешно сохранена.")

        except Exception as e:
            print(f"   ❌ Ошибка на этапе очистки: {e}")

    doc.close()
    print(f"\n🏁 Обработка завершена!")


if __name__ == "__main__":
    process_book(start_page=187, end_page=187)