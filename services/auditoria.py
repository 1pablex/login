from database import db
from models import LogAuditoria
from datetime import datetime

#1.8 - evento de auditoria
def registrar(evento: str, nome: str = None, usuario_id: int = None,
              ip: str = None, descricao: str = None):
    """
    registra um evento de auditoria no banco de dados.
    eventos:
        LOGIN_OK      — credenciais válidas, aguardando 2FA
        LOGIN_FALHA   — usuário ou senha inválidos
        2FA_OK        — código 2FA validado, sessão iniciada
        2FA_FALHA     — código 2FA inválido ou expirado
        LOGOUT        — sessão encerrada pelo usuário
        RESET_SOLICIT — solicitação de recuperação de senha
        RESET_OK      — senha redefinida com sucesso
    """
    log = LogAuditoria(
        usuario_id=usuario_id,
        nome=nome,
        evento=evento,
        ip=ip,
        descricao=descricao,
        criado_em=datetime.utcnow()
    )
    db.session.add(log)  # 5.3 — somente db.session.add (INSERT). Nunca update/delete.
    db.session.commit()


def listar_logs():
    """Retorna todos os logs ordenados do mais recente para o mais antigo."""
    return LogAuditoria.query.order_by(LogAuditoria.criado_em.desc()).all()