import { useRef, useState } from 'react';
import { Badge, EmptyState, Icon } from './ui';
const IA_UNAVAILABLE = 'Diagnóstico de IA indisponível no momento. Tente novamente mais tarde.';
export function AlertSimulator() {
  const [form, setForm] = useState({
    equipamento: 'Switch de teste',
    ip_origem: '192.0.2.10',
    descricao_erro: 'Cenário fictício: perda de pacotes e desconexões intermitentes no enlace de teste.'
  });
  const [state, setState] = useState('idle');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const pending = useRef(false);
  const setField = event => {
    const {
      name,
      value
    } = event.target;
    setForm(previous => ({
      ...previous,
      [name]: value
    }));
  };
  async function submit(event) {
    event.preventDefault();
    if (pending.current) return;
    if (Object.values(form).some(value => !value.trim())) {
      setResult(null);
      setError('Preencha todos os campos com informações do cenário de teste.');
      setState('error');
      return;
    }
    pending.current = true;
    setState('loading');
    setResult(null);
    setError('');
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 20000);
    try {
      const response = await fetch('http://localhost:8000/api/alertas', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(Object.fromEntries(Object.entries(form).map(([key, value]) => [key, value.trim()]))),
        signal: controller.signal
      });
      if (!response.ok) throw new Error(response.status === 422 ? 'Confira os dados informados e tente novamente. (HTTP 422)' : `Não foi possível processar o alerta. Tente novamente mais tarde. (HTTP ${response.status})`);
      let data;
      try {
        data = await response.json();
      } catch {
        throw new Error('A API retornou uma resposta inválida. Tente novamente mais tarde.');
      }
      if (!data || ['status', 'dados_enviados_nuvem', 'diagnostico_ia'].some(key => typeof data[key] !== 'string' || !data[key].trim())) throw new Error('A API retornou uma resposta inválida. Tente novamente mais tarde.');
      setResult(data);
      setState(data.diagnostico_ia.trim() === IA_UNAVAILABLE ? 'unavailable' : 'success');
    } catch (failure) {
      setError(controller.signal.aborted ? 'O tempo de espera de 20 segundos foi excedido. O processamento no servidor pode continuar. Confira antes de enviar novamente.' : failure instanceof TypeError ? 'Não foi possível conectar ao serviço. Verifique a conexão e tente novamente.' : failure.message);
      setState('error');
    } finally {
      clearTimeout(timeout);
      pending.current = false;
    }
  }
  return <>
    <div className="api-banner">
      <Icon name="send" />
      <div>
        <strong>Simulação com envio à API configurada</strong>
        <p>Use somente informações fictícias. Este envio é independente dos dados demonstrativos do painel.</p>
      </div>
    </div>
    <div className="simulator-grid">
      <section className="panel form-panel">
        <div className="panel-heading">
          <div>
            <h2>Novo cenário de teste</h2>
            <p>Descreva o comportamento observado na rede.</p>
          </div>
          <span className="metric-icon blue"><Icon name="send" /></span>
        </div>
        <form onSubmit={submit}>
          <fieldset disabled={state === 'loading'}>
            <legend className="sr-only">Dados do alerta</legend>
            <label htmlFor="equipamento">Equipamento <span className="required">*</span></label>
            <input id="equipamento" name="equipamento" value={form.equipamento} onChange={setField} required />
            <p className="field-help">Nome fictício para identificar o cenário.</p>
            <label htmlFor="ip_origem">IP de origem <span className="required">*</span></label>
            <input id="ip_origem" name="ip_origem" value={form.ip_origem} onChange={setField} required spellCheck={false} autoCapitalize="off" />
            <p className="field-help">Exemplo reservado para documentação: 192.0.2.10.</p>
            <label htmlFor="descricao_erro">Descrição do problema <span className="required">*</span></label>
            <textarea id="descricao_erro" name="descricao_erro" rows={5} value={form.descricao_erro} onChange={setField} aria-describedby="description-help" required />
            <p id="description-help" className="field-help">Informe os sintomas. Não inclua dados pessoais ou informações reais do hospital.</p>
            <button className="button primary submit-button" type="submit" disabled={state === 'loading'}><Icon name={state === 'loading' ? 'clock' : 'send'} />{state === 'loading' ? 'Processando cenário…' : 'Enviar para diagnóstico'}</button>
          </fieldset>
          <p className="form-footnote"><Icon name="info" size={16} />* Todos os campos são obrigatórios. Nenhum envio é automático.</p>
        </form>
      </section>
      <section className="panel diagnosis-panel">
        <div className="panel-heading">
          <div>
            <h2>Diagnóstico assistido</h2>
            <p>Resposta da API para o último envio.</p>
          </div>
          <Icon name="activity" />
        </div>
        <div className="diagnosis-body">
          <div role="status" aria-live="polite" className="sr-only">
            {state === 'loading' ? 'Processando cenário. Aguardando resposta da API.' : state === 'success' ? 'Resposta recebida. Diagnóstico disponível.' : state === 'unavailable' ? 'Resposta recebida, mas o diagnóstico de IA está indisponível.' : ''}
          </div>
          {state === 'idle' && <EmptyState title="Pronto para analisar" description="Envie um cenário fictício no formulário para consultar o diagnóstico assistido por IA." />}
          {state === 'loading' && <div className="empty-state">
            <span className="loading-ring" aria-hidden="true" />
            <h3>Analisando o cenário</h3>
            <p>Aguardando a resposta do serviço. Isso pode levar alguns segundos.</p>
          </div>}
          {state === 'error' && <div className="feedback error-feedback" role="alert">
            <Icon name="warning" />
            <div>
              <h3>Não foi possível concluir</h3>
              <p>{error}</p>
              <p>Os campos foram preservados para você tentar novamente.</p>
            </div>
          </div>}
          {result && <>
            <div className={`feedback ${state === 'unavailable' ? 'warning-feedback' : 'success-feedback'}`}>
              <Icon name={state === 'unavailable' ? 'warning' : 'check'} />
              <div>
                <h3>{state === 'unavailable' ? 'Diagnóstico de IA indisponível' : 'Resposta recebida'}</h3>
                <p>Status informado pela API: {result.status}</p>
                <small>A resposta não comprova persistência do incidente.</small>
              </div>
            </div>
            <div className="diagnosis-result">
              <div className="section-label">
                <Icon name="activity" size={18} />
                <h3>Diagnóstico da IA</h3>
              </div>
              {state === 'unavailable' && <Badge tone="warning">Análise indisponível</Badge>}
              <p className="response-text">{result.diagnostico_ia}</p>
            </div>
            <details className="payload-details">
              <summary><Icon name="shield" size={18} />Conteúdo enviado ao provedor<Icon name="chevron" size={16} /></summary>
              <p>Conteúdo retornado pela API. A anonimização atual é limitada; use apenas dados fictícios.</p>
              <pre>{result.dados_enviados_nuvem}</pre>
            </details>
          </>}
        </div>
      </section>
    </div>
  </>;
}
