from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, flash, send_file, abort, Response, session

from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, MAX_CONTENT_LENGTH, SECRET_KEY

from pdf.file_handler import (

    sanitize_filename,

    generate_unique_filename,

    compute_file_sha256

)

from pdf.metadata import extract_basic_metadata

from database.dao import (

    get_or_create_paper,

    get_or_create_keyword,

    get_or_create_author,

    link_paper_keyword_ignore,

    link_paper_author_ignore,

    search_papers,

    export_query,

    verify_user,

    get_user_by_username,

    create_user,

    import_paper_with_relations,

    get_pending_papers,

    approve_paper,

    admin_get_table_names,

    admin_get_table_config,

    admin_search_table,

    admin_get_row_by_pk,

    admin_update_row_by_pk,

    get_paper_by_id,

    update_paper_from_doi_metadata,

    set_paper_pending,

    update_paper_basic

)

from export.exporter import rows_to_csv, rows_to_json

from functools import wraps

from pymysql.err import IntegrityError, DataError, OperationalError

from pdf.doi_metadata import get_crossref_metadata_by_doi



app = Flask(__name__)



app.secret_key = SECRET_KEY



app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH



def login_required(func):

    @wraps(func)

    def wrapper(*args, **kwargs):



        if current_user() is None:

            flash("璇峰厛鐧诲綍")

            return redirect(url_for("login"))



        return func(*args, **kwargs)



    return wrapper



def allowed_file(filename):

    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route("/")

@login_required

def index():

    return render_template("index.html")



@app.route("/upload", methods=["GET", "POST"])

@login_required

def upload_pdf():

    if request.method == "GET":

        return render_template("upload.html")



    if "pdf_file" not in request.files:

        flash("没有选择文件")

        return redirect(url_for("upload_pdf"))



    file = request.files["pdf_file"]



    if file.filename == "":

        flash("文件名为空")

        return redirect(url_for("upload_pdf"))



    if not allowed_file(file.filename):

        flash("只允许上传 PDF 文件")

        return redirect(url_for("upload_pdf"))



    upload_folder = Path(app.config["UPLOAD_FOLDER"])

    upload_folder.mkdir(parents=True, exist_ok=True)



    original_filename = file.filename

    safe_name = sanitize_filename(original_filename)

    unique_name = generate_unique_filename(original_filename)



    save_path = upload_folder / unique_name



    file.save(save_path)



    file_hash = compute_file_sha256(save_path)



    metadata = extract_basic_metadata(save_path)



    return render_template(

        "confirm_import.html",

        original_filename=original_filename,

        safe_filename=safe_name,

        stored_filename=unique_name,

        paper_file_path=f"static/uploads/{unique_name}",

        file_hash=file_hash,

        doi=metadata.get("doi") or "",

        title=metadata.get("title") or "",

        abstract="",

        public_date="",

        public_date_precision="day",

        keywords="",

        authors=""

)



@app.route("/confirm_import", methods=["POST"])

@login_required

def confirm_import():

    paper_doi = request.form.get("paper_doi") or None

    paper_name = request.form.get("paper_name")

    paper_abstract = request.form.get("paper_abstract") or None

    paper_public_date = request.form.get("paper_public_date") or None

    paper_public_date_precision = request.form.get("paper_public_date_precision") or None

    paper_file_path = request.form.get("paper_file_path")

    papersource_id = request.form.get("papersource_id") or None



    keywords_text = request.form.get("keywords") or ""

    authors_text = request.form.get("authors") or ""



    if not paper_name:

        flash("论文标题不能为空")

        return redirect(url_for("upload_pdf"))



    skip_review = request.form.get("skip_review") == "1"



    if is_admin() and skip_review:

        paper_review_status = "approved"

    else:

        paper_review_status = "pending"



    keyword_names = [

        item.strip().lower()

        for item in keywords_text.split(",")

        if item.strip()

    ]



    author_names = [

        item.strip()

        for item in authors_text.split(",")

        if item.strip()

    ]



    import_paper_with_relations(

        paper_doi=paper_doi,

        paper_name=paper_name,

        paper_abstract=paper_abstract,

        paper_public_date=paper_public_date,

        paper_public_date_precision=paper_public_date_precision,

        paper_file_path=paper_file_path,

        papersource_id=papersource_id,

        paper_review_status=paper_review_status,

        paper_uploaded_by=current_user()["dbuser_id"],

        author_names=author_names,

        keyword_names=keyword_names

    )



    flash("论文已确认导入数据库")



    return redirect(url_for("index"))



@app.route("/search", methods=["GET"])

@login_required

def search():

    search_type = request.args.get("search_type", "title")

    keyword = request.args.get("keyword", "")



    papers = None



    if keyword.strip() != "":

        papers = search_papers(search_type, keyword, include_pending=is_admin())



    return render_template(

        "search.html",

        papers=papers,

        search_type=search_type,

        keyword=keyword,

        current_user=current_user()

    )



@app.route("/paper/<int:paper_id>/download")

@login_required

def download_paper(paper_id):

    paper = get_paper_by_id(paper_id)



    if paper is None:

        abort(404)



    if not is_admin() and paper["paper_review_status"] != "approved":

        abort(403)



    paper_file_path = paper.get("paper_file_path")



    if not paper_file_path:

        abort(404)



    upload_root = Path(app.config["UPLOAD_FOLDER"]).resolve()



    file_path = (Path.cwd() / paper_file_path).resolve()



    if upload_root not in file_path.parents:

        abort(403)



    if not file_path.exists() or not file_path.is_file():

        abort(404)



    return send_file(

        file_path,

        as_attachment=True,

        download_name=f"{paper['paper_name']}.pdf"

    )



@app.route("/export", methods=["GET", "POST"])

@login_required

def export_data():

    if request.method == "GET":

        return render_template("export.html")



    selected_fields = request.form.getlist("fields")



    export_format = request.form.get("export_format", "csv")



    paper_keyword = request.form.get("paper_keyword") or None

    author_keyword = request.form.get("author_keyword") or None

    institution_keyword = request.form.get("institution_keyword") or None

    keyword_keyword = request.form.get("keyword_keyword") or None

    start_date = request.form.get("start_date") or None

    end_date = request.form.get("end_date") or None



    rows = export_query(

        selected_fields=selected_fields,

        paper_keyword=paper_keyword,

        author_keyword=author_keyword,

        institution_keyword=institution_keyword,

        keyword_keyword=keyword_keyword,

        start_date=start_date,

        end_date=end_date,

        include_pending=is_admin()

    )



    if export_format == "json":



        content = rows_to_json(rows)



        return Response(

            content,

            mimetype="application/json",

            headers={

                "Content-Disposition": "attachment; filename=export.json"

            }

        )



    content = rows_to_csv(rows)



    return Response(

        content,

        mimetype="text/csv; charset=utf-8",

        headers={

            "Content-Disposition": "attachment; filename=export.csv"

        }

    )



def current_user():

    return session.get("user")





def is_admin():

    user = current_user()



    return user is not None and user["dbuser_role"] == "admin"





def login_required(func):

    @wraps(func)

    def wrapper(*args, **kwargs):



        if current_user() is None:

            flash("璇峰厛鐧诲綍")

            return redirect(url_for("login"))



        return func(*args, **kwargs)



    return wrapper





def admin_required(func):

    @wraps(func)

    def wrapper(*args, **kwargs):



        if not is_admin():

            flash("需要管理员权限")

            return redirect(url_for("index"))



        return func(*args, **kwargs)



    return wrapper



@app.route("/login", methods=["GET", "POST"])

def login():

    if request.method == "GET":

        return render_template("login.html")



    username = request.form.get("username")

    password = request.form.get("password")



    user = verify_user(username, password)



    if user is None:

        flash("用户名或密码错误")

        return redirect(url_for("login"))



    session["user"] = {

        "dbuser_id": user["dbuser_id"],

        "dbuser_name": user["dbuser_name"],

        "dbuser_role": user["dbuser_role"]

    }



    flash("鐧诲綍鎴愬姛")



    return redirect(url_for("index"))





@app.route("/logout")

def logout():

    session.clear()



    flash("已退出登录")



    return redirect(url_for("login"))



@app.route("/admin/pending")

@login_required

@admin_required

def admin_pending():

    papers = get_pending_papers()



    return render_template(

        "admin_pending.html",

        papers=papers

    )



@app.context_processor

def inject_user():

    return {

        "current_user": current_user()

    }



@app.route("/register", methods=["GET", "POST"])

def register():

    if request.method == "GET":

        return render_template("register.html")



    username = request.form.get("username")

    password = request.form.get("password")

    confirm_password = request.form.get("confirm_password")



    if password != confirm_password:

        flash("请输入相同的密码")

        return redirect(url_for("register"))



    existing_user = get_user_by_username(username)



    if existing_user is not None:

        flash("用户名已存在")

        return redirect(url_for("register"))



    create_user(

        username=username,

        password=password,

        user_role="user"

    )



    flash("注册成功")



    return redirect(url_for("login"))



@app.route("/admin/paper/<int:paper_id>/approve", methods=["POST"])

@login_required

@admin_required

def admin_approve_paper(paper_id):

    approve_paper(paper_id)



    flash("论文已审核通过")



    return redirect(url_for("admin_pending"))



@app.route("/admin/database", methods=["GET"])

@login_required

@admin_required

def admin_database():

    tables = admin_get_table_names()



    return render_template(

        "admin_database.html",

        tables=tables

    )



@app.route("/admin/database/<table_name>", methods=["GET"])

@login_required

@admin_required

def admin_table_view(table_name):

    table_config = admin_get_table_config(table_name)



    if table_config is None:

        abort(404)



    filter_column = request.args.get("filter_column")

    filter_value = request.args.get("filter_value")



    rows = admin_search_table(

        table_name,

        filter_column,

        filter_value

    )



    return render_template(

        "admin_table.html",

        table_name=table_name,

        table_config=table_config,

        rows=rows,

        filter_column=filter_column,

        filter_value=filter_value

    )



@app.route("/admin/database/<table_name>/<int:pk_value>/edit", methods=["GET", "POST"])

@login_required

@admin_required

def admin_edit_row(table_name, pk_value):

    table_config = admin_get_table_config(table_name)



    if table_config is None:

        abort(404)



    if table_config["pk"] is None:

        flash("该表没有单一主键，暂不支持通用编辑")

        return redirect(url_for("admin_table_view", table_name=table_name))



    if request.method == "GET":



        row = admin_get_row_by_pk(table_name, pk_value)



        if row is None:

            abort(404)



        return render_template(

            "admin_edit_row.html",

            table_name=table_name,

            table_config=table_config,

            row=row

        )



    update_data = {}



    for column in table_config["editable"]:

        update_data[column] = request.form.get(column)



    try:

        admin_update_row_by_pk(

            table_name,

            pk_value,

            update_data

        )



        flash("操作成功")



    except (IntegrityError, DataError, OperationalError) as e:

        flash(f"修改失败：{e}")



    return redirect(url_for("admin_table_view", table_name=table_name))



@app.route("/admin/paper/<int:paper_id>/fetch_doi_metadata", methods=["POST"])

@login_required

@admin_required

def admin_fetch_doi_metadata(paper_id):

    paper = get_paper_by_id(paper_id)



    if paper is None:

        abort(404)



    doi = paper.get("paper_doi")



    if not doi:

        flash("该论文没有 DOI，无法联网查询")

        return redirect(url_for("admin_pending"))



    metadata = get_crossref_metadata_by_doi(doi)



    if metadata is None:

        flash("未能通过 DOI 查询到元数据")

        return redirect(url_for("admin_pending"))



    update_paper_from_doi_metadata(

        paper_id,

        metadata

    )



    flash("已通过 DOI 自动补全论文信息")



    return redirect(url_for("admin_pending"))



@app.route("/admin/paper/<int:paper_id>/review", methods=["GET", "POST"])

@login_required

@admin_required

def admin_review_paper(paper_id):

    paper = get_paper_by_id(paper_id)



    if paper is None:

        abort(404)



    if request.method == "GET":

        return render_template(

            "admin_review_paper.html",

            paper=paper

        )



    paper_doi = request.form.get("paper_doi") or None

    paper_name = request.form.get("paper_name")

    paper_abstract = request.form.get("paper_abstract") or None

    paper_public_date = request.form.get("paper_public_date") or None

    paper_public_date_precision = request.form.get("paper_public_date_precision") or None

    papersource_id = request.form.get("papersource_id") or None



    action = request.form.get("action")



    update_paper_basic(

        paper_id,

        paper_doi,

        paper_name,

        paper_abstract,

        paper_public_date,

        paper_public_date_precision,

        papersource_id

    )



    if action == "approve":

        approve_paper(paper_id)

        flash("论文已审核通过")

    else:

        flash("论文信息已保存，仍处于待审核状态")



    return redirect(url_for("admin_pending"))



@app.route("/admin/paper/<int:paper_id>/set_pending", methods=["POST"])

@login_required

@admin_required

def admin_set_paper_pending(paper_id):

    paper = get_paper_by_id(paper_id)



    if paper is None:

        abort(404)



    set_paper_pending(paper_id)



    flash("论文已设为待审核状态")



    return redirect(url_for("search"))



if __name__ == "__main__":

    app.run(host='0.0.0.0', debug=True)

