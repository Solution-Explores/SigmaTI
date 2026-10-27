import { useId } from 'react';
import { devices, incidents, findDevice, severityLabels, statusLabels, deviceStatusLabels } from '../data/demo';
import { Badge, EmptyState, Icon } from './ui';
const severityTone = {
  critical: 'danger',
  high: 'warning',
  medium: 'info',
  low: 'neutral'
};
const statusTone = {
  open: 'warning',
  investigating: 'info',
  resolved: 'success',
  online: 'success',
  warning: 'warning',
  offline: 'danger'
};
const severityOptions = {
  criticalHigh: 'Crítica e alta',
  ...severityLabels
};
const situationLabels = {
  active: 'Ativos',
  all: 'Todos',
  open: 'Abertos',
  investigating: 'Em análise',
  resolved: 'Resolvidos'
};
const isActive = incident => incident.status !== 'resolved';

// Keep native disclosure semantics while sharing expansion across table and card views.
function Disclosure({
  expanded,
  onToggle,
  label,
  children,
  summary
}) {
  return <details className="row-details" open={expanded}>
    <summary aria-label={label} onClick={event => {
      event.preventDefault();
      onToggle();
    }}>
      {summary}<Icon name="chevron" size={14} />
    </summary>
    <div>
      {children}
    </div>
  </details>;
}
function IncidentDetails({
  incident,
  expanded,
  onToggle
}) {
  return <Disclosure expanded={expanded} onToggle={onToggle} label={`Ver detalhes do incidente ${incident.id}`} summary="Ver detalhes">
    <strong>{incident.id} · {findDevice(incident.deviceId).sector}</strong>
    <p>{incident.description}</p>
  </Disclosure>;
}
function IncidentRows({
  items,
  expanded,
  onToggle
}) {
  if (!items.length) return <EmptyState />;
  const details = item => <IncidentDetails incident={item} expanded={Boolean(expanded[item.id])} onToggle={() => onToggle(item.id)} />;
  return <>
    <div className="desktop-table">
      <table>
        <thead>
          <tr>
            <th scope="col">Incidente / equipamento</th>
            <th scope="col">Severidade</th>
            <th scope="col">Situação</th>
            <th scope="col">Horário¹</th>
            <th scope="col"><span className="sr-only">Detalhes</span></th>
          </tr>
        </thead>
        <tbody>
          {items.map(item => <tr key={item.id}>
            <td><strong>{item.title}</strong><span className="table-secondary">{findDevice(item.deviceId).name} · {item.id}</span></td>
            <td><Badge tone={severityTone[item.severity]}>{severityLabels[item.severity]}</Badge></td>
            <td><Badge tone={statusTone[item.status]}>{statusLabels[item.status]}</Badge></td>
            <td className="time-cell">{item.time}</td>
            <td>{details(item)}</td>
          </tr>)}
        </tbody>
      </table>
    </div>
    <div className="mobile-cards">
      {items.map(item => <article className="list-card" key={item.id}>
        <div className="card-line">
          <small>{item.id} · {item.time}¹</small>
          <Badge tone={severityTone[item.severity]}>{severityLabels[item.severity]}</Badge>
        </div>
        <h3>{item.title}</h3>
        <p>{findDevice(item.deviceId).name}</p>
        <Badge tone={statusTone[item.status]}>{statusLabels[item.status]}</Badge>
        {details(item)}
      </article>)}
    </div>
  </>;
}
export function Overview({
  onOpenIncidents,
  onOpenDevices,
  expanded,
  onToggle
}) {
  const active = incidents.filter(isActive);
  const severityOrder = {
    critical: 0,
    high: 1,
    medium: 2,
    low: 3
  };
  const priorities = active.filter(i => i.severity === 'critical' || i.severity === 'high').sort((a, b) => severityOrder[a.severity] - severityOrder[b.severity] || b.time.localeCompare(a.time));
  const metrics = [{
    label: 'Equipamentos',
    value: devices.length,
    text: `${devices.filter(d => d.status === 'online').length} operacionais no cenário`,
    icon: 'server',
    tone: 'blue',
    action: onOpenDevices,
    accessible: `Ver os ${devices.length} equipamentos, sem filtros`
  }, {
    label: 'Incidentes ativos',
    value: active.length,
    text: 'Abertos ou em análise',
    icon: 'activity',
    tone: 'amber',
    action: () => onOpenIncidents({
      situation: 'active'
    }),
    accessible: `Ver os ${active.length} incidentes ativos`
  }, {
    label: 'Criticidade alta',
    value: priorities.length,
    text: 'Incidentes ativos críticos ou altos',
    icon: 'warning',
    tone: 'red',
    action: () => onOpenIncidents({
      situation: 'active',
      severity: 'criticalHigh'
    }),
    accessible: `Ver os ${priorities.length} incidentes ativos críticos ou altos`
  }, {
    label: 'Resolvidos',
    value: incidents.filter(i => i.status === 'resolved').length,
    text: 'Incidentes encerrados no cenário',
    icon: 'check',
    tone: 'green',
    action: () => onOpenIncidents({
      situation: 'resolved'
    }),
    accessible: 'Ver os incidentes resolvidos'
  }];
  return <>
    <div className="metric-grid">
      {metrics.map(metric => <button type="button" className="metric-card" key={metric.label} onClick={metric.action} aria-label={metric.accessible}>
      <div className="metric-top">
          <span>{metric.label}</span>
          <span className={`metric-icon ${metric.tone}`}><Icon name={metric.icon} /></span>
        </div>
      <strong className="metric-value">{String(metric.value).padStart(2, '0')}</strong><p>{metric.text}</p>
    </button>)}
    </div>
    <div className="overview-grid investigation-grid">
      <section className="panel priority-panel" aria-labelledby="priority-heading">
        <div className="panel-heading">
          <div>
            <h2 id="priority-heading">Incidentes prioritários</h2>
            <p>Ativos de severidade crítica ou alta</p>
          </div>
        </div>
        <div className="priority-list">
          {priorities.map(item => <article className="priority-incident" key={item.id}>
            <div className="priority-heading">
              <h3 className="priority-title">{item.title}</h3>
              <Badge tone={severityTone[item.severity]}>{severityLabels[item.severity]}</Badge>
            </div>
            <p className="priority-context">{findDevice(item.deviceId).name} · {item.id} · {item.time}¹</p>
            <div className="priority-actions">
              <Badge tone={statusTone[item.status]}>{statusLabels[item.status]}</Badge>
              <IncidentDetails incident={item} expanded={Boolean(expanded[item.id])} onToggle={() => onToggle(item.id)} />
            </div>
          </article>)}
        </div>
        <div className="priority-footer">
          <button type="button" className="text-link text-button" onClick={() => onOpenIncidents({
            situation: 'active'
          })}>Ver todos os ativos ({active.length})<Icon name="arrow" size={16} /></button>
          <p className="table-note">¹ Horários ilustrativos do cenário fictício.</p>
        </div>
      </section>
      <section className="panel severity-panel" aria-labelledby="severity-heading">
        <div className="panel-heading">
          <div>
            <h2 id="severity-heading">Por severidade</h2>
            <p>Distribuição dos {active.length} incidentes ativos</p>
          </div>
          <Icon name="activity" />
        </div>
        <div className="severity-bars">
          {Object.entries(severityLabels).map(([key, label]) => {
            const count = active.filter(i => i.severity === key).length;
            return <button type="button" className="severity-row" key={key} onClick={() => onOpenIncidents({
              situation: 'active',
              severity: key
            })} aria-label={`Ver incidentes ativos de severidade ${label.toLocaleLowerCase('pt-BR')}: ${count}`}>
            <div>
              <span><span className={`severity-dot ${key}`} />{label}</span>
              <strong>{count}</strong>
            </div>
            <div className="bar-track" aria-hidden="true">
              <span className={`bar-fill ${key}`} style={{
                  width: `${active.length ? count / active.length * 100 : 0}%`
                }} />
            </div>
          </button>;
          })}
        </div>
      </section>
    </div>
    <div className="simulation-shortcut">
      <span>Quer explorar o diagnóstico assistido?</span>
      <a className="text-link" href="#simulator">Simular alerta<Icon name="arrow" size={16} /></a>
    </div>
  </>;
}
function SearchField({
  value,
  onChange,
  label,
  placeholder
}) {
  return <label className="filter-field search-field"><span>{label}</span><span className="search-input"><Icon name="search" size={18} /><input type="search" value={value} onChange={e => onChange(e.target.value)} placeholder={placeholder} /></span></label>;
}
function SelectFilter({
  label,
  value,
  onChange,
  options,
  allLabel = 'Todas'
}) {
  const id = useId();
  return <div className="filter-field">
    <label htmlFor={id}>{label}</label>
    <select id={id} value={value} onChange={e => onChange(e.target.value)}>{allLabel && <option value="">{allLabel}</option>}{Object.entries(options).map(([key, text]) => <option key={key} value={key}>{text}</option>)}</select>
  </div>;
}
function matches(text, search) {
  return text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('pt-BR').includes(search.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('pt-BR').trim());
}
export function IncidentList({
  filters,
  onChange,
  expanded,
  onToggle
}) {
  const {
    search,
    severity,
    situation
  } = filters;
  const items = incidents.filter(i => matches(`${i.id} ${findDevice(i.deviceId).name} ${i.title} ${i.description}`, search) && (!severity || (severity === 'criticalHigh' ? ['critical', 'high'].includes(i.severity) : i.severity === severity)) && (situation === 'all' || (situation === 'active' ? isActive(i) : i.status === situation)));
  return <section className="panel">
    <div className="panel-heading">
      <div>
        <h2>Registro de incidentes</h2>
        <p>Pesquise e consulte os detalhes de cada ocorrência.</p>
      </div>
      <Badge>{incidents.length} registros</Badge>
    </div>
    <div className="filters">
      <SearchField label="Buscar incidente" value={search} onChange={value => onChange({
        ...filters,
        search: value
      })} placeholder="ID, equipamento ou descrição" />
      <SelectFilter label="Severidade" value={severity} onChange={value => onChange({
        ...filters,
        severity: value
      })} options={severityOptions} />
      <SelectFilter label="Situação" value={situation} onChange={value => onChange({
        ...filters,
        situation: value
      })} options={situationLabels} allLabel={null} />
    </div>
    <div className="filter-summary">
      <p className="result-count" role="status">{items.length} de {incidents.length} incidentes · {situationLabels[situation]}</p>
      <button type="button" className="text-button" onClick={() => onChange({
        search: '',
        severity: '',
        situation: 'all'
      })}>Limpar filtros</button>
    </div>
    <IncidentRows items={items} expanded={expanded} onToggle={onToggle} />
    <p className="table-note">¹ Horários ilustrativos do mesmo cenário fictício.</p>
  </section>;
}
function DeviceDetails({
  device,
  expanded,
  onToggle
}) {
  const related = incidents.filter(i => i.deviceId === device.id);
  return <Disclosure expanded={expanded} onToggle={onToggle} label={`Ver incidentes do equipamento ${device.name}`} summary={`Ver incidentes (${related.length})`}>
    <strong>Incidentes relacionados</strong><ul>
      {related.map(i => <li key={i.id}>{i.id} · {i.title} — {statusLabels[i.status]}</li>)}
    </ul>
  </Disclosure>;
}
export function DeviceList({
  filters,
  onChange,
  expanded,
  onToggle
}) {
  const {
    search,
    status
  } = filters;
  const items = devices.filter(d => matches(`${d.name} ${d.sector} ${d.ip}`, search) && (!status || d.status === status));
  const details = device => <DeviceDetails device={device} expanded={Boolean(expanded[device.id])} onToggle={() => onToggle(device.id)} />;
  return <section className="panel">
    <div className="panel-heading">
      <div>
        <h2>Inventário demonstrativo</h2>
        <p>Equipamentos e endereços fictícios para explorar o painel.</p>
      </div>
      <Badge>{devices.length} equipamentos</Badge>
    </div>
    <div className="filters">
      <SearchField label="Buscar equipamento" value={search} onChange={value => onChange({
        ...filters,
        search: value
      })} placeholder="Nome, setor ou IP" />
      <SelectFilter label="Estado" value={status} onChange={value => onChange({
        ...filters,
        status: value
      })} options={deviceStatusLabels} allLabel="Todos" />
    </div>
    <div className="filter-summary">
      <p className="result-count" role="status">{items.length} de {devices.length} equipamentos</p>
      <button type="button" className="text-button" onClick={() => onChange({
        search: '',
        status: ''
      })}>Limpar filtros</button>
    </div>
    {!items.length ? <EmptyState /> : <>
      <div className="desktop-table">
        <table>
          <thead>
            <tr>
              <th scope="col">Equipamento</th>
              <th scope="col">Setor / endereço IP</th>
              <th scope="col">Estado</th>
              <th scope="col"><span className="sr-only">Incidentes relacionados</span></th>
            </tr>
          </thead>
          <tbody>
            {items.map(d => <tr key={d.id}>
              <td><strong>{d.name}</strong><span className="table-secondary">{d.type}</span></td>
              <td>{d.sector}<span className="table-secondary mono">{d.ip}</span></td>
              <td><Badge tone={statusTone[d.status]}>{deviceStatusLabels[d.status]}</Badge></td>
              <td>{details(d)}</td>
            </tr>)}
          </tbody>
        </table>
      </div>
      <div className="mobile-cards">
        {items.map(d => <article className="list-card" key={d.id}>
          <div className="card-line">
            <span className="metric-icon blue"><Icon name="server" /></span>
            <Badge tone={statusTone[d.status]}>{deviceStatusLabels[d.status]}</Badge>
          </div>
          <h3>{d.name}</h3>
          <p>{d.sector}</p>
          <p className="mono">{d.ip}</p>
          {details(d)}
        </article>)}
      </div>
    </>}
  </section>;
}
