import fitz  # Библиотека PyMuPDF


def get_raw_text_from_pdf(pdf_path, page_num):
    """
    Открывает PDF и достает текст с указанной страницы.
    (page_num начинается с 0, поэтому 10-я страница в PDF — это индекс 9)
    """
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_num)
    raw_text = page.get_text()
    doc.close()

    return raw_text
