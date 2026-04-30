from database import db
from datetime import datetime


class Role(db.Model):
    __tablename__ = "roles"

    id   = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)

    usuarios = db.relationship("Usuario", backref="role", lazy=True)

    def __repr__(self):
        return f"<Role {self.nome}>"


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id         = db.Column(db.Integer, primary_key=True)
    nome       = db.Column(db.String(80), unique=True, nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)
    Role_id    = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)

    # Recuperação de senha
    reset_token        = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

    # 2FA
    codigo_2fa        = db.Column(db.String(6),  nullable=True)
    codigo_2fa_expiry = db.Column(db.DateTime,   nullable=True)

    def __repr__(self):
        return f"<Usuario {self.nome}>"


class LogAuditoria(db.Model):
    __tablename__ = "logs_auditoria"

    id         = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    nome       = db.Column(db.String(80),  nullable=True)
    evento     = db.Column(db.String(50),  nullable=False)
    ip         = db.Column(db.String(45),  nullable=True)
    descricao  = db.Column(db.String(200), nullable=True)
    criado_em  = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Log {self.evento} | {self.nome} | {self.criado_em}>"