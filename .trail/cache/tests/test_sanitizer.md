# tests/test_sanitizer.py

- TestIdentificadoresRede · class · L15-L52 — class TestIdentificadoresRede
- test_ipv4_generalizacao_para_subrede_24 · method · L18-L25 — def test_ipv4_generalizacao_para_subrede_24(self)
- test_ipv4_preserva_numeros_de_versao · method · L27-L33 — def test_ipv4_preserva_numeros_de_versao(self): # Versões com 3 octetos não devem ser tratadas como IPv4
- test_ipv6_generalizacao_para_prefixo_64 · method · L35-L40 — def test_ipv6_generalizacao_para_prefixo_64(self)
- test_mac_address_mascarado · method · L42-L52 — def test_mac_address_mascarado(self)
- TestIdentificadoresEquipamentos · class · L55-L90 — class TestIdentificadoresEquipamentos
- test_categorizacao_equipamentos · method · L81-L82 — def test_categorizacao_equipamentos(self, hostname, categoria_esperada)
- test_hostnames_em_logs_sao_substituidos · method · L84-L90 — def test_hostnames_em_logs_sao_substituidos(self)
- TestIdentificadoresPessoaisEMedicos · class · L93-L137 — class TestIdentificadoresPessoaisEMedicos
- test_email_removido · method · L96-L101 — def test_email_removido(self)
- test_cpf_formatado_removido · method · L103-L108 — def test_cpf_formatado_removido(self)
- test_cns_cartao_sus_removido · method · L110-L115 — def test_cns_cartao_sus_removido(self)
- test_prontuario_medico_removido · method · L117-L122 — def test_prontuario_medico_removido(self)
- test_literal_dr_joao_legado_preservado · method · L124-L129 — def test_literal_dr_joao_legado_preservado(self)
- test_nomes_profissionais_e_clinicos_contextuais · method · L131-L137 — def test_nomes_profissionais_e_clinicos_contextuais(self)
- TestZeroPseudonimizacao · class · L140-L149 — class TestZeroPseudonimizacao
- test_sem_tabela_reversivel_em_memoria · method · L143-L149 — def test_sem_tabela_reversivel_em_memoria(self)
