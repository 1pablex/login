import os
import firebase_admin
from firebase_admin import credentials, firestore

_db = None


def init_db(app=None):
    """
    Inicializa a conexão com o Firebase Firestore.
    Usa o arquivo de credenciais definido em FIREBASE_CREDENTIALS no .env
    """
    global _db

    if not firebase_admin._apps:
        cred_path = os.environ.get("FIREBASE_CREDENTIALS", "firebase-credentials.json")
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

    _db = firestore.client()
    return _db


def get_db():
    """Retorna a instância do cliente Firestore."""
    global _db
    if _db is None:
        init_db()
    return _db