from database.db import (
    get_connection,
    close_connection
)
from werkzeug.security import generate_password_hash, check_password_hash

ADMIN_TABLES = {
    "Paper": {
        "pk": "paper_id",
        "columns": [
            "paper_id",
            "paper_doi",
            "paper_name",
            "paper_abstract",
            "paper_public_date",
            "paper_public_date_precision",
            "paper_file_path",
            "papersource_id",
            "paper_review_status",
            "paper_uploaded_by"
        ],
        "editable": [
            "paper_doi",
            "paper_name",
            "paper_abstract",
            "paper_public_date",
            "paper_public_date_precision",
            "paper_file_path",
            "papersource_id",
            "paper_review_status",
            "paper_uploaded_by"
        ]
    },
    "Author": {
        "pk": "author_id",
        "columns": [
            "author_id",
            "author_name",
            "author_orcid",
            "author_email"
        ],
        "editable": [
            "author_name",
            "author_orcid",
            "author_email"
        ]
    },
    "AuthorInstitution": {
        "pk": "authorinstitution_id",
        "columns": [
            "authorinstitution_id",
            "authorinstitution_name",
            "authorinstitution_address",
            "authorinstitution_email"
        ],
        "editable": [
            "authorinstitution_name",
            "authorinstitution_address",
            "authorinstitution_email"
        ]
    },
    "PaperSource": {
        "pk": "papersource_id",
        "columns": [
            "papersource_id",
            "papersource_type",
            "papersource_name",
            "papersource_location",
            "papersource_start_date",
            "papersource_start_date_precision",
            "papersource_end_date",
            "papersource_end_date_precision"
        ],
        "editable": [
            "papersource_type",
            "papersource_name",
            "papersource_location",
            "papersource_start_date",
            "papersource_start_date_precision",
            "papersource_end_date",
            "papersource_end_date_precision"
        ]
    },
    "Keyword": {
        "pk": "keyword_id",
        "columns": [
            "keyword_id",
            "keyword_name"
        ],
        "editable": [
            "keyword_name"
        ]
    },
    "PaperAuthor": {
        "pk": None,
        "columns": [
            "paper_id",
            "author_id",
            "author_role"
        ],
        "editable": [
            "author_role"
        ]
    },
    "PaperKeyword": {
        "pk": None,
        "columns": [
            "paper_id",
            "keyword_id"
        ],
        "editable": []
    },
    "Subordination": {
        "pk": "subordination_id",
        "columns": [
            "subordination_id",
            "author_id",
            "authorinstitution_id",
            "subordination_start_date",
            "subordination_start_date_precision",
            "subordination_end_date",
            "subordination_end_date_precision"
        ],
        "editable": [
            "author_id",
            "authorinstitution_id",
            "subordination_start_date",
            "subordination_start_date_precision",
            "subordination_end_date",
            "subordination_end_date_precision"
        ]
    },
    "User": {
        "pk": "dbuser_id",
        "columns": [
            "dbuser_id",
            "dbuser_name",
            "dbuser_role"
        ],
        "editable": [
            "dbuser_name",
            "dbuser_role"
        ]
    }
}

EXPORT_FIELDS = {
    "paper_id": "p.paper_id",
    "paper_doi": "p.paper_doi",
    "paper_name": "p.paper_name",
    "paper_abstract": "p.paper_abstract",
    "paper_public_date": "p.paper_public_date",
    "paper_file_path": "p.paper_file_path",

    "author_name": "a.author_name",
    "author_orcid": "a.author_orcid",
    "author_email": "a.author_email",
    "author_role": "pa.author_role",

    "institution_name": "ai.authorinstitution_name",
    "institution_address": "ai.authorinstitution_address",

    "keyword_name": "k.keyword_name",

    "source_type": "ps.papersource_type",
    "source_name": "ps.papersource_name",
    "source_location": "ps.papersource_location"
}

def execute_query(sql, params=None): #SQL SELECT -> list[dict]
    connection = None

    try:
        connection = get_connection()

        with connection.cursor() as cursor:

            cursor.execute(sql, params)

            result = cursor.fetchall()

        return result

    finally:
        close_connection(connection)

def execute_query_one(sql, params=None): #SQL SELECT -> dict OR None
    connection = None

    try:
        connection = get_connection()

        with connection.cursor() as cursor:

            cursor.execute(sql, params)

            result = cursor.fetchone()

        return result

    finally:
        close_connection(connection)

def execute_update(sql, params=None): #SQL INSERT UPDATE DELETE -> int
    connection = None

    try:

        connection = get_connection()

        with connection.cursor() as cursor:

            affected = cursor.execute(sql, params)

        connection.commit()

        return affected

    except:

        connection.rollback()

        raise

    finally:

        close_connection(connection)

def execute_insert(sql, params=None):

    connection = None

    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            last_id = cursor.lastrowid

        connection.commit()

        return last_id

    except:
        connection.rollback()
        raise

    finally:
        close_connection(connection)

def get_all_papers():

    sql = """
    SELECT *
    FROM Paper
    ORDER BY paper_id
    """

    return execute_query(sql)

def get_paper_by_id(paper_id):

    sql = """
    SELECT *
    FROM Paper
    WHERE paper_id=%s
    """

    return execute_query_one(sql, (paper_id,))

def get_paper_by_doi(doi):

    sql = """
    SELECT *
    FROM Paper
    WHERE paper_doi=%s
    """

    return execute_query_one(sql, (doi,))

def search_paper_by_name(keyword):

    sql = """
    SELECT *
    FROM Paper
    WHERE paper_name LIKE %s
    """

    return execute_query(
        sql,
        ("%" + keyword + "%",)
    )

def get_author_by_id(author_id):

    sql = """
    SELECT *
    FROM Author
    WHERE author_id=%s
    """

    return execute_query_one(sql, (author_id,))

def get_author_by_orcid(orcid):

    sql = """
    SELECT *
    FROM Author
    WHERE author_orcid=%s
    """

    return execute_query_one(sql, (orcid,))

def get_paper_authors(paper_id):

    sql = """
    SELECT
        a.author_id,
        a.author_name,
        a.author_orcid,
        a.author_email,
        pa.author_role
    FROM Author a
    JOIN PaperAuthor pa
    ON a.author_id = pa.author_id
    WHERE pa.paper_id = %s
    ORDER BY a.author_id
    """

    return execute_query(sql, (paper_id,))

def get_paper_keywords(paper_id):

    sql = """
    SELECT
        k.keyword_id,
        k.keyword_name
    FROM Keyword k
    JOIN PaperKeyword pk
   ON k.keyword_id = pk.keyword_id
    WHERE pk.paper_id = %s
    ORDER BY k.keyword_name
    """

    return execute_query(sql, (paper_id,))

def get_paper_source(paper_id):

    sql = """
    SELECT
        ps.*
    FROM PaperSource ps
    JOIN Paper p
   ON ps.papersource_id = p.papersource_id
    WHERE p.paper_id = %s
    """

    return execute_query_one(sql, (paper_id,))

def search_papers_by_keyword(keyword_name):

    sql = """
    SELECT DISTINCT
        p.*
    FROM Paper p
    JOIN PaperKeyword pk
    ON p.paper_id = pk.paper_id
    JOIN Keyword k
    ON pk.keyword_id = k.keyword_id
    WHERE k.keyword_name LIKE %s
    ORDER BY p.paper_id
    """

    return execute_query(sql, ("%" + keyword_name + "%",))

def insert_paper(
    paper_doi,
    paper_name,
    paper_abstract,
    paper_public_date,
    paper_public_date_precision,
    paper_file_path,
    papersource_id,
    paper_review_status="pending",
    paper_uploaded_by=None
):

    sql = """
    INSERT INTO Paper(
        paper_doi,
        paper_name,
        paper_abstract,
        paper_public_date,
        paper_public_date_precision,
        paper_file_path,
        papersource_id,
        paper_review_status,
        paper_uploaded_by
    )
    VALUES(%s, %s, %s, %s, %s, %s, %s)
    """

    return execute_insert(
        sql,
        (
            paper_doi,
            paper_name,
            paper_abstract,
            paper_public_date,
            paper_public_date_precision,
            paper_file_path,
            papersource_id,
            paper_review_status,
            paper_uploaded_by
        )
    )

def insert_author(
    author_name,
    author_orcid=None,
    author_email=None
):

    sql = """
    INSERT INTO Author(
        author_name,
        author_orcid,
        author_email
    )
    VALUES(%s, %s, %s)
    """

    return execute_insert(
        sql,
        (
            author_name,
            author_orcid,
            author_email
        )
    )

def insert_keyword(keyword_name):

    sql = """
    INSERT INTO Keyword(
        keyword_name
    )
    VALUES(%s)
    """

    return execute_insert(sql, (keyword_name,))

def link_paper_author(
    paper_id,
    author_id,
    author_role
):

    sql = """
    INSERT INTO PaperAuthor(
        paper_id,
        author_id,
        author_role
    )
    VALUES(%s, %s, %s)
    """

    return execute_update(
        sql,
        (
            paper_id,
            author_id,
            author_role
        )
    )

def link_paper_keyword(
    paper_id,
    keyword_id
):

    sql = """
    INSERT INTO PaperKeyword(
        paper_id,
        keyword_id
    )
    VALUES(%s, %s)
    """

    return execute_update(
        sql,
        (
            paper_id,
            keyword_id
        )
    )

def get_or_create_author(
    author_name,
    author_orcid=None,
    author_email=None
):

    if author_orcid is not None:

        author = get_author_by_orcid(author_orcid)

        if author is not None:
            return author["author_id"]

    author_id = insert_author(
        author_name,
        author_orcid,
        author_email
    )

    return author_id

def get_keyword_by_name(keyword_name):

    sql = """
    SELECT *
    FROM Keyword
    WHERE keyword_name=%s
    """

    return execute_query_one(sql, (keyword_name,))

def get_or_create_keyword(keyword_name):

    keyword_name = keyword_name.strip().lower()

    keyword = get_keyword_by_name(keyword_name)

    if keyword is not None:
        return keyword["keyword_id"]

    keyword_id = insert_keyword(keyword_name)

    return keyword_id

def get_or_create_paper(
    paper_doi,
    paper_name,
    paper_abstract,
    paper_public_date,
    paper_public_date_precision,
    paper_file_path,
    papersource_id,
    paper_review_status,
    paper_uploaded_by
):

    if paper_doi is not None:

        paper = get_paper_by_doi(paper_doi)

        if paper is not None:
            return paper["paper_id"]

    paper_id = insert_paper(
        paper_doi,
        paper_name,
        paper_abstract,
        paper_public_date,
        paper_public_date_precision,
        paper_file_path,
        papersource_id,
        paper_review_status,
        paper_uploaded_by
    )

    return paper_id

def link_paper_author_ignore(
    paper_id,
    author_id,
    author_role
):

    sql = """
    INSERT IGNORE INTO PaperAuthor(
        paper_id,
        author_id,
        author_role
    )
    VALUES(%s, %s, %s)
    """

    return execute_update(
        sql,
        (
            paper_id,
            author_id,
            author_role
        )
    )

def link_paper_keyword_ignore(
    paper_id,
    keyword_id
):

    sql = """
    INSERT IGNORE INTO PaperKeyword(
        paper_id,
        keyword_id
    )
    VALUES(%s, %s)
    """

    return execute_update(
        sql, 
        (
            paper_id,
            keyword_id
        )
    )

def search_papers(search_type, keyword, include_pending=False):
    keyword = keyword.strip()

    status_condition = ""

    if not include_pending:
        status_condition = "AND p.paper_review_status='approved'"

    if keyword == "":
        sql = f"""
        SELECT *
        FROM Paper p
        WHERE 1=1
        {status_condition}
        ORDER BY p.paper_id
        """
        return execute_query(sql)

    if search_type == "title":

        sql = f"""
        SELECT *
        FROM Paper p
        WHERE p.paper_name LIKE %s
        {status_condition}
        ORDER BY p.paper_id
        """

        return execute_query(sql, ("%" + keyword + "%",))

    if search_type == "doi":

        sql = """
        SELECT *
        FROM Paper
        WHERE paper_doi LIKE %s
        {status_condition}
        ORDER BY paper_id
        """

        return execute_query(sql, ("%" + keyword + "%",))

    if search_type == "keyword":

        sql = """
        SELECT DISTINCT
            p.*
        FROM Paper p
        JOIN PaperKeyword pk
        ON p.paper_id = pk.paper_id
        JOIN Keyword k
        ON pk.keyword_id = k.keyword_id
        WHERE k.keyword_name LIKE %s
        {status_condition}
        ORDER BY p.paper_id
        """

        return execute_query(sql, ("%" + keyword.lower() + "%",))

    if search_type == "author":

        sql = """
        SELECT DISTINCT
            p.*
        FROM Paper p
        JOIN PaperAuthor pa
        ON p.paper_id = pa.paper_id
        JOIN Author a
        ON pa.author_id = a.author_id
        WHERE a.author_name LIKE %s
        {status_condition}
        ORDER BY p.paper_id
        """

        return execute_query(sql, ("%" + keyword + "%",))

    return []

def export_query(
    selected_fields,
    paper_keyword=None,
    author_keyword=None,
    institution_keyword=None,
    keyword_keyword=None,
    start_date=None,
    end_date=None,
    include_pending=False
):
    if not selected_fields:
        selected_fields = ["paper_id", "paper_name"]

    select_parts = []

    for field in selected_fields:

        if field not in EXPORT_FIELDS:
            raise ValueError(f"Invalid export field: {field}")

        select_parts.append(f"{EXPORT_FIELDS[field]} AS {field}")

    sql = f"""
    SELECT DISTINCT
        {", ".join(select_parts)}
    FROM Paper p
    LEFT JOIN PaperSource ps
    ON p.papersource_id = ps.papersource_id

    LEFT JOIN PaperAuthor pa
    ON p.paper_id = pa.paper_id

    LEFT JOIN Author a
    ON pa.author_id = a.author_id

    LEFT JOIN Subordination s
    ON a.author_id = s.author_id

    LEFT JOIN AuthorInstitution ai
    ON s.authorinstitution_id = ai.authorinstitution_id

    LEFT JOIN PaperKeyword pk
    ON p.paper_id = pk.paper_id

    LEFT JOIN Keyword k
    ON pk.keyword_id = k.keyword_id

    WHERE 1 = 1
    """

    if not include_pending:
        sql += """
        AND p.paper_review_status='approved'
        """

    params = []

    if paper_keyword:
        sql += """
        AND p.paper_name LIKE %s
        """
        params.append("%" + paper_keyword + "%")

    if author_keyword:
        sql += """
        AND a.author_name LIKE %s
        """
        params.append("%" + author_keyword + "%")

    if institution_keyword:
        sql += """
        AND ai.authorinstitution_name LIKE %s
        """
        params.append("%" + institution_keyword + "%")

    if keyword_keyword:
        sql += """
        AND k.keyword_name LIKE %s
        """
        params.append("%" + keyword_keyword.lower() + "%")

    if start_date:
        sql += """
        AND p.paper_public_date >= %s
        """
        params.append(start_date)

    if end_date:
        sql += """
        AND p.paper_public_date <= %s
        """
        params.append(end_date)

    sql += """
    ORDER BY p.paper_id
    """

    return execute_query(sql, tuple(params))

def create_user(username, password, user_role="user"):
    password_hash = generate_password_hash(password)

    sql = """
    INSERT INTO DBUser(
        dbuser_name,
        password_hash,
        dbuser_role
    )
    VALUES(%s, %s, %s)
    """

    return execute_insert(
        sql,
        (
            username,
            password_hash,
            user_role
        )
    )


def get_user_by_username(username):
    sql = """
    SELECT *
    FROM DBUser
    WHERE dbuser_name=%s
    """

    return execute_query_one(sql, (username,))


def verify_user(username, password):
    user = get_user_by_username(username)

    if user is None:
        return None

    if check_password_hash(user["password_hash"], password):
        return user

    return None

def get_pending_papers():
    sql = """
    SELECT *
    FROM Paper
    WHERE paper_review_status='pending'
    ORDER BY paper_id
    """

    return execute_query(sql)


def approve_paper(paper_id):
    sql = """
    UPDATE Paper
    SET paper_review_status='approved'
    WHERE paper_id=%s
    """

    return execute_update(sql, (paper_id,))


def update_paper_basic(
    paper_id,
    paper_doi,
    paper_name,
    paper_abstract,
    paper_public_date,
    paper_public_date_precision,
    papersource_id
):
    sql = """
    UPDATE Paper
    SET
        paper_doi=%s,
        paper_name=%s,
        paper_abstract=%s,
        paper_public_date=%s,
        paper_public_date_precision=%s,
        papersource_id=%s
    WHERE paper_id=%s
    """

    return execute_update(
        sql,
        (
            paper_doi,
            paper_name,
            paper_abstract,
            paper_public_date,
            paper_public_date_precision,
            papersource_id,
            paper_id
        )
    )

def import_paper_with_relations(
    paper_doi,
    paper_name,
    paper_abstract,
    paper_public_date,
    paper_public_date_precision,
    paper_file_path,
    papersource_id,
    paper_review_status,
    paper_uploaded_by,
    author_names,
    keyword_names
):
    connection = None

    try:
        connection = get_connection()

        with connection.cursor() as cursor:

            if paper_doi:
                cursor.execute(
                    """
                    SELECT *
                    FROM Paper
                    WHERE paper_doi=%s
                    """,
                    (paper_doi,)
                )

                paper = cursor.fetchone()
            else:
                paper = None

            if paper is not None:
                paper_id = paper["paper_id"]
            else:
                cursor.execute(
                    """
                    INSERT INTO Paper(
                        paper_doi,
                        paper_name,
                        paper_abstract,
                        paper_public_date,
                        paper_public_date_precision,
                        paper_file_path,
                        papersource_id,
                        paper_review_status,
                        paper_uploaded_by
                    )
                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        paper_doi,
                        paper_name,
                        paper_abstract,
                        paper_public_date,
                        paper_public_date_precision,
                        paper_file_path,
                        papersource_id,
                        paper_review_status,
                        paper_uploaded_by
                    )
                )

                paper_id = cursor.lastrowid

            for author_name in author_names:

                cursor.execute(
                    """
                    SELECT *
                    FROM Author
                    WHERE author_name=%s
                    """,
                    (author_name,)
                )

                author = cursor.fetchone()

                if author is not None:
                    author_id = author["author_id"]
                else:
                    cursor.execute(
                        """
                        INSERT INTO Author(
                            author_name
                        )
                        VALUES(%s)
                        """,
                        (author_name,)
                    )

                    author_id = cursor.lastrowid

                author_index = author_names.index(author_name)

                if author_index == 0:
                    author_role = "first"
                else:
                    author_role = "co-author"

                cursor.execute(
                    """
                    INSERT IGNORE INTO PaperAuthor(
                        paper_id,
                        author_id,
                        author_role
                    )
                    VALUES(%s, %s, %s)
                    """,
                    (
                        paper_id,
                        author_id,
                        author_role
                    )
                )

            for keyword_name in keyword_names:

                keyword_name = keyword_name.strip().lower()

                if not keyword_name:
                    continue

                cursor.execute(
                    """
                    SELECT *
                    FROM Keyword
                    WHERE keyword_name=%s
                    """,
                    (keyword_name,)
                )

                keyword = cursor.fetchone()

                if keyword is not None:
                    keyword_id = keyword["keyword_id"]
                else:
                    cursor.execute(
                        """
                        INSERT INTO Keyword(
                            keyword_name
                        )
                        VALUES(%s)
                        """,
                        (keyword_name,)
                    )

                    keyword_id = cursor.lastrowid

                cursor.execute(
                    """
                    INSERT IGNORE INTO PaperKeyword(
                        paper_id,
                        keyword_id
                    )
                    VALUES(%s, %s)
                    """,
                    (
                        paper_id,
                        keyword_id
                    )
                )

        connection.commit()

        return paper_id

    except:

        if connection is not None:
            connection.rollback()

        raise

    finally:

        close_connection(connection)

def admin_get_table_names():
    return list(ADMIN_TABLES.keys())


def admin_get_table_config(table_name):
    return ADMIN_TABLES.get(table_name)


def admin_search_table(table_name, filter_column=None, filter_value=None):
    table_config = admin_get_table_config(table_name)

    if table_config is None:
        raise ValueError("Invalid table name")

    columns = table_config["columns"]

    select_clause = ", ".join(columns)

    sql = f"""
    SELECT {select_clause}
    FROM {table_name}
    WHERE 1=1
    """

    params = []

    if filter_column and filter_value:

        if filter_column not in columns:
            raise ValueError("Invalid filter column")

        sql += f"""
        AND {filter_column} LIKE %s
        """

        params.append("%" + filter_value + "%")

    pk = table_config["pk"]

    if pk:
        sql += f"""
        ORDER BY {pk}
        """

    return execute_query(sql, tuple(params))


def admin_get_row_by_pk(table_name, pk_value):
    table_config = admin_get_table_config(table_name)

    if table_config is None:
        raise ValueError("Invalid table name")

    pk = table_config["pk"]

    if pk is None:
        raise ValueError("This table has no single primary key")

    columns = table_config["columns"]

    sql = f"""
    SELECT {", ".join(columns)}
    FROM {table_name}
    WHERE {pk}=%s
    """

    return execute_query_one(sql, (pk_value,))


def admin_update_row_by_pk(table_name, pk_value, update_data):
    table_config = admin_get_table_config(table_name)

    if table_config is None:
        raise ValueError("Invalid table name")

    pk = table_config["pk"]

    if pk is None:
        raise ValueError("This table has no single primary key")

    editable = table_config["editable"]

    clean_data = {}

    for key, value in update_data.items():

        if key in editable:
            clean_data[key] = value if value != "" else None

    if not clean_data:
        return 0

    set_clause = ", ".join([f"{column}=%s" for column in clean_data.keys()])

    params = list(clean_data.values())
    params.append(pk_value)

    sql = f"""
    UPDATE {table_name}
    SET {set_clause}
    WHERE {pk}=%s
    """

    return execute_update(sql, tuple(params))

def get_papersource_by_name(papersource_name):
    sql = """
    SELECT *
    FROM PaperSource
    WHERE papersource_name=%s
    """

    return execute_query_one(sql, (papersource_name,))


def get_or_create_papersource(
    papersource_type,
    papersource_name
):
    if not papersource_name:
        return None

    source = get_papersource_by_name(papersource_name)

    if source is not None:
        return source["papersource_id"]

    sql = """
    INSERT INTO PaperSource(
        papersource_type,
        papersource_name
    )
    VALUES(%s, %s)
    """

    return execute_insert(
        sql,
        (
            papersource_type,
            papersource_name
        )
    )

def update_paper_from_doi_metadata(
    paper_id,
    metadata
):
    papersource_id = None

    if metadata.get("source_name"):

        papersource_id = get_or_create_papersource(
            metadata.get("source_type"),
            metadata.get("source_name")
        )

    sql = """
    UPDATE Paper
    SET
        paper_doi=%s,
        paper_name=%s,
        paper_abstract=%s,
        paper_public_date=%s,
        paper_public_date_precision=%s,
        papersource_id=%s
    WHERE paper_id=%s
    """

    execute_update(
        sql,
        (
            metadata.get("doi"),
            metadata.get("title"),
            metadata.get("abstract"),
            metadata.get("public_date"),
            metadata.get("public_date_precision"),
            papersource_id,
            paper_id
        )
    )

    for index, author in enumerate(metadata.get("authors", [])):

        author_id = get_or_create_author(
            author_name=author["author_name"],
            author_orcid=author.get("author_orcid"),
            author_email=author.get("author_email")
        )

        if index == 0:
            author_role = "first"
        else:
            author_role = "co-author"

        link_paper_author_ignore(
            paper_id,
            author_id,
            author_role
        )

def set_paper_pending(paper_id):
    sql = """
    UPDATE Paper
    SET paper_review_status='pending'
    WHERE paper_id=%s
    """

    return execute_update(sql, (paper_id,))