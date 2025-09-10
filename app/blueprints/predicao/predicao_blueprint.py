from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import os, uuid
from ...db import db
from ...models import Documentos
from ...utils.file_loader import load_dataframe  #  agora usa a função centralizada

predicao_bp = Blueprint(
    "predicao", __name__, template_folder="templates", url_prefix="/predicao"
)


@predicao_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        file = request.files.get("file")
        if not file or file.filename.strip() == "":
            flash("Nenhum arquivo válido enviado.", "danger")
            return redirect(url_for("predicao.upload"))

        filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"

        save_dir = os.path.join("app", "static", "uploads", f"user_{current_user.id}")
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, filename)

        file.save(save_path)

        try:
            df = load_dataframe(save_path)  # reaproveita utilitário
            tamanho_kb = os.path.getsize(save_path) / 1024
            linhas = len(df)
        except Exception as e:
            flash(f"Erro ao processar arquivo: {str(e)}", "danger")
            return redirect(url_for("predicao.upload"))

        doc = Documentos(
            nome_documento=filename,
            caminho=save_path,
            user_id=current_user.id,
            tamanho_kb=tamanho_kb,
            linhas=linhas,
        )
        db.session.add(doc)
        db.session.commit()

        flash("Arquivo enviado com sucesso!", "success")
        return redirect(url_for("predicao.view_doc", id=doc.id))

    docs = db.session.query(Documentos).filter_by(user_id=current_user.id).all()
    return render_template("predicao.html", documentos=docs)


@predicao_bp.route("/<int:id>")
@login_required
def view_doc(id):
    doc = db.session.query(Documentos).filter_by(id=id, user_id=current_user.id).first()
    if not doc:
        flash("Documento não encontrado.", "danger")
        return redirect(url_for("predicao.page"))

    try:
        df = load_dataframe(doc.caminho)  # idem
        sample = df.head(20).to_dict(orient="records")
        columns = df.columns.tolist()
    except Exception as e:
        flash(f"Erro ao ler o arquivo: {str(e)}", "danger")
        return redirect(url_for("predicao.page"))

    return render_template(
        "predicao.html",
        documento=doc,
        columns=columns,
        sample=sample,
        documentos=db.session.query(Documentos).filter_by(user_id=current_user.id).all(),
    )


@predicao_bp.route("/")
@login_required
def page():
    docs = db.session.query(Documentos).filter_by(user_id=current_user.id).all()
    return render_template("predicao.html", documentos=docs)
