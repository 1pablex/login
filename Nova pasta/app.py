import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from database import init_db
from repositories.usuario_repository import buscar_por_nome, nome_existe, criar_usuario
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "chave-secreta-dev")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///usuarios.db")

bcrypt = Bcrypt(app)
init_db(app)


@app.route("/")
def index():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    nome = session.get("usuario_nome", "Usuário")
    role = session.get("usuario_role", "")
    return render_template("index.html", nome=nome, role=role)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nome  = request.form["username"].strip()
        senha = request.form["password"]
        usuario = buscar_por_nome(nome)

        if usuario and bcrypt.check_password_hash(usuario.senha_hash, senha):
            session["usuario_id"]   = usuario.id
            session["usuario_nome"] = usuario.nome
            session["usuario_role"] = usuario.role.nome  # "Psicologo" ou "Paciente"
            return redirect(url_for("index"))
        flash("Usuário ou senha inválidos.", "danger")

    return render_template("login.html", modo="login")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome    = request.form["username"].strip()
        senha   = request.form["password"]
        role_id = int(request.form.get("role_id", 2))  # padrão: Paciente

        if nome_existe(nome):
            flash("Usuário já existe.", "danger")
        elif len(senha) < 8:
            flash("Senha deve ter pelo menos 8 caracteres.", "danger")
        elif role_id not in (1, 2):
            flash("Papel inválido.", "danger")
        else:
            hash_senha = bcrypt.generate_password_hash(senha).decode("utf-8")
            criar_usuario(nome, hash_senha, role_id)
            flash("Conta criada! Faça login.", "success")
            return redirect(url_for("login"))

    return render_template("login.html", modo="cadastro")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
