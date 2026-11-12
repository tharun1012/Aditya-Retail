import { BACKEND_URL } from '../config/api';

// /api/... paths live on the backend; everything else is used as-is
export const imgSrc = (u) => {
  if (!u) return '';
  if (/^(https?:|data:)/.test(u)) return u;
  return u.startsWith('/api/') ? `${BACKEND_URL}${u}` : u;
};
