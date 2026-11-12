import React, { useState, useRef, useEffect } from 'react';
import authFetch from './authFetch';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const CHIPS = ['Where is my order?', 'When does my warranty end?', 'What should I reorder?'];

export default function AskAIAssistant({ user }) {
  const [open, setOpen] = useState(false);
  const [mode, setMode] = useState('chat');
  const [messages, setMessages] = useState([{ role: 'assistant', content: 'Hi! Ask me about your orders, warranty, reminders or service requests.' }]);
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const [products, setProducts] = useState([]);
  const [prodId, setProdId] = useState('');
  const [desc, setDesc] = useState('');
  const [result, setResult] = useState(null);
  const [note, setNote] = useState(null);
  const endRef = useRef(null);

  const authHeaders = () => ({ 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` });
  useEffect(() => { endRef.current && endRef.current.scrollIntoView({ behavior: 'smooth' }); }, [messages, open]);
  useEffect(() => {
    if (open && mode === 'report' && products.length === 0 && user) {
      authFetch(`${BACKEND_URL}/api/customer/my-products?user_id=${user.id}`)
        .then(r => r.json()).then(d => setProducts(d.products || [])).catch(() => {});
    }
  }, [open, mode, user, products.length]);

  const send = async (text) => {
    const msg = (text || input).trim();
    if (!msg || busy) return;
    const history = messages.filter((m, i) => i > 0).slice(-6);
    setMessages(m => [...m, { role: 'user', content: msg }]);
    setInput(''); setBusy(true);
    try {
      const r = await authFetch(`${BACKEND_URL}/api/customer/ai/ask`, { method: 'POST', headers: authHeaders(), body: JSON.stringify({ message: msg, history }) });
      const d = await r.json().catch(() => ({}));
      setMessages(m => [...m, { role: 'assistant', content: r.ok ? d.reply : (d.detail || 'Something went wrong. Please try again.') }]);
    } catch (e) { setMessages(m => [...m, { role: 'assistant', content: 'Network error. Please try again.' }]); }
    setBusy(false);
  };

  const triage = async () => {
    setBusy(true); setResult(null); setNote(null);
    try {
      const r = await authFetch(`${BACKEND_URL}/api/customer/ai/triage`, { method: 'POST', headers: authHeaders(), body: JSON.stringify({ registered_product_id: prodId || null, description: desc }) });
      const d = await r.json().catch(() => ({}));
      if (r.ok) setResult(d); else setNote({ ok: false, text: d.detail || 'Could not analyse the problem' });
    } catch (e) { setNote({ ok: false, text: 'Network error. Please try again.' }); }
    setBusy(false);
  };

  const createRequest = async () => {
    const prod = products.find(p => p.id === prodId);
    setBusy(true); setNote(null);
    try {
      const r = await authFetch(`${BACKEND_URL}/api/customer/service-request?user_id=${user.id}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          registered_product_id: prodId || null,
          product_name: prod ? prod.product_name : 'Not specified',
          issue_description: `${result.title}\n\n${desc}`,
          issue_type: result.issue_type || 'general',
          brand: prod ? prod.brand : undefined
        })
      });
      const d = await r.json().catch(() => ({}));
      if (r.ok) { setNote({ ok: true, text: 'Service request created. You can follow it in the Service Requests tab.' }); setResult(null); setDesc(''); }
      else setNote({ ok: false, text: d.detail || 'Could not create the request' });
    } catch (e) { setNote({ ok: false, text: 'Network error. Please try again.' }); }
    setBusy(false);
  };

  const urgencyCls = { high: 'bg-red-100 text-red-800', medium: 'bg-yellow-100 text-yellow-800', low: 'bg-green-100 text-green-800' };

  if (!open) {
    return (
      <button onClick={() => setOpen(true)} className="fixed bottom-6 left-6 z-40 bg-blue-600 text-white rounded-full px-5 py-3 shadow-lg hover:bg-blue-700 font-medium">
        ✨ Ask AI
      </button>
    );
  }
  return (
    <div className="fixed bottom-6 left-6 z-40 w-[22rem] max-w-[calc(100vw-2rem)] bg-white rounded-xl shadow-2xl border flex flex-col" style={{ height: '30rem' }}>
      <div className="flex items-center justify-between px-4 py-3 bg-blue-600 text-white rounded-t-xl">
        <div className="font-semibold">Aditya AI Assistant</div>
        <button onClick={() => setOpen(false)} className="text-white text-xl leading-none">×</button>
      </div>
      <div className="flex border-b text-sm">
        <button onClick={() => setMode('chat')} className={`flex-1 py-2 ${mode === 'chat' ? 'border-b-2 border-blue-600 text-blue-600 font-medium' : 'text-gray-500'}`}>Ask a question</button>
        <button onClick={() => setMode('report')} className={`flex-1 py-2 ${mode === 'report' ? 'border-b-2 border-blue-600 text-blue-600 font-medium' : 'text-gray-500'}`}>Report a problem</button>
      </div>

      {mode === 'chat' ? (
        <>
          <div className="flex-1 overflow-y-auto p-3 space-y-2 text-sm">
            {messages.map((m, i) => (
              <div key={i} className={`max-w-[85%] rounded-lg px-3 py-2 whitespace-pre-wrap ${m.role === 'user' ? 'bg-blue-600 text-white ml-auto' : 'bg-gray-100 text-gray-800'}`}>{m.content}</div>
            ))}
            {busy && <div className="bg-gray-100 text-gray-500 rounded-lg px-3 py-2 w-16">...</div>}
            <div ref={endRef} />
          </div>
          {messages.length === 1 && (
            <div className="px-3 pb-2 flex flex-wrap gap-2">
              {CHIPS.map(c => <button key={c} onClick={() => send(c)} className="text-xs border border-blue-200 text-blue-700 rounded-full px-3 py-1 hover:bg-blue-50">{c}</button>)}
            </div>
          )}
          <div className="p-3 border-t flex gap-2">
            <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && send()} maxLength={1000}
              placeholder="Type your question..." className="flex-1 border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            <button onClick={() => send()} disabled={busy || !input.trim()} className="bg-blue-600 text-white rounded-lg px-4 text-sm disabled:opacity-50">Send</button>
          </div>
        </>
      ) : (
        <div className="flex-1 overflow-y-auto p-3 text-sm space-y-3">
          <select value={prodId} onChange={e => setProdId(e.target.value)} className="w-full border rounded-lg px-3 py-2">
            <option value="">Select your product (optional)</option>
            {products.map(p => <option key={p.id} value={p.id}>{p.product_name}</option>)}
          </select>
          <textarea value={desc} onChange={e => setDesc(e.target.value)} rows={4} maxLength={1500} placeholder="Describe the problem..."
            className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" />
          <button onClick={triage} disabled={busy || desc.trim().length < 5} className="w-full bg-blue-600 text-white rounded-lg py-2 disabled:opacity-50">{busy && !result ? 'Analysing...' : 'Get help'}</button>
          {note && <div className={`rounded-lg p-3 ${note.ok ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>{note.text}</div>}
          {result && (
            <div className="border rounded-lg p-3 space-y-2">
              <div className="flex items-center justify-between">
                <div className="font-semibold text-gray-900">{result.title}</div>
                <span className={`px-2 py-0.5 rounded-full text-xs ${urgencyCls[result.urgency]}`}>{result.urgency}</span>
              </div>
              {result.troubleshooting_steps.length > 0 && (
                <ol className="list-decimal ml-5 text-gray-700 space-y-1">{result.troubleshooting_steps.map((s, i) => <li key={i}>{s}</li>)}</ol>
              )}
              {result.warranty_status === 'active' && <p className="text-xs text-green-700">This product appears to be under warranty. Our team confirms coverage.</p>}
              {result.warranty_status === 'expired' && <p className="text-xs text-yellow-700">This product's warranty has ended. Service may be chargeable.</p>}
              <button onClick={createRequest} disabled={busy} className="w-full bg-gray-900 text-white rounded-lg py-2 disabled:opacity-50">Still not fixed? Create service request</button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
