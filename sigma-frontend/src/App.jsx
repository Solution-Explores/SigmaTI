import { useState } from 'react';
import './App.css';

function App() {
  const [equipamento, setEquipamento] = useState('Switch Core UTI');
  const [ipOrigem, setIpOrigem] = useState('192.168.1.50');
  const [descricaoErro, setDescricaoErro] = useState('O computador do dr.joao no IP 10.0.5.15 está perdendo pacotes críticos e desconectando do sistema oncológico.');
  
  const [loading, setLoading] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [erroApi, setErroApi] = useState(null);

  const enviarAlerta = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResultado(null);
    setErroApi(null);

    try {
      const resposta = await fetch('http://localhost:8000/api/alertas', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          equipamento: equipamento,
          ip_origem: ipOrigem,
          descricao_erro: descricaoErro
        }),
      });

      if (!resposta.ok) {
        throw new Error(`Erro na API: ${resposta.statusText}`);
      }

      const dados = await resposta.json();
      setResultado(dados);
    } catch (err) {
      setErroApi('Não foi possível conectar à API do FastAPI. Verifique se o servidor está rodando na porta 8000.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#13131a', padding: '40px 20px', fontFamily: 'Arial, sans-serif' }}>
      <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
        
        {/* Cabeçalho */}
        <header style={{ borderBottom: '2px solid #0056b3', paddingBottom: '15px', marginBottom: '30px', textAlign: 'center' }}>
          <h1 style={{ color: '#007bff', margin: '0', fontSize: '36px', fontWeight: 'normal' }}>
            SIGMA - Painel de Monitoramento
          </h1>
          <p style={{ color: '#6c757d', margin: '5px 0 0 0', fontSize: '16px' }}>
            Sistema Inteligente de Gestão e Monitoramento Ativo (Fcecon)
          </p>
        </header>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>
          
          {/* Formulário de Simulação de Alerta */}
          <div style={{ background: '#ffffff', padding: '30px', borderRadius: '8px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
            <h2 style={{ textAlign: 'center', color: '#f1f1f1', marginTop: 0 }}>Simular Alerta de Rede</h2>
            <form onSubmit={enviarAlerta}>
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '8px', color: '#888', textAlign: 'center' }}>Equipamento:</label>
                <input 
                  type="text" 
                  value={equipamento} 
                  onChange={(e) => setEquipamento(e.target.value)} 
                  style={{ width: '100%', padding: '12px', boxSizing: 'border-box', backgroundColor: '#2d2d35', color: '#fff', border: '1px solid #444', borderRadius: '4px' }}
                />
              </div>

              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '8px', color: '#888', textAlign: 'center' }}>IP de Origem:</label>
                <input 
                  type="text" 
                  value={ipOrigem} 
                  onChange={(e) => setIpOrigem(e.target.value)} 
                  style={{ width: '100%', padding: '12px', boxSizing: 'border-box', backgroundColor: '#2d2d35', color: '#fff', border: '1px solid #444', borderRadius: '4px' }}
                />
              </div>

              <div style={{ marginBottom: '25px' }}>
                <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '8px', color: '#888', textAlign: 'center' }}>Descrição do Erro (com dados sensíveis):</label>
                <textarea 
                  value={descricaoErro} 
                  onChange={(e) => setDescricaoErro(e.target.value)} 
                  rows="4"
                  style={{ width: '100%', padding: '12px', boxSizing: 'border-box', backgroundColor: '#2d2d35', color: '#fff', border: '1px solid #444', borderRadius: '4px', resize: 'vertical' }}
                />
              </div>

              <button 
                type="submit" 
                disabled={loading}
                style={{ background: '#007bff', color: 'white', border: 'none', padding: '14px 15px', borderRadius: '4px', cursor: 'pointer', width: '100%', fontWeight: 'bold', fontSize: '16px' }}
              >
                {loading ? 'Processando...' : 'Disparar Alerta para a API'}
              </button>
            </form>
          </div>

          {/* Área de Exibição dos Resultados */}
          <div style={{ background: '#ffffff', padding: '30px', borderRadius: '8px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', display: 'flex', flexDirection: 'column' }}>
            <h2 style={{ textAlign: 'center', color: '#f1f1f1', marginTop: 0 }}>Diagnóstico em Tempo Real</h2>
            
            {erroApi && (
              <div style={{ background: '#f8d7da', color: '#721c24', padding: '15px', borderRadius: '4px', marginBottom: '15px', textAlign: 'center' }}>
                {erroApi}
              </div>
            )}

            {!resultado && !erroApi && !loading && (
              <p style={{ color: '#aaa', fontStyle: 'italic', textAlign: 'center', marginTop: '40px' }}>
                Envie um alerta ao lado para ver a resposta da API e da Inteligência Artificial.
              </p>
            )}

            {loading && (
              <p style={{ color: '#007bff', textAlign: 'center', marginTop: '40px' }}>Aguardando processamento e anonimização (LGPD)...</p>
            )}

            {resultado && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '25px' }}>
                
                <div style={{ background: '#d4edda', color: '#155724', padding: '12px', borderRadius: '4px', fontSize: '16px', textAlign: 'center' }}>
                  <strong>Status:</strong> {resultado.status}
                </div>

                <div>
                  <strong style={{ display: 'block', fontSize: '14px', color: '#333', textAlign: 'center', marginBottom: '8px' }}>
                    Dados Sanitizados (Enviados à Nuvem / LGPD):
                  </strong>
                  <pre style={{ background: '#f8f9fa', color: '#a0a0a0', padding: '15px', borderRadius: '4px', fontSize: '12px', whiteSpace: 'pre-wrap', wordBreak: 'break-all', margin: '0', border: '1px solid #eee' }}>
                    {resultado.dados_enviados_nuvem}
                  </pre>
                </div>

                <div>
                  <strong style={{ display: 'block', fontSize: '14px', color: '#007bff', textAlign: 'center', marginBottom: '8px' }}>
                    Diagnóstico da IA (Qwen/Llama):
                  </strong>
                  <div style={{ background: '#e7f5ff', borderLeft: '4px solid #007bff', padding: '20px', borderRadius: '0 4px 4px 0', fontSize: '13px', color: '#777', whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>
                    {resultado.diagnostico_ia}
                  </div>
                </div>

              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}

export default App;