"""Testes unitários para o módulo sanitizer em conformidade com o RF05."""

import re
import pytest

from sanitizer import (
    ResultadoSanitizacao,
    SanitizationResidualError,
    anonimizar_dados,
    categorizar_equipamento,
    sanitizar_texto,
)


class TestIdentificadoresRede:
    """Validação de sanitização e generalização de dados de rede."""

    def test_ipv4_generalizacao_para_subrede_24(self):
        texto = "Falha de conexão com host 192.168.1.55 e gateway 10.0.4.1"
        resultado = sanitizar_texto(texto)
        assert resultado.sucesso is True
        assert "192.168.1.0/24" in resultado.texto_sanitizado
        assert "10.0.4.0/24" in resultado.texto_sanitizado
        assert "192.168.1.55" not in resultado.texto_sanitizado
        assert "10.0.4.1" not in resultado.texto_sanitizado

    def test_ipv4_preserva_numeros_de_versao(self):
        # Versões com 3 octetos não devem ser tratadas como IPv4
        texto = "Executando zabbix 6.4.21 e n8n 1.80.0"
        resultado = sanitizar_texto(texto)
        assert resultado.sucesso is True
        assert "6.4.21" in resultado.texto_sanitizado
        assert "1.80.0" in resultado.texto_sanitizado

    def test_ipv6_generalizacao_para_prefixo_64(self):
        texto = "Erro no host 2001:0db8:85a3:0000:0000:8a2e:0370:7334 na interface eth0"
        resultado = sanitizar_texto(texto)
        assert resultado.sucesso is True
        assert "2001:db8:85a3::/64" in resultado.texto_sanitizado or "2001:0db8:85a3" in resultado.texto_sanitizado
        assert "0370:7334" not in resultado.texto_sanitizado

    def test_mac_address_mascarado(self):
        casos = [
            ("MAC 00:1B:44:11:3A:B7 offline", "[MAC_MASCARADO]"),
            ("Interface com 00-1B-44-11-3A-B7 com erro", "[MAC_MASCARADO]"),
            ("Hardware 0123.4567.89ab falhou", "[MAC_MASCARADO]"),
        ]
        for entrada, esperado in casos:
            resultado = sanitizar_texto(entrada)
            assert resultado.sucesso is True
            assert esperado in resultado.texto_sanitizado
            assert "00:1B:44:11:3A:B7" not in resultado.texto_sanitizado


class TestIdentificadoresEquipamentos:
    """Validação de classificação de hostnames em categorias funcionais."""

    @pytest.mark.parametrize(
        ("hostname", "categoria_esperada"),
        [
            ("sw-core-01", "[SWITCH_REDE]"),
            ("switch-borda-bloco-a", "[SWITCH_REDE]"),
            ("rt-gateway-fcecon", "[ROTEADOR_REDE]"),
            ("router-externo", "[ROTEADOR_REDE]"),
            ("fw-pfsense-01", "[FIREWALL_REDE]"),
            ("firewall-corp", "[FIREWALL_REDE]"),
            ("srv-prontuario-db", "[SERVIDOR_HOSPITALAR]"),
            ("database-postgres", "[SERVIDOR_HOSPITALAR]"),
            ("tomografo-ge-01", "[EQUIPAMENTO_IMAGEM]"),
            ("ct-scan-oncologia", "[EQUIPAMENTO_IMAGEM]"),
            ("ressonancia-magnetica", "[EQUIPAMENTO_IMAGEM]"),
            ("monitor-multiparametrico-03", "[DISPOSITIVO_BIOMEDICO]"),
            ("bomba-infusao-uti", "[DISPOSITIVO_BIOMEDICO]"),
            ("term-triagem-02", "[ESTACAO_CLINICA]"),
            ("ws-ambulatorio-1", "[ESTACAO_CLINICA]"),
            ("ap-enfermaria-bloco-b", "[ACCESS_POINT]"),
            ("", "[EQUIPAMENTO_GENERICO]"),
            ("desconhecido-xyz", "[EQUIPAMENTO_REDE]"),
        ],
    )
    def test_categorizacao_equipamentos(self, hostname, categoria_esperada):
        assert categorizar_equipamento(hostname) == categoria_esperada

    def test_hostnames_em_logs_sao_substituidos(self):
        texto = "Perda de pacotes entre sw-core-01 e srv-prontuario.fcecon"
        resultado = sanitizar_texto(texto)
        assert resultado.sucesso is True
        assert "[SWITCH_REDE]" in resultado.texto_sanitizado
        assert "[SERVIDOR_HOSPITALAR]" in resultado.texto_sanitizado
        assert "sw-core-01" not in resultado.texto_sanitizado


class TestIdentificadoresPessoaisEMedicos:
    """Validação de remoção de dados pessoais e de saúde (LGPD / RF05)."""

    def test_email_removido(self):
        texto = "Contato de suporte: carlos.almeida@fcecon.am.gov.br ou ti@hospital.org"
        resultado = sanitizar_texto(texto)
        assert resultado.sucesso is True
        assert "[EMAIL_REMOVIDO]" in resultado.texto_sanitizado
        assert "carlos.almeida@fcecon.am.gov.br" not in resultado.texto_sanitizado

    def test_cpf_formatado_removido(self):
        texto = "Paciente CPF: 123.456.789-00 relatou lentidão no terminal"
        resultado = sanitizar_texto(texto)
        assert resultado.sucesso is True
        assert "[CPF_REMOVIDO]" in resultado.texto_sanitizado
        assert "123.456.789-00" not in resultado.texto_sanitizado

    def test_cns_cartao_sus_removido(self):
        texto = "CNS informado: 700001234567890 para atendimento ambulatorial"
        resultado = sanitizar_texto(texto)
        assert resultado.sucesso is True
        assert "[CNS_REMOVIDO]" in resultado.texto_sanitizado
        assert "700001234567890" not in resultado.texto_sanitizado

    def test_prontuario_medico_removido(self):
        texto = "Erro ao carregar prontuário #REC-987654 no visualizador"
        resultado = sanitizar_texto(texto)
        assert resultado.sucesso is True
        assert "[PRONTUARIO_REMOVIDO]" in resultado.texto_sanitizado
        assert "REC-987654" not in resultado.texto_sanitizado

    def test_literal_dr_joao_legado_preservado(self):
        texto = "Solicitação aberta por dr.joao na ala leste"
        resultado = sanitizar_texto(texto)
        assert resultado.sucesso is True
        assert "[USUARIO_MEDICO]" in resultado.texto_sanitizado
        assert "dr.joao" not in resultado.texto_sanitizado

    def test_nomes_profissionais_e_clinicos_contextuais(self):
        texto = "Dra. Ana Paula e o enfermeiro Roberto Santos identificaram parada no link"
        resultado = sanitizar_texto(texto)
        assert resultado.sucesso is True
        assert "[NOME_REMOVIDO]" in resultado.texto_sanitizado
        assert "Ana Paula" not in resultado.texto_sanitizado
        assert "Roberto Santos" not in resultado.texto_sanitizado


class TestZeroPseudonimizacao:
    """Verifica cumprimento estrito do RF05 (Art. 12 LGPD: sem tabela de/para)."""

    def test_sem_tabela_reversivel_em_memoria(self):
        import sanitizer
        # Confere que não há atributos de dicionário de correspondência (de/para) no módulo
        for attr in dir(sanitizer):
            val = getattr(sanitizer, attr)
            if isinstance(val, dict):
                assert attr not in {"de_para", "mapeamento_reverso", "lookup_table", "tabela_correspondencia"}
