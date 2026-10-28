import { useEffect, useRef, useState } from 'react';
import Diagnostic from './Diagnostic';
import { HealthPage, IncidentsPage, ApprovalsPage, AuditPage } from './OperationalPages';
import { useEvents } from './useEvents';

const level = { suporte_n1: 1, analista_redes: 2, gestor_ti: 3 };
const pages = [
  { id: 'health', label: 'Saúde dos serviços', minimum: 1, Component: HealthPage },
  { id: 'incidents', label: 'Incidentes', minimum: 2, Component: IncidentsPage },
  { id: 'approvals', label: 'Aprovações', minimum: 2, Component: ApprovalsPage },
  { id: 'audit', label: 'Auditoria', minimum: 3, Component: AuditPage },
  { id: 'diagnosis', label: 'Diagnóstico', minimum: 1, Component: Diagnostic },
];
export default function Operations({ session, onExpire }) {
  const [page, setPage] = useState('health');
  const [tick, setTick] = useState(0);
  const heading = useRef(null);
  const { connection, revision } = useEvents(session.token, onExpire);
  useEffect(() => { const timer = setInterval(() => setTick(n => n + 1), 15000); return () => clearInterval(timer); }, []);
  useEffect(() => { heading.current?.focus(); }, [page]);
  const visible = pages.filter(item => item.minimum <= (level[session.papel] || 0));
  const selected = visible.find(item => item.id === page) || visible[0];
  if (!selected) return <p role="alert">Perfil sem acesso ao painel.</p>;
  const Content = selected.Component;
  return <>
    <nav aria-label="Áreas do painel">{visible.map(item => <button key={item.id} aria-current={item.id === selected.id ? 'page' : undefined}
      onClick={() => setPage(item.id)}>{item.label}</button>)}</nav>
    <p className="stream-state" role="status">{connection === 'connected' ? 'Tempo real ativo' : connection === 'connecting' ? 'Conectando ao tempo real…' : 'Reconectando ao tempo real; dados atualizados também a cada 15 segundos.'}</p>
    <section className="workspace" aria-labelledby="page-title"><h2 id="page-title" ref={heading} tabIndex={-1}>{selected.label}</h2>
      <Content key={selected.id} session={session} onExpire={onExpire} revision={revision + tick} />
    </section>
  </>;
}
