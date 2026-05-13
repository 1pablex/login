import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from flask_talisman import Talisman
from database import init_db, db
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models import Usuario
from repositories.usuario_repository import nome_existe, criar_usuario, buscar_por_id
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
from services.perfil_service import atualizar_dados
from services.exclusao_service import excluir_conta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") #3.6 - via .env
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///usuarios.db")

bcrypt = Bcrypt(app) ###criptografia de senhas 1.1 / 3.5 
init_db(app)
init_mail(app)
Talisman(app, force_https=False) #3.1 e 3.2(talisman) quando por em produção colocar force_https=True e configurar o certificado SSL
limiter = Limiter(app=app, key_func=get_remote_address)  #proteção como rage limit


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


#1.7 -Login

@app.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute") #1.11 rage limit
def login():
    if request.method == "POST":
        nome  = request.form["username"].strip()
        senha = request.form["password"]

        usuario = validar_credenciais(nome, senha)

        if usuario:
            #5.1 - log de autenticacao para auditoria
            registrar("LOGIN_OK", nome=nome, usuario_id=usuario.id,
                      ip=_ip(), descricao="Credenciais válidas, aguardando 2FA")
            codigo = gerar_codigo_2fa(usuario)  # 1.5 - 2FA - gera um código de 6 digitos e armazena no banco com validade de 5 minutos
            try:
                enviar_codigo_2fa(usuario.email, usuario.nome, codigo)
            except Exception as e:
                app.logger.error(f"Erro ao enviar código 2FA: {e}")
            session["2fa_usuario_id"] = usuario.id
            return redirect(url_for("verificar_2fa")) #redireciona para a tela de verificação do código 2FA
        #5.2 - log de falha de autenticacao para auditoria
        registrar("LOGIN_FALHA", nome=nome, ip=_ip(),
                  descricao="Usuário ou senha inválidos")
        flash("Usuário ou senha inválidos.", "danger")

    return render_template("login.html", modo="login")
@app.errorhandler(429)
def limite_excedido(e):
    return render_template("login.html", modo="login", 
                           erro="Muitas tentativas. Aguarde 1 minuto."), 429


#1.6 - Verificacao 2FA funçao services/email_service.py

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
            #5.2 - log de sucesso na verificação 2FA para auditoria
            registrar("2FA_OK", nome=usuario.nome, usuario_id=usuario.id,
                      ip=_ip(), descricao="Autenticação 2FA concluída")
            session.pop("2fa_usuario_id", None)
            iniciar_sessao(usuario)
            return redirect(url_for("index"))
        #5.2 - log de falha na verificação 2FA para auditoria
        registrar("2FA_FALHA", nome=usuario.nome, usuario_id=usuario.id,
                  ip=_ip(), descricao="Código 2FA inválido ou expirado")
        flash("Código inválido ou expirado.", "danger")

    return render_template("verificar_2fa.html")


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
            hash_senha = bcrypt.generate_password_hash(senha).decode("utf-8") #salt unico por usuario 1.3 (cria um salt aleatório para cada senha, aumentando a segurança contra ataques)
            criar_usuario(nome, email, hash_senha, role_id)
            flash("Conta criada! Faça login.", "success")
            return redirect(url_for("login"))

    return render_template("cadastro.html", modo="cadastro")


#1.10 - Logout 

@app.route("/logout")
def logout():
    dados = encerrar_sessao()
    registrar("LOGOUT", nome=dados["nome"], usuario_id=dados["id"],
              ip=_ip(), descricao="Sessão encerrada")
    return redirect(url_for("login"))


# 2.1 - Recuperação de senha 

@app.route("/recuperar-senha", methods=["GET", "POST"])
def recuperar_senha():
    if request.method == "POST":
        email   = request.form["email"].strip().lower()
        usuario = Usuario.query.filter_by(email=email).first()

        flash("Se esse e-mail estiver cadastrado, você receberá um link em breve.", "success")
        #2.6 log de solicitação de recuperação de senha
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
    #2.5 falha token de recuperação de senha
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
                #2.7 log de sucesso ou falha na redefinição de senha
                atualizar_senha(usuario, nova_senha)
                registrar("RESET_OK", nome=usuario.nome, usuario_id=usuario.id,
                          ip=_ip(), descricao="Senha redefinida com sucesso")
                flash("Senha redefinida com sucesso! Faça login.", "success")
                return redirect(url_for("login"))

    return render_template("redefinir_senha.html", token=token)

@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    if not sessao_ativa():
        return redirect(url_for("login"))
 
    usuario = buscar_por_id(session["usuario_id"])
 
    if request.method == "POST":
        novo_nome   = request.form["username"].strip()
        nova_senha  = request.form.get("nova_senha", "").strip() or None
        senha_atual = request.form.get("senha_atual", "").strip() or None
 
        erro = atualizar_dados(usuario, novo_nome, nova_senha, senha_atual)
        if erro:
            flash(erro, "danger")
        else:
            session["usuario_nome"] = usuario.nome
            registrar("PERFIL_ATUALIZADO", nome=usuario.nome, usuario_id=usuario.id,
                      ip=_ip(), descricao="Dados do perfil atualizados")
            flash("Dados atualizados com sucesso!", "success")
 
    return render_template("perfil.html", usuario=usuario)
 
 #4.10 - exclusão de conta
@app.route("/deletar-conta", methods=["POST"])
def deletar_conta():
    if not sessao_ativa():
        return redirect(url_for("login"))
 
    usuario = buscar_por_id(session["usuario_id"])
    senha   = request.form.get("senha_confirmacao", "")
 
    erro = excluir_conta(usuario, senha)
    if erro:
        flash(erro, "danger")
        return redirect(url_for("perfil"))
 
    registrar("CONTA_DELETADA", nome=usuario.nome,
              ip=_ip(), descricao="Conta excluída pelo titular")
    session.clear()
    flash("Sua conta foi excluída com sucesso.", "success")
    return redirect(url_for("login"))


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
    return f" {len(logs)} log(s) impresso(s) no terminal.", 200


if __name__ == "__main__":
    app.run(debug=True)