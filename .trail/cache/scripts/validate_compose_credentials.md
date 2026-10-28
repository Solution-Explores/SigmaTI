# scripts/validate_compose_credentials.py

- ValidationError · class · L26-L27 — class ValidationError(RuntimeError)
- require · function · L30-L32 — def require(condition: bool, message: str) -> None
- CredentialChecks · class · L35-L168 — class CredentialChecks
- __init__ · method · L36-L52 — def __init__(self) -> None
- passed · method · L54-L56 — def passed(self, label: str) -> None
- compose · method · L58-L70 — def compose(self, env_file: Path, env: dict[str, str], profile: str | None = None, *, render: bool = False) -> subprocess.CompletedProcess
- check_template · method · L72-L88 — def check_template(self) -> None
- check_gitignore · method · L90-L94 — def check_gitignore(self) -> None
- expect_success · method · L96-L101 — def expect_success(self, env_file: Path, label: str, profile: str | None = None) -> None
- check_rendered_values · method · L103-L131 — def check_rendered_values(self, env_file: Path, profile: str | None = None) -> None
- expect_rejection · method · L133-L141 — def expect_rejection(self, env_file: Path, env: dict[str, str], label: str, profile: str | None = None, variable: str | None = None) -> None
- run · method · L143-L168 — def run(self) -> None
- main · function · L171-L180 — def main() -> int
