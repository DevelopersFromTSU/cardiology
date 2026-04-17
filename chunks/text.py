import json
import os

def merge_chunks_to_text(json_folder, output_file):
    all_text = []

    # Сортируем файлы, чтобы текст шел по порядку (стр 10 чанк 1, чанк 2 и т.д.)
    files = sorted([f for f in os.listdir(json_folder) if f.endswith('.json')])

    for filename in files:
        with open(os.path.join(json_folder, filename), 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Добавляем разделитель, чтобы видеть границы чанков при сравнении
            all_text.append(f"--- {filename} ---\n{data['clean_text']}")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n\n".join(all_text))

    print(f"✅ Готово! Весь текст собран в файл: {output_file}")

# Запуск
merge_chunks_to_text('result', 'result_book_cleaned.txt')