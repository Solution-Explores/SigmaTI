export const severityLabels = {
  critical: 'Crítica',
  high: 'Alta',
  medium: 'Média',
  low: 'Baixa'
};
export const statusLabels = {
  open: 'Aberto',
  investigating: 'Em análise',
  resolved: 'Resolvido'
};
export const deviceStatusLabels = {
  online: 'Operacional',
  warning: 'Atenção',
  offline: 'Indisponível'
};
export const devices = [{
  id: 'sw-core',
  name: 'Switch Core UTI',
  type: 'Switch',
  sector: 'Unidade de terapia intensiva',
  ip: '192.0.2.10',
  status: 'warning'
}, {
  id: 'fw',
  name: 'Firewall Principal',
  type: 'Firewall',
  sector: 'Data center',
  ip: '192.0.2.1',
  status: 'online'
}, {
  id: 'srv',
  name: 'Servidor de Aplicações',
  type: 'Servidor',
  sector: 'Data center',
  ip: '192.0.2.20',
  status: 'online'
}, {
  id: 'ap',
  name: 'Access Point Ambulatório',
  type: 'Access point',
  sector: 'Ambulatório',
  ip: '192.0.2.30',
  status: 'offline'
}, {
  id: 'sw-lab',
  name: 'Switch Laboratório',
  type: 'Switch',
  sector: 'Laboratório',
  ip: '192.0.2.40',
  status: 'online'
}, {
  id: 'ws',
  name: 'Estação de Atendimento',
  type: 'Estação',
  sector: 'Recepção',
  ip: '192.0.2.50',
  status: 'online'
}];
export const incidents = [{
  id: 'INC-008',
  deviceId: 'sw-core',
  title: 'Perda de pacotes acima do limite',
  severity: 'critical',
  status: 'investigating',
  time: '10:42',
  description: 'Cenário fictício: perda de pacotes na comunicação com a UTI. Verificar enlaces, erros de interface e utilização de banda.'
}, {
  id: 'INC-007',
  deviceId: 'ap',
  title: 'Equipamento sem resposta',
  severity: 'high',
  status: 'open',
  time: '10:35',
  description: 'Cenário fictício: o ponto de acesso não responde às verificações. Conferir alimentação e conexão com o switch.'
}, {
  id: 'INC-006',
  deviceId: 'sw-core',
  title: 'Latência elevada no enlace',
  severity: 'high',
  status: 'open',
  time: '10:28',
  description: 'Cenário fictício: aumento da latência no enlace principal da unidade. Correlacionar com a perda de pacotes.'
}, {
  id: 'INC-005',
  deviceId: 'srv',
  title: 'Pico de conexões simultâneas',
  severity: 'medium',
  status: 'investigating',
  time: '10:15',
  description: 'Cenário fictício: volume de conexões acima da referência. Avaliar carga da aplicação e disponibilidade de recursos.'
}, {
  id: 'INC-004',
  deviceId: 'fw',
  title: 'Tentativas de conexão bloqueadas',
  severity: 'medium',
  status: 'resolved',
  time: '09:50',
  description: 'Cenário fictício: tentativas bloqueadas pelas regras do firewall; regras revisadas no cenário de exemplo.'
}, {
  id: 'INC-003',
  deviceId: 'sw-lab',
  title: 'Oscilação em porta de acesso',
  severity: 'low',
  status: 'resolved',
  time: '09:32',
  description: 'Cenário fictício: conexão estabilizada após revisão do cabeamento.'
}, {
  id: 'INC-002',
  deviceId: 'ws',
  title: 'Resolução DNS intermitente',
  severity: 'medium',
  status: 'resolved',
  time: '09:18',
  description: 'Cenário fictício: resolução normalizada após verificação da configuração de DNS.'
}, {
  id: 'INC-001',
  deviceId: 'fw',
  title: 'Utilização de banda elevada',
  severity: 'low',
  status: 'resolved',
  time: '08:56',
  description: 'Cenário fictício: utilização retornou à referência após encerramento de transferência programada.'
}];
export const findDevice = id => devices.find(device => device.id === id);
