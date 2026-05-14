"""
Modelos de dados do sistema.
Coleções:
    usuarios      — dados dos usuários
    logs_auditoria — registro de eventos de segurança
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Usuario:
    """Representa um documento da coleção 'usuarios'."""
    id: str                              # ID do documento no Firestore
    nome: str
    email: str
    senha_hash: str
    role_id: int                         # 1=Psicologo, 2=Paciente
    role_nome: str                       # "Psicologo" ou "Paciente"

    # Recuperação de senha
    reset_token: Optional[str] = None
    reset_token_expiry: Optional[datetime] = None

    # 2FA
    codigo_2fa: Optional[str] = None
    codigo_2fa_expiry: Optional[datetime] = None

    def to_dict(self) -> dict:
        """converte para dicionário para salvar no firestore."""
        return {
            "nome": self.nome,
            "email": self.email,
            "senha_hash": self.senha_hash,
            "role_id": self.role_id,
            "role_nome": self.role_nome,
            "reset_token": self.reset_token,
            "reset_token_expiry": self.reset_token_expiry,
            "codigo_2fa": self.codigo_2fa,
            "codigo_2fa_expiry": self.codigo_2fa_expiry,
        }

    @staticmethod
    def from_dict(doc_id: str, data: dict) -> "Usuario":
        """cria uma instancia de usuario a partir de um documento firestore."""
        return Usuario(
            id=doc_id,
            nome=data.get("nome", ""),
            email=data.get("email", ""),
            senha_hash=data.get("senha_hash", ""),
            role_id=data.get("role_id", 2),
            role_nome=data.get("role_nome", "Paciente"),
            reset_token=data.get("reset_token"),
            reset_token_expiry=data.get("reset_token_expiry"),
            codigo_2fa=data.get("codigo_2fa"),
            codigo_2fa_expiry=data.get("codigo_2fa_expiry"),
        )


@dataclass
class LogAuditoria:
    """Representa um documento da coleção 'logs_auditoria'."""
    evento: str
    nome: Optional[str] = None
    usuario_id: Optional[str] = None
    ip: Optional[str] = None
    descricao: Optional[str] = None
    criado_em: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "evento": self.evento,
            "nome": self.nome,
            "usuario_id": self.usuario_id,
            "ip": self.ip,
            "descricao": self.descricao,
            "criado_em": self.criado_em,
        }