# main.py
import os
import io
from datetime import datetime

import pandas as pd
from flask import (
    Flask, render_template, request, jsonify, send_file,
    session, redirect, url_for, flash
)
from flask_login import LoginManager, current_user, login_required
from flask_migrate import upgrade
from dotenv import load_dotenv

# imports locais
from .db import db, migrate
from .models import User, Documentos, RawRecord, CleanRecord
from .blueprints.auth.auth_blueprint import auth_bp
from .blueprints.user.user_blueprint import user_bp
from .blueprints.predicao.predicao_blueprint import predicao_bp
from .cleaning import analyze_dataframe, clean_dataframe, validate_dataframe
from .utils.file_loader import load_dataframe
from .utils.report_generator import gerar_relatorio_pdf

load_dotenv()


def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///neodata.db")
    app.config["UPLOAD_FOLDER"] = os.environ.get("UPLOAD_FOLDER", "uploads")
    app.config["OUTPUT_FOLDER"] = os.environ.get("OUTPUT_FOLDER", "outputs")

    # Secret key
    secret_key = os.getenv("SECRET_KEY") or os.urandom(24).hex()
    app.secret_key = secret_key

    # Pastas
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)

    # DB + Migrate
    db.init_app(app)
    migrate.init_app(app, db)

    # Login
    lm = LoginManager()
    lm.login_view = "auth.login"
    lm.init_app(app)

    @lm.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(predicao_bp)

    with app.app_context():
        try:
            upgrade()
        except Exception:
            pass

    # ---------------- Upload ----------------
    @app.route("/upload", methods=["GET"])
    @login_required
    def show_upload_form():
        return render_template("upload_form.html")

    @app.route("/api/upload", methods=["GET", "POST"])
    @login_required
    def api_upload():
        if request.method == "GET":
            return redirect(url_for("show_upload_form"))

        file = request.files.get("file")
        if not file or file.filename.strip() == "":
            return render_template("upload_result.html", error="Nenhum arquivo enviado.")

        allowed_ext = (".csv", ".xls", ".xlsx", ".json", ".zip")
        if not file.filename.lower().endswith(allowed_ext):
            return render_template("upload_result.html", error="Formato não suportado.")

        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        safe_name = f"{timestamp}_{file.filename}"
        save_dir = os.path.join(app.config["UPLOAD_FOLDER"], f"user_{current_user.id}")
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, safe_name)

        try:
            file_bytes = file.read()
            size_kb = len(file_bytes) / 1024
            file.seek(0)
            df = load_dataframe(file)
        except Exception as e:
            return render_template("upload_result.html", error=f"Erro ao processar arquivo: {str(e)}")

        file.seek(0)
        file.save(save_path)

        doc = Documentos(
            nome_documento=file.filename,
            user_id=current_user.id,
            caminho=save_path,
            tamanho_kb=float(size_kb),
            linhas=int(df.shape[0]),
            uploaded_at=datetime.utcnow()
        )
        db.session.add(doc)
        db.session.commit()

        db.session.query(RawRecord).filter_by(documento_id=doc.id).delete()
        for rec in df.to_dict(orient="records"):
            db.session.add(RawRecord(documento_id=doc.id, data=rec))
        db.session.commit()

        session["last_doc_id"] = doc.id

        return render_template(
            "upload_result.html",
            message=f"Arquivo '{file.filename}' salvo com sucesso ({size_kb:.2f} KB, {df.shape[0]} linhas).",
            columns=df.columns.tolist()[:15],
            sample=df.head(10).to_dict(orient="records"),
            doc_id=doc.id,
        )

    # ---------------- Limpeza ----------------
    @app.route("/api/clean/run", methods=["POST"])
    @login_required
    def api_clean_run():
        doc_id = request.args.get("doc_id", type=int) or session.get("last_doc_id")
        if not doc_id:
            return render_template("clean_result.html", error="Documento não informado.")

        doc = Documentos.query.filter_by(id=doc_id, user_id=current_user.id).first()
        if not doc:
            return render_template("clean_result.html", error="Acesso negado ao documento.")

        raw_q = RawRecord.query.filter_by(documento_id=doc.id).all()
        if not raw_q:
            return render_template("clean_result.html", error="Nenhum dado encontrado.")

        df_raw = pd.DataFrame([r.data for r in raw_q])

        before = analyze_dataframe(df_raw)
        df_cleaned = clean_dataframe(df_raw)
        after = analyze_dataframe(df_cleaned)
        val = validate_dataframe(df_cleaned)

        summary = {
            "linhas_antes": int(df_raw.shape[0]) if not df_raw.empty else 0,
            "linhas_depois": int(df_cleaned.shape[0]),
            "colunas": int(df_cleaned.shape[1]),
            "ausentes_antes": int(df_raw.isna().sum().sum()) if not df_raw.empty else 0,
            "ausentes_depois": int(df_cleaned.isna().sum().sum()),
            "duplicadas_antes": int(df_raw.duplicated().sum()) if not df_raw.empty else 0,
            "duplicadas_depois": int(df_cleaned.duplicated().sum()),
        }

        db.session.query(CleanRecord).filter_by(documento_id=doc.id).delete()
        for rec in df_cleaned.to_dict(orient="records"):
            db.session.add(CleanRecord(documento_id=doc.id, data=rec))
        db.session.commit()

        pdf_buffer = gerar_relatorio_pdf(doc.id, df_raw, df_cleaned, before, after, val)
        pdf_path = os.path.join(app.config["OUTPUT_FOLDER"], f"relatorio_{doc.id}.pdf")
        with open(pdf_path, "wb") as f:
            f.write(pdf_buffer.getvalue())

        return render_template(
            "clean_result.html",
            message=f"Limpeza concluída ({len(df_cleaned)} linhas). Relatório salvo em outputs.",
            summary=summary,
            validation=val,
            columns=df_cleaned.columns.tolist(),
            sample=df_cleaned.head(5).to_dict(orient="records"),
            doc_id=doc.id,
        )

    # ---------------- Excluir Documento ----------------
    @app.route("/delete/<int:doc_id>", methods=["POST"])
    @login_required
    def delete_doc(doc_id):
        doc = Documentos.query.filter_by(id=doc_id, user_id=current_user.id).first()
        if not doc:
            flash("Documento não encontrado ou você não tem permissão.", "danger")
            return redirect(url_for("home"))

        db.session.query(RawRecord).filter_by(documento_id=doc.id).delete()
        db.session.query(CleanRecord).filter_by(documento_id=doc.id).delete()

        if os.path.exists(doc.caminho):
            try:
                os.remove(doc.caminho)
            except Exception:
                pass

        db.session.delete(doc)
        db.session.commit()

        flash("Documento excluído com sucesso.", "success")
        return redirect(url_for("home"))

    # ---------------- Downloads ----------------

    @app.route("/api/download/clean.csv")
    @login_required
    def download_csv():
        doc_id = request.args.get("doc_id", type=int)
        if not doc_id:
            return jsonify({"error": "Documento não informado"}), 400

        records = CleanRecord.query.filter_by(documento_id=doc_id).all()
        if not records:
            return jsonify({"error": "Nenhum dado limpo"}), 404

        df = pd.DataFrame([r.data for r in records])
        out = io.StringIO()
        df.to_csv(out, index=False)
        return send_file(
            io.BytesIO(out.getvalue().encode()),
            as_attachment=True,
            download_name=f"dados_limpos_{doc_id}.csv",
            mimetype="text/csv",
        )

    @app.route("/api/download/clean.xlsx")
    @login_required
    def download_xlsx():
        doc_id = request.args.get("doc_id", type=int)
        if not doc_id:
            return jsonify({"error": "Documento não informado"}), 400

        records = CleanRecord.query.filter_by(documento_id=doc_id).all()
        if not records:
            return jsonify({"error": "Nenhum dado limpo"}), 404

        df = pd.DataFrame([r.data for r in records])
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Limpos")
        out.seek(0)

        return send_file(
            out,
            as_attachment=True,
            download_name=f"dados_limpos_{doc_id}.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    
    @app.route("/api/download/clean.json") 
    @login_required
    def download_json():
        doc_id = request.args.get("doc_id", type=int)
        if not doc_id:
            return jsonify({"error": "Documento não informado"}), 400

        records = CleanRecord.query.filter_by(documento_id=doc_id).all()
        if not records:
            return jsonify({"error": "Nenhum dado limpo"}), 404

        df = pd.DataFrame([r.data for r in records])
        out = io.StringIO()
        df.to_json(out, orient="records", force_ascii=False, indent=2)  # Exporta como JSON formatado
        out.seek(0)

        return send_file(
            io.BytesIO(out.getvalue().encode("utf-8")),  # Cria o arquivo JSON em memória
            as_attachment=True,
            download_name=f"dados_limpos_{doc_id}.json",  # Nome do arquivo
            mimetype="application/json",  # Tipo MIME para JSON
    )


    @app.route("/api/download/report.pdf")
    @login_required
    def download_report_pdf():
        doc_id = request.args.get("doc_id", type=int)
        if not doc_id:
            return jsonify({"error": "Documento não informado"}), 400

        pdf_path = os.path.join(app.config["OUTPUT_FOLDER"], f"relatorio_{doc_id}.pdf")
        if not os.path.exists(pdf_path):
            return jsonify({"error": "Relatório ainda não foi gerado."}), 404

        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"relatorio_{doc_id}.pdf",
            mimetype="application/pdf",
        )

    # ---------------- Home & Dashboard ----------------
    @app.route("/")
    @login_required
    def home():
        documents = Documentos.query.filter_by(user_id=current_user.id).order_by(Documentos.id.desc()).all()
        return render_template("index.html", documents=documents)

    @app.route("/dashboard")
    @login_required
    def dashboard_redirect():
        doc = Documentos.query.filter_by(user_id=current_user.id).order_by(Documentos.id.desc()).first()
        if not doc:
            flash("Nenhum documento encontrado. Faça upload primeiro.", "warning")
            return redirect(url_for("home"))
        return redirect(url_for("dashboard", doc_id=doc.id))

    @app.route("/dashboard/<int:doc_id>")
    @login_required
    def dashboard(doc_id):
        doc = Documentos.query.filter_by(id=doc_id, user_id=current_user.id).first()
        if not doc:
            flash("Acesso negado ao documento.", "danger")
            return redirect(url_for("home"))

        records_raw = RawRecord.query.filter_by(documento_id=doc.id).all()
        records_clean = CleanRecord.query.filter_by(documento_id=doc.id).all()

        if not records_clean:
            flash("Nenhum dado limpo encontrado. Execute a limpeza primeiro.", "warning")
            return redirect(url_for("home"))

        df_raw = pd.DataFrame([r.data for r in records_raw]) if records_raw else pd.DataFrame()
        df_clean = pd.DataFrame([r.data for r in records_clean])

        stats = df_clean.describe(include="all").transpose().reset_index().fillna("").to_dict(orient="records")

        summary = {
            "linhas_antes": int(df_raw.shape[0]) if not df_raw.empty else 0,
            "linhas_depois": int(df_clean.shape[0]),
            "colunas": int(df_clean.shape[1]),
            "ausentes_antes": int(df_raw.isna().sum().sum()) if not df_raw.empty else 0,
            "ausentes_depois": int(df_clean.isna().sum().sum()),
            "duplicadas_antes": int(df_raw.duplicated().sum()) if not df_raw.empty else 0,
            "duplicadas_depois": int(df_clean.duplicated().sum()),
        }

        numeric_cols = sorted(df_clean.select_dtypes(include="number").columns.tolist())
        charts = {}
        for col in numeric_cols:
            before_series = df_raw[col].fillna(0).tolist() if (not df_raw.empty and col in df_raw.columns) else []
            after_series = df_clean[col].fillna(0).tolist()
            labels = list(range(len(after_series)))
            charts[col] = {
                "labels": labels,
                "before": before_series if before_series else [0] * len(after_series),
                "after": after_series
            }

        return render_template(
            "dashboard.html",
            doc_id=doc.id,
            clean_exists=True,
            stats=stats,
            summary=summary,
            charts=charts
        )

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
