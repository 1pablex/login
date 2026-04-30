from database import db
from models import Usuario
from typing import Optional


def buscar_por_nome(nome):
    return Usuario.query.filter_by(nome=nome).first()

def buscar_por_id(usuario_id: int) -> Optional[Usuario]:
    """Busca um usuário pelo ID."""
    return db.session.get(Usuario, usuario_id)


def nome_existe(nome):
    return Usuario.query.filter_by(nome=nome).first() is not None


def criar_usuario(nome, email, senha_hash, role_id):
    usuario = Usuario(nome=nome, email=email, senha_hash=senha_hash, Role_id=role_id)
    db.session.add(usuario)
    db.session.commit()
    return usuario


def listar_todos():
    return Usuario.query.all()

def atualizar_usuario(usuario: Usuario, novo_nome: str, nova_senha_hash: Optional[str] = None) -> None:
    """
    Atualiza os dados permitidos do usuário (nome e senha).
 
    Args:
        usuario: instância do modelo Usuario
        novo_nome: novo nome de usuário
        nova_senha_hash: novo hash de senha (opcional)
    """
    usuario.nome = novo_nome
    if nova_senha_hash:
        usuario.senha_hash = nova_senha_hash
    db.session.commit()
 

def deletar_usuario(id):
    usuario = Usuario.query.get(id)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
