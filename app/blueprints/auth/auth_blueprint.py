from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import User
from app.db import db
from flask_login import login_user, logout_user, login_required
import hashlib

auth_bp = Blueprint('auth', __name__, template_folder='templates', url_prefix='/auth')

def hash(txt):
    return hashlib.sha256(txt.encode('utf-8')).hexdigest()

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        user = db.session.query(User).filter_by(email=email, senha=hash(senha)).first()

        if user:
            login_user(user)
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for('home'))
        else:
            flash("Email ou senha inválidos", "danger")
            return redirect(url_for('auth.login'))

    return render_template('login.html')


@auth_bp.route('/cadastro', methods=['GET','POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        confirmar = request.form['confirmar_senha']

        # Validações
        if senha != confirmar:
            flash("As senhas não coincidem", "danger")
            return redirect(url_for('auth.cadastro'))

        # Checa se já existe usuário
        user_existente = db.session.query(User).filter_by(email=email).first()
        if user_existente:
            flash("Esse email já está cadastrado", "warning")
            return redirect(url_for('auth.cadastro'))

        # Cria usuário
        user = User(nome=nome, email=email, senha=hash(senha))
        db.session.add(user)
        db.session.commit()
        login_user(user)

        flash("Cadastro realizado com sucesso! Bem-vindo(a)!", "success")
        return redirect(url_for('home'))

    return render_template('cadastro.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout realizado.", "info")
    return redirect(url_for('home'))
