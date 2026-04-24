from database import db


class Role(db.Model):
    __tablename__ = "roles"

    id   = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)

    usuarios = db.relationship("Usuario", backref="role", lazy=True)

    def __repr__(self):
        return f"<Role {self.nome}>"


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id  = db.Column(db.Integer, primary_key=True)
    nome  = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)
    Role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<Usuario {self.nome}>"
