import fitz  # Библиотека PyMuPDF


def get_raw_text_from_pdf(pdf_path, page_num):
    """
    Открывает PDF, достает текст текущей страницы,
    а также захватывает контекст до и после неё.
    """
    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    # 1. НАХЛЁСТ НАЗАД: Берем конец предыдущей страницы
    prev_context = ""
    if page_num > 0:
        prev_page = doc.load_page(page_num - 1)
        # Берем последние 600 символов (чуть больше, для запаса)
        prev_text_full = prev_page.get_text()
        prev_context = prev_text_full[-600:]

        # 2. ОСНОВНОЙ ТЕКТ: Берем текст текущей страницы
    page = doc.load_page(page_num)
    current_text = page.get_text()

    # 3. НАХЛЁСТ ВПЕРЕД: Берем начало следующей страницы
    next_context = ""
    if page_num + 1 < total_pages:
        next_page = doc.load_page(page_num + 1)
        next_context = next_page.get_text()[:600]

    doc.close()

    # Собираем все в одну структуру с четкими маркерами
    combined_content = (
        f"--- НАЧАЛО ПРЕДЫДУЩЕЙ СТРАНИЦЫ (КОНТЕКСТ) ---\n{prev_context}\n"
        f"--- ТЕКСТ ТЕКУЩЕЙ СТРАНИЦЫ ---\n{current_text}\n"
        f"--- НАЧАЛО СЛЕДУЮЩЕЙ СТРАНИЦЫ (КОНТЕКСТ) ---\n{next_context}"
    )

    return combined_content