"""
Controller principal da aplicação.

Responsabilidade exclusiva: mapear rotas HTTP para respostas.
Toda lógica de negócio está nos services.
"""

import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from flask_talisman import Talisman
from database import init_db, db
from models import Usuario
from repositories.usuario_repository import nome_existe, criar_usuario
from services.autenticacao import (
    validar_credenciais,
    iniciar_sessao,
    encerrar_sessao,
    sessao_ativa,
    senha_valida,
    role_valida,
    atualizar_senha,
)
from services.email_service import (
    init_mail,
    enviar_email_recuperacao,
    enviar_codigo_2fa,
    gerar_token_recuperacao,
    gerar_codigo_2fa,
    codigo_2fa_valido,
    token_valido,
)
from services.auditoria import registrar, listar_logs
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///usuarios.db")

bcrypt = Bcrypt(app)
init_db(app)
init_mail(app)
Talisman(app, force_https=False)


def _ip() -> str:
    """Retorna o IP real do cliente."""
    return request.headers.get("X-Forwarded-For", request.remote_addr)


#Rota principal

@app.route("/")
def index():
    if not sessao_ativa():
        return redirect(url_for("login"))
    return render_template("index.html",
                           nome=session.get("usuario_nome", "Usuário"),
                           role=session.get("usuario_role", ""))


#Login

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nome  = request.form["username"].strip()
        senha = request.form["password"]

        usuario = validar_credenciais(nome, senha)

        if usuario:
            registrar("LOGIN_OK", nome=nome, usuario_id=usuario.id,
                      ip=_ip(), descricao="Credenciais válidas, aguardando 2FA")
            codigo = gerar_codigo_2fa(usuario)
            try:
                enviar_codigo_2fa(usuario.email, usuario.nome, codigo)
            except Exception as e:
                app.logger.error(f"Erro ao enviar código 2FA: {e}")
            session["2fa_usuario_id"] = usuario.id
            return redirect(url_for("verificar_2fa"))

        registrar("LOGIN_FALHA", nome=nome, ip=_ip(),
                  descricao="Usuário ou senha inválidos")
        flash("Usuário ou senha inválidos.", "danger")

    return render_template("login.html", modo="login")


#Verificacao 2FA

@app.route("/verificar-2fa", methods=["GET", "POST"])
def verificar_2fa():
    usuario_id = session.get("2fa_usuario_id")
    if not usuario_id:
        return redirect(url_for("login"))

    usuario = db.session.get(Usuario, usuario_id)

    if request.method == "POST":
        codigo = request.form["codigo"].strip()

        if codigo_2fa_valido(usuario, codigo):
            usuario.codigo_2fa        = None
            usuario.codigo_2fa_expiry = None
            db.session.commit()

            registrar("2FA_OK", nome=usuario.nome, usuario_id=usuario.id,
                      ip=_ip(), descricao="Autenticação 2FA concluída")
            session.pop("2fa_usuario_id", None)
            iniciar_sessao(usuario)
            return redirect(url_for("index"))

        registrar("2FA_FALHA", nome=usuario.nome, usuario_id=usuario.id,
                  ip=_ip(), descricao="Código 2FA inválido ou expirado")
        flash("Código inválido ou expirado.", "danger")

    return render_template("2fa.html")


#Cadastro 

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome    = request.form["username"].strip()
        email   = request.form["email"].strip().lower()
        senha   = request.form["password"]
        role_id = int(request.form.get("role_id", 2))

        erro = senha_valida(senha)

        if nome_existe(nome):
            flash("Usuário já existe.", "danger")
        elif erro:
            flash(erro, "danger")
        elif not role_valida(role_id):
            flash("Papel inválido.", "danger")
        else:
            hash_senha = bcrypt.generate_password_hash(senha).decode("utf-8")
            criar_usuario(nome, email, hash_senha, role_id)
            flash("Conta criada! Faça login.", "success")
            return redirect(url_for("login"))

    return render_template("cadastro.html", modo="cadastro")


#Logout 

@app.route("/logout")
def logout():
    dados = encerrar_sessao()
    registrar("LOGOUT", nome=dados["nome"], usuario_id=dados["id"],
              ip=_ip(), descricao="Sessão encerrada")
    return redirect(url_for("login"))


#Recuperação de senha 

@app.route("/recuperar-senha", methods=["GET", "POST"])
def recuperar_senha():
    if request.method == "POST":
        email   = request.form["email"].strip().lower()
        usuario = Usuario.query.filter_by(email=email).first()

        flash("Se esse e-mail estiver cadastrado, você receberá um link em breve.", "success")

        if usuario:
            registrar("RESET_SOLICIT", nome=usuario.nome, usuario_id=usuario.id,
                      ip=_ip(), descricao="Solicitação de recuperação de senha")
            token = gerar_token_recuperacao(usuario)
            link  = url_for("redefinir_senha", token=token, _external=True)
            try:
                enviar_email_recuperacao(usuario.email, usuario.nome, link)
            except Exception as e:
                app.logger.error(f"Erro ao enviar e-mail de recuperação: {e}")

        return redirect(url_for("recuperar_senha"))

    return render_template("recuperar_senha.html")


@app.route("/redefinir-senha/<token>", methods=["GET", "POST"])
def redefinir_senha(token: str):
    usuario = Usuario.query.filter_by(reset_token=token).first()

    if not usuario or not token_valido(usuario):
        flash("Link inválido ou expirado.", "danger")
        return redirect(url_for("recuperar_senha"))

    if request.method == "POST":
        nova_senha = request.form["password"]
        confirmar  = request.form["confirm_password"]

        if nova_senha != confirmar:
            flash("As senhas não coincidem.", "danger")
        else:
            erro = senha_valida(nova_senha)
            if erro:
                flash(erro, "danger")
            else:
                atualizar_senha(usuario, nova_senha)
                registrar("RESET_OK", nome=usuario.nome, usuario_id=usuario.id,
                          ip=_ip(), descricao="Senha redefinida com sucesso")
                flash("Senha redefinida com sucesso! Faça login.", "success")
                return redirect(url_for("login"))

    return render_template("redefinir_senha.html", token=token)


#Auditoria

@app.route("/auditoria")
def auditoria():
    logs = listar_logs()
    print("\n" + "=" * 70)
    print(f"{'DATA/HORA':<22} {'EVENTO':<15} {'USUÁRIO':<15} {'IP':<16} DESCRIÇÃO")
    print("=" * 70)
    for log in logs:
        data = log.criado_em.strftime("%d/%m/%Y %H:%M:%S")
        print(f"{data:<22} {log.evento:<15} {(log.nome or '—'):<15} {(log.ip or '—'):<16} {log.descricao or '—'}")
    print("=" * 70 + "\n")
    return f"✅ {len(logs)} log(s) impresso(s) no terminal.", 200


if __name__ == "__main__":
    app.run(debug=True)