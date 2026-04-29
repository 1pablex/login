from database import db
from models import Usuario
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def atualizar_senha(usuario, nova_senha_hash):

    usuario.senha_hash         = bcrypt.generate_password_hash(nova_senha_hash).decode("utf-8")
    usuario.reset_token        = None
    usuario.reset_token_expiry = None
    db.session.commit()


def senha_valida(senha):

    if len(senha) < 8:
        return "Senha deve ter pelo menos 8 caracteres."
    return None


def role_valida(role_id):
    return role_id in (1, 2)