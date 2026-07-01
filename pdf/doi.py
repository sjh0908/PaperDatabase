import re

DOI_PATTERN = re.compile(
    r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+",
    re.IGNORECASE
)

def normalize_doi(doi):
    if doi is None:
        return None

    doi = doi.strip()

    doi = doi.rstrip(".,;:)，。；）")

    return doi.lower()

def extract_doi_from_text(text):
    if not text:
        return None

    match = DOI_PATTERN.search(text)

    if match is None:
        return None

    return normalize_doi(match.group(0))