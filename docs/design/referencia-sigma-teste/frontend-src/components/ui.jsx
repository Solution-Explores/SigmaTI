const paths = {
  pulse: 'M3 12h4l3-8 4 16 3-8h4',
  activity: 'M3 12h4l3-8 4 16 3-8h4',
  grid: 'M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z',
  server: 'M4 3h16v7H4z M4 14h16v7H4z M7 6.5h.01 M7 17.5h.01 M11 6.5h6 M11 17.5h6',
  send: 'm21 3-7 18-4-7-7-4 18-7ZM10 14l5-5',
  plus: 'M12 5v14 M5 12h14',
  sun: 'M12 3V1 M12 23v-2 M3 12H1 M23 12h-2 M4.2 4.2l1.4 1.4 M18.4 18.4l1.4 1.4 M4.2 19.8l1.4-1.4 M18.4 5.6l1.4-1.4 M16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0',
  moon: 'M21 13a9 9 0 0 1-10-10 9 9 0 1 0 10 10Z',
  menu: 'M4 6h16 M4 12h16 M4 18h16',
  close: 'm6 6 12 12 M6 18 18 6',
  info: 'M12 11v6 M12 7h.01 M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0',
  flask: 'M9 3h6 M10 3v6L4 19q-1 2 2 2h12q3 0 2-2L14 9V3 M7 14h10',
  building: 'M4 21V3h12v18 M16 9h4v12 M8 7h4 M8 11h4 M8 15h4 M9 21v-2h2v2',
  arrow: 'M5 12h14 m-5-5 5 5-5 5',
  chevron: 'm9 5 7 7-7 7',
  check: 'm5 12 4 4L19 6',
  warning: 'm12 3 10 18H2L12 3Z M12 9v5 M12 17h.01',
  clock: 'M12 7v5l3 2 M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0',
  search: 'M21 21l-5-5 M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0',
  shield: 'm12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6l8-3Z m-4 9 3 3 5-6'
};
export function Icon({
  name,
  size = 20,
  className = ''
}) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" className={className}><path d={paths[name] || paths.info} /></svg>;
}
export function Badge({
  tone = 'neutral',
  children
}) {
  return <span className={`badge badge-${tone}`}><Icon name={tone === 'success' ? 'check' : tone === 'danger' || tone === 'warning' ? 'warning' : tone === 'info' ? 'clock' : 'info'} size={13} />{children}</span>;
}
export function EmptyState({
  title = 'Nenhum resultado encontrado',
  description = 'Tente outros termos ou ajuste os filtros.'
}) {
  return <div className="empty-state">
    <span className="empty-icon"><Icon name="search" size={28} /></span>
    <h3>{title}</h3>
    <p>{description}</p>
  </div>;
}
