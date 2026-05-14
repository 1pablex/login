"""
serviço de auditoria — registra eventos de segurança no firestore.

Coleção: 'logs_auditoria'

Eventos:
    LOGIN_OK        — credenciais válidas, aguardando 2FA
    LOGIN_FALHA     — usuário ou senha inválidos
    2FA_OK          — código 2FA validado, sessão iniciada
    2FA_FALHA       — código 2FA inválido ou expirado
    LOGOUT          — sessão encerrada pelo usuário
    RESET_SOLICIT   — solicitação de recuperação de senha
    RESET_OK        — senha redefinida com sucesso
    PERFIL_ATUALIZADO — dados do perfil atualizados
    CONTA_DELETADA  — conta excluída pelo titular
"""

from typing import Optional
from datetime import datetime
from database import get_db
from models import LogAuditoria

COLECAO = "logs_auditoria"


def registrar(evento: str, nome: str = None, usuario_id: str = None,
              ip: str = None, descricao: str = None) -> None:
    """Registra um evento de auditoria no Firestore."""
    db = get_db()
    log = LogAuditoria(
        evento=evento,
        nome=nome,
        usuario_id=usuario_id,
        ip=ip,
        descricao=descricao,
        criado_em=datetime.utcnow()
    )
    db.collection(COLECAO).add(log.to_dict())


def listar_logs() -> list:
    """Retorna todos os logs ordenados do mais recente para o mais antigo."""
    db = get_db()
    docs = db.collection(COLECAO).order_by(
        "criado_em",
        direction="DESCENDING"
    ).get()
    return [doc.to_dict() for doc in docs]