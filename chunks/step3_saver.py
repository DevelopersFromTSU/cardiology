import os
import json


def save_chunk_to_folder(chunk_data, filename):
    """
    Создает папку chunks (если ее нет) и сохраняет туда данные в формате JSON.
    """
    # 1. Задаем имя папки
    folder_name = "result"

    # 2. Если папки еще нет в проекте - создаем ее автоматически
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"📁 Создана новая директория: {folder_name}/")

    # 3. Формируем полный путь (например: chunks/chunk_page14.json)
    file_path = os.path.join(folder_name, filename)

    # 4. Записываем наш словарик в файл
    with open(file_path, "w", encoding="utf-8") as file:
        # ensure_ascii=False нужен, чтобы русский текст не превратился в кракозябры
        # indent=4 делает файл красивым и читаемым для человека
        json.dump(chunk_data, file, ensure_ascii=False, indent=4)

    print(f"✅ Чанк успешно сохранен в файл: {file_path}")