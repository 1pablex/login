from database import db
from models import Usuario


def buscar_por_nome(nome):
    return Usuario.query.filter_by(nome=nome).first()


def nome_existe(nome):
    return Usuario.query.filter_by(nome=nome).first() is not None


def criar_usuario(nome, email, senha_hash, role_id):
    usuario = Usuario(nome=nome, email=email, senha_hash=senha_hash, Role_id=role_id)
    db.session.add(usuario)
    db.session.commit()
    return usuario


def listar_todos():
    return Usuario.query.all()


def deletar_usuario(id):
    usuario = Usuario.query.get(id)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
