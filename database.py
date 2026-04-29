from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        _seed_roles()


def _seed_roles():
    from models import Role
    if not Role.query.first():
        db.session.add_all([
            Role(id=1, nome="Psicologo"),
            Role(id=2, nome="Paciente"),
        ])
        db.session.commit()
