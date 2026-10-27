# sanitizer.py

- SanitizationError · class · L24-L26 — class SanitizationError(RuntimeError)
- SanitizationResidualError · class · L29-L31 — class SanitizationResidualError(SanitizationError)
- ResultadoSanitizacao · class · L35-L41 — class ResultadoSanitizacao
- categorizar_equipamento · function · L88-L127 — def categorizar_equipamento(nome: str) -> str
- _validar_digitos_cpf · function · L130-L149 — def _validar_digitos_cpf(cpf: str) -> bool
- _substituir_ipv4 · function · L152-L161 — def _substituir_ipv4(match: re.Match) -> str
- _substituir_ipv6 · function · L164-L172 — def _substituir_ipv6(match: re.Match) -> str
- registrar_auditoria_privacidade · function · L175-L177 — def registrar_auditoria_privacidade(categoria: str, detalhe: str) -> None
- sanitizar_texto · function · L180-L316 — def sanitizar_texto(texto: str) -> ResultadoSanitizacao
- _sub_nome_contextual · function · L201-L203 — def _sub_nome_contextual(m: re.Match) -> str
- _sub_cpf_contextual · function · L217-L222 — def _sub_cpf_contextual(m: re.Match) -> str
- _sub_hostname · function · L232-L236 — def _sub_hostname(m: re.Match) -> str
- anonimizar_dados · function · L319-L334 — def anonimizar_dados(texto: str) -> str
