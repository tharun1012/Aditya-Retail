import authFetch from './authFetch';
import React, { useState, useEffect, useCallback } from 'react';
import { BACKEND_URL } from '../config/api';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import {
  Users, Plus, Search, ArrowLeft, Flame, Trophy, TrendingUp, Kanban, List, Mail, Phone,
} from 'lucide-react';
import { LeadKanban } from './crm/LeadKanban';
import { LeadDetailDrawer } from './crm/LeadDetailDrawer';
import { QuotationPipeline } from './crm/QuotationPipeline';
import MailLeads from './MailLeads';
import { TEAMS, STAGES, statusToStage, getStatusColor, getTeamBadge, leadDisplayName, timeAgo, safeText } from './crm/leadUtils';

const isAiChatLead = (l) => {
  const src = (l.source || '').toLowerCase();
  return src.startsWith('ai_chat') || src.includes('neural') || !!l.ai_chat_session_id;
};
const aiChatAgent = (l) => {
  const a = (l.agent_type || '').toLowerCase();
  if (['sales', 'service', 'delivery'].includes(a)) return a;
  const src = (l.source || '').toLowerCase();
  if (src.includes('service')) return 'service';
  if (src.includes('delivery')) return 'delivery';
  return 'sales';
};
const isWebsiteLead = (l) => (l.source || '') === 'website_signup';
const AI_AGENT_TABS = [
  { key: 'sales', label: 'Sales' },
  { key: 'service', label: 'Service' },
  { key: 'delivery', label: 'Delivery' },
  { key: 'all', label: 'All AI Chat' },
];

const LeadManagement = ({ storeMode = false }) => {
  const navigate = useNavigate();
  const L = storeMode ? `${BACKEND_URL}/api/leads/store` : `${BACKEND_URL}/api/leads`;
  const leadFetch = (url, opts = {}) => storeMode
    ? fetch(url, { ...opts, headers: { ...(opts.headers || {}), Authorization: `Bearer ${localStorage.getItem('storeToken') || ''}` } })
    : authFetch(url, opts);
  const [leads, setLeads] = useState([]);
  const [funnel, setFunnel] = useState({});
  const [loading, setLoading] = useState(true);
  const [selectedLead, setSelectedLead] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [activeTeam, setActiveTeam] = useState('all');
  const [viewMode, setViewMode] = useState('pipeline');
  const [searchTerm, setSearchTerm] = useState('');
  const [quotationCount, setQuotationCount] = useState(null);
  const [mailCount, setMailCount] = useState(null);
  const [aiAgentFilter, setAiAgentFilter] = useState('sales');
  const [formData, setFormData] = useState({ name: '', email: '', phone: '', source: 'website', notes: '', product: '', brand: '', quantity: '', expected_value: '' });

  const fetchData = useCallback(async () => {
    try {
      const [leadsRes, funnelRes] = await Promise.all([
        leadFetch(storeMode ? `${L}/list` : `${L}/`, { cache: 'no-store' }),
        leadFetch(`${L}/funnel`, { cache: 'no-store' }),
      ]);
      const leadsData = await leadsRes.json();
      const funnelData = await funnelRes.json();
      let extra = [];
      {
        try {
          const [mRes, qRes] = await Promise.all([
            leadFetch(storeMode ? `${L}/mail` : `${BACKEND_URL}/api/mail-leads`, { cache: 'no-store' }),
            leadFetch(storeMode ? `${L}/quotations` : `${BACKEND_URL}/api/quotations/crm/pipeline`, { cache: 'no-store' }),
          ]);
          const mData = mRes.ok ? await mRes.json() : [];
          const qData = qRes.ok ? await qRes.json() : {};
          extra = [
            ...(Array.isArray(mData) ? mData : []).map((m) => ({
              id: m.id, _src: 'mail', lead_type: 'mail', source: 'mail',
              name: m.name || m.customer_name || 'Mail lead', phone: m.phone, email: m.email,
              status: m.status || 'new', notes: m.message || m.notes || '',
              interested_products: [m.brand, m.category].filter(Boolean),
              created_at: m.received_at || m.created_at,
            })),
            ...(qData.quotations || []).map((q) => ({
              id: q.id, _src: 'quotation', lead_type: 'quotation', source: 'quotation',
              name: q.customer_name || 'Quotation', phone: q.customer_phone, email: q.customer_email,
              status: q.crm_stage || 'new', notes: q.quotation_number || '',
              expected_value: q.amount, created_at: q.created_at,
            })),
          ];
        } catch (e) { console.error('Error merging mail/quotation leads:', e); }
      }
      setLeads([...(leadsData.leads || []), ...extra]);
      setFunnel({ ...(funnelData.funnel || {}), total_leads: ((funnelData.funnel || {}).total_leads || 0) + extra.length });
    } catch (error) {
      console.error('Error fetching lead data:', error);
    } finally {
      setLoading(false);
    }
  }, [storeMode]);

  useEffect(() => { fetchData(); }, [fetchData]);

  useEffect(() => {
    fetch(storeMode ? `${BACKEND_URL}/api/leads/store/quotations?limit=1` : `${BACKEND_URL}/api/quotations/crm/pipeline?limit=1`,
      storeMode ? { headers: { Authorization: `Bearer ${localStorage.getItem('storeToken') || ''}` } } : undefined)
      .then((r) => r.json())
      .then((d) => setQuotationCount(typeof d.total === 'number' ? d.total : null))
      .catch(() => {});
  }, [activeTeam]);

  useEffect(() => {
    fetch(storeMode ? `${BACKEND_URL}/api/leads/store/mail` : `${BACKEND_URL}/api/mail-leads`,
      storeMode ? { headers: { Authorization: `Bearer ${localStorage.getItem('storeToken') || ''}` } } : undefined)
      .then((r) => r.json())
      .then((d) => setMailCount(Array.isArray(d) ? d.length : null))
      .catch(() => {});
  }, [activeTeam]);

  const refreshSelected = async (leadId) => {
    try {
      const res = await leadFetch(`${L}/${leadId}`);
      const data = await res.json();
      if (data.lead) setSelectedLead(data.lead);
    } catch (e) { /* ignore */ }
  };

  const handleUpdateLead = async (leadId, payload, followUpPayload = null) => {
    const prevLeads = leads;
    if (payload && payload.status && !followUpPayload) {
      setLeads((cur) => cur.map((l) => (l.id === leadId ? { ...l, status: payload.status } : l)));
    }
    try {
      let res;
      if (followUpPayload) {
        res = await leadFetch(`${L}/follow-up`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(followUpPayload),
        });
      } else if (payload && payload.status && (leads.find((l) => l.id === leadId) || {})._src === 'mail') {
        res = await leadFetch(storeMode ? `${L}/mail/${leadId}/status` : `${BACKEND_URL}/api/mail-leads/${leadId}/status`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: payload.status }),
        });
      } else if (payload && payload.status && (leads.find((l) => l.id === leadId) || {})._src === 'quotation') {
        res = await leadFetch(storeMode ? `${L}/quotations/${leadId}/crm-stage` : `${BACKEND_URL}/api/quotations/${leadId}/crm-stage`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ crm_stage: payload.status }),
        });
      } else if (payload) {
        res = await leadFetch(`${L}/${leadId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      }
      if (res && !res.ok) {
        const err = await res.json().catch(() => ({}));
        setLeads(prevLeads);
        alert(`Update failed: ${err.detail || res.status}`);
        return;
      }
      await fetchData();
      if (selectedLead && selectedLead.id === leadId) await refreshSelected(leadId);
    } catch (error) {
      console.error('Error updating lead:', error);
      setLeads(prevLeads);
      alert('Update failed. Please check your connection and try again.');
    }
  };

  const handleDeleteLead = async (leadId) => {
    if (!window.confirm('Delete this lead permanently?')) return;
    try {
      const res = await leadFetch(`${L}/${leadId}`, { method: 'DELETE' });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        alert(`Delete failed: ${err.detail || res.status}`);
        return;
      }
      setSelectedLead(null);
      await fetchData();
    } catch (error) {
      console.error('Error deleting lead:', error);
      alert('Delete failed. Please check your connection and try again.');
    }
  };

  const handleCreateLead = async (e) => {
    e.preventDefault();
    try {
      const response = await leadFetch(storeMode ? `${L}/create` : `${L}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          email: formData.email || null,
          phone: formData.phone || null,
          product: formData.product || null,
          brand: formData.brand || null,
          quantity: formData.quantity ? parseInt(formData.quantity, 10) : null,
          expected_value: formData.expected_value ? parseFloat(formData.expected_value) : null,
        }),
      });
      if (response.ok) {
        setShowCreateModal(false);
        setFormData({ name: '', email: '', phone: '', source: 'website', notes: '', product: '', brand: '', quantity: '', expected_value: '' });
        fetchData();
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
      }
    } catch (error) {
      alert('Failed to create lead');
    }
  };

  const teamCounts = TEAMS.reduce((acc, t) => {
    acc[t.key] = t.key === 'all' ? leads.length : leads.filter((l) => l.lead_type === t.key).length;
    return acc;
  }, {});

  const aiChatLeads = leads.filter(isAiChatLead);
  const aiChatCount = aiChatLeads.length;
  const websiteCount = leads.filter(isWebsiteLead).length;

  const q = searchTerm.toLowerCase();
  const filteredLeads = leads.filter((lead) => {
    if (activeTeam === 'aichat') {
      if (!isAiChatLead(lead)) return false;
      if (aiAgentFilter !== 'all' && aiChatAgent(lead) !== aiAgentFilter) return false;
    } else if (activeTeam === 'website') {
      if (!isWebsiteLead(lead)) return false;
    } else if (activeTeam !== 'all' && lead.lead_type !== activeTeam) return false;
    if (!q) return true;
    return (
      (lead.name || '').toLowerCase().includes(q) ||
      (lead.email || '').toLowerCase().includes(q) ||
      (lead.phone || '').includes(searchTerm) ||
      safeText(lead.notes).toLowerCase().includes(q)
    );
  });

  const hotCount = filteredLeads.filter((l) => l.status === 'hot').length;
  const wonCount = filteredLeads.filter((l) => l.status === 'won').length;

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading CRM...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8" data-testid="lead-management-page">
      <div className="max-w-[1400px] mx-auto">
        <button
          onClick={() => navigate(storeMode ? '/store/dashboard' : '/admin')}
          className="flex items-center px-4 py-2 mb-6 text-gray-700 bg-white hover:bg-gray-100 rounded-lg transition-colors border border-gray-300 shadow-sm"
          data-testid="back-to-dashboard-btn"
        >
          <ArrowLeft className="h-5 w-5 mr-2" />
          <span className="font-medium">Back to Dashboard</span>
        </button>

        {/* Header */}
        <div className="mb-6 flex flex-wrap justify-between items-center gap-3">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Lead CRM</h1>
            <p className="text-gray-600 text-sm mt-1">All leads captured by AI agents, consultations & manual entry — organized by team</p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            data-testid="add-lead-btn"
          >
            <Plus className="w-5 h-5" /> Add Lead
          </button>
        </div>

        {activeTeam !== 'quotations' && activeTeam !== 'mail' && (
        <>
        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <Card data-testid="stat-total-leads">
            <CardContent className="p-4 flex items-center gap-3">
              <div className="p-2.5 bg-blue-100 rounded-lg"><Users className="w-5 h-5 text-blue-600" /></div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{filteredLeads.length}</p>
                <p className="text-xs text-gray-500">{activeTeam === 'all' ? 'Total Leads' : activeTeam === 'aichat' ? 'AI Chat Leads' : activeTeam === 'website' ? 'Website Leads' : `${TEAMS.find(t => t.key === activeTeam)?.label} Leads`}</p>
              </div>
            </CardContent>
          </Card>
          <Card data-testid="stat-hot-leads">
            <CardContent className="p-4 flex items-center gap-3">
              <div className="p-2.5 bg-red-100 rounded-lg"><Flame className="w-5 h-5 text-red-600" /></div>
              <div>
                <p className="text-2xl font-bold text-red-600">{hotCount}</p>
                <p className="text-xs text-gray-500">Hot Leads</p>
              </div>
            </CardContent>
          </Card>
          <Card data-testid="stat-won-leads">
            <CardContent className="p-4 flex items-center gap-3">
              <div className="p-2.5 bg-green-100 rounded-lg"><Trophy className="w-5 h-5 text-green-600" /></div>
              <div>
                <p className="text-2xl font-bold text-green-600">{wonCount}</p>
                <p className="text-xs text-gray-500">Converted</p>
              </div>
            </CardContent>
          </Card>
          <Card data-testid="stat-conversion-rate">
            <CardContent className="p-4 flex items-center gap-3">
              <div className="p-2.5 bg-purple-100 rounded-lg"><TrendingUp className="w-5 h-5 text-purple-600" /></div>
              <div>
                <p className="text-2xl font-bold text-purple-600">{funnel.conversion_rate || 0}%</p>
                <p className="text-xs text-gray-500">Conversion Rate</p>
              </div>
            </CardContent>
          </Card>
        </div>

        </>
        )}

        {/* Team tabs */}
        <div className="flex flex-wrap gap-2 mb-4 bg-white p-2 rounded-xl border border-gray-200 shadow-sm">
          {TEAMS.map((team) => (
            <button
              key={team.key}
              onClick={() => setActiveTeam(team.key)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTeam === team.key
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
              data-testid={`team-tab-${team.key}`}
            >
              {team.label}
              <span className={`ml-2 px-1.5 py-0.5 rounded-full text-xs font-bold ${activeTeam === team.key ? 'bg-white/20' : 'bg-gray-100'}`}>
                {teamCounts[team.key] || 0}
              </span>
            </button>
          ))}
          <button
            onClick={() => setActiveTeam('quotations')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTeam === 'quotations' ? 'bg-orange-600 text-white' : 'text-gray-600 hover:bg-gray-100'
            }`}
            data-testid="team-tab-quotations"
            
          >
            Quotations
            {quotationCount !== null && (
              <span className={`ml-2 px-1.5 py-0.5 rounded-full text-xs font-bold ${activeTeam === 'quotations' ? 'bg-white/20' : 'bg-gray-100'}`}>
                {quotationCount}
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTeam('mail')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTeam === 'mail' ? 'bg-emerald-600 text-white' : 'text-gray-600 hover:bg-gray-100'
            }`}
            data-testid="team-tab-mail"
            
          >
            Mail
            {mailCount !== null && (
              <span className={`ml-2 px-1.5 py-0.5 rounded-full text-xs font-bold ${activeTeam === 'mail' ? 'bg-white/20' : 'bg-gray-100'}`}>
                {mailCount}
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTeam('aichat')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTeam === 'aichat' ? 'bg-violet-600 text-white' : 'text-gray-600 hover:bg-gray-100'
            }`}
            data-testid="team-tab-aichat"
          >
            AI Chat
            <span className={`ml-2 px-1.5 py-0.5 rounded-full text-xs font-bold ${activeTeam === 'aichat' ? 'bg-white/20' : 'bg-gray-100'}`}>
              {aiChatCount}
            </span>
          </button>
          <button
            onClick={() => setActiveTeam('website')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTeam === 'website' ? 'bg-cyan-600 text-white' : 'text-gray-600 hover:bg-gray-100'
            }`}
            data-testid="team-tab-website"
          >
            Website
            <span className={`ml-2 px-1.5 py-0.5 rounded-full text-xs font-bold ${activeTeam === 'website' ? 'bg-white/20' : 'bg-gray-100'}`}>
              {websiteCount}
            </span>
          </button>
        </div>

        {activeTeam === 'aichat' && (
          <div className="flex gap-2 mb-3">
            {AI_AGENT_TABS.map((t) => {
              const n = t.key === 'all' ? aiChatCount : aiChatLeads.filter((l) => aiChatAgent(l) === t.key).length;
              return (
                <button
                  key={t.key}
                  onClick={() => setAiAgentFilter(t.key)}
                  className={`px-3 py-1 rounded-md text-sm border ${aiAgentFilter === t.key ? 'bg-slate-900 text-white' : 'bg-white'}`}
                  data-testid={`ai-agent-tab-${t.key}`}
                >
                  {t.label} <span className="ml-1 text-xs opacity-70">{n}</span>
                </button>
              );
            })}
          </div>
        )}

        {/* Toolbar: search + view toggle */}
        {activeTeam !== 'mail' && (
        <div className="flex flex-wrap gap-3 items-center mb-5">
          <div className="relative flex-1 min-w-[240px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder={activeTeam === 'quotations' ? "Search by quotation #, customer or phone..." : "Search by name, phone, email or notes..."}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 bg-white"
              data-testid="lead-search-input"
            />
          </div>
          <div className="flex bg-white border border-gray-300 rounded-lg overflow-hidden">
            <button
              onClick={() => setViewMode('pipeline')}
              className={`flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium ${viewMode === 'pipeline' ? 'bg-gray-900 text-white' : 'text-gray-600 hover:bg-gray-50'}`}
              data-testid="view-toggle-pipeline"
            >
              <Kanban className="w-4 h-4" /> Pipeline
            </button>
            <button
              onClick={() => setViewMode('table')}
              className={`flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium ${viewMode === 'table' ? 'bg-gray-900 text-white' : 'text-gray-600 hover:bg-gray-50'}`}
              data-testid="view-toggle-table"
            >
              <List className="w-4 h-4" /> Table
            </button>
          </div>
        </div>
        )}

        {/* Content */}
        {activeTeam === 'mail' ? (
          <MailLeads storeMode={storeMode} />
        ) : activeTeam === 'quotations' ? (
          <QuotationPipeline searchTerm={searchTerm} viewMode={viewMode} storeMode={storeMode} />
        ) : viewMode === 'pipeline' ? (
          <LeadKanban
            leads={filteredLeads}
            onSelectLead={(lead) => setSelectedLead(lead)}
            onMoveStage={(leadId, stage) => handleUpdateLead(leadId, { status: stage })}
          />
        ) : (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Leads ({filteredLeads.length})</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full" data-testid="leads-table">
                  <thead>
                    <tr className="border-b text-left text-xs font-semibold text-gray-500 uppercase">
                      <th className="py-3 px-3">Lead</th>
                      <th className="py-3 px-3">Contact</th>
                      <th className="py-3 px-3">Team</th>
                      <th className="py-3 px-3">Interest</th>
                      <th className="py-3 px-3">Stage</th>
                      <th className="py-3 px-3">Assigned</th>
                      <th className="py-3 px-3">Created</th>
                      <th className="py-3 px-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredLeads.length === 0 && (
                      <tr><td colSpan={8} className="py-8 text-center text-sm text-gray-400">No leads found</td></tr>
                    )}
                    {filteredLeads.map((lead) => {
                      const team = getTeamBadge(lead.lead_type);
                      return (
                        <tr key={lead.id} className="border-b hover:bg-gray-50 text-sm">
                          <td className="py-3 px-3">
                            <span className="font-medium text-gray-900">{leadDisplayName(lead)}</span>
                            {['hot', 'warm', 'cold'].includes(lead.status) && (
                              <span className={`ml-2 px-1.5 py-0.5 rounded text-[10px] font-bold uppercase ${getStatusColor(lead.status)}`}>{lead.status}</span>
                            )}
                          </td>
                          <td className="py-3 px-3 text-xs text-gray-600">
                            {lead.phone && <div className="flex items-center gap-1"><Phone className="w-3 h-3" />{lead.phone}</div>}
                            {lead.email && <div className="flex items-center gap-1"><Mail className="w-3 h-3" />{lead.email}</div>}
                            {!lead.phone && !lead.email && <span className="text-gray-400">—</span>}
                          </td>
                          <td className="py-3 px-3">
                            <span className={`px-2 py-0.5 rounded text-xs font-semibold ${team.cls}`}>{team.label}</span>
                          </td>
                          <td className="py-3 px-3 text-xs text-gray-600 max-w-[180px] truncate">
                            {(lead.interested_products || []).map(safeText).join(', ') || safeText(lead.interested_in) || '—'}
                          </td>
                          <td className="py-3 px-3">
                            <select
                              value={statusToStage(lead.status)}
                              onChange={(e) => handleUpdateLead(lead.id, { status: e.target.value })}
                              className={`px-2 py-1 rounded-full text-xs font-semibold border-0 ${getStatusColor(statusToStage(lead.status))}`}
                              data-testid={`table-stage-select-${lead.id}`}
                            >
                              {STAGES.map((s) => <option key={s.key} value={s.key}>{s.label}</option>)}
                            </select>
                          </td>
                          <td className="py-3 px-3 text-xs text-gray-600">{lead.assigned_to || '—'}</td>
                          <td className="py-3 px-3 text-xs text-gray-500">{timeAgo(lead.created_at)}</td>
                          <td className="py-3 px-3 text-right">
                            <button
                              onClick={() => setSelectedLead(lead)}
                              className="text-blue-600 hover:text-blue-800 font-medium text-xs"
                              data-testid={`view-lead-btn-${lead.id}`}
                            >
                              View Details
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Detail drawer */}
        {selectedLead && (
          <LeadDetailDrawer
            lead={selectedLead}
            onClose={() => setSelectedLead(null)}
            onUpdate={handleUpdateLead}
            onDelete={storeMode ? undefined : handleDeleteLead}
          />
        )}

        {/* Create modal */}
        {showCreateModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-black/40" onClick={() => setShowCreateModal(false)} />
            <div className="relative bg-white rounded-xl shadow-2xl w-full max-w-md p-6" data-testid="create-lead-modal">
              <h2 className="text-lg font-bold text-gray-900 mb-4">Add New Lead</h2>
              <form onSubmit={handleCreateLead} className="space-y-3">
                <input
                  required
                  placeholder="Name *"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm"
                  data-testid="create-lead-name-input"
                />
                <input
                  placeholder="Phone"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm"
                  data-testid="create-lead-phone-input"
                />
                <input
                  type="email"
                  placeholder="Email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm"
                  data-testid="create-lead-email-input"
                />
                <select
                  value={formData.source}
                  onChange={(e) => setFormData({ ...formData, source: e.target.value })}
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm"
                >
                  <option value="website">Website</option>
                  <option value="phone">Phone Call</option>
                  <option value="walk_in">Walk-in</option>
                  <option value="referral">Referral</option>
                  <option value="social_media">Social Media</option>
                  <option value="other">Other</option>
                </select>
                <input
                  placeholder="Product (e.g. WGA1220SIN washing machine)"
                  value={formData.product}
                  onChange={(e) => setFormData({ ...formData, product: e.target.value })}
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm"
                  data-testid="create-lead-product-input"
                />
                <div className="grid grid-cols-3 gap-2">
                  <input
                    placeholder="Brand"
                    value={formData.brand}
                    onChange={(e) => setFormData({ ...formData, brand: e.target.value })}
                    className="px-3 py-2.5 border border-gray-300 rounded-lg text-sm"
                    data-testid="create-lead-brand-input"
                  />
                  <input
                    type="number" min="1" placeholder="Qty"
                    value={formData.quantity}
                    onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                    className="px-3 py-2.5 border border-gray-300 rounded-lg text-sm"
                    data-testid="create-lead-qty-input"
                  />
                  <input
                    type="number" min="0" placeholder="Price ₹"
                    value={formData.expected_value}
                    onChange={(e) => setFormData({ ...formData, expected_value: e.target.value })}
                    className="px-3 py-2.5 border border-gray-300 rounded-lg text-sm"
                    data-testid="create-lead-price-input"
                  />
                </div>
                <textarea
                  placeholder="Notes"
                  rows={2}
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm"
                />
                <div className="flex gap-2 pt-1">
                  <button type="button" onClick={() => setShowCreateModal(false)} className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50">
                    Cancel
                  </button>
                  <button type="submit" className="flex-1 px-4 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700" data-testid="create-lead-submit-btn">
                    Create Lead
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LeadManagement;
