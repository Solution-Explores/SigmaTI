// Grava em vídeo (webm) o percurso da demonstração, para usar como contingência.
// Requer a API da demo (subir_demo.py) e o painel (vite) no ar, e o Playwright do frontend.
//
//   $env:SIGMA_DEMO_SENHA = '<senha impressa por subir_demo.py>'
//   $env:SIGMA_FRONTEND   = 'C:\...\sigmati-develop\frontend'
//   $env:SIGMA_PYTHON     = 'C:\...\sigmati-develop\.venv\Scripts\python.exe'
//   node docs/demo/gravar_contingencia.mjs <arquivo-de-saida.webm>
//
// Faz o que o roteiro faz: perfis, coleta ao vivo (derruba um serviço TCP local), SLO,
// governança e IA com anonimização. Só dados fictícios.
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import { mkdirSync, mkdtempSync, renameSync, rmSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';

const frontend = process.env.SIGMA_FRONTEND;
const senha = process.env.SIGMA_DEMO_SENHA;
const python = process.env.SIGMA_PYTHON || 'python';
const saida = process.argv[2];
if (!frontend || !senha || !saida) {
  console.error('Defina SIGMA_FRONTEND, SIGMA_DEMO_SENHA e informe o arquivo de saída.');
  process.exit(2);
}
const { chromium } = createRequire(join(frontend, 'package.json'))('@playwright/test');

const API = 'http://127.0.0.1:18000';
const PAINEL = 'http://127.0.0.1:5173';
const PORTA = 9099;
const pausa = (ms) => new Promise((r) => setTimeout(r, ms));

async function token(usuario) {
  const r = await fetch(`${API}/api/auth/login`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: usuario, password: senha }),
  });
  return (await r.json()).access_token;
}
async function api(usuario, metodo, rota, corpo) {
  const r = await fetch(`${API}${rota}`, {
    method: metodo,
    headers: { Authorization: `Bearer ${await token(usuario)}`, 'Content-Type': 'application/json' },
    body: corpo === undefined ? undefined : JSON.stringify(corpo),
  });
  return { status: r.status, corpo: await r.json().catch(() => null) };
}

let servico = null;
function subirServico() {
  servico = spawn(python, ['-m', 'http.server', String(PORTA), '--bind', '127.0.0.1'], { stdio: 'ignore', windowsHide: true });
}
function derrubarServico() { servico?.kill(); servico = null; }

const dir = mkdtempSync(join(tmpdir(), 'sigma-video-'));
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 }, recordVideo: { dir, size: { width: 1280, height: 900 } } });
const page = await ctx.newPage();

async function legenda(texto, ms = 3500) {
  await page.evaluate((t) => {
    let el = document.getElementById('__legenda');
    if (!el) {
      el = document.createElement('div');
      el.id = '__legenda';
      el.style.cssText = 'position:fixed;left:0;right:0;bottom:0;z-index:99999;padding:14px 24px;background:#14213D;color:#F4F6F2;font:600 20px/1.35 system-ui,sans-serif;border-top:3px solid #2A6FDB';
      document.body.appendChild(el);
    }
    el.textContent = t;
  }, texto);
  await pausa(ms);
}
async function entrar(usuario) {
  await page.goto(PAINEL);
  await page.getByLabel('Usuário').fill(usuario);
  await page.getByLabel('Senha').fill(senha);
  await page.getByRole('button', { name: 'Entrar' }).click();
  await page.getByRole('button', { name: 'Sair' }).waitFor();
  await pausa(1200);
}
async function sair() { await page.getByRole('button', { name: 'Sair' }).click(); await pausa(800); }
const aba = async (nome) => { await page.getByRole('button', { name: nome, exact: true }).click(); await pausa(1200); };

try {
  // Abertura
  await page.goto(PAINEL);
  await legenda('SigmaTI · demonstração gravada (contingência) · dados fictícios, provedor de IA simulado, loopback', 4000);

  // 1. Perfis
  await entrar('browser.demo');
  await legenda('Perfil N1 (suporte_n1): só as abas Saúde dos serviços e Diagnóstico', 4000);
  const n1 = await api('browser.demo', 'GET', '/api/usuarios');
  await legenda(`A API quem garante: browser.demo → GET /api/usuarios → HTTP ${n1.status}`, 4000);
  await sair();
  await entrar('browser.manager');
  const gestor = await api('browser.manager', 'GET', '/api/usuarios');
  await legenda(`Perfil gestor_ti: as cinco abas · GET /api/usuarios → HTTP ${gestor.status}`, 4000);
  await sair();

  // 2. Coleta ao vivo
  subirServico();
  await pausa(1500);
  await entrar('browser.analyst');
  const alvo = await api('browser.analyst', 'POST', '/api/eng/alvos', { nome: 'Switch UTI', host: '127.0.0.1', porta: PORTA, intervalo_s: 0.5, timeout_s: 0.3 });
  await legenda('Analista cadastra o alvo "Switch UTI" (TCP, intervalo 0,5 s)', 2500);
  await page.locator('tr', { hasText: 'Switch UTI' }).getByText('Disponível').waitFor({ timeout: 20000 });
  await legenda('Alvo Disponível na aba Saúde', 3000);
  await aba('Incidentes');
  await legenda('Aba Incidentes, com "Tempo real ativo". Agora o serviço de teste será derrubado', 3000);
  derrubarServico();
  const queda = new Date();
  const linhasDisp = page.locator('tr', { hasText: 'Switch UTI' }).filter({ hasText: 'availability' });
  await linhasDisp.filter({ hasText: 'Aberto' }).first().waitFor({ timeout: 30000 });
  const ate = ((Date.now() - queda.getTime()) / 1000).toFixed(1);
  await linhasDisp.first().scrollIntoViewIfNeeded();
  await legenda(`O incidente de disponibilidade apareceu sem recarregar a página (cerca de ${ate} s após a queda)`, 4000);
  const linhaDisp = linhasDisp.first(); // o mais recente fica no topo da lista
  await linhaDisp.getByRole('button', { name: 'Reconhecer' }).click();
  await pausa(1500);
  subirServico();
  await pausa(2000);
  await legenda('Serviço de volta. Resolver o incidente', 2500);
  await linhaDisp.getByRole('button', { name: 'Resolver incidente' }).click();
  await pausa(2000);
  await page.getByText('Histórico de incidentes').scrollIntoViewIfNeeded();
  await page.evaluate(() => window.scrollTo({ top: 0 }));
  await legenda('Cartões de MTTA e MTTR: média, mediana, p95 e amostras', 4500);
  const lista = (await api('browser.analyst', 'GET', '/api/eng/incidentes')).corpo.incidentes;
  const inc = lista.find((i) => i.resolvido_em && i.tipo === 'availability' && i.alvo_id === alvo.corpo.id);
  const met = await api('browser.analyst', 'POST', '/api/eng/incidentes/metricas', [{
    id: String(inc.id), severidade: 'P2', inicio_real: queda.toISOString(),
    detectado_em: inc.detectado_em, reconhecido_em: inc.reconhecido_em, resolvido_em: inc.resolvido_em,
  }]);
  const m = met.corpo;
  await legenda(`MTTD pela API, com a hora real da queda: ${m.MTTD.media_s} s · MTTA ${m.MTTA.media_s} s · MTTR ${m.MTTR.media_s} s`, 5000);
  derrubarServico();

  // 3. SLO
  await aba('Saúde dos serviços');
  await page.locator('tr', { hasText: 'Portal de testes' }).first().scrollIntoViewIfNeeded();
  await legenda('SLO do "Portal de testes": meta de 95% em 1 dia, 12 min de orçamento restante, 25 h de histórico', 5000);
  const agora = new Date();
  const burn = await api('browser.analyst', 'POST', '/api/eng/slo/avaliar', {
    alvo_pct: 95, janela_dias: 1,
    indisponibilidades: [{ inicio: new Date(agora - 3600e3).toISOString(), fim: agora.toISOString() }],
  });
  await legenda(`Burn rate pela API: status ${burn.corpo.orcamento.status}, restam ${burn.corpo.orcamento.restante_min} min, alerta "${burn.corpo.alertas[0]?.acao}"`, 5000);

  // 4. Governança
  await aba('Aprovações');
  await page.getByText('Nova solicitação').click();
  await page.getByLabel('Ação a revisar').fill('Revisar mudança de regra de alerta da UTI');
  await page.getByRole('button', { name: 'Solicitar revisão' }).click();
  await legenda('Analista pede uma aprovação; quem pediu não pode decidir (quatro olhos)', 4500);
  await sair();
  await entrar('browser.reviewer');
  await aba('Aprovações');
  await page.getByRole('textbox', { name: 'Justificativa da decisão' }).last().fill('Regra revisada: sem impacto na UTI, aprovado.');
  await page.getByRole('button', { name: 'Aprovar' }).last().click();
  await legenda('Segundo integrante (revisor) aprova com justificativa: "Solicitação aprovada."', 4500);
  await sair();
  await entrar('browser.manager');
  await aba('Auditoria');
  await legenda('Gestor abre a Auditoria: integridade consistente e eventos operacionais recentes', 5500);

  // 5. IA e LGPD
  await aba('Diagnóstico');
  await page.getByLabel('Equipamento').fill('sw-uti-01');
  await page.getByLabel('IP de origem').fill('10.0.0.5');
  await page.getByLabel('Descrição do erro').fill('Paciente Maria Silva CPF 529.982.247-25 relatou falha no sw-uti-01');
  await page.getByRole('button', { name: 'Solicitar diagnóstico' }).click();
  await page.getByText('Dados enviados à IA').waitFor({ timeout: 20000 });
  await legenda('Nome e CPF fictícios removidos antes da chamada ao provedor simulado (sanitização fail-closed)', 6000);
  await legenda('Fim da gravação de contingência', 2500);
} catch (erro) {
  console.error('Falha durante a gravação:', erro.message);
  process.exitCode = 1;
} finally {
  derrubarServico();
  const video = page.video();
  await ctx.close();
  mkdirSync(dirname(saida), { recursive: true });
  await video.saveAs(saida);
  await browser.close();
  rmSync(dir, { recursive: true, force: true });
  console.log('Vídeo salvo em', saida);
}
