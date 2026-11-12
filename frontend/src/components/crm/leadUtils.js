export const TEAMS = [
  { key: 'all', label: 'All Leads' },
  { key: 'sales', label: 'Sales' },
  { key: 'expert', label: 'Expert Consultation' },
  { key: 'service', label: 'Service' },
  { key: 'delivery', label: 'Delivery' },
  { key: 'other', label: 'Other' },
];

export const STAGES = [
  { key: 'new', label: 'New', headerClass: 'bg-blue-50 border-blue-200 text-blue-800' },
  { key: 'contacted', label: 'Contacted', headerClass: 'bg-purple-50 border-purple-200 text-purple-800' },
  { key: 'qualified', label: 'Qualified', headerClass: 'bg-indigo-50 border-indigo-200 text-indigo-800' },
  { key: 'negotiation', label: 'Negotiation', headerClass: 'bg-amber-50 border-amber-200 text-amber-800' },
  { key: 'won', label: 'Won', headerClass: 'bg-green-50 border-green-200 text-green-800' },
  { key: 'lost', label: 'Lost', headerClass: 'bg-gray-100 border-gray-300 text-gray-600' },
];

export const statusToStage = (status) => {
  if (['contacted', 'qualified', 'negotiation', 'won', 'lost'].includes(status)) return status;
  return 'new';
};

export const getStatusColor = (status) => {
  const colors = {
    new: 'bg-blue-100 text-blue-800',
    contacted: 'bg-purple-100 text-purple-800',
    qualified: 'bg-indigo-100 text-indigo-800',
    hot: 'bg-red-100 text-red-800',
    warm: 'bg-orange-100 text-orange-800',
    cold: 'bg-gray-100 text-gray-800',
    negotiation: 'bg-amber-100 text-amber-800',
    won: 'bg-green-100 text-green-800',
    lost: 'bg-red-50 text-red-900',
  };
  return colors[status] || 'bg-gray-100 text-gray-800';
};

export const getTeamBadge = (leadType) => {
  const badges = {
    sales: { label: 'Sales', cls: 'bg-blue-100 text-blue-700' },
    expert: { label: 'Expert', cls: 'bg-violet-100 text-violet-700' },
    service: { label: 'Service', cls: 'bg-teal-100 text-teal-700' },
    delivery: { label: 'Delivery', cls: 'bg-orange-100 text-orange-700' },
    other: { label: 'Other', cls: 'bg-gray-100 text-gray-600' },
    mail: { label: 'Mail', cls: 'bg-emerald-100 text-emerald-700' },
    quotation: { label: 'Quotation', cls: 'bg-red-100 text-red-700' },
  };
  return badges[leadType] || badges.other;
};

export const leadDisplayName = (lead) => lead.name || 'Unknown Visitor';

export const safeText = (value) => {
  if (value == null) return '';
  if (typeof value === 'string') return value;
  if (Array.isArray(value)) return value.map(safeText).filter(Boolean).join(' · ');
  if (typeof value === 'object') {
    return String(value.message || value.content || value.note || value.text || JSON.stringify(value));
  }
  return String(value);
};

export const timeAgo = (iso) => {
  if (!iso) return '';
  const d = new Date(iso);
  if (isNaN(d)) return '';
  const mins = Math.floor((Date.now() - d.getTime()) / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  if (days < 30) return `${days}d ago`;
  return d.toLocaleDateString('en-IN');
};
