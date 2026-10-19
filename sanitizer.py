"""Módulo de anonimização e privacidade em conformidade com a LGPD (RF05).

Implementa generalização de rede (IPv4 -> /24, IPv6 -> /64), mascaramento de MAC,
categorização de equipamentos/hostnames e remoção de dados pessoais e médicos
(CPF, CNS, prontuário, e-mail, nomes).

Garante o princípio Fail-Closed: se o filtro falhar por exceção ou se houver
detecção de PII residual após a sanitização, a execução é abortada e auditada,
impedindo qualquer tráfego para a nuvem.
"""

from __future__ import annotations

import ipaddress
import logging
import re
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("sigma.sanitizer")
audit_logger = logging.getLogger("sigma.audit")


class SanitizationError(RuntimeError):
    """Exceção base para erros do processo de sanitização de dados."""
    pass


class SanitizationResidualError(SanitizationError):
    """Disparada quando detectores residuais encontram PII após a transformação."""
    pass


@dataclass
class ResultadoSanitizacao:
    """Resultado estruturado da sanitização."""
    sucesso: bool
    texto_sanitizado: str
    identificadores_removidos: list[str] = field(default_factory=list)
    residuos: list[str] = field(default_factory=list)
    motivo_bloqueio: str | None = None


# --- Expressões Regulares de Detecção ---

RE_IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
RE_IPV6 = re.compile(
    r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b|"
    r"\b(?:[0-9a-fA-F]{1,4}:){1,7}:[0-9a-fA-F]{1,4}\b|"
    r"\b::(?:[0-9a-fA-F]{1,4}:){0,6}[0-9a-fA-F]{1,4}\b|"
    r"\b(?:[0-9a-fA-F]{1,4}:){1,6}:(?:[0-9a-fA-F]{1,4}:){0,5}[0-9a-fA-F]{1,4}\b"
)
RE_MAC = re.compile(
    r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b|\b[0-9A-Fa-f]{4}\.[0-9A-Fa-f]{4}\.[0-9A-Fa-f]{4}\b"
)
RE_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
RE_CPF_FORMATADO = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")
RE_CPF_CONTEXTUAL = re.compile(r"(?:\bCPF[:\s]*|\bcpf[:\s]*)(\d{11}|\d{3}\.\d{3}\.\d{3}-\d{2})\b")
RE_CNS = re.compile(
    r"(?:\bCNS[:\s]*|\bcart[aã]o\s+(?:sus|nacional\s+de\s+sa[uú]de)[:\s]*)(\d{15}|\d{3}[\s.-]?\d{4}[\s.-]?\d{4}[\s.-]?\d{4})\b|"
    r"\b[12789]\d{2}[\s.-]?\d{4}[\s.-]?\d{4}[\s.-]?\d{4}\b"
)
RE_PRONTUARIO = re.compile(r"(?i:\bprontu[aá]rio[:\s#]+|\bpront[:\s#]+)([A-Za-z0-9_-]{3,20})\b")

# Nomes precedidos por termos médicos, cargos ou papéis no hospital
RE_NOMES_CONTEXTUAIS = re.compile(
    r"(?i:\b(?:dr\.|dra\.|doutor\b|doutora\b|enf\.|enfermeir[oa]\b|m[eé]dic[oa]\b|t[eé]cnic[oa]\b|paciente\b|usu[aá]rio\b)\s+)"
    r"([A-ZÀ-Úa-zà-ú]{2,}(?:\s+[A-ZÀ-Úa-zà-ú]{2,})*)"
)

# Hostnames comuns em logs hospitalares
RE_HOSTNAME_LOG = re.compile(
    r"\b([a-zA-Z0-9_-]+\.(?:fcecon|hospital|rede|local|lan|internal))\b|"
    r"\b((?:sw(?:itch)?|rt|router|srv|server|fw|firewall|tomo(?:grafo)?|ct|mon(?:itor)?|ws|term(?:inal)?|ap|wifi)-[a-zA-Z0-9_.-]+)\b",
    re.IGNORECASE,
)

NOMES_CONFIGURADOS: set[str] = {
    "dr.joao",
    "dr. joao",
    "dr joao",
    "dra.maria",
    "dra. maria",
    "dra maria",
}


def categorizar_equipamento(nome: str) -> str:
    """Mapeia um hostname ou nome de equipamento para uma categoria funcional genérica (RF05)."""
    if not nome or not str(nome).strip():
        return "[EQUIPAMENTO_GENERICO]"

    limpo = str(nome).strip().lower()

    # Switches
    if re.search(r"\b(sw|switch|core-sw|sw-core|sw-dist|sw-edge)\b|^(sw|switch)[-_]", limpo):
        return "[SWITCH_REDE]"

    # Roteadores e Gateways
    if re.search(r"\b(rt|router|roteador|gw|gateway|borda)\b|^(rt|router|gw)[-_]", limpo):
        return "[ROTEADOR_REDE]"

    # Firewalls e Segurança
    if re.search(r"\b(fw|firewall|pfsense|fortigate|iptables)\b|^(fw|firewall)[-_]", limpo):
        return "[FIREWALL_REDE]"

    # Servidores e Bancos de Dados
    if re.search(r"\b(srv|server|servidor|bd|db|database|postgre|zabbix|ad|ldap)\b|^(srv|server|bd|db)[-_]", limpo):
        return "[SERVIDOR_HOSPITALAR]"

    # Equipamentos Médicos de Imagem
    if re.search(r"\b(tomo|tomografo|ct|mri|ressonancia|raio-?x|rx|mamografo|ultrassom|usg|pet-?scan)\b", limpo):
        return "[EQUIPAMENTO_IMAGEM]"

    # Dispositivos Biomédicos de Monitoramento e Suporte à Vida
    if re.search(r"\b(mon|monitor|ecg|eletro|ventilador|bomba-?infusao|desfibrilador|oximetro)\b", limpo):
        return "[DISPOSITIVO_BIOMEDICO]"

    # Estações Clínicas e Terminais
    if re.search(r"\b(term|terminal|ws|workstation|pc|desktop|estacao)\b|^(term|ws|pc)[-_]", limpo):
        return "[ESTACAO_CLINICA]"

    # Pontos de Acesso Sem Fio
    if re.search(r"\b(ap|wifi|wireless|wlan)\b|^(ap|wifi)[-_]", limpo):
        return "[ACCESS_POINT]"

    return "[EQUIPAMENTO_REDE]"


def _validar_digitos_cpf(cpf: str) -> bool:
    """Verifica se os 11 dígitos formam um CPF numericamente válido."""
    numeros = [int(d) for d in cpf if d.isdigit()]
    if len(numeros) != 11:
        return False
    if len(set(numeros)) == 1:
        return False
    # Primeiro dígito verificador
    soma = sum(a * b for a, b in zip(numeros[:9], range(10, 1, -1)))
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    if resto != numeros[9]:
        return False
    # Segundo dígito verificador
    soma = sum(a * b for a, b in zip(numeros[:10], range(11, 1, -1)))
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    return resto == numeros[10]


def _substituir_ipv4(match: re.Match) -> str:
    candidato = match.group(0)
    try:
        ip = ipaddress.IPv4Address(candidato)
        # Generaliza o endereço IP para a sub-rede /24 correspondente (RF05)
        # Ex: 192.168.1.55 -> 192.168.1.0/24
        net = ipaddress.IPv4Network(f"{ip}/24", strict=False)
        return f"{net.network_address}/24"
    except ValueError:
        return candidato


def _substituir_ipv6(match: re.Match) -> str:
    candidato = match.group(0)
    try:
        ip = ipaddress.IPv6Address(candidato)
        # Generaliza o endereço IPv6 para o prefixo /64 correspondente
        net = ipaddress.IPv6Network(f"{ip}/64", strict=False)
        return f"{net.network_address}/64"
    except ValueError:
        return candidato


def registrar_auditoria_privacidade(categoria: str, detalhe: str) -> None:
    """Grava registro na trilha de auditoria sem expor payloads ou dados brutos."""
    audit_logger.warning("AUDIT_PRIVACY event=%s detalhe=%s", categoria, detalhe)


def sanitizar_texto(texto: str) -> ResultadoSanitizacao:
    """Aplica o pipeline two-pass de sanitização e validação residual sobre o texto."""
    if not isinstance(texto, str):
        return ResultadoSanitizacao(
            sucesso=False,
            texto_sanitizado="",
            motivo_bloqueio="Entrada inválida (não é texto)",
        )

    removidos: list[str] = []
    saida = texto

    try:
        # 1. Nomes literais configurados (ex: dr.joao)
        for nome in NOMES_CONFIGURADOS:
            if nome in saida.lower():
                pattern = re.compile(re.escape(nome), re.IGNORECASE)
                saida = pattern.sub("[USUARIO_MEDICO]", saida)
                removidos.append(f"nome_configurado:{nome}")

        # 2. Nomes por heurística profissional / clínica
        def _sub_nome_contextual(m: re.Match) -> str:
            removidos.append("nome_contextual")
            return "[NOME_REMOVIDO]"

        saida = RE_NOMES_CONTEXTUAIS.sub(_sub_nome_contextual, saida)

        # 3. E-mails
        if RE_EMAIL.search(saida):
            saida = RE_EMAIL.sub("[EMAIL_REMOVIDO]", saida)
            removidos.append("email")

        # 4. CPF (Formatado e Contextual com validação de dígitos)
        if RE_CPF_FORMATADO.search(saida):
            saida = RE_CPF_FORMATADO.sub("[CPF_REMOVIDO]", saida)
            removidos.append("cpf_formatado")

        def _sub_cpf_contextual(m: re.Match) -> str:
            digitos = re.sub(r"\D", "", m.group(0))
            if len(digitos) == 11 and _validar_digitos_cpf(digitos):
                removidos.append("cpf_contextual")
                return "[CPF_REMOVIDO]"
            return m.group(0)

        saida = RE_CPF_CONTEXTUAL.sub(_sub_cpf_contextual, saida)

        # 5. CNS (Cartão Nacional de Saúde)
        if RE_CNS.search(saida):
            saida = RE_CNS.sub("[CNS_REMOVIDO]", saida)
            removidos.append("cns")

        # 6. Hostnames em logs
        def _sub_hostname(m: re.Match) -> str:
            h = m.group(0)
            categoria = categorizar_equipamento(h)
            removidos.append(f"hostname:{categoria}")
            return categoria

        saida = RE_HOSTNAME_LOG.sub(_sub_hostname, saida)

        # 7. Número de Prontuário
        if RE_PRONTUARIO.search(saida):
            saida = RE_PRONTUARIO.sub("[PRONTUARIO_REMOVIDO]", saida)
            removidos.append("prontuario")

        # 8. Endereços MAC
        if RE_MAC.search(saida):
            saida = RE_MAC.sub("[MAC_MASCARADO]", saida)
            removidos.append("mac")

        # 9. Endereços IPv4 (conversão para /24)
        if RE_IPV4.search(saida):
            saida = RE_IPV4.sub(_substituir_ipv4, saida)
            removidos.append("ipv4_subrede")

        # 10. Endereços IPv6 (conversão para /64)
        if RE_IPV6.search(saida):
            saida = RE_IPV6.sub(_substituir_ipv6, saida)
            removidos.append("ipv6_subrede")

        # --- SEGUNDA PASSADA: Detecção Residual (Two-Pass Verification) ---
        residuos: list[str] = []

        # Detecção de IPv4 residual que não seja sub-rede /24
        for match in RE_IPV4.finditer(saida):
            cand = match.group(0)
            try:
                ipaddress.IPv4Address(cand)
                # Verifica se o IP está seguido por '/24' ou faz parte de token
                inicio, fim = match.span()
                sufixo = saida[fim:fim + 3]
                if sufixo != "/24":
                    residuos.append(f"ipv4_residual:{cand}")
            except ValueError:
                pass

        # Detecção de MAC residual
        if RE_MAC.search(saida):
            residuos.append("mac_residual")

        # Detecção de E-mail residual
        if RE_EMAIL.search(saida):
            residuos.append("email_residual")

        # Detecção de CPF formatado residual
        if RE_CPF_FORMATADO.search(saida):
            residuos.append("cpf_residual")

        # Detecção de CNS residual
        if RE_CNS.search(saida):
            residuos.append("cns_residual")

        if residuos:
            return ResultadoSanitizacao(
                sucesso=False,
                texto_sanitizado=saida,
                identificadores_removidos=removidos,
                residuos=residuos,
                motivo_bloqueio=f"Detecção residual de dados: {','.join(residuos)}",
            )

        return ResultadoSanitizacao(
            sucesso=True,
            texto_sanitizado=saida,
            identificadores_removidos=removidos,
            residuos=[],
        )

    except Exception as exc:
        logger.error("Erro interno no pipeline de sanitização: %s", type(exc).__name__)
        return ResultadoSanitizacao(
            sucesso=False,
            texto_sanitizado="",
            identificadores_removidos=removidos,
            residuos=["erro_execucao"],
            motivo_bloqueio=f"Exceção durante anonimização: {type(exc).__name__}",
        )


def anonimizar_dados(texto: str) -> str:
    """Função pública de anonimização (compatível com a API).

    Garante Fail-Closed: se houver resíduo de PII ou falha de processamento,
    dispara exceção e audita o evento, impedindo a continuidade do fluxo.
    """
    resultado = sanitizar_texto(texto)
    if not resultado.sucesso:
        registrar_auditoria_privacidade(
            categoria="sanitization_failed",
            detalhe=resultado.motivo_bloqueio or "falha_desconhecida",
        )
        raise SanitizationResidualError(
            f"Falha de conformidade LGPD: {resultado.motivo_bloqueio}"
        )
    return resultado.texto_sanitizado
