from database import db
from datetime import datetime


class Role(db.Model):
    __tablename__ = "roles"

    id   = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)

    usuarios = db.relationship("Usuario", backref="role", lazy=True)

    def __repr__(self):
        return f"<Role {self.nome}>"

#4.1 - listagem de dados coletados foi utilizado a minimização de dados alem do necessario
class Usuario(db.Model):
    __tablename__ = "usuarios"

    id         = db.Column(db.Integer, primary_key=True) #4.2 - id auto-incrementável
    nome       = db.Column(db.String(80), unique=True, nullable=False) #4.2 - nome de usuário unico
    email      = db.Column(db.String(120), unique=True, nullable=False) # 4.2 - e-mail unico para recuperação de senha e comunicação
    #3.4 criptografia de senhas
    senha_hash = db.Column(db.String(200), nullable=False) # 1.4 - Armazena o hash da senha, não a senha em texto plano 
    Role_id    = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False) #4.2 - associação com a tabela de roles

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