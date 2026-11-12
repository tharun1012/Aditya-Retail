import React, { useState, useEffect } from 'react';
import { Sparkles, CheckCircle2 } from 'lucide-react';
import { BACKEND_URL } from '../config/api';

export const AISummarySection = ({ productId }) => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!productId) return;
    let cancelled = false;
    setLoading(true);
    setSummary(null);
    fetch(`${BACKEND_URL}/api/products/${productId}/ai-summary`)
      .then(res => res.json())
      .then(data => {
        if (!cancelled && data.status === 'success' && data.ai_summary) {
          setSummary(data.ai_summary);
        }
      })
      .catch(err => console.error('AI summary error:', err))
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [productId]);

  if (!loading && !summary) return null;

  return (
    <div
      className="rounded-xl border border-violet-200 bg-gradient-to-br from-violet-50 via-white to-indigo-50 p-4 md:p-5"
      data-testid="ai-summary-section"
    >
      <div className="flex items-center gap-2 mb-3">
        <div className="p-1.5 rounded-lg bg-gradient-to-r from-violet-600 to-indigo-600">
          <Sparkles className="w-4 h-4 text-white" />
        </div>
        <h2 className="text-base md:text-lg font-bold text-gray-900">AI Summary</h2>
      </div>

      {loading ? (
        <div className="space-y-2 animate-pulse" data-testid="ai-summary-loading">
          <div className="h-3 bg-violet-100 rounded w-full"></div>
          <div className="h-3 bg-violet-100 rounded w-11/12"></div>
          <div className="h-3 bg-violet-100 rounded w-4/5"></div>
          <div className="h-3 bg-violet-100 rounded w-2/3"></div>
        </div>
      ) : (
        <>
          {summary.summary && (
            <p className="text-sm md:text-base text-gray-700 leading-relaxed mb-3" data-testid="ai-summary-text">
              {summary.summary}
            </p>
          )}
          {Array.isArray(summary.key_points) && summary.key_points.length > 0 && (
            <ul className="space-y-2" data-testid="ai-summary-points">
              {summary.key_points.map((point, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                  <CheckCircle2 className="w-4 h-4 text-violet-600 mt-0.5 flex-shrink-0" />
                  <span>{point}</span>
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </div>
  );
};

export default AISummarySection;
