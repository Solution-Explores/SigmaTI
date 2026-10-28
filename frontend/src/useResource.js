import { useEffect, useState } from 'react';
import { apiRequest } from './api';

export function useResource(path, token, onExpire, revision = 0) {
  const [value, setValue] = useState({ data: null, error: null });
  const [refreshIndex, setRefreshIndex] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    async function load() {
      try {
        const data = await apiRequest(path, { token, signal: controller.signal });
        if (!controller.signal.aborted) setValue({ data, error: null });
      } catch (error) {
        if (controller.signal.aborted) return;
        if (error.status === 401) { onExpire(error.message); return; }
        setValue({ data: null, error: error.message });
      }
    }
    load();
    return () => controller.abort();
  }, [path, token, onExpire, revision, refreshIndex]);
  function refresh() { setValue({ data: null, error: null }); setRefreshIndex(n => n + 1); }
  return { ...value, refresh, loading: !value.data && !value.error };
}
