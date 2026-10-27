# config.py

- ConfigurationError · class · L13-L14 — class ConfigurationError(RuntimeError)
- Settings · class · L18-L21 — class Settings
- _required · function · L24-L28 — def _required(name: str) -> str
- _is_origin · function · L31-L55 — def _is_origin(value: str) -> bool: # Uma origem não contém caminho, credenciais, query ou fragmento.
- load_settings · function · L58-L77 — def load_settings(env_file: Path | None = None) -> Settings
