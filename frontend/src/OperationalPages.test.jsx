import { describe, it, expect, vi } from 'vitest';
import { render, screen, within, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HealthContent, IncidentMetrics, ApprovalItem, AuditContent } from './OperationalPages';
import Operations from './Operations';

vi.mock('./useEvents', () => ({ useEvents: () => ({ connection: 'connected', revision: 0 }) }));
vi.mock('./useResource', () => ({ useResource: path => ({ loading: false, error: null, refresh: vi.fn(),
  data: path.includes('resumo') ? { incidentes: [], metricas: {} } : path.includes('aprovacoes') ? { aprovacoes: [] }
    : path.includes('verificar') ? { integra: true, entradas: 0 } : { servicos: [], eventos: [] },
}) }));
const pending = { id: 'synthetic', acao: 'Revisar configuração do switch', solicitante: 'other',
  expira_em: new Date(Date.now() + 600000).toISOString(), papel_minimo: 'analista_redes' };
const analyst = { usuario: 'analyst', papel: 'analista_redes', token: 'synthetic' };

describe('dados operacionais honestos', () => {
  it('não transforma serviço vazio em disponibilidade total', () => {
    render(<HealthContent data={{ servicos: [] }} />);
    expect(screen.getByText(/Nenhum serviço cadastrado/)).toBeVisible();
    expect(screen.queryByText(/100%/)).not.toBeInTheDocument();
  });
  it('expõe lacuna de observação e orçamento apenas como limite', () => {
    render(<HealthContent data={{ servicos: [{ id: 'a', nome: 'Portal', host: '127.0.0.1', porta: 80,
      kind: 'http', status: 'unknown', alvo_pct: 99.9, janela_dias: 30, ultima_em: null,
      orcamento: { completo: false, cobertura_pct: 2, restante_max_min: 30, status: 'partial' } }] }} />);
    expect(screen.getByText('Sem dados recentes')).toBeVisible();
    expect(screen.getByText('Até 30 min')).toBeVisible();
    expect(screen.getByText('Observação parcial')).toBeVisible();
    expect(screen.getByText('Sem projeção suficiente')).toBeVisible();
  });
  it('não inventa MTTD com ausência de início real', () => {
    render(<IncidentMetrics data={{ MTTD: { n: 0 }, MTTA: { n: 2, media_s: 10, mediana_s: 9, p95_s: 12 } }} />);
    expect(within(screen.getByRole('region', { name: 'MTTD' })).getByText(/Sem início real/)).toBeVisible();
    expect(within(screen.getByRole('region', { name: 'MTTA' })).getByText('10 s')).toBeVisible();
  });
  it('não atesta uma trilha vazia', () => {
    render(<AuditContent chain={{ integra: true, entradas: 0 }} events={[]} />);
    expect(screen.getByText(/Trilha vazia/)).toBeVisible();
    expect(screen.queryByText('Integridade consistente')).not.toBeInTheDocument();
  });
  it('anuncia falha de integridade e escapa conteúdo dos eventos', () => {
    render(<AuditContent chain={{ integra: false, entradas: 2 }} events={[{ id: 1, acao: '<script>alert(1)</script>' }]} />);
    expect(screen.getByRole('alert')).toHaveTextContent('Falha de integridade');
    expect(screen.getByText('<script>alert(1)</script>')).toBeVisible();
    expect(document.querySelector('script')).toBeNull();
  });
});

describe('aprovação por outro integrante', () => {
  it('impede autoaprovação', () => {
    render(<ApprovalItem item={{ ...pending, solicitante: analyst.usuario }} session={analyst} onDecide={vi.fn()} />);
    expect(screen.getByRole('button', { name: 'Aprovar' })).toBeDisabled();
    expect(screen.getByText(/Outro integrante precisa decidir/)).toBeVisible();
  });
  it('respeita perfil mínimo', () => {
    render(<ApprovalItem item={{ ...pending, papel_minimo: 'gestor_ti' }} session={analyst} onDecide={vi.fn()} />);
    expect(screen.getByRole('button', { name: 'Rejeitar' })).toBeDisabled();
  });
  it.each([[true, 'Aprovar'], [false, 'Rejeitar']])('registra decisão %s com justificativa', async (approved, label) => {
    const decide = vi.fn();
    render(<ApprovalItem item={pending} session={analyst} onDecide={decide} />);
    const user = userEvent.setup();
    expect(screen.getByRole('button', { name: label })).toBeDisabled();
    await user.type(screen.getByLabelText('Justificativa da decisão'), 'Revisão técnica concluída');
    await user.click(screen.getByRole('button', { name: label }));
    await waitFor(() => expect(decide).toHaveBeenCalledWith(pending.id, approved, 'Revisão técnica concluída'));
  });
});

it.each([['suporte_n1', 2], ['analista_redes', 4], ['gestor_ti', 5]])('navegação de %s respeita RBAC', (papel, count) => {
  render(<Operations session={{ token: 'synthetic', usuario: 'reader', papel }} onExpire={vi.fn()} />);
  const nav = screen.getByRole('navigation', { name: 'Áreas do painel' });
  expect(within(nav).getAllByRole('button')).toHaveLength(count);
  if (papel !== 'gestor_ti') expect(within(nav).queryByText('Auditoria')).not.toBeInTheDocument();
  if (papel === 'suporte_n1') expect(within(nav).queryByText('Aprovações')).not.toBeInTheDocument();
});
