import { useState } from 'react';
import { useActionRequest } from './useActionRequest';

export default function Diagnostic({ session, onExpire }) {
  const request = useActionRequest(session.token);
  const [equipamento, setEquipamento] = useState('Switch de teste');
  const [ipOrigem, setIpOrigem] = useState('192.0.2.10');
  const [descricaoErro, setDescricaoErro] = useState('Perda de pacotes no IP 192.0.2.10.');
  const [loading, setLoading] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [erro, setErro] = useState(null);

  async function enviarAlerta(event) {
    event.preventDefault();
    setLoading(true);
    setErro(null);
    setResultado(null);
    try {
      setResultado(await request('/api/alertas', {
        method: 'POST', token: session.token,
        body: { equipamento, ip_origem: ipOrigem, descricao_erro: descricaoErro },
      }));
    } catch (error) {
      if (error.name === 'AbortError') return;
      if (error.status === 401) onExpire(error.message);
      setErro(error.message);
    } finally {
      setLoading(false);
    }
  }

  return <>
    {erro && <p role="alert" className="error">{erro}</p>}
          <div className="columns">
            <section className="card" aria-labelledby="alert-title">
              <h2 id="alert-title">Enviar alerta</h2>
              <form onSubmit={enviarAlerta}>
                <label htmlFor="equipment">Equipamento</label>
                <input id="equipment" value={equipamento} onChange={e => setEquipamento(e.target.value)} required disabled={loading} />
                <label htmlFor="ip">IP de origem</label>
                <input id="ip" value={ipOrigem} onChange={e => setIpOrigem(e.target.value)} required disabled={loading} />
                <label htmlFor="description">Descrição do erro</label>
                <textarea id="description" rows={6} value={descricaoErro} onChange={e => setDescricaoErro(e.target.value)} required disabled={loading} />
                <button type="submit" disabled={loading}>{loading ? 'Processando…' : 'Solicitar diagnóstico'}</button>
              </form>
            </section>
            <section className="card" aria-labelledby="result-title" aria-live="polite" aria-busy={loading}>
              <h2 id="result-title">Resultado</h2>
              {resultado ? <>
                <h4>Dados enviados à IA</h4>
                <pre>{resultado.dados_enviados_nuvem}</pre>
                <h4>Diagnóstico da IA</h4>
                <p className="diagnosis">{resultado.diagnostico_ia}</p>
              </> : <p>O diagnóstico aparecerá aqui após o envio.</p>}
            </section>
          </div>
  </>;
}
