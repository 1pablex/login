import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from database import init_db
from flask_talisman import Talisman 
from models import Usuario
from repositories.usuario_repository import buscar_por_nome, nome_existe, criar_usuario
from services.email_service import init_mail, enviar_email_recuperacao, gerar_token_recuperacao, token_valido
from services.autenticacao import atualizar_senha, senha_valida, role_valida
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///usuarios.db")

bcrypt = Bcrypt(app)
init_db(app)
init_mail(app)
Talisman(app, force_https=False)

#rota principal

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
            session["usuario_role"] = usuario.role.nome
            return redirect(url_for("index"))
        flash("Usuário ou senha inválidos.", "danger")

    return render_template("login.html", modo="login")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome    = request.form["username"].strip()
        email   = request.form["email"].strip().lower()
        senha   = request.form["password"]
        role_id = int(request.form.get("role_id", 2))

        if nome_existe(nome):
            flash("Usuário já existe.", "danger")
        elif len(senha) < 8:
            flash("Senha deve ter pelo menos 8 caracteres.", "danger")
        elif role_id not in (1, 2):
            flash("Papel inválido.", "danger")
        else:
            hash_senha = bcrypt.generate_password_hash(senha).decode("utf-8")
            criar_usuario(nome, email, hash_senha, role_id)
            flash("Conta criada! Faça login.", "success")
            return redirect(url_for("login"))

    return render_template("cadastro.html", modo="cadastro")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

#recuperar senha
@app.route("/recuperar-senha", methods=["GET", "POST"])
def recuperar_senha():
    if request.method == "POST":
        email   = request.form["email"].strip().lower()
        usuario = Usuario.query.filter_by(email=email).first()
 
        flash("Se esse e-mail estiver cadastrado, você receberá um link em breve.", "success")
 
        if usuario:
            token = gerar_token_recuperacao(usuario)
            link  = url_for("redefinir_senha", token=token, _external=True)
            try:
                enviar_email_recuperacao(usuario.email, usuario.nome, link)
            except Exception as e:
                app.logger.error(f"Erro ao enviar e-mail de recuperação: {e}")
 
        return redirect(url_for("recuperar_senha"))
 
    return render_template("recuperar_senha.html")

#redefinir
@app.route("/redefinir-senha/<token>", methods=["GET", "POST"])
def redefinir_senha(token):
    usuario = Usuario.query.filter_by(reset_token=token).first()

    if not usuario or not token_valido(usuario):
        flash("Link inválido ou expirado.")
        return redirect(url_for("recuperar_senha"))

    if request.method == "POST":
        nova_senha = request.form["password"]
        confirmar  = request.form["confirm_password"]

        if nova_senha != confirmar:
            flash("As senhas não coincidem.")
        else:
            erro = senha_valida(nova_senha)
            if erro:
                flash(erro, "danger")
            else:
                atualizar_senha(usuario, nova_senha)
                flash("Senha redefinida com sucesso! Faça login.", "success")
                return redirect(url_for("login"))

    return render_template("redefinir_senha.html", token=token)


if __name__ == "__main__":
    app.run(debug=True)
