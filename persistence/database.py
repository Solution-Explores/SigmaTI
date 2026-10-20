"""Conexão explícita: PostgreSQL indisponível nunca seleciona memória."""
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError


class PersistenceUnavailable(RuntimeError):
    pass


def open_database(url: str):
    engine = None
    try:
        parsed = make_url(url)
        if parsed.drivername != "postgresql+psycopg":
            raise ValueError()
        engine = create_engine(parsed, pool_pre_ping=True, hide_parameters=True,
                               connect_args={"connect_timeout": 5}, pool_timeout=5)
        with engine.connect() as connection:
            version = connection.scalar(text("SELECT version_num FROM alembic_version"))
            if version != "002_operational":
                raise ValueError()
        return engine
    except (SQLAlchemyError, ValueError):
        if engine is not None:
            engine.dispose()
        raise PersistenceUnavailable("PostgreSQL indisponível ou migrações pendentes.") from None
