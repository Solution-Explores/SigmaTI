"""Cria hashes locais para a demonstração; não imprime nem armazena a senha."""
import argparse
from dataclasses import asdict
from getpass import getpass
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from auth import UsuarioRepository


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(".local/users.json"))
    args = parser.parse_args()
    if args.output.exists():
        parser.error("O arquivo já existe; use outro destino para preservar as contas.")
    repo = UsuarioRepository()
    for nome, papel in (("suporte.n1", "suporte_n1"), ("analista.redes", "analista_redes"),
                        ("gestor.ti", "gestor_ti")):
        senha = getpass(f"Senha temporária para {nome} (mínimo 12 caracteres): ")
        if len(senha) < 12 or senha != getpass("Confirme a senha: "):
            parser.error("Senha curta ou confirmação diferente; nenhum arquivo criado.")
        repo.adicionar_usuario(nome, senha, papel)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump([asdict(u) for u in repo._usuarios.values()], stream)
    print("Arquivo de usuários criado. Configure SIGMA_USERS_FILE com seu caminho absoluto.")


if __name__ == "__main__":
    main()
