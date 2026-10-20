"""Manutenção explícita do banco configurado; preserva agregados minuto/hora."""
import argparse
import json
import os

from persistence.database import open_database
from persistence.operational import PostgresOperationalStore


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=os.getenv("SIGMA_MEASUREMENT_RETENTION_DAYS", "30"))
    args = parser.parse_args()
    if not 1 <= args.days <= 3650:
        parser.error("--days deve estar entre 1 e 3650")
    engine = open_database(os.environ["SIGMA_DATABASE_URL"])
    try:
        print(json.dumps(PostgresOperationalStore(engine).retain(args.days)))
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
