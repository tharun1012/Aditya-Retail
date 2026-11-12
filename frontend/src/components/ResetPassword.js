import React, { useState } from 'react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';

export default function ResetPassword() {
  const token = new URLSearchParams(window.location.search).get('token');
  const [email, setEmail] = useState('');
  const [pw, setPw] = useState('');
  const [pw2, setPw2] = useState('');
  const [msg, setMsg] = useState(null);
  const [busy, setBusy] = useState(false);

  const post = async (path, body) => {
    setBusy(true); setMsg(null);
    try {
      const r = await fetch(`${BACKEND_URL}/api/auth/customer/${path}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
      });
      const d = await r.json().catch(() => ({}));
      if (!r.ok) setMsg({ type: 'err', text: d.detail || 'Something went wrong' });
      else setMsg({ type: 'ok', text: d.message });
      return r.ok;
    } catch (e) { setMsg({ type: 'err', text: 'Network error. Please try again.' }); return false; }
    finally { setBusy(false); }
  };

  const submitReset = async (e) => {
    e.preventDefault();
    if (pw !== pw2) return setMsg({ type: 'err', text: 'Passwords do not match' });
    const ok = await post('reset-password', { token, new_password: pw });
    if (ok) setTimeout(() => { window.location.href = '/login'; }, 2000);
  };

  const submitForgot = (e) => { e.preventDefault(); post('forgot-password', { email }); };

  const input = 'w-full border border-gray-300 rounded-lg px-3 py-2 mb-3 focus:outline-none focus:ring-2 focus:ring-blue-500';
  const btn = 'w-full bg-blue-600 text-white rounded-lg py-2 font-medium hover:bg-blue-700 disabled:opacity-50';

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow p-8 w-full max-w-md">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">{token ? 'Set a new password' : 'Forgot your password?'}</h1>
        <p className="text-sm text-gray-500 mb-5">
          {token ? 'At least 8 characters, with a letter and a number.' : "Enter your email and we'll send you a reset link."}
        </p>
        {msg && <div className={`text-sm rounded-lg p-3 mb-4 ${msg.type === 'ok' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>{msg.text}</div>}
        {token ? (
          <form onSubmit={submitReset}>
            <input type="password" className={input} placeholder="New password" value={pw} onChange={e => setPw(e.target.value)} required />
            <input type="password" className={input} placeholder="Confirm new password" value={pw2} onChange={e => setPw2(e.target.value)} required />
            <button className={btn} disabled={busy}>{busy ? 'Saving...' : 'Update password'}</button>
          </form>
        ) : (
          <form onSubmit={submitForgot}>
            <input type="email" className={input} placeholder="Email address" value={email} onChange={e => setEmail(e.target.value)} required />
            <button className={btn} disabled={busy}>{busy ? 'Sending...' : 'Send reset link'}</button>
          </form>
        )}
        <a href="/login" className="block text-center text-sm text-blue-600 mt-4">Back to login</a>
      </div>
    </div>
  );
}
