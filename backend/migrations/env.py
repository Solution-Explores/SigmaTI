"""Migrações explícitas, sem DDL automático durante importação da API."""
import os

from alembic import context
from sqlalchemy import create_engine

from persistence.models import Base
from persistence import operational_models  # registra o esquema no metadata de autogenerate

url = os.environ["SIGMA_DATABASE_URL"]
engine = create_engine(url, hide_parameters=True)
with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=Base.metadata)
    with context.begin_transaction():
        context.run_migrations()
