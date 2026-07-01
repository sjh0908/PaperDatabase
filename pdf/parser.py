import fitz

def extract_text_from_pdf(pdf_path, max_pages=None):
    text_parts = []

    with fitz.open(pdf_path) as doc:

        total_pages = len(doc)

        if max_pages is None:
            pages_to_read = total_pages
        else:
            pages_to_read = min(max_pages, total_pages)

        for page_index in range(pages_to_read):

            page = doc[page_index]
            text = page.get_text("text")

            if text:
                text_parts.append(text)

    return "\n".join(text_parts)

def extract_first_page_text(pdf_path):
    return extract_text_from_pdf(pdf_path, max_pages=1)