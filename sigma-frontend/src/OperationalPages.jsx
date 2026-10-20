import { useEffect, useState } from 'react';
import { useActionRequest } from './useActionRequest';
import { useResource } from './useResource';

const roles = { suporte_n1: 1, analista_redes: 2, gestor_ti: 3 };
const number = (value, digits = 2) => typeof value === 'number' && Number.isFinite(value)
  ? value.toLocaleString('pt-BR', { maximumFractionDigits: digits }) : '—';
const date = value => value && Number.isFinite(Date.parse(value)) ? new Date(value).toLocaleString('pt-BR') : '—';
const statuses = { up: 'Disponível', down: 'Indisponível', unknown: 'Sem dados recentes', inactive: 'Desativado' };

function ResourceState({ resource }) {
  if (resource.error) return <div className="error"><p role="alert">{resource.error}</p><button onClick={resource.refresh}>Tentar novamente</button></div>;
  if (resource.loading) return <p role="status">Carregando dados…</p>;
  return null;
}

export function HealthContent({ data }) {
  const services = data.servicos || [];
  if (!services.length) return <p className="empty">Nenhum serviço cadastrado. Solicite ao Analista de Redes o cadastro de um alvo.</p>;
  return <>
    <p className="muted">Até {data.limite || 500} serviços. Dados de {date(data.gerado_em)}. Sem coleta recente, o estado é desconhecido.</p>
    <div className="table-scroll" role="region" aria-label="Saúde dos serviços, tabela com rolagem horizontal" tabIndex={0}>
      <table><caption>Saúde e orçamento de disponibilidade</caption><thead><tr>
        <th scope="col">Serviço</th><th scope="col">Estado</th><th scope="col">Última medição</th>
        <th scope="col">Orçamento restante</th><th scope="col">Cobertura da janela</th><th scope="col">Projeção de esgotamento</th>
      </tr></thead><tbody>{services.map(service => <tr key={service.id}>
        <th scope="row">{service.nome}<small>{service.host}:{service.porta} · {service.kind.toUpperCase()}</small></th>
        <td><span className={`badge ${service.status}`}>{statuses[service.status] || 'Desconhecido'}</span></td>
        <td>{date(service.ultima_em)}<small>{service.latencia_ms == null ? 'Sem latência medida' : `${number(service.latencia_ms)} ms`}</small></td>
        <td>{!service.orcamento ? 'SLO não configurado' : <>
          <strong>{service.orcamento.completo ? '' : 'Até '}{number(service.orcamento.restante_max_min)} min</strong>
          <small>Meta {number(service.alvo_pct, 3)}% · {service.janela_dias} {service.janela_dias === 1 ? 'dia' : 'dias'}</small>
          {service.orcamento.status === 'breaching' && <span className="badge down">Orçamento esgotado</span>}
        </>}</td>
        <td>{service.orcamento ? <>{number(service.orcamento.cobertura_pct)}%<small>{service.orcamento.completo ? 'Janela observada' : 'Observação parcial'}</small></> : '—'}</td>
        <td>{service.orcamento?.esgota_em ? date(service.orcamento.esgota_em) : service.orcamento?.status === 'breaching' ? 'Orçamento já esgotado' : service.orcamento?.completo ? 'Sem esgotamento projetado' : 'Sem projeção suficiente'}</td>
      </tr>)}</tbody></table>
    </div>
    <p className="muted">Em janelas parciais, “até” é um limite máximo do orçamento restante. Períodos sem observação não contam como disponíveis. A projeção exige cobertura completa da janela.</p>
  </>;
}

export function HealthPage({ session, onExpire, revision }) {
  const resource = useResource('/api/eng/saude', session.token, onExpire, revision);
  return <><ResourceState resource={resource} />{resource.data && <HealthContent data={resource.data} />}
    <button className="secondary" onClick={resource.refresh}>Atualizar saúde</button></>;
}

export function IncidentMetrics({ data }) {
  return <div className="metric-grid">{['MTTD', 'MTTA', 'MTTR'].map(name => {
    const metric = data[name] || { n: 0 };
    return <section key={name} aria-label={name}><h3>{name}</h3>{metric.n ? <dl>
      <div><dt>Média</dt><dd>{number(metric.media_s)} s</dd></div>
      <div><dt>Mediana</dt><dd>{number(metric.mediana_s)} s</dd></div>
      <div><dt>p95</dt><dd>{number(metric.p95_s)} s</dd></div>
      <div><dt>Amostras</dt><dd>{metric.n}</dd></div>
    </dl> : <p>{name === 'MTTD' ? 'Sem início real de falha registrado.' : 'Sem transições suficientes para calcular.'}</p>}</section>;
  })}</div>;
}

export function IncidentsPage({ session, onExpire, revision }) {
  const request = useActionRequest(session.token);
  const resource = useResource('/api/eng/incidentes/resumo', session.token, onExpire, revision);
  const [feedback, setFeedback] = useState(null);
  const [busy, setBusy] = useState(null);
  async function transition(id, action) {
    setBusy(id); setFeedback(null);
    try {
      await request(`/api/eng/incidentes/${id}/${action}`, { method: 'POST', token: session.token });
      setFeedback({ message: action === 'resolver' ? 'Incidente resolvido.' : 'Incidente reconhecido.' });
      resource.refresh();
    } catch (error) {
      if (error.name === 'AbortError') return;
      if (error.status === 401) onExpire(error.message);
      else setFeedback({ error: true, message: error.message });
    } finally { setBusy(null); }
  }
  return <>
    <p>Tempos calculados a partir de até 500 incidentes mais recentes. Horários no fuso do navegador.</p>
    {feedback && <p role={feedback.error ? 'alert' : 'status'} className={feedback.error ? 'error' : 'notice'}>{feedback.message}</p>}
    <ResourceState resource={resource} />
    {resource.data && <><IncidentMetrics data={resource.data.metricas} />
      {!resource.data.incidentes.length ? <p className="empty">Nenhum incidente registrado.</p> :
      <div className="table-scroll" role="region" aria-label="Incidentes, tabela com rolagem horizontal" tabIndex={0}>
        <table><caption>Histórico de incidentes</caption><thead><tr><th scope="col">Incidente / alvo</th><th scope="col">Detecção</th><th scope="col">Estado</th><th scope="col">Ações</th></tr></thead>
          <tbody>{resource.data.incidentes.map(item => <tr key={item.id}>
            <th scope="row">{item.severidade} · {item.tipo}<small>{item.nome_alvo || item.alvo_id}</small><small className="identifier">{item.id}</small></th>
            <td>{date(item.detectado_em)}</td><td>{item.resolvido_em ? 'Resolvido' : item.reconhecido_em ? 'Reconhecido' : 'Aberto'}</td>
            <td><div className="actions"><button disabled={!!busy || !!item.reconhecido_em || !!item.resolvido_em} onClick={() => transition(item.id, 'reconhecer')}>Reconhecer</button>
              <button disabled={!!busy || !!item.resolvido_em} onClick={() => transition(item.id, 'resolver')}>Resolver incidente</button></div></td>
          </tr>)}</tbody></table>
      </div>}</>}
    <button className="secondary" onClick={resource.refresh}>Atualizar incidentes</button>
  </>;
}

export function ApprovalItem({ item, session, onDecide }) {
  const [reason, setReason] = useState('');
  const [busy, setBusy] = useState(false);
  const own = item.solicitante === session.usuario;
  const insufficient = (roles[session.papel] || 0) < (roles[item.papel_minimo] || 99);
  const [expired, setExpired] = useState(() => Date.parse(item.expira_em) <= Date.now());
  useEffect(() => {
    const timer = setTimeout(() => setExpired(true), Math.max(0, Math.min(2147483647, Date.parse(item.expira_em) - Date.now())));
    return () => clearTimeout(timer);
  }, [item.expira_em]);
  const disabled = busy || own || insufficient || expired;
  async function decide(event) {
    event.preventDefault();
    const approved = event.nativeEvent.submitter?.value === 'approve';
    setBusy(true);
    try { await onDecide(item.id, approved, reason.trim()); }
    finally { setBusy(false); }
  }
  return <article className="approval-item" aria-label={`Solicitação: ${item.acao}`}>
    <h3>{item.acao}</h3><p>Solicitado por <strong>{item.solicitante}</strong> · Expira em {date(item.expira_em)}</p>
    {own && <p className="notice">Você solicitou esta ação. Outro integrante precisa decidir.</p>}
    {insufficient && <p className="notice">Esta solicitação exige o perfil {item.papel_minimo}.</p>}
    {expired && <p className="notice">Solicitação expirada. Atualize a lista.</p>}
    <form onSubmit={decide}>
      <label htmlFor={`reason-${item.id}`}>Justificativa da decisão</label>
      <textarea id={`reason-${item.id}`} value={reason} onChange={e => setReason(e.target.value)} required maxLength={500} rows={2} disabled={disabled} />
      <div className="actions"><button type="submit" value="approve" disabled={disabled || !reason.trim()}>Aprovar</button>
        <button className="secondary" type="submit" value="reject" disabled={disabled || !reason.trim()}>Rejeitar</button></div>
    </form>
  </article>;
}

export function ApprovalsPage({ session, onExpire, revision }) {
  const request = useActionRequest(session.token);
  const resource = useResource('/api/eng/aprovacoes', session.token, onExpire, revision);
  const [feedback, setFeedback] = useState(null);
  const [action, setAction] = useState('');
  const [role, setRole] = useState('analista_redes');
  const [creating, setCreating] = useState(false);
  async function decide(id, approved, reason) {
    setFeedback(null);
    try {
      await request(`/api/eng/aprovacoes/${id}/decidir`, { method: 'POST', token: session.token,
        body: { aprovar: approved, justificativa: reason } });
      setFeedback({ message: approved ? 'Solicitação aprovada.' : 'Solicitação rejeitada.' });
      resource.refresh();
    } catch (error) {
      if (error.name === 'AbortError') return;
      if (error.status === 401) onExpire(error.message);
      else { setFeedback({ error: true, message: error.message }); if (error.status === 409) resource.refresh(); }
    }
  }
  async function create(event) {
    event.preventDefault(); setCreating(true); setFeedback(null);
    try {
      await request('/api/eng/aprovacoes', { method: 'POST', token: session.token, body: { acao: action.trim(), papel_minimo: role } });
      setAction(''); setFeedback({ message: 'Solicitação enviada para revisão por outro integrante.' }); resource.refresh();
    } catch (error) {
      if (error.name === 'AbortError') return;
      if (error.status === 401) onExpire(error.message);
      else setFeedback({ error: true, message: error.message });
    } finally { setCreating(false); }
  }
  return <>
    <p>Solicitar ou aprovar registra uma decisão. Nenhum comando é executado por esta página.</p>
    {feedback && <p role={feedback.error ? 'alert' : 'status'} className={feedback.error ? 'error' : 'notice'}>{feedback.message}</p>}
    <details className="request-details"><summary>Nova solicitação</summary><form onSubmit={create}>
      <label htmlFor="approval-action">Ação a revisar</label><input id="approval-action" value={action} onChange={e => setAction(e.target.value)} required maxLength={200} disabled={creating} />
      <label htmlFor="approval-role">Perfil mínimo do decisor</label><select id="approval-role" value={role} onChange={e => setRole(e.target.value)} disabled={creating}>
        <option value="analista_redes">Analista de Redes</option><option value="gestor_ti">Gestor de TI</option></select>
      <button disabled={creating || !action.trim()} type="submit">{creating ? 'Enviando…' : 'Solicitar revisão'}</button>
    </form></details>
    <ResourceState resource={resource} />
    {resource.data && (resource.data.aprovacoes.length ? resource.data.aprovacoes.map(item =>
      <ApprovalItem key={item.id} item={item} session={session} onDecide={decide} />) : <p className="empty">Nenhuma aprovação pendente.</p>)}
    <button className="secondary" onClick={resource.refresh}>Atualizar aprovações</button>
  </>;
}

export function AuditContent({ chain, events }) {
  return <>
    <section aria-labelledby="chain-heading"><h3 id="chain-heading">Integridade da trilha de sondas</h3>
      {chain.entradas === 0 ? <p className="notice">Trilha vazia: não há registros para verificar.</p> :
        <p role={chain.integra ? 'status' : 'alert'} className={chain.integra ? 'notice' : 'error'}>
          {chain.integra ? 'Integridade consistente' : 'Falha de integridade detectada'} · {chain.entradas} registros
        </p>}
      <p className="muted">Esta verificação cobre a trilha de sondas. Os eventos operacionais abaixo têm armazenamento separado.</p>
    </section>
    <div className="table-scroll" role="region" aria-label="Eventos operacionais, tabela com rolagem horizontal" tabIndex={0}>
      <table><caption>Até 100 eventos operacionais mais recentes</caption><thead><tr><th scope="col">Horário</th><th scope="col">Operador</th><th scope="col">Ação</th><th scope="col">Recurso</th></tr></thead>
        <tbody>{events.map(item => <tr key={item.id}><td>{date(item.ts)}</td><td>{item.ator}</td><td>{item.acao}</td><td className="identifier">{item.recurso}</td></tr>)}</tbody>
      </table>{!events.length && <p className="empty">Nenhum evento operacional registrado.</p>}
    </div>
  </>;
}

export function AuditPage({ session, onExpire, revision }) {
  const chain = useResource('/api/eng/auditoria/verificar', session.token, onExpire, revision);
  const events = useResource('/api/eng/auditoria/recentes', session.token, onExpire, revision);
  return <><ResourceState resource={chain} /><ResourceState resource={events} />
    {chain.data && events.data && <AuditContent chain={chain.data} events={events.data.eventos} />}
    <button className="secondary" onClick={() => { chain.refresh(); events.refresh(); }}>Atualizar auditoria</button></>;
}
