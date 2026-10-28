import { useEffect, useState } from 'react';
import { readEventStream } from './api';

export function useEvents(token, onExpire) {
  const [connection, setConnection] = useState(() => navigator.onLine ? 'connecting' : 'reconnecting');
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    let cursor = null;
    let debounce;
    let timer;
    let resume;
    let active;
    const offline = () => { active?.abort(); setConnection('reconnecting'); };
    const online = () => { clearTimeout(timer); resume?.(); };
    window.addEventListener('offline', offline);
    window.addEventListener('online', online);
    const wait = ms => new Promise(resolve => { resume = resolve; timer = setTimeout(resolve, ms); });
    async function connect() {
      let delay = 1000;
      while (!controller.signal.aborted) {
        if (!navigator.onLine) { await wait(15000); continue; }
        active = new AbortController();
        try {
          await readEventStream({ token, cursor, signal: AbortSignal.any([controller.signal, active.signal]),
            onReady: () => { setConnection('connected'); delay = 1000; setRevision(value => value + 1); },
            onEvent: id => {
              if (cursor && BigInt(id) <= BigInt(cursor)) return;
              cursor = id;
              if (!debounce) debounce = setTimeout(() => { debounce = null; setRevision(value => value + 1); }, 100);
            },
          });
        } catch (error) {
          if (controller.signal.aborted) return;
          if (error.status === 401) { onExpire(error.message); return; }
          setConnection('reconnecting');
          await wait(delay);
          delay = Math.min(delay * 2, 15000);
        }
      }
    }
    connect();
    return () => {
      window.removeEventListener('offline', offline); window.removeEventListener('online', online);
      controller.abort(); active?.abort(); clearTimeout(debounce); clearTimeout(timer); resume?.();
    };
  }, [token, onExpire]);
  return { connection, revision };
}
