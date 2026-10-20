import { useEffect, useRef } from 'react';
import { apiRequest } from './api';

export function useActionRequest(token) {
  const lifetime = useRef(null);
  useEffect(() => {
    const controller = new AbortController();
    lifetime.current = controller;
    return () => controller.abort();
  }, [token]);
  return async (path, options = {}) => {
    const signal = lifetime.current?.signal;
    if (!signal || signal.aborted) throw new DOMException('Cancelado', 'AbortError');
    try {
      const data = await apiRequest(path, { ...options, token, signal });
      if (signal.aborted) throw new DOMException('Cancelado', 'AbortError');
      return data;
    } catch (error) {
      if (signal.aborted) { const aborted = new Error('Cancelado', { cause: error }); aborted.name = 'AbortError'; throw aborted; }
      throw error;
    }
  };
}
