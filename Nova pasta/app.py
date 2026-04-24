import os
import secrets
from datetime import datetime, timedelta
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from database import init_db, db
from models import Usuario
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




# ── Recuperação de senha ────────────────────────────────────────────────────

def enviar_email_recuperacao(destinatario_email, destinatario_nome, link):
    """Envia e-mail de recuperação via API do Brevo."""
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": os.environ.get("BREVO_API_KEY", ""),
    }
    payload = {
        "sender": {
            "name": os.environ.get("BREVO_SENDER_NAME", "Suporte"),
            "email": os.environ.get("BREVO_SENDER_EMAIL"),
        },
        "to": [{"email": destinatario_email, "name": destinatario_nome}],
        "subject": "Recuperação de senha",
        "htmlContent": f"""
            <p>Olá, <strong>{destinatario_nome}</strong>!</p>
            <p>Clique no botão abaixo para redefinir sua senha.
               O link expira em <strong>1 hora</strong>.</p>
            <p>
              <a href="{link}"
                 style="background:#1D9E75;color:white;padding:10px 20px;
                        border-radius:8px;text-decoration:none;font-weight:600;">
                Redefinir senha
              </a>
            </p>
            <p style="color:#999;font-size:12px;">
              Se você não solicitou isso, ignore este e-mail.
            </p>
        """,
    }
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()


@app.route("/recuperar-senha", methods=["GET", "POST"])
def recuperar_senha():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        usuario = Usuario.query.filter_by(email=email).first()

        # Sempre mostra a mesma mensagem (evita enumeração de e-mails)
        flash("Se esse e-mail estiver cadastrado, você receberá um link em breve.", "success")

        if usuario:
            token = secrets.token_urlsafe(32)
            usuario.reset_token = token
            usuario.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()

            link = url_for("redefinir_senha", token=token, _external=True)
            try:
                enviar_email_recuperacao(usuario.email, usuario.nome, link)
            except Exception as e:
                app.logger.error(f"Erro ao enviar e-mail de recuperação: {e}")

        return redirect(url_for("recuperar_senha"))

    return render_template("recuperar_senha.html")


@app.route("/redefinir-senha/<token>", methods=["GET", "POST"])
def redefinir_senha(token):
    usuario = Usuario.query.filter_by(reset_token=token).first()

    if not usuario or usuario.reset_token_expiry < datetime.utcnow():
        flash("Link inválido ou expirado.", "danger")
        return redirect(url_for("recuperar_senha"))

    if request.method == "POST":
        nova_senha = request.form["password"]
        confirmar  = request.form["confirm_password"]

        if nova_senha != confirmar:
            flash("As senhas não coincidem.", "danger")
        elif len(nova_senha) < 8:
            flash("Senha deve ter pelo menos 8 caracteres.", "danger")
        else:
            usuario.senha_hash         = bcrypt.generate_password_hash(nova_senha).decode("utf-8")
            usuario.reset_token        = None
            usuario.reset_token_expiry = None
            db.session.commit()
            flash("Senha redefinida com sucesso! Faça login.", "success")
            return redirect(url_for("login"))

    return render_template("redefinir_senha.html", token=token)


if __name__ == "__main__":
    app.run(debug=True)
