import fitz  # Библиотека PyMuPDF


def get_raw_text_from_pdf(pdf_path, page_num):
    """
    Открывает PDF, достает текст со страницы + берет нахлест со следующей.
    """
    doc = fitz.open(pdf_path)

    # 1. Берем текст текущей страницы
    page = doc.load_page(page_num)
    raw_text = page.get_text()

    # 2. УМНЫЙ НАХЛЕСТ: Заглядываем на следующую страницу (если она есть)
    if page_num + 1 < len(doc):
        next_page = doc.load_page(page_num + 1)
        # Берем первые 500 символов со следующей страницы
        next_page_start = next_page.get_text()[:500]
        # Приклеиваем их к текущему тексту
        raw_text += " \n " + next_page_start

    doc.close()

    return raw_text