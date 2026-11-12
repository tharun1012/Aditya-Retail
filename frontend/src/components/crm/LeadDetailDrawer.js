import React, { useState } from 'react';
import {
  X, Phone, Mail, MessageSquare, Trash2, UserPlus, CalendarPlus, StickyNote,
} from 'lucide-react';
import { STAGES, statusToStage, getStatusColor, getTeamBadge, leadDisplayName, timeAgo, safeText } from './leadUtils';

export const LeadDetailDrawer = ({ lead, onClose, onUpdate, onDelete }) => {
  const [note, setNote] = useState('');
  const [assignee, setAssignee] = useState(lead.assigned_to || '');
  const [followUp, setFollowUp] = useState({ date: '', action: '' });
  const [saving, setSaving] = useState(false);

  if (!lead) return null;
  const team = getTeamBadge(lead.lead_type);

  const doUpdate = async (payload) => {
    setSaving(true);
    await onUpdate(lead.id, payload);
    setSaving(false);
  };

  const handleAddNote = async () => {
    if (!note.trim()) return;
    await doUpdate({ notes: note.trim() });
    setNote('');
  };

  const handleAssign = async () => {
    if (!assignee.trim()) return;
    await doUpdate({ assigned_to: assignee.trim() });
  };

  const handleFollowUp = async () => {
    if (!followUp.date || !followUp.action.trim()) return;
    await onUpdate(lead.id, null, {
      lead_id: lead.id,
      follow_up_date: followUp.date,
      action: followUp.action.trim(),
      assigned_to: assignee || null,
    });
    setFollowUp({ date: '', action: '' });
  };

  return (
    <div className="fixed inset-0 z-50 flex" data-testid="lead-detail-drawer">
      <div className="flex-1 bg-black/40" onClick={onClose} />
      <div className="w-full max-w-lg bg-white h-full overflow-y-auto shadow-2xl">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-start justify-between z-10">
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h2 className="text-xl font-bold text-gray-900">{leadDisplayName(lead)}</h2>
              <span className={`px-2 py-0.5 rounded text-xs font-semibold ${team.cls}`}>{team.label}</span>
              <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${getStatusColor(lead.status)}`}>{lead.status}</span>
            </div>
            <p className="text-xs text-gray-500 mt-1">{lead.id} · {timeAgo(lead.created_at)}</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              style={onDelete ? undefined : { display: 'none' }}
              onClick={() => onDelete && onDelete(lead.id)}
              className="p-2 text-red-500 hover:bg-red-50 rounded-lg"
              title="Delete lead"
              data-testid="lead-delete-btn"
            >
              <Trash2 className="w-4 h-4" />
            </button>
            <button onClick={onClose} className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg" data-testid="lead-drawer-close-btn">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="px-6 py-4 space-y-5">
          {/* Contact actions */}
          <div className="flex gap-2">
            {lead.phone && (
              <a href={`tel:${lead.phone}`} className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700" data-testid="lead-call-btn">
                <Phone className="w-4 h-4" /> Call {lead.phone}
              </a>
            )}
            {lead.email && (
              <a href={`mailto:${lead.email}`} className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700" data-testid="lead-email-btn">
                <Mail className="w-4 h-4" /> Email
              </a>
            )}
            {!lead.phone && !lead.email && (
              <p className="text-sm text-gray-500 italic">No contact info captured yet</p>
            )}
          </div>

          {/* Pipeline stage */}
          <div>
            <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">Pipeline Stage</h3>
            <div className="flex flex-wrap gap-1.5">
              {STAGES.map((s) => (
                <button
                  key={s.key}
                  disabled={saving}
                  onClick={() => doUpdate({ status: s.key })}
                  className={`px-3 py-1.5 rounded-full text-xs font-semibold border transition-colors ${
                    statusToStage(lead.status) === s.key
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'bg-white text-gray-600 border-gray-300 hover:border-blue-400'
                  }`}
                  data-testid={`lead-stage-btn-${s.key}`}
                >
                  {s.label}
                </button>
              ))}
            </div>
          </div>

          {/* Details grid */}
          <div>
            <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">Details</h3>
            <div className="bg-gray-50 rounded-lg p-4 grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
              <span className="text-gray-500">Source</span>
              <span className="text-gray-900 font-medium capitalize">{(lead.source || 'unknown').replace(/_/g, ' ')}</span>
              <span className="text-gray-500">Score</span>
              <span className="text-gray-900 font-medium">{lead.score ?? '—'}</span>
              <span className="text-gray-500">Budget</span>
              <span className="text-gray-900 font-medium">{safeText(lead.budget_range || lead.budget) || '—'}</span>
              <span className="text-gray-500">Brand / Model</span>
              <span className="text-gray-900 font-medium">{[lead.product_brand, lead.product_model].filter(Boolean).map(safeText).join(' / ') || '—'}</span>
              <span className="text-gray-500">Interested In</span>
              <span className="text-gray-900 font-medium">{(lead.interested_products || []).map(safeText).join(', ') || safeText(lead.interested_in) || '—'}</span>
              <span className="text-gray-500">Assigned To</span>
              <span className="text-gray-900 font-medium">{lead.assigned_to || 'Unassigned'}</span>
            </div>
          </div>

          {/* Notes / AI summary */}
          {(lead.notes || lead.ai_agent_interaction) && (
            <div>
              <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">AI Summary / Notes</h3>
              <div className="bg-amber-50 border border-amber-100 rounded-lg p-3 text-sm text-gray-800 space-y-1">
                {lead.notes && <p>{lead.notes}</p>}
                {lead.ai_agent_interaction && <p className="text-xs text-gray-600">{lead.ai_agent_interaction}</p>}
              </div>
            </div>
          )}

          {/* Conversation */}
          {lead.conversation_excerpt && (
            <div>
              <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2 flex items-center gap-1">
                <MessageSquare className="w-3.5 h-3.5" /> Conversation Transcript
              </h3>
              <pre className="bg-gray-900 text-gray-100 rounded-lg p-3 text-xs whitespace-pre-wrap max-h-64 overflow-y-auto" data-testid="lead-conversation-excerpt">
                {lead.conversation_excerpt}
              </pre>
            </div>
          )}

          {/* Assign */}
          <div>
            <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2 flex items-center gap-1">
              <UserPlus className="w-3.5 h-3.5" /> Assign To Team Member
            </h3>
            <div className="flex gap-2">
              <input
                value={assignee}
                onChange={(e) => setAssignee(e.target.value)}
                placeholder="e.g., Ramesh"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm"
                data-testid="lead-assignee-input"
              />
              <button onClick={handleAssign} disabled={saving} className="px-4 py-2 bg-gray-900 text-white rounded-lg text-sm font-medium hover:bg-gray-700" data-testid="lead-assign-btn">
                Assign
              </button>
            </div>
          </div>

          {/* Add note */}
          <div>
            <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2 flex items-center gap-1">
              <StickyNote className="w-3.5 h-3.5" /> Add Note
            </h3>
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              rows={2}
              placeholder="Called customer, will confirm tomorrow..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              data-testid="lead-note-input"
            />
            <button onClick={handleAddNote} disabled={saving || !note.trim()} className="mt-1 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50" data-testid="lead-add-note-btn">
              Save Note
            </button>
          </div>

          {/* Schedule follow-up */}
          <div>
            <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2 flex items-center gap-1">
              <CalendarPlus className="w-3.5 h-3.5" /> Schedule Follow-up
            </h3>
            <div className="flex gap-2">
              <input
                type="date"
                value={followUp.date}
                onChange={(e) => setFollowUp({ ...followUp, date: e.target.value })}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                data-testid="lead-followup-date-input"
              />
              <input
                value={followUp.action}
                onChange={(e) => setFollowUp({ ...followUp, action: e.target.value })}
                placeholder="Action (e.g., Call back)"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm"
                data-testid="lead-followup-action-input"
              />
              <button onClick={handleFollowUp} disabled={saving || !followUp.date || !followUp.action.trim()} className="px-3 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50" data-testid="lead-add-followup-btn">
                Add
              </button>
            </div>
            {(lead.follow_ups || []).length > 0 && (
              <div className="mt-2 space-y-1.5">
                {(lead.follow_ups || []).slice().reverse().map((f, i) => (
                  <div key={f.id || i} className="flex items-center justify-between bg-indigo-50 rounded px-3 py-1.5 text-xs">
                    <span className="font-medium text-indigo-900">{safeText(f.action)}</span>
                    <span className="text-indigo-600">{safeText(f.date)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Activity log */}
          {(lead.interactions || []).length > 0 && (
            <div>
              <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">Activity Log</h3>
              <div className="space-y-1.5 max-h-48 overflow-y-auto">
                {(lead.interactions || []).slice().reverse().map((it, i) => (
                  <div key={i} className="bg-gray-50 rounded px-3 py-2 text-xs">
                    <div className="flex items-center justify-between text-gray-500">
                      <span className="font-semibold capitalize">{safeText(it.type) || 'note'} · {safeText(it.agent)}</span>
                      <span>{timeAgo(typeof it.timestamp === 'string' ? it.timestamp : '')}</span>
                    </div>
                    <p className="text-gray-800 mt-0.5">{safeText(it.content || it.message)}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
