from typing import Optional
from flask_bcrypt import Bcrypt
from models import Usuario
from repositories.usuario_repository import deletar_usuario

bcrypt = Bcrypt()


def excluir_conta(usuario: Usuario, senha_confirmacao: str) -> Optional[str]:
    """
    Exclui permanentemente a conta do usuário após confirmação de senha.

    Args:
        usuario: instância do modelo Usuario
        senha_confirmacao: senha atual para confirmação da exclusão
    """
    if not bcrypt.check_password_hash(usuario.senha_hash, senha_confirmacao):
        return "Senha incorreta. Exclusão cancelada."

    deletar_usuario(usuario)
    return None