"""
Serviço de atualização de perfil do usuário.
"""

from typing import Optional
from flask_bcrypt import Bcrypt
from models import Usuario
from repositories.usuario_repository import atualizar_usuario, nome_existe

bcrypt = Bcrypt()


def atualizar_dados(
    usuario: Usuario,
    novo_nome: str,
    nova_senha: Optional[str] = None,
    senha_atual: Optional[str] = None,
) -> Optional[str]:
    """
    Atualiza nome e/ou senha do usuário.
    Returns: Mensagem de erro se inválido, None se bem-sucedido.
    """
    if novo_nome != usuario.nome and nome_existe(novo_nome):
        return "Nome de usuário já está em uso."

    nova_senha_hash: Optional[str] = None

    if nova_senha:
        if not senha_atual:
            return "Informe a senha atual para alterá-la."
        if not bcrypt.check_password_hash(usuario.senha_hash, senha_atual):
            return "Senha atual incorreta."
        if len(nova_senha) < 8:
            return "Nova senha deve ter pelo menos 8 caracteres."
        nova_senha_hash = bcrypt.generate_password_hash(nova_senha).decode("utf-8")

    atualizar_usuario(usuario, novo_nome, nova_senha_hash)
    return None