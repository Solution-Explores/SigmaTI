# scripts/validate_infrastructure.py

- image_map · function · L34-L51 — def image_map(lock: dict) -> dict[str, str]
- validate_model · function · L54-L75 — def validate_model(model: dict, images: dict[str, str], bindings: dict[str, str]) -> None
- render · function · L78-L84 — def render(checks: CredentialChecks, env: dict[str, str], profile: str | None = "monitoring") -> dict
- verify_registry · function · L87-L107 — def verify_registry(lock: dict) -> None: # Somente endpoints de metadados fixos do registro oficial; não buscar camadas.
- main · function · L110-L147 — def main() -> int
