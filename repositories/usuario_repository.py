"""
Repositorio de acesso a dados do modelo Usuario no firestore

Coleçao: 'usuarios'
responsabilidade: operações CRUD no firestore.

"""

from typing import Optional
from datetime import datetime
from database import get_db
from models import Usuario

COLECAO = "usuarios"


def buscar_por_nome(nome: str) -> Optional[Usuario]:
    """Busca um usuário pelo nome de usuário."""
    db = get_db()
    docs = db.collection(COLECAO).where("nome", "==", nome).limit(1).get()
    for doc in docs:
        return Usuario.from_dict(doc.id, doc.to_dict())
    return None


def buscar_por_id(usuario_id: str) -> Optional[Usuario]:
    """Busca um usuário pelo ID do documento."""
    db = get_db()
    doc = db.collection(COLECAO).document(usuario_id).get()
    if doc.exists:
        return Usuario.from_dict(doc.id, doc.to_dict())
    return None


def buscar_por_email(email: str) -> Optional[Usuario]:
    """Busca um usuário pelo e-mail."""
    db = get_db()
    docs = db.collection(COLECAO).where("email", "==", email).limit(1).get()
    for doc in docs:
        return Usuario.from_dict(doc.id, doc.to_dict())
    return None


def buscar_por_token(token: str) -> Optional[Usuario]:
    """Busca um usuário pelo token de recuperação de senha."""
    db = get_db()
    docs = db.collection(COLECAO).where("reset_token", "==", token).limit(1).get()
    for doc in docs:
        return Usuario.from_dict(doc.id, doc.to_dict())
    return None


def nome_existe(nome: str) -> bool:
    """Verifica se o nome de usuário já está em uso."""
    return buscar_por_nome(nome) is not None


def criar_usuario(nome: str, email: str, senha_hash: str, role_id: int) -> Usuario:
    """Cria e persiste um novo usuário no Firestore."""
    db = get_db()
    role_nome = "Psicologo" if role_id == 1 else "Paciente"
    usuario = Usuario(
        id="",
        nome=nome,
        email=email,
        senha_hash=senha_hash,
        role_id=role_id,
        role_nome=role_nome,
    )
    doc_ref = db.collection(COLECAO).add(usuario.to_dict())
    usuario.id = doc_ref[1].id
    return usuario


def atualizar_usuario(usuario: Usuario, novo_nome: str,
                      nova_senha_hash: Optional[str] = None) -> None:
    """Atualiza nome e opcionalmente senha do usuário."""
    db = get_db()
    dados = {"nome": novo_nome}
    if nova_senha_hash:
        dados["senha_hash"] = nova_senha_hash
    db.collection(COLECAO).document(usuario.id).update(dados)
    usuario.nome = novo_nome
    if nova_senha_hash:
        usuario.senha_hash = nova_senha_hash


def atualizar_campos(usuario_id: str, campos: dict) -> None:
    """Atualiza campos específicos do documento do usuário."""
    db = get_db()
    db.collection(COLECAO).document(usuario_id).update(campos)


def deletar_usuario(usuario: Usuario) -> None:
    """Remove permanentemente o usuário do Firestore."""
    db = get_db()
    db.collection(COLECAO).document(usuario.id).delete()


def listar_todos() -> list:
    """Retorna todos os usuários cadastrados."""
    db = get_db()
    docs = db.collection(COLECAO).get()
    return [Usuario.from_dict(doc.id, doc.to_dict()) for doc in docs]