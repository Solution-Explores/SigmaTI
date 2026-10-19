import { useState } from 'react';
import { apiRequest } from './api';
import './App.css';

function App() {
  const [session, setSession] = useState(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [equipamento, setEquipamento] = useState('Switch de teste');
  const [ipOrigem, setIpOrigem] = useState('192.0.2.10');
  const [descricaoErro, setDescricaoErro] = useState('Perda de pacotes no IP 192.0.2.10.');
  const [loading, setLoading] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [erro, setErro] = useState(null);

  async function login(event) {
    event.preventDefault();
    setLoading(true);
    setErro(null);
    let token;
    try {
      const data = await apiRequest('/api/auth/login', { method: 'POST', body: { username, password } });
      token = data.access_token;
      const me = await apiRequest('/api/auth/me', { token });
      setSession({ token, ...me });
      setResultado(null);
    } catch (error) {
      if (token) await apiRequest('/api/auth/logout', { method: 'POST', token }).catch(() => {});
      setErro(error.message);
    } finally {
      setPassword('');
      setLoading(false);
    }
  }

  async function logout() {
    setLoading(true);
    setErro(null);
    try {
      await apiRequest('/api/auth/logout', { method: 'POST', token: session.token });
      setSession(null);
      setResultado(null);
    } catch (error) {
      if (error.status === 401) {
        setSession(null);
        setResultado(null);
      }
      setErro(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function enviarAlerta(event) {
    event.preventDefault();
    setLoading(true);
    setErro(null);
    setResultado(null);
    try {
      setResultado(await apiRequest('/api/alertas', {
        method: 'POST', token: session.token,
        body: { equipamento, ip_origem: ipOrigem, descricao_erro: descricaoErro },
      }));
    } catch (error) {
      if (error.status === 401) setSession(null);
      setErro(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="sigma-panel">
      <header>
        <h1>SIGMA — Painel de Monitoramento</h1>
        <p>Diagnóstico assistido de alertas de rede</p>
        <p className="notice">Demonstração controlada: utilize somente dados fictícios.</p>
      </header>
      {erro && <p role="alert" className="error">{erro}</p>}
      {!session ? (
        <section aria-labelledby="login-title" className="card login">
          <h2 id="login-title">Entrar</h2>
          <form onSubmit={login}>
            <label htmlFor="username">Usuário</label>
            <input id="username" autoComplete="username" value={username} onChange={e => setUsername(e.target.value)} required disabled={loading} />
            <label htmlFor="password">Senha</label>
            <input id="password" type="password" autoComplete="current-password" value={password} onChange={e => setPassword(e.target.value)} required disabled={loading} />
            <button disabled={loading} type="submit">{loading ? 'Entrando…' : 'Entrar'}</button>
          </form>
        </section>
      ) : (
        <>
          <div className="session">
            <p>Sessão: <strong>{session.usuario}</strong> · {session.papel}</p>
            <button type="button" onClick={logout} disabled={loading}>Sair</button>
          </div>
          <div className="columns">
            <section className="card" aria-labelledby="alert-title">
              <h2 id="alert-title">Enviar alerta</h2>
              <form onSubmit={enviarAlerta}>
                <label htmlFor="equipment">Equipamento</label>
                <input id="equipment" value={equipamento} onChange={e => setEquipamento(e.target.value)} required disabled={loading} />
                <label htmlFor="ip">IP de origem</label>
                <input id="ip" value={ipOrigem} onChange={e => setIpOrigem(e.target.value)} required disabled={loading} />
                <label htmlFor="description">Descrição do erro</label>
                <textarea id="description" rows={6} value={descricaoErro} onChange={e => setDescricaoErro(e.target.value)} required disabled={loading} />
                <button type="submit" disabled={loading}>{loading ? 'Processando…' : 'Solicitar diagnóstico'}</button>
              </form>
            </section>
            <section className="card" aria-labelledby="result-title" aria-live="polite" aria-busy={loading}>
              <h2 id="result-title">Resultado</h2>
              {resultado ? <>
                <h3>Dados enviados à IA</h3>
                <pre>{resultado.dados_enviados_nuvem}</pre>
                <h3>Diagnóstico da IA</h3>
                <p className="diagnosis">{resultado.diagnostico_ia}</p>
              </> : <p>O diagnóstico aparecerá aqui após o envio.</p>}
            </section>
          </div>
        </>
      )}
    </main>
  );
}

export default App;
