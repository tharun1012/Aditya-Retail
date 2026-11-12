import React, { useEffect, useState, useRef } from 'react';
import { BACKEND_URL } from '../config/api';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const AuthCallback = () => {
  const [status, setStatus] = useState('processing');
  const [error, setError] = useState('');
  const [debugInfo, setDebugInfo] = useState('');
  const hasProcessed = useRef(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  useEffect(() => {
    if (hasProcessed.current) return;
    hasProcessed.current = true;
    processSessionId();
  }, []);

  const processSessionId = async () => {
    try {
      // Extract session_id from URL
      let sessionId = null;
      const fullUrl = window.location.href;
      
      setDebugInfo(`URL: ${fullUrl}`);
      
      // Method 1: Full URL regex
      const urlMatch = fullUrl.match(/[#&?]session_id=([^&#\s]+)/);
      if (urlMatch) sessionId = urlMatch[1];
      
      // Method 2: Hash fragment
      if (!sessionId && window.location.hash) {
        const hashMatch = window.location.hash.match(/session_id=([^&#\s]+)/);
        if (hashMatch) sessionId = hashMatch[1];
      }
      
      // Method 3: Query params
      if (!sessionId) {
        const urlParams = new URLSearchParams(window.location.search);
        sessionId = urlParams.get('session_id');
      }

      if (!sessionId) {
        setStatus('error');
        setError('No session_id found in URL');
        setDebugInfo(`URL: ${fullUrl} | Hash: ${window.location.hash}`);
        setTimeout(() => doRedirect('/login'), 3000);
        return;
      }

      // Determine backend URL
      const apiBase = BACKEND_URL || window.location.origin;
      setDebugInfo(`Session: ${sessionId.substring(0, 8)}... | API: ${apiBase}`);

      // Exchange session_id with backend
      const response = await fetch(`${apiBase}/api/auth/session?session_id=${sessionId}`, {
        credentials: 'include'
      });

      if (!response.ok) {
        let errMsg = `Server returned ${response.status}`;
        try {
          const errData = await response.json();
          errMsg = errData.detail || errMsg;
        } catch (e) {}
        throw new Error(errMsg);
      }

      const data = await response.json();

      if (!data || !data.user) {
        throw new Error('No user data returned from server');
      }

      // Clean URL
      window.history.replaceState({}, document.title, window.location.pathname || '/');

      // Store auth data
      const user = data.user;
      const accessToken = data.access_token || '';
      
      // Store in localStorage
      localStorage.setItem('user', JSON.stringify(user));
      localStorage.setItem('userData', JSON.stringify(user));
      localStorage.setItem('token', accessToken);
      localStorage.setItem('userToken', accessToken);
      
      // Admin-specific storage
      if (user.role === 'admin' || user.role === 'super_admin' || user.role === 'manager') {
        localStorage.setItem('adminToken', accessToken);
        localStorage.setItem('authToken', accessToken);
        localStorage.setItem('adminUser', JSON.stringify(user));
      }

      // Call AuthContext login
      try { login(user, accessToken); } catch (e) {}

      setStatus('success');

      // Determine redirect destination
      const returnUrl = localStorage.getItem('authReturnUrl');
      if (returnUrl) {
        localStorage.removeItem('authReturnUrl');
        try {
          const url = new URL(returnUrl);
          doRedirect(url.pathname || '/');
          return;
        } catch (e) {}
      }
      
      if (user.role === 'admin' || user.role === 'super_admin' || user.role === 'manager') {
        doRedirect('/admin');
      } else {
        doRedirect('/my-account');
      }

    } catch (err) {
      console.error('[AuthCallback] Error:', err);
      setStatus('error');
      setError(err.message || 'Authentication failed');
      setTimeout(() => doRedirect('/login'), 4000);
    }
  };

  const doRedirect = (path) => {
    // First, make sure the URL hash is cleared so the App-level `hasSessionId`
    // re-evaluates correctly. Then navigate. If we're already on the target
    // path (e.g., Emergent redirected to /admin#session_id=...), React Router
    // would treat navigate(path) as a no-op, so use window.location.assign
    // as a safety net to force a full re-render of the App tree.
    try {
      // Clear hash first
      if (window.location.hash) {
        window.history.replaceState({}, document.title, window.location.pathname + window.location.search);
      }
      const currentPath = window.location.pathname || '/';
      if (currentPath === path) {
        // Same path — navigate() would be a no-op. Force a clean reload.
        window.location.assign(path);
        return;
      }
      if (navigate) {
        navigate(path, { replace: true });
        // Belt-and-suspenders: if the App tree still hasn't switched after 500ms, hard reload
        setTimeout(() => {
          if (window.location.hash.includes('session_id=')) {
            window.location.assign(path);
          }
        }, 500);
      } else {
        window.location.assign(path);
      }
    } catch (e) {
      window.location.assign(path);
    }
  };

  if (status === 'processing') {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f0f4ff' }}>
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <div style={{ 
            width: '48px', height: '48px', border: '4px solid #e0e0e0', borderTopColor: '#2563eb', 
            borderRadius: '50%', animation: 'spin 1s linear infinite', margin: '0 auto'
          }} />
          <p style={{ marginTop: '1rem', color: '#374151', fontWeight: '600' }}>Completing authentication...</p>
          <p style={{ marginTop: '0.5rem', color: '#6b7280', fontSize: '0.875rem' }}>Please wait</p>
          {debugInfo && <p style={{ marginTop: '1rem', color: '#9ca3af', fontSize: '0.75rem', wordBreak: 'break-all' }}>{debugInfo}</p>}
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        </div>
      </div>
    );
  }

  if (status === 'success') {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f0fdf4' }}>
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <div style={{ width: '48px', height: '48px', background: '#dcfce7', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto' }}>
            <span style={{ color: '#16a34a', fontSize: '24px' }}>✓</span>
          </div>
          <p style={{ marginTop: '1rem', color: '#374151', fontWeight: '600' }}>Signed in successfully!</p>
          <p style={{ marginTop: '0.5rem', color: '#6b7280', fontSize: '0.875rem' }}>Redirecting...</p>
        </div>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#fef2f2' }}>
        <div style={{ textAlign: 'center', maxWidth: '400px', padding: '2rem' }}>
          <div style={{ width: '48px', height: '48px', background: '#fee2e2', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto' }}>
            <span style={{ color: '#dc2626', fontSize: '24px' }}>✕</span>
          </div>
          <h2 style={{ marginTop: '1rem', fontSize: '1.25rem', fontWeight: '700', color: '#111827' }}>Authentication Failed</h2>
          <p style={{ marginTop: '0.5rem', color: '#6b7280' }}>{error}</p>
          {debugInfo && <p style={{ marginTop: '0.5rem', color: '#9ca3af', fontSize: '0.75rem', wordBreak: 'break-all' }}>{debugInfo}</p>}
          <p style={{ marginTop: '1rem', color: '#9ca3af', fontSize: '0.875rem' }}>Redirecting to login...</p>
          <button 
            onClick={() => doRedirect('/login')}
            style={{ marginTop: '1rem', padding: '0.5rem 1.5rem', background: '#2563eb', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  return null;
};

export default AuthCallback;
