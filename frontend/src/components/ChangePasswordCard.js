import React, { useState } from 'react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';

export default function ChangePasswordCard() {
  const [cur, setCur] = useState('');
  const [pw, setPw] = useState('');
  const [pw2, setPw2] = useState('');
  const [msg, setMsg] = useState(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    if (pw !== pw2) return setMsg({ ok: false, text: 'New passwords do not match' });
    setBusy(true); setMsg(null);
    try {
      const r = await fetch(`${BACKEND_URL}/api/auth/customer/change-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
        body: JSON.stringify({ current_password: cur, new_password: pw })
      });
      const d = await r.json().catch(() => ({}));
      if (r.ok) { setMsg({ ok: true, text: d.message || 'Password changed' }); setCur(''); setPw(''); setPw2(''); }
      else setMsg({ ok: false, text: d.detail || 'Could not change password' });
    } catch (err) { setMsg({ ok: false, text: 'Network error. Please try again.' }); }
    setBusy(false);
  };

  const input = 'w-full border border-gray-300 rounded-lg px-3 py-2 mb-3 focus:outline-none focus:ring-2 focus:ring-blue-500';
  return (
    <div className="bg-white rounded-xl shadow-lg p-6 mt-6">
      <h3 className="text-xl font-bold text-gray-900 mb-1">Change Password</h3>
      <p className="text-sm text-gray-500 mb-4">At least 8 characters, with a letter and a number.</p>
      {msg && <div className={`text-sm rounded-lg p-3 mb-4 ${msg.ok ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>{msg.text}</div>}
      <form onSubmit={submit} className="max-w-md">
        <input type="password" className={input} placeholder="Current password" value={cur} onChange={e => setCur(e.target.value)} required />
        <input type="password" className={input} placeholder="New password" value={pw} onChange={e => setPw(e.target.value)} required />
        <input type="password" className={input} placeholder="Confirm new password" value={pw2} onChange={e => setPw2(e.target.value)} required />
        <button disabled={busy} className="bg-blue-600 text-white rounded-lg px-5 py-2 font-medium hover:bg-blue-700 disabled:opacity-50">
          {busy ? 'Saving...' : 'Update password'}
        </button>
      </form>
    </div>
  );
}
