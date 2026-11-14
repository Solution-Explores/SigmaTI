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


class TestRegressaoAuditoriaOrientador:
    """Regressão estrita para os 14 casos adversariais da conferência de 31/10/2026 (#5).

    Os 14 casos correspondem às 13 linhas da tabela do orientador, com a linha de
    hostname desdobrada em duas entradas de teste (ADV-09a para 'PACS-01' e ADV-09b
    para 'pacs01'). Cada caso fixa explicitamente se deve ser transformado (13 casos)
    ou bloqueado em modo fail-closed (ADV-04, 'Maria Oliveira (leito 12)').
    """

    @pytest.mark.parametrize(
        ("id_caso", "entrada", "fragmentos_proibidos", "espera_transformacao", "marcador_esperado"),
        [
            (
                "ADV-01",
                "Paciente: Ana Beatriz Souza sem acesso ao portal de exames",
                ["Ana", "Beatriz", "Souza"],
                True,
                "[NOME_REMOVIDO]",
            ),
            (
                "ADV-02",
                "Dr Pedro Alves sem acesso ao sistema de laudos",
                ["Pedro", "Alves"],
                True,
                "[NOME_REMOVIDO]",
            ),
            (
                "ADV-03",
                "Sra. Carla Mendes ligou informando queda no totem da recepção",
                ["Carla", "Mendes"],
                True,
                "[NOME_REMOVIDO]",
            ),
            (
                "ADV-04",
                "Maria Oliveira (leito 12) não consegue sincronizar monitor multiparamétrico",
                ["Maria", "Oliveira"],
                False,
                "nome_sem_contexto_residual",
            ),
            (
                "ADV-05",
                "usuario joao.silva bloqueado no AD após múltiplas tentativas",
                ["joao.silva", "joao", ".silva", "silva"],
                True,
                "[LOGIN_REMOVIDO]",
            ),
            (
                "ADV-06",
                "login: maria.souza falhou 5 vezes na autenticação RADIUS",
                ["maria.souza", "maria", ".souza", "souza"],
                True,
                "[LOGIN_REMOVIDO]",
            ),
            (
                "ADV-07",
                "CPF 123 456 789 09 do paciente recusado na validação cadastral",
                ["123 456 789 09", "123 456", "789 09"],
                True,
                "[CPF_REMOVIDO]",
            ),
            (
                "ADV-08",
                "Registro de atendimento 2026-000123 falhou ao sincronizar com o HIS",
                ["2026-000123", "000123"],
                True,
                "[REGISTRO_REMOVIDO]",
            ),
            (
                "ADV-09a",
                "Equipamento PACS-01 fora do ar no setor de imagem",
                ["PACS-01"],
                True,
                "[SERVIDOR_HOSPITALAR]",
            ),
            (
                "ADV-09b",
                "Servidor pacs01 sem resposta ao ping de monitoramento",
                ["pacs01"],
                True,
                "[SERVIDOR_HOSPITALAR]",
            ),
            (
                "ADV-10",
                "Telefone do responsável: (92) 99123-4567 não recebeu alerta SMS",
                ["(92) 99123-4567", "99123-4567", "991234567"],
                True,
                "[TELEFONE_REMOVIDO]",
            ),
            (
                "ADV-11",
                "RG 12.345.678-9 do acompanhante gerou erro de digitação no cadastro",
                ["12.345.678-9", "12.345.678"],
                True,
                "[RG_REMOVIDO]",
            ),
            (
                "ADV-12",
                "Data de nascimento 12/03/1984 divergente na integração HL7",
                ["12/03/1984", "1984"],
                True,
                "[DATA_NASCIMENTO_REMOVIDA]",
            ),
            (
                "ADV-13",
                "Endereço Rua das Flores, 123, Manaus falhou na validação de CEP",
                ["Rua das Flores", "Flores", "123", "Manaus"],
                True,
                "[ENDERECO_REMOVIDO]",
            ),
        ],
    )
    def test_casos_adversariais_nao_vazam_para_ia(
        self, id_caso, entrada, fragmentos_proibidos, espera_transformacao, marcador_esperado,
    ):
        """Fixa o resultado esperado de cada um dos 14 casos (13 transformados e ADV-04 bloqueado)."""
        resultado = sanitizar_texto(entrada)
        if espera_transformacao:
            assert resultado.sucesso is True, (
                f"Caso {id_caso} deveria ser transformado, mas foi bloqueado: {resultado.residuos!r}"
            )
            assert resultado.texto_sanitizado != entrada, (
                f"Caso {id_caso} passou inalterado sem bloqueio: {entrada!r}"
            )
            assert marcador_esperado in resultado.texto_sanitizado, (
                f"Caso {id_caso} não gerou o marcador esperado {marcador_esperado!r} em {resultado.texto_sanitizado!r}"
            )
            for proibido in fragmentos_proibidos:
                assert not re.search(re.escape(proibido), resultado.texto_sanitizado, re.IGNORECASE), (
                    f"Caso {id_caso} vazou fragmento proibido {proibido!r} em {resultado.texto_sanitizado!r}"
                )
        else:
            assert resultado.sucesso is False, (
                f"Caso {id_caso} deveria ser bloqueado em modo fail-closed, mas passou: {resultado.texto_sanitizado!r}"
            )
            assert marcador_esperado in resultado.residuos, (
                f"Caso {id_caso} bloqueado sem o resíduo esperado {marcador_esperado!r}: {resultado.residuos!r}"
            )


class TestConjuntoCegoE6:
    """Executa o conjunto de avaliação cega da #5: zero vazamentos e proteção relatada com intervalo.

    O critério original do E6 (recall de transformação) não é afirmado aqui: o conjunto cego é para
    relatar o recall com IC e declarar a limitação, não para ajustar a regra olhando o resultado.
    """

    def test_conjunto_cego_sem_vazamentos_e_protecao_relatada(self):
        from pathlib import Path
        import sys

        root = Path(__file__).resolve().parents[2]
        if str(root / "scripts") not in sys.path:
            sys.path.insert(0, str(root / "scripts"))
        from executar_experimento_e6 import carregar_corpus, executar_experimento

        caminho = Path(__file__).resolve().parent / "data" / "corpus_cego_pii.json"
        corpus = carregar_corpus(caminho)
        metricas = executar_experimento(corpus)

        assert metricas["total_identificadores"] >= 40
        assert metricas["negativos"] >= 20
        assert metricas["vazados"] == 0, f"Vazamentos detectados no conjunto cego: {metricas['detalhes']}"
        assert metricas["recall_protecao"] >= 99.0
        assert metricas["taxa_fp"] <= 5.0
        assert metricas["taxa_bloqueio"] <= 20.0
        assert metricas["aprovado_protecao"] is True
        # Bloqueio e transformação somam a proteção; nada fica sem contabilizar.
        assert metricas["removidos"] + metricas["bloqueados"] + metricas["vazados"] == metricas["total_identificadores"]
        lim_inf, lim_sup = metricas["ic_protecao"]
        assert lim_inf <= metricas["recall_protecao"] <= lim_sup

    def test_bloquear_todos_os_positivos_nao_aprova_protecao(self, monkeypatch):
        from pathlib import Path
        import sys
        import sanitizer

        root = Path(__file__).resolve().parents[2]
        if str(root / "scripts") not in sys.path:
            sys.path.insert(0, str(root / "scripts"))
        import executar_experimento_e6 as e6

        corpus = [
            {
                "id": "pos-1",
                "tipo": "positivo",
                "entrada": "CPF 52998224725",
                "identificadores": [{"classe": "cpf", "valor": "52998224725", "substituto": "[CPF_REMOVIDO]"}],
            },
            {
                "id": "neg-1",
                "tipo": "negativo",
                "entrada": "Link Ethernet estável",
                "identificadores": [],
            },
        ]
        monkeypatch.setattr(
            e6,
            "sanitizar_texto",
            lambda texto: (
                sanitizer.ResultadoSanitizacao(False, "", residuos=["bloqueio_total"])
                if "52998224725" in texto
                else sanitizer.ResultadoSanitizacao(True, texto)
            ),
        )
        m = e6.executar_experimento(corpus)
        assert m["recall_protecao"] == 100.0
        assert m["taxa_bloqueio"] == 100.0
        assert m["aprovado"] is False
        assert m["aprovado_protecao"] is False
