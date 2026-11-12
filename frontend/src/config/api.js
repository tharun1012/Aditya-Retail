// Runtime API configuration

const getBackendUrl = () => {
  if (typeof window !== 'undefined') {
    const currentHost = window.location.hostname;

    // Production domains
    if (
      currentHost.includes('adityaretail.com') ||
      currentHost.includes('emergent.host')
    ) {
      return window.location.origin;
    }

    // Local development
    if (
      currentHost === 'localhost' ||
      currentHost === '127.0.0.1'
    ) {
      return process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
    }

    // Any other domain
    return window.location.origin;
  }

  // Build-time / SSR fallback
  return process.env.REACT_APP_BACKEND_URL || '';
};

export const BACKEND_URL = getBackendUrl();
export const API_BASE = `${BACKEND_URL}/api`;

export default BACKEND_URL;