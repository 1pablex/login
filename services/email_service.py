import os
import secrets
import random
import requests
from datetime import datetime, timedelta
from database import db


def init_mail(app):
    """Mantido para compatibilidade com app.py."""
    pass


def _post_brevo(payload: dict):
    """Envia e-mail via API REST do Brevo."""
    api_key      = os.environ.get("BREVO_API_KEY")
    sender_email = os.environ.get("BREVO_SENDER_EMAIL")
    sender_name  = os.environ.get("BREVO_SENDER_NAME", "Suporte")

    if not api_key:
        raise ValueError("BREVO_API_KEY não definida no .env")

    payload["sender"] = {"name": sender_name, "email": sender_email}
    #3.3 (HTTPS na chamada da API)
    response = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": api_key,
        },
        json=payload,
        timeout=10,
    )

    if response.status_code not in (200, 201):
        raise RuntimeError(f"Brevo API error {response.status_code}: {response.text}")


def enviar_email_recuperacao(destinatario_email: str, destinatario_nome: str, link: str):
    """Envia e-mail de recuperação de senha."""
    _post_brevo({
        "to": [{"email": destinatario_email, "name": destinatario_nome}],
        "subject": "Recuperação de senha",
        "htmlContent": f"""
        <p>Olá, <strong>{destinatario_nome}</strong>!</p>
        <p>Clique no botão abaixo para redefinir sua senha. O link expira em <strong>1 hora</strong>.</p>
        <p>
            <a href="{link}"
               style="display:inline-block;padding:12px 24px;background:#4F46E5;
                      color:#fff;border-radius:6px;text-decoration:none;font-weight:bold;">
                Redefinir senha
            </a>
        </p>
        <p>Se você não solicitou a recuperação, ignore este e-mail.</p>
        """,
    })


def enviar_codigo_2fa(destinatario_email: str, destinatario_nome: str, codigo: str):
    """Envia código de verificação 2FA por e-mail."""
    _post_brevo({
        "to": [{"email": destinatario_email, "name": destinatario_nome}],
        "subject": "Código de verificação",
        "htmlContent": f"""
        <p>Olá, <strong>{destinatario_nome}</strong>!</p>
        <p>Seu código de verificação é:</p>
        <p style="font-size:32px;font-weight:bold;letter-spacing:8px;color:#4F46E5;">
            {codigo}
        </p>
        <p>Este código expira em <strong>10 minutos</strong>.</p>
        <p>Se não foi você, ignore este e-mail.</p>
        """,
    })


def gerar_codigo_2fa(usuario) -> str:
    """Gera e persiste um código 2FA de 6 dígitos."""
    codigo = f"{random.randint(0, 999999):06d}"
    usuario.codigo_2fa        = codigo
    usuario.codigo_2fa_expiry = datetime.utcnow() + timedelta(minutes=10)
    db.session.commit()
    return codigo


def codigo_2fa_valido(usuario, codigo: str) -> bool:
    """Verifica se o código 2FA é válido e não expirou."""
    if not usuario.codigo_2fa or not usuario.codigo_2fa_expiry:
        return False
    if datetime.utcnow() > usuario.codigo_2fa_expiry:
        return False
    return usuario.codigo_2fa == codigo

# 2.2 e 2.3 - token criptografado para recuperação de senha
def gerar_token_recuperacao(usuario) -> str:
    """Gera e persiste um token de recuperação no usuário."""
    token = secrets.token_urlsafe(32)  #2.2 - token criptografado para recuperação de senha, usando secrets para gerar o token
    usuario.reset_token        = token
    usuario.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
    db.session.commit()
    return token

# 2.5 - validação do token de recuperação de senha
def token_valido(usuario) -> bool:
    """Verifica se o token ainda está dentro do prazo."""
    if not usuario or not usuario.reset_token_expiry:
        return False
    return datetime.utcnow() < usuario.reset_token_expiry