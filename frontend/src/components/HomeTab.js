import React from 'react';

const inr = (n) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(Number(n) || 0);
const fmt = (d) => { const x = new Date(d); return isNaN(x) ? '' : x.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }); };
const daysLeft = (d) => { const x = new Date(d); return isNaN(x) ? null : Math.ceil((x - new Date()) / 86400000); };
const CLOSED = ['resolved', 'closed', 'completed', 'cancelled'];

function Card({ title, action, children }) {
  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        {action}
      </div>
      {children}
    </div>
  );
}
const Empty = ({ text }) => <p className="text-sm text-gray-500">{text}</p>;
const Link2 = ({ onClick, children }) => (
  <button onClick={onClick} className="text-sm text-blue-600 hover:underline">{children}</button>
);

export default function HomeTab({ user, orders, myProducts, serviceRequests, suggestions, setActiveTab, onViewOrder }) {
  const sorted = [...(orders || [])].sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));
  const latest = sorted[0];

  const warranties = (myProducts || [])
    .map(p => ({ p, d: daysLeft(p.warranty_end_date || p.warranty_end) }))
    .filter(x => x.d !== null && x.d >= 0 && x.d <= 90)
    .sort((a, b) => a.d - b.d);

  const openReqs = (serviceRequests || []).filter(s => !CLOSED.includes(String(s.status || '').toLowerCase()));

  const due = (suggestions || [])
    .filter(s => s.urgency === 'high' || (s.days_until_needed !== undefined && s.days_until_needed <= 14))
    .slice(0, 4);

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-xl font-bold text-gray-900">Hello, {(user && (user.first_name || (user.email || '').split('@')[0])) || 'there'}</h2>
        <p className="text-sm text-gray-500 mt-1">Here is a quick summary of your account.</p>
      </div>

      <Card title="Latest order" action={<Link2 onClick={() => setActiveTab('orders')}>All orders</Link2>}>
        {latest ? (
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <p className="font-medium text-gray-900">#{latest.order_number || String(latest.id).slice(0, 8)}</p>
              <p className="text-sm text-gray-500">{fmt(latest.created_at)} · {inr(latest.total_amount)}</p>
              <span className="inline-block mt-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded capitalize">
                {String(latest.order_status || 'placed').replace(/_/g, ' ')}
              </span>
            </div>
            <div className="flex gap-2">
              {(latest.tracking_url || latest.sr_awb_code) && ['processing', 'shipped'].includes(latest.order_status) && (
                <a href={latest.tracking_url || `https://shiprocket.co/tracking/${latest.sr_awb_code}`} target="_blank" rel="noopener noreferrer"
                   className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700">Track shipment</a>
              )}
              <button onClick={() => onViewOrder(latest.id)} className="px-4 py-2 bg-gray-100 text-gray-800 rounded-lg text-sm hover:bg-gray-200">View details</button>
            </div>
          </div>
        ) : <Empty text="You have no orders yet." />}
      </Card>

      <div className="grid md:grid-cols-2 gap-6">
        <Card title="Warranty ending soon" action={<Link2 onClick={() => setActiveTab('products')}>My products</Link2>}>
          {warranties.length ? (
            <ul className="space-y-3">
              {warranties.map(({ p, d }) => (
                <li key={p.id} className="flex justify-between gap-3 text-sm">
                  <span className="text-gray-800">{p.product_name}</span>
                  <span className={d <= 30 ? 'text-red-600 font-medium whitespace-nowrap' : 'text-yellow-700 whitespace-nowrap'}>{d} days left</span>
                </li>
              ))}
            </ul>
          ) : <Empty text="No warranty ends in the next 90 days." />}
        </Card>

        <Card title="Open service requests" action={<Link2 onClick={() => setActiveTab('service')}>View all</Link2>}>
          {openReqs.length ? (
            <ul className="space-y-3">
              {openReqs.slice(0, 4).map(s => (
                <li key={s.id} className="flex justify-between gap-3 text-sm">
                  <span className="text-gray-800">{s.product_name || 'Service request'}</span>
                  <span className="text-gray-500 capitalize whitespace-nowrap">{String(s.status || 'open').replace(/_/g, ' ')}</span>
                </li>
              ))}
            </ul>
          ) : <Empty text="No open service requests." />}
        </Card>
      </div>

      <Card title="Due for reorder" action={<Link2 onClick={() => setActiveTab('consumables')}>Quick orders</Link2>}>
        {due.length ? (
          <ul className="space-y-3">
            {due.map((s, i) => (
              <li key={i} className="flex justify-between gap-3 text-sm">
                <span className="text-gray-800">{s.consumable_name || s.product_name}</span>
                <span className="text-gray-500 whitespace-nowrap">
                  {s.days_until_needed === 0 ? 'due now' : `in ${s.days_until_needed} days`}
                </span>
              </li>
            ))}
          </ul>
        ) : <Empty text="Nothing is due for reorder right now." />}
      </Card>
    </div>
  );
}
