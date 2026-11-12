import React from 'react';
import { Phone, Mail, Flame, Snowflake, Sun } from 'lucide-react';
import { STAGES, statusToStage, getTeamBadge, leadDisplayName, timeAgo } from './leadUtils';

const TempBadge = ({ status }) => {
  if (status === 'hot') return <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-bold bg-red-100 text-red-700"><Flame className="w-3 h-3" />HOT</span>;
  if (status === 'warm') return <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-bold bg-orange-100 text-orange-700"><Sun className="w-3 h-3" />WARM</span>;
  if (status === 'cold') return <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-bold bg-sky-100 text-sky-700"><Snowflake className="w-3 h-3" />COLD</span>;
  return null;
};

export const LeadKanban = ({ leads, onSelectLead, onMoveStage }) => {
  const columns = STAGES.map((stage) => ({
    ...stage,
    leads: leads.filter((l) => statusToStage(l.status) === stage.key),
  }));

  return (
    <div className="flex gap-4 overflow-x-auto pb-4" data-testid="lead-kanban-board">
      {columns.map((col) => (
        <div key={col.key} className="flex-shrink-0 w-72" data-testid={`kanban-column-${col.key}`}>
          <div className={`px-3 py-2 rounded-t-lg border ${col.headerClass} flex items-center justify-between`}>
            <span className="font-semibold text-sm">{col.label}</span>
            <span className="text-xs font-bold bg-white/70 px-2 py-0.5 rounded-full">{col.leads.length}</span>
          </div>
          <div className="bg-gray-50 border border-t-0 border-gray-200 rounded-b-lg p-2 space-y-2 min-h-[200px] max-h-[600px] overflow-y-auto">
            {col.leads.length === 0 && (
              <p className="text-xs text-gray-400 text-center py-6">No leads</p>
            )}
            {col.leads.map((lead) => {
              const team = lead._src ? { cls: lead._src === 'mail' ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700', label: lead._src === 'mail' ? 'Mail' : 'Quotation' } : getTeamBadge(lead.lead_type);
              return (
                <div
                  key={lead.id}
                  onClick={() => onSelectLead(lead)}
                  className="bg-white rounded-lg border border-gray-200 p-3 cursor-pointer hover:shadow-md hover:border-blue-300 transition-shadow"
                  data-testid={`kanban-lead-card-${lead.id}`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <span className="font-medium text-sm text-gray-900 truncate">{leadDisplayName(lead)}</span>
                    <TempBadge status={lead.status} />
                  </div>
                  <div className="mt-1.5 space-y-0.5">
                    {lead.phone && (
                      <div className="flex items-center gap-1 text-xs text-gray-600"><Phone className="w-3 h-3" />{lead.phone}</div>
                    )}
                    {lead.email && (
                      <div className="flex items-center gap-1 text-xs text-gray-600 truncate"><Mail className="w-3 h-3" />{lead.email}</div>
                    )}
                  </div>
                  {(lead.interested_products || []).length > 0 && (
                    <p className="mt-1 text-xs text-gray-500 truncate">🛒 {(lead.interested_products || []).join(', ')}</p>
                  )}
                  {!!(lead.quantity || lead.expected_value > 0) && (
                    <p className="mt-1 text-xs font-medium text-gray-700">
                      {lead.quantity ? `Qty ${lead.quantity}` : ''}{lead.quantity && lead.expected_value > 0 ? ' · ' : ''}{lead.expected_value > 0 ? `₹${Number(lead.expected_value).toLocaleString('en-IN')}` : ''}
                    </p>
                  )}
                  <div className="mt-2 flex items-center justify-between">
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${team.cls}`}>{team.label}</span>
                    <span className="text-[10px] text-gray-400">{timeAgo(lead.created_at)}</span>
                  </div>
                  <select
                    value={statusToStage(lead.status)}
                    onClick={(e) => e.stopPropagation()}
                    onChange={(e) => onMoveStage(lead.id, e.target.value)}
                    className="mt-2 w-full text-xs border border-gray-200 rounded px-1.5 py-1 text-gray-600 bg-gray-50"
                    data-testid={`kanban-stage-select-${lead.id}`}
                  >
                    {STAGES.map((s) => (
                      <option key={s.key} value={s.key}>{s.label}</option>
                    ))}
                  </select>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
};
