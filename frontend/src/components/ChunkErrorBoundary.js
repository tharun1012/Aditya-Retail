import React from 'react';

/**
 * Catches ChunkLoadError (occurs when the browser tries to load a JS chunk that no longer
 * exists on the server — typically after a new deployment). When this happens, we unregister
 * any service workers, clear all caches, and reload the page so the user gets the fresh build.
 *
 * Without this, the app shows a blank screen until the user does a hard refresh.
 */
class ChunkErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, isChunkError: false };
  }

  static getDerivedStateFromError(error) {
    const message = (error?.message || '').toLowerCase();
    const name = (error?.name || '').toLowerCase();
    const isChunkError =
      name === 'chunkloaderror' ||
      message.includes('loading chunk') ||
      message.includes('loading css chunk') ||
      message.includes("failed to fetch dynamically imported module") ||
      message.includes('importing a module script failed');

    return { hasError: true, isChunkError, errorMessage: error?.message || String(error || 'Unknown error') };
  }

  componentDidCatch(error, info) {
    // eslint-disable-next-line no-console
    console.error('[ChunkErrorBoundary]', error, info);

    if (this.state.isChunkError) {
      this.recoverFromStaleAssets();
    }
  }

  async recoverFromStaleAssets() {
    try {
      // Avoid an infinite reload loop — only auto-reload once per session
      const reloadKey = 'chunk_error_reload_attempt';
      const lastAttempt = sessionStorage.getItem(reloadKey);
      const now = Date.now();
      if (lastAttempt && now - parseInt(lastAttempt, 10) < 10000) {
        // Already tried within the last 10s — show manual recovery UI instead
        return;
      }
      sessionStorage.setItem(reloadKey, String(now));

      // Clear caches
      if ('caches' in window) {
        const names = await caches.keys();
        await Promise.all(names.map((n) => caches.delete(n)));
      }

      // Unregister service workers
      if ('serviceWorker' in navigator) {
        const regs = await navigator.serviceWorker.getRegistrations();
        await Promise.all(regs.map((r) => r.unregister()));
      }

      // Hard reload bypassing cache
      window.location.reload();
    } catch (e) {
      // Fall through to manual UI
    }
  }

  manualRecover = async () => {
    // Disable the button immediately so a stuck user doesn't double-click
    this.setState({ recovering: true });
    try {
      if ('caches' in window) {
        const names = await caches.keys();
        await Promise.all(names.map((n) => caches.delete(n)));
      }
      if ('serviceWorker' in navigator) {
        const regs = await navigator.serviceWorker.getRegistrations();
        await Promise.all(regs.map((r) => r.unregister()));
      }
    } catch (_) {
      // Swallow — we still want to reload below
    } finally {
      // Clear the auto-reload-guard so we can attempt fresh recovery again
      try { sessionStorage.removeItem('chunk_error_reload_attempt'); } catch (_) {}

      // Hard-bust: append a cache-busting query and use replace() so the
      // browser can't reuse anything from history. This is the most reliable
      // way to force a full re-fetch of index.html and the JS chunks.
      const bust = `_cb=${Date.now()}`;
      const sep = window.location.search ? '&' : '?';
      const target = `${window.location.pathname}${window.location.search}${sep}${bust}${window.location.hash}`;
      window.location.replace(target);

      // Belt-and-braces: if `replace()` didn't trigger navigation for any reason
      // (rare on Safari with broken SW), force a reload after 800ms.
      setTimeout(() => {
        try { window.location.reload(); } catch (_) {}
      }, 800);
    }
  };

  render() {
    if (!this.state.hasError) return this.props.children;

    const isChunk = this.state.isChunkError;
    const title = isChunk ? 'Updating to the latest version' : 'Something went wrong';
    const subtitle = isChunk
      ? 'We deployed an update. Please reload to load the latest assets.'
      : 'A page error prevented this view from rendering. Try reloading, or go back to the dashboard.';
    const icon = isChunk ? '🔄' : '⚠️';
    const goHome = () => { window.location.href = '/'; };

    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
        fontFamily: 'system-ui, -apple-system, sans-serif',
        background: '#f8fafc',
        color: '#0f172a',
      }}>
        <div style={{
          maxWidth: 460,
          background: '#ffffff',
          padding: 32,
          borderRadius: 14,
          boxShadow: '0 8px 32px rgba(15,23,42,0.08)',
          textAlign: 'center',
        }}>
          <div style={{ fontSize: 48, marginBottom: 12 }}>{icon}</div>
          <h1 style={{ margin: '0 0 8px', fontSize: 22, fontWeight: 700 }}>
            {title}
          </h1>
          <p style={{ margin: '0 0 20px', fontSize: 14, color: '#64748b', lineHeight: 1.5 }}>
            {subtitle}
          </p>
          {!isChunk && this.state.errorMessage && (
            <pre style={{
              textAlign: 'left',
              fontSize: 12,
              background: '#fef2f2',
              color: '#991b1b',
              padding: '10px 12px',
              borderRadius: 8,
              border: '1px solid #fecaca',
              overflowX: 'auto',
              margin: '0 0 20px',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
            }}>
              {this.state.errorMessage}
            </pre>
          )}
          <div style={{ display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap' }}>
            <button
              onClick={this.manualRecover}
              disabled={this.state.recovering}
              style={{
                padding: '10px 24px',
                fontSize: 14,
                fontWeight: 600,
                color: '#ffffff',
                background: this.state.recovering ? '#94a3b8' : '#4f46e5',
                border: 'none',
                borderRadius: 8,
                cursor: this.state.recovering ? 'wait' : 'pointer',
              }}
            >
              {this.state.recovering ? 'Reloading…' : 'Reload Now'}
            </button>
            {!isChunk && (
              <button
                onClick={goHome}
                style={{
                  padding: '10px 24px',
                  fontSize: 14,
                  fontWeight: 600,
                  color: '#4f46e5',
                  background: '#ffffff',
                  border: '1px solid #c7d2fe',
                  borderRadius: 8,
                  cursor: 'pointer',
                }}
              >
                Go to Dashboard
              </button>
            )}
          </div>
          <p style={{ margin: '16px 0 0', fontSize: 12, color: '#94a3b8', lineHeight: 1.5 }}>
            Still stuck? Clear site data in your browser: DevTools → Application → Clear storage.
          </p>
        </div>
      </div>
    );
  }
}

export default ChunkErrorBoundary;
