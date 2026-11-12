import { BACKEND_URL } from '../config/api';

export const trackFestive = (event) => {
  try {
    fetch(`${BACKEND_URL}/api/promotions/festive-track`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ event }),
      keepalive: true
    }).catch(() => {});
  } catch (e) { /* ignore */ }
};
