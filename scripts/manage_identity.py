"""Administração local: python -m scripts.manage_identity create gestor gestor_ti."""
import argparse
import getpass
import json
import os

from argon2 import PasswordHasher

from auth import PAPEIS, Usuario, UsuarioRepository
from persistence.database import open_database
from persistence.identity import PostgresIdentityStore


def main():
    parser = argparse.ArgumentParser(description="Administrar identidades no PostgreSQL migrado.")
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create")
    create.add_argument("username")
    create.add_argument("papel", choices=list(PAPEIS))
    imported = commands.add_parser("import-hashes")
    imported.add_argument("file")
    args = parser.parse_args()
    store = PostgresIdentityStore(open_database(os.environ["SIGMA_DATABASE_URL"]))
    try:
        if args.command == "create":
            if not 1 <= len(args.username) <= 100:
                parser.error("Usuário deve ter entre 1 e 100 caracteres.")
            if store.get_user(args.username):
                parser.error("Usuário existente: criação não sobrescreve contas.")
            password = getpass.getpass("Senha (12 a 128 caracteres): ")
            if not 12 <= len(password) <= 128 or password != getpass.getpass("Confirme a senha: "):
                parser.error("Senha inválida ou confirmação diferente.")
            store.import_users([Usuario(args.username, PasswordHasher().hash(password), args.papel)])
        else:
            repository = UsuarioRepository()
            repository.carregar(args.file)
            users = list(repository._usuarios.values())
            if any(store.get_user(user.username) for user in users):
                parser.error("Importação recusada: usuário já existe.")
            store.import_users(users)
        print(json.dumps({"status": "ok", "operation": args.command}))
    finally:
        store.engine.dispose()


if __name__ == "__main__":
    main()
