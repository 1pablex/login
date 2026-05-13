from database import db
from models import Usuario
from flask_bcrypt import Bcrypt
from flask import session
from typing import Optional
from repositories.usuario_repository import buscar_por_nome

bcrypt = Bcrypt()


def validar_credenciais(nome: str, senha: str) -> Optional[Usuario]:
    """
    Valida usuário e senha.
 
    Returns:
        Usuario se credenciais válidas, None caso contrário.
    """
    usuario = buscar_por_nome(nome)
    if usuario and bcrypt.check_password_hash(usuario.senha_hash, senha):
        return usuario
    return None


def iniciar_sessao(usuario: Usuario) -> None:
    """Popula a sessão Flask com os dados do usuário autenticado."""
    session["usuario_id"]   = usuario.id
    session["usuario_nome"] = usuario.nome
    session["usuario_role"] = usuario.role.nome


def encerrar_sessao() -> dict:
    """
    Retorna os dados da sessão atual e a limpa.
 
    Returns:
        Dicionário com nome e id do usuário antes do logout.
    """
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
    Valida os critérios mínimos de segurança da senha.
 
    Returns:
        Mensagem de erro se inválida, None se válida.
    """
    if len(senha) < 8:
        return "Senha deve ter pelo menos 8 caracteres."
    return None
 
 
def role_valida(role_id: int) -> bool:
    """Verifica se o role_id é permitido (1=Psicólogo, 2=Paciente)."""
    return role_id in (1, 2)
 
 

def atualizar_senha(usuario, nova_senha_hash):

    usuario.senha_hash         = bcrypt.generate_password_hash(nova_senha_hash).decode("utf-8") #usando bcrypt para hash da nova senha, com o custo padrão do bcrypt (mais seguro)
    #2.4 - token invalido apos o uso
    usuario.reset_token        = None 
    usuario.reset_token_expiry = None
    db.session.commit()


def role_valida(role_id):
    return role_id in (1, 2)