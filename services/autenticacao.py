"""
Serviço de autenticação.

Centraliza toda a lógica  relacionado:
- Validação de credenciais
- Gestão de sessão
- Validação de senha e role
- Atualização de senha
"""

from typing import Optional
from flask import session
from flask_bcrypt import Bcrypt
from repositories.usuario_repository import atualizar_campos
from models import Usuario

bcrypt = Bcrypt()


def validar_credenciais(nome: str, senha: str) -> Optional[Usuario]:
    """
    Valida usuário e senha.
    Returns: Usuario se credenciais válidas, None caso contrário.
    """
    from repositories.usuario_repository import buscar_por_nome
    usuario = buscar_por_nome(nome)
    if usuario and bcrypt.check_password_hash(usuario.senha_hash, senha):
        return usuario
    return None


def iniciar_sessao(usuario: Usuario) -> None:
    """Popula a sessão Flask com os dados do usuário autenticado."""
    session["usuario_id"]   = usuario.id
    session["usuario_nome"] = usuario.nome
    session["usuario_role"] = usuario.role_nome


def encerrar_sessao() -> dict:
    """Retorna dados da sessão atual e a limpa."""
    dados = {
        "nome": session.get("usuario_nome"),
        "id":   session.get("usuario_id"),
    }
    session.clear()
    return dados


def sessao_ativa() -> bool:
    """Verifica se há uma sessão autenticada ativa."""
    return "usuario_id" in session


def senha_valida(senha: str) -> Optional[str]:
    """
    Valida critérios mínimos de segurança da senha.
    Returns: Mensagem de erro se inválida, None se válida.
    """
    if len(senha) < 8:
        return "Senha deve ter pelo menos 8 caracteres."
    return None


def role_valida(role_id: int) -> bool:
    """Verifica se o role_id é permitido."""
    return role_id in (1, 2)


def atualizar_senha(usuario: Usuario, nova_senha: str) -> None:
    """Gera novo hash e persiste a nova senha, invalidando o token de reset."""
    nova_hash = bcrypt.generate_password_hash(nova_senha).decode("utf-8")
    atualizar_campos(usuario.id, {
        "senha_hash": nova_hash,
        "reset_token": None,
        "reset_token_expiry": None,
    })
    usuario.senha_hash = nova_hash