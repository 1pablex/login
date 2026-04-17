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

    id         = db.Column(db.Integer, primary_key=True)
    nome       = db.Column(db.String(80), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)
    Role_id    = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)

    def __repr__(self):
        return f"<Usuario {self.nome}>"
