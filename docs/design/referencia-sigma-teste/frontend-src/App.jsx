import { useEffect, useRef, useState } from 'react';
import { incidents } from './data/demo';
import { Icon, Badge } from './components/ui';
import { Overview, IncidentList, DeviceList } from './components/Dashboard';
import { AlertSimulator } from './components/AlertSimulator';
import './App.css';
const pages = {
  overview: {
    label: 'Visão geral',
    icon: 'grid',
    eyebrow: 'CENTRAL DE OPERAÇÕES',
    description: 'Uma visão clara da infraestrutura e dos incidentes de rede.'
  },
  incidents: {
    label: 'Incidentes',
    icon: 'activity',
    eyebrow: 'ACOMPANHAMENTO',
    description: 'Explore os alertas e identifique o que precisa de atenção.'
  },
  devices: {
    label: 'Equipamentos',
    icon: 'server',
    eyebrow: 'INFRAESTRUTURA',
    description: 'Conheça os equipamentos e os incidentes relacionados.'
  },
  simulator: {
    label: 'Simular alerta',
    icon: 'send',
    eyebrow: 'DIAGNÓSTICO ASSISTIDO',
    description: 'Envie um cenário de teste e consulte a resposta da inteligência artificial.'
  }
};
function readPage() {
  return Object.hasOwn(pages, location.hash.slice(1)) ? location.hash.slice(1) : 'overview';
}
function initialTheme() {
  try {
    const saved = localStorage.getItem('sigma-theme-v1');
    if (saved === 'light' || saved === 'dark') return saved;
  } catch {/* Storage is optional. */}
  return matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}
export default function App() {
  const [page, setPage] = useState(readPage);
  const [theme, setTheme] = useState(initialTheme);
  const [menuOpen, setMenuOpen] = useState(false);
  const [incidentFilters, setIncidentFilters] = useState({
    search: '',
    severity: '',
    situation: 'active'
  });
  const [deviceFilters, setDeviceFilters] = useState({
    search: '',
    status: ''
  });
  const [expandedIncidents, setExpandedIncidents] = useState({});
  const [expandedDevices, setExpandedDevices] = useState({});
  const toggleIncident = id => setExpandedIncidents(previous => ({
    ...previous,
    [id]: !previous[id]
  }));
  const toggleDevice = id => setExpandedDevices(previous => ({
    ...previous,
    [id]: !previous[id]
  }));
  const openIncidents = preset => {
    setIncidentFilters({
      search: '',
      severity: '',
      situation: 'active',
      ...preset
    });
    window.location.hash = 'incidents';
  };
  const openDevices = () => {
    setDeviceFilters({
      search: '',
      status: ''
    });
    window.location.hash = 'devices';
  };
  const heading = useRef(null);
  useEffect(() => {
    const navigate = () => {
      setPage(readPage());
      setMenuOpen(false);
      requestAnimationFrame(() => heading.current?.focus());
    };
    window.addEventListener('hashchange', navigate);
    return () => window.removeEventListener('hashchange', navigate);
  }, []);
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document.documentElement.style.colorScheme = theme;
  }, [theme]);
  function toggleTheme() {
    const next = theme === 'light' ? 'dark' : 'light';
    setTheme(next);
    try {
      localStorage.setItem('sigma-theme-v1', next);
    } catch {/* Keep the in-memory preference. */}
  }
  const current = pages[page];
  return <div className="app-shell">
    <a href="#main-content" className="skip-link" onClick={event => {
      event.preventDefault();
      document.getElementById('main-content').focus();
    }}>Pular para o conteúdo</a>
    <aside className="sidebar" aria-label="Barra de navegação">
      <a className="brand" href="#overview" aria-label="SigmaTI — visão geral"><span className="brand-mark"><Icon name="pulse" size={26} /></span><span>Sigma<span className="brand-ti">TI</span><small>INTELIGÊNCIA EM REDE</small></span></a>
      <button className="mobile-menu icon-button" aria-expanded={menuOpen} aria-controls="main-nav" onClick={() => setMenuOpen(!menuOpen)}><Icon name={menuOpen ? 'close' : 'menu'} /><span className="sr-only">{menuOpen ? 'Fechar menu' : 'Abrir menu'}</span></button>
      <nav id="main-nav" className={`main-nav ${menuOpen ? 'is-open' : ''}`} aria-label="Principal">
        <p className="nav-caption">ESPAÇO DE TRABALHO</p>
        {Object.entries(pages).map(([key, item]) => <a key={key} href={`#${key}`} className={`nav-link ${page === key ? 'active' : ''}`} aria-current={page === key ? 'page' : undefined}><Icon name={item.icon} /><span>{item.label}</span>{key === 'incidents' && <span className="nav-count">{incidents.filter(i => i.status !== 'resolved').length} ativos</span>}</a>)}
        <div className="sidebar-note">
          <Icon name="info" />
          <div>
            <strong>Ambiente demonstrativo</strong>
            <p>Explore um cenário fictício de monitoramento hospitalar.</p>
          </div>
        </div>
      </nav>
      <div className="sidebar-footer">
        <span className="organization-icon"><Icon name="building" /></span>
        <div>
          <strong>Fundação CECON</strong>
          <small>Tecnologia da informação</small>
        </div>
      </div>
    </aside>
    <div className="workspace">
      <header className="topbar">
        <div className="breadcrumb">Área de trabalho <span>/</span> <strong>{current.label}</strong></div>
        <div className="topbar-actions">
          <span className="environment-label"><span className="dot" /> Ambiente de teste</span>
          <button className="icon-button" onClick={toggleTheme} aria-label={`Ativar tema ${theme === 'light' ? 'escuro' : 'claro'}`} title={`Ativar tema ${theme === 'light' ? 'escuro' : 'claro'}`}><Icon name={theme === 'light' ? 'moon' : 'sun'} /></button>
        </div>
      </header>
      <main id="main-content" className={page === 'overview' ? 'overview-page' : undefined} tabIndex={-1}>
        <div className="page-heading">
          <div>
            {page !== 'overview' && <p className="eyebrow">{current.eyebrow}</p>}
            <h1 ref={heading} tabIndex={-1}>{current.label}</h1>
            <p className="page-description">{current.description}</p>
          </div>
        </div>
        {page !== 'simulator' && <div className="demo-banner">
          <Icon name="flask" />
          <span><strong>Demonstração — dados fictícios</strong><span className="banner-detail"> Cenário ilustrativo. Os indicadores não representam a rede real.</span></span>
          <Badge tone="neutral">DEMO</Badge>
        </div>}
        {page === 'overview' && <Overview onOpenIncidents={openIncidents} onOpenDevices={openDevices} expanded={expandedIncidents} onToggle={toggleIncident} />}
        {page === 'incidents' && <IncidentList filters={incidentFilters} onChange={setIncidentFilters} expanded={expandedIncidents} onToggle={toggleIncident} />}
        {page === 'devices' && <DeviceList filters={deviceFilters} onChange={setDeviceFilters} expanded={expandedDevices} onToggle={toggleDevice} />}
        <div hidden={page !== 'simulator'}>
          <AlertSimulator />
        </div>
        <footer className="content-footer">
          <span>SigmaTI · Gestão e monitoramento ativo</span>
          <span>Projeto acadêmico · FCECON</span>
        </footer>
      </main>
    </div>
  </div>;
}
