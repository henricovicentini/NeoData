from flask import Blueprint, render_template, redirect, request, url_for, flash
from app.models import User
from app.db import db
from flask_login import current_user, login_required
import hashlib

user_bp = Blueprint("user", __name__, template_folder="templates", url_prefix="/user")

def hash(txt: str) -> str:
    """Retorna SHA-256 hash em string hex."""
    return hashlib.sha256(txt.encode("utf-8")).hexdigest()


@user_bp.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip()
        senha_atual = request.form.get("senha_atual", "")

        # Verifica senha atual
        if not senha_atual or current_user.senha != hash(senha_atual):
            flash("Senha atual incorreta.", "danger")
            return redirect(url_for("user.perfil"))

        if not nome or not email:
            flash("Nome e e-mail são obrigatórios.", "warning")
            return redirect(url_for("user.perfil"))

        try:
            u = db.session.query(User).filter_by(id=current_user.id).first()
            if not u:
                flash("Usuário não encontrado.", "danger")
                return redirect(url_for("user.perfil"))

            # Atualiza dados
            u.nome = nome
            u.email = email

            nova_senha = request.form.get("nova_senha", "").strip()
            if nova_senha:
                u.senha = hash(nova_senha)

            db.session.commit()
            flash("Perfil atualizado com sucesso!", "success")

        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao atualizar perfil: {str(e)}", "danger")

        return redirect(url_for("user.perfil"))

    return render_template("perfil.html", user=current_user)
