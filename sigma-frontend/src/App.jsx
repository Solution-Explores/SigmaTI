import { useCallback, useState } from 'react';
import { apiRequest } from './api';
import Operations from './Operations';
import './App.css';

export default function App() {
  const [session, setSession] = useState(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState(null);
  const [theme, setTheme] = useState('dark');
  const expire = useCallback(message => { setSession(null); setErro(message); }, []);
  async function login(event) {
    event.preventDefault(); setLoading(true); setErro(null);
    let token;
    try {
      const data = await apiRequest('/api/auth/login', { method: 'POST', body: { username, password } });
      token = data.access_token;
      const me = await apiRequest('/api/auth/me', { token });
      setSession({ token, ...me });
    } catch (error) {
      if (token) await apiRequest('/api/auth/logout', { method: 'POST', token }).catch(() => {});
      setErro(error.message);
    } finally { setPassword(''); setLoading(false); }
  }
  async function logout() {
    setLoading(true); setErro(null);
    try {
      await apiRequest('/api/auth/logout', { method: 'POST', token: session.token });
      setSession(null);
    } catch (error) {
      if (error.status === 401) setSession(null);
      setErro(error.message);
    } finally { setLoading(false); }
  }
  return <div className="app-surface" data-theme={theme}>
    <a className="skip-link" href="#conteudo">Ir para o conteúdo</a>
    <main className="sigma-panel" id="conteudo">
      <header className="masthead">
        <div><h1>SIGMA — Painel de Monitoramento</h1><p>Saúde dos serviços e resposta a incidentes</p></div>
        <button type="button" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          aria-pressed={theme === 'light'}>Tema {theme === 'dark' ? 'claro' : 'escuro'}</button>
      </header>
      <p className="notice">Demonstração controlada: utilize somente dados fictícios.</p>
      {erro && <p role="alert" className="error">{erro}</p>}
      {!session ? <section aria-labelledby="login-title" className="card login">
        <h2 id="login-title">Entrar</h2>
        <form onSubmit={login}>
          <label htmlFor="username">Usuário</label>
          <input id="username" autoComplete="username" value={username} onChange={e => setUsername(e.target.value)} required disabled={loading} />
          <label htmlFor="password">Senha</label>
          <input id="password" type="password" autoComplete="current-password" value={password} onChange={e => setPassword(e.target.value)} required disabled={loading} />
          <button disabled={loading} type="submit">{loading ? 'Entrando…' : 'Entrar'}</button>
        </form>
      </section> : <>
        <div className="session"><p>Sessão: <strong>{session.usuario}</strong> · {session.papel}</p>
          <button type="button" onClick={logout} disabled={loading}>Sair</button></div>
        <Operations key={session.token} session={session} onExpire={expire} />
      </>}
    </main>
  </div>;
}
