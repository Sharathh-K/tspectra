import { useEffect, useState } from 'react';
import { fetchScene } from '../api/risk';

export function useRiskData() {
  const [scene, setScene] = useState(null);
  const [error, setError] = useState('');
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    setError('');
    fetchScene(controller.signal).then(setScene).catch(e => {
      if (!controller.signal.aborted) setError(e.message);
    });
    return () => controller.abort();
  }, [attempt]);
  return { scene, error, retry: () => setAttempt(n => n + 1) };
}
