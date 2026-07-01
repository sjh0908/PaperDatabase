from pdf.parser import extract_first_page_text
from pdf.doi import extract_doi_from_text

def guess_title_from_first_page_text(text): #以第一页中第一个较长且非空的文本行为标题
    if not text:
        return None

    lines = text.splitlines()

    for line in lines:

        line = line.strip()

        if len(line) >= 8:
            return line

    return None

def extract_basic_metadata(pdf_path): #PATH -> {'doi':..., 'title':..., 'first_page_text':...}
    first_page_text = extract_first_page_text(pdf_path)

    doi = extract_doi_from_text(first_page_text)

    title = guess_title_from_first_page_text(first_page_text)

    return {
        "doi": doi,
        "title": title,
        "first_page_text": first_page_text
    }