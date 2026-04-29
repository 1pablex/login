import os
import secrets
import requests
from datetime import datetime, timedelta
from database import db


def init_mail(app):
#funcionar com o app.py
    pass


def enviar_email_recuperacao(destinatario_email: str, destinatario_nome: str, link: str):
    """Envia e-mail de recuperação de senha via API REST do Brevo."""
    api_key      = os.environ.get("BREVO_API_KEY")
    sender_email = os.environ.get("BREVO_SENDER_EMAIL")
    sender_name  = os.environ.get("BREVO_SENDER_NAME", "Suporte")

    if not api_key:
        raise ValueError("BREVO_API_KEY não definida no .env")

    payload = {
        "sender": {"name": sender_name, "email": sender_email},
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
    }

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
        raise RuntimeError(
            f"Brevo API error {response.status_code}: {response.text}"
        )


def gerar_token_recuperacao(usuario) -> str:
    """Gera e persiste um token de recuperação no usuário."""
    token = secrets.token_urlsafe(32)
    usuario.reset_token        = token
    usuario.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
    db.session.commit()
    return token


def token_valido(usuario) -> bool:
    """Verifica se o token ainda está dentro do prazo."""
    if not usuario or not usuario.reset_token_expiry:
        return False
    return datetime.utcnow() < usuario.reset_token_expiry