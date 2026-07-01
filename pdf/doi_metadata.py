import requests

def normalize_orcid(orcid):
    if not orcid:
        return None

    orcid = orcid.strip()

    orcid = orcid.replace("https://orcid.org/", "")
    orcid = orcid.replace("http://orcid.org/", "")
    orcid = orcid.replace("orcid.org/", "")

    if len(orcid) > 19:
        return None

    return orcid

def get_crossref_metadata_by_doi(doi):
    if not doi:
        return None

    doi = doi.strip()

    url = f"https://api.crossref.org/works/{doi}"

    response = requests.get(
        url,
        timeout=10,
        headers={
            "User-Agent": "PaperDatabase/1.0"
        }
    )

    if response.status_code != 200:
        return None

    data = response.json()

    message = data.get("message", {})

    title_list = message.get("title") or []
    title = title_list[0] if title_list else None

    abstract = message.get("abstract")

    published = (
        message.get("published-print")
        or message.get("published-online")
        or message.get("published")
        or {}
    )

    date_parts = published.get("date-parts", [[]])[0]

    public_date = None
    public_date_precision = None

    if len(date_parts) == 1:
        public_date = f"{date_parts[0]}-01-01"
        public_date_precision = "year"
    elif len(date_parts) == 2:
        public_date = f"{date_parts[0]}-{date_parts[1]:02d}-01"
        public_date_precision = "month"
    elif len(date_parts) >= 3:
        public_date = f"{date_parts[0]}-{date_parts[1]:02d}-{date_parts[2]:02d}"
        public_date_precision = "day"

    source_name = None
    source_type = None

    container_title = message.get("container-title") or []

    if container_title:
        source_name = container_title[0]

    crossref_type = message.get("type")

    if crossref_type == "journal-article":
        source_type = "journal"
    elif crossref_type == "proceedings-article":
        source_type = "conference"

    authors = []

    for item in message.get("author", []):

        given = item.get("given", "")
        family = item.get("family", "")

        author_name = f"{given} {family}".strip()

        if not author_name:
            continue

        authors.append({
            "author_name": author_name,
            "author_orcid": normalize_orcid(item.get("ORCID")),
            "author_email": None
        })

    return {
        "doi": doi.lower(),
        "title": title,
        "abstract": abstract,
        "public_date": public_date,
        "public_date_precision": public_date_precision,
        "source_name": source_name,
        "source_type": source_type,
        "authors": authors
    }