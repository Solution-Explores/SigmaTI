"""Repositório transacional de usuários e sessões, compartilhável entre workers."""
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Protocol

from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .database import PersistenceUnavailable
from .models import SessionRow, UserRow


class IdentityStore(Protocol):
    def get_user(self, username: str) -> dict | None: ...
    def save_user(self, username: str, senha_hash: str, papel: str, ativo: bool = True) -> None: ...
    def save_session(self, payload: dict, expected_hash: str | None = None,
                     expected_version: int | None = None) -> None: ...
    def valid_session(self, payload: dict) -> bool: ...
    def revoke_session(self, jti: str) -> None: ...
    def list_users(self) -> list[str]: ...
    def upgrade_hash(self, username: str, old_hash: str, new_hash: str) -> bool: ...


class PostgresIdentityStore:
    def __init__(self, engine):
        self.engine = engine

    @contextmanager
    def transaction(self):
        try:
            with Session(self.engine) as session, session.begin():
                yield session
        except SQLAlchemyError:
            raise PersistenceUnavailable("Operação de persistência indisponível.") from None

    def get_user(self, username):
        with self.transaction() as session:
            row = session.get(UserRow, username)
            return None if row is None else {k: getattr(row, k) for k in
                                              ("username", "senha_hash", "papel", "ativo", "versao")}

    def list_users(self):
        with self.transaction() as session:
            return list(session.scalars(select(UserRow.username).order_by(UserRow.username)))

    def import_users(self, users):
        # Todo o arquivo é importado ou toda a transação é revertida.
        with self.transaction() as session:
            for user in users:
                if session.get(UserRow, user.username) is not None:
                    raise ValueError("Importação recusada: usuário existente.")
                session.add(UserRow(username=user.username, senha_hash=user.senha_hash,
                                    papel=user.papel, ativo=user.ativo, versao=1))


    def save_user(self, username, senha_hash, papel, ativo=True):
        with self.transaction() as session:
            # Todas as emissões/alterações serializam pela identidade.
            row = session.scalar(select(UserRow).where(UserRow.username == username).with_for_update())
            if row is None:
                session.add(UserRow(username=username, senha_hash=senha_hash, papel=papel,
                                    ativo=ativo, versao=1))
            else:
                row.senha_hash, row.papel, row.ativo = senha_hash, papel, ativo
                row.versao += 1
                session.execute(update(SessionRow).where(SessionRow.username == username)
                                .values(revogada=True))

    def upgrade_hash(self, username, old_hash, new_hash):
        with self.transaction() as session:
            # Rehash não é troca de senha: preserva sessões e não sobrescreve troca concorrente.
            result = session.execute(update(UserRow).where(UserRow.username == username,
                                                 UserRow.senha_hash == old_hash).values(senha_hash=new_hash))
            return result.rowcount == 1

    def save_session(self, payload, expected_hash=None, expected_version=None):
        with self.transaction() as session:
            user = session.scalar(select(UserRow).where(UserRow.username == payload["sub"])
                                  .with_for_update())
            if (user is None or not user.ativo or user.papel != payload["papel"]
                    or (expected_hash is not None and user.senha_hash != expected_hash)
                    or (expected_version is not None and user.versao != expected_version)):
                raise ValueError("Identidade alterada durante autenticação.")
            session.add(SessionRow(jti=payload["jti"], username=user.username, papel=user.papel,
                                   versao_usuario=user.versao,
                                   emitida_em=datetime.fromtimestamp(payload["iat"], timezone.utc),
                                   expira_em=datetime.fromtimestamp(payload["exp"], timezone.utc)))

    def valid_session(self, payload):
        with self.transaction() as session:
            row = session.get(SessionRow, payload["jti"])
            user = session.get(UserRow, payload["sub"])
            return bool(row and user and user.ativo and not row.revogada
                        and row.username == payload["sub"] and row.papel == payload["papel"] == user.papel
                        and row.versao_usuario == user.versao
                        and int(row.emitida_em.timestamp()) == payload["iat"]
                        and int(row.expira_em.timestamp()) == payload["exp"]
                        and row.expira_em > datetime.now(timezone.utc))

    def revoke_session(self, jti):
        with self.transaction() as session:
            session.execute(update(SessionRow).where(SessionRow.jti == jti).values(revogada=True))
