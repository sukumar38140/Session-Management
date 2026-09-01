import React, { useEffect, useState } from 'react';
import { BarChart3, TrendingUp, AlertTriangle, CheckCircle2, RefreshCw } from 'lucide-react';
import { getFrictionHeatmap, getSessionValueScore } from '../api';

export default function AnalyticsDashboard() {
  const [frictionMap, setFrictionMap] = useState(null);
  const [svsData, setSvsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const [fData, sData] = await Promise.all([
        getFrictionHeatmap(),
        getSessionValueScore()
      ]);
      setFrictionMap(fData);
      setSvsData(sData);
    } catch (err) {
      console.error("Failed to load analytics:", err);
      setError(err.message || "Failed to load dashboard metrics");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="glass-panel rounded-2xl p-12 text-center border border-slate-800 flex flex-col items-center justify-center">
        <div className="w-8 h-8 border-3 border-indigo-500 border-t-transparent rounded-full animate-spin mb-3"></div>
        <p className="text-xs text-slate-400">Loading friction telemetry & SVS performance metrics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-panel rounded-2xl p-8 text-center border border-red-500/30 bg-red-950/20">
        <AlertTriangle className="w-8 h-8 text-red-400 mx-auto mb-2" />
        <h4 className="text-sm font-bold text-red-300">Analytics Load Failed</h4>
        <p className="text-xs text-slate-400 mt-1">{error}</p>
        <button
          onClick={loadAnalytics}
          className="mt-4 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-semibold"
        >
          Retry Load
        </button>
      </div>
    );
  }

  const funnel = frictionMap?.funnel || [];
  const smartFunnel = frictionMap?.smart_funnel || [];
  const trend = svsData?.trend || [];

  return (
    <div className="glass-panel rounded-2xl p-6 shadow-2xl border border-slate-800 space-y-8">
      <div className="flex items-center justify-between pb-5 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-indigo-500/10 text-indigo-400 rounded-xl border border-indigo-500/20">
            <BarChart3 className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">Panel 4 — Friction & Session Value Analytics</h2>
            <p className="text-xs text-slate-400">In-session funnel drop-off heatmap & 30-day SVS trend comparison</p>
          </div>
        </div>

        <button
          onClick={loadAnalytics}
          className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-all"
          title="Refresh metrics"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Metric Highlights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="glass-card p-5 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400 font-medium">Standard App Avg SVS</span>
          <div className="text-2xl font-bold font-mono text-slate-300 mt-1">
            {svsData?.standard_avg_svs?.toFixed(2) || '0.42'}
          </div>
          <span className="text-[11px] text-slate-500">Fixed static ranking baseline</span>
        </div>

        <div className="glass-card p-5 rounded-xl border border-emerald-500/30 bg-emerald-950/20">
          <span className="text-xs text-emerald-400 font-medium">SmartSession Engine Avg SVS</span>
          <div className="text-2xl font-bold font-mono text-emerald-400 mt-1">
            {svsData?.smartsession_avg_svs?.toFixed(2) || '0.75'}
          </div>
          <span className="text-[11px] text-emerald-500/80 font-medium">+{svsData?.improvement_pct || '78.6'}% overall value lift</span>
        </div>

        <div className="glass-card p-5 rounded-xl border border-purple-500/30 bg-purple-950/20">
          <span className="text-xs text-purple-300 font-medium">Biggest Drop-Off Funnel Step</span>
          <div className="text-xl font-bold text-purple-400 uppercase font-mono mt-1">
            {frictionMap?.biggest_drop_off || 'content_detail'}
          </div>
          <span className="text-[11px] text-purple-300/80">SmartSession reduces drop-off from 60% → 22%</span>
        </div>
      </div>

      {/* Section 1: Friction Heatmap Funnel */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-indigo-400" />
            Session Funnel Drop-off Comparison
          </h3>
          <div className="flex items-center gap-4 text-xs font-medium">
            <span className="flex items-center gap-1.5 text-slate-400">
              <span className="w-3 h-3 rounded-sm bg-slate-600 inline-block"></span> Standard App
            </span>
            <span className="flex items-center gap-1.5 text-emerald-400">
              <span className="w-3 h-3 rounded-sm bg-emerald-500 inline-block"></span> SmartSession Adaptive
            </span>
          </div>
        </div>

        <div className="glass-card p-5 rounded-xl border border-slate-800 space-y-4">
          {funnel.map((item, idx) => {
            const smartStep = smartFunnel[idx] || item;
            const stdDropPct = (item.drop_off_rate * 100).toFixed(0);
            const smartDropPct = (smartStep.drop_off_rate * 100).toFixed(0);

            return (
              <div key={item.step} className="space-y-1.5">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-bold text-slate-200 capitalize font-mono">{idx + 1}. {item.step.replace(/_/g, ' ')}</span>
                  <div className="flex items-center gap-4 font-mono text-[11px]">
                    <span className="text-slate-400">Standard Drop: <strong className="text-slate-200">{stdDropPct}%</strong></span>
                    <span className="text-emerald-400">Smart Drop: <strong className="text-emerald-300">{smartDropPct}%</strong></span>
                  </div>
                </div>

                {/* Progress bars split */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="w-full bg-slate-900 h-3 rounded-full overflow-hidden border border-slate-800">
                    <div
                      className={`h-full rounded-full ${item.drop_off_rate > 0.5 ? 'bg-red-500' : item.drop_off_rate > 0.25 ? 'bg-amber-500' : 'bg-slate-500'}`}
                      style={{ width: `${Math.max(item.drop_off_rate * 100, 5)}%` }}
                    ></div>
                  </div>

                  <div className="w-full bg-slate-900 h-3 rounded-full overflow-hidden border border-slate-800">
                    <div
                      className="h-full bg-emerald-500 rounded-full transition-all duration-700"
                      style={{ width: `${Math.max(smartStep.drop_off_rate * 100, 5)}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Insight Box */}
        <div className="p-4 bg-indigo-950/30 border border-indigo-500/30 rounded-xl text-xs text-indigo-200 flex items-start gap-2.5">
          <CheckCircle2 className="w-4 h-4 text-indigo-400 mt-0.5 shrink-0" />
          <div>
            <strong className="text-indigo-300">Automated Friction Insight:</strong>
            <p className="mt-0.5">{frictionMap?.insight}</p>
          </div>
        </div>
      </div>

      {/* Section 2: 30-Day Session Value Score (SVS) Trend */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-emerald-400" />
          30-Day Session Value Score (SVS) Performance Trend
        </h3>

        <div className="glass-card p-6 rounded-xl border border-slate-800">
          {/* Custom SVG Line Chart */}
          <div className="w-full h-64 relative">
            <svg viewBox="0 0 800 240" className="w-full h-full overflow-visible">
              {/* Grid lines */}
              <line x1="40" y1="200" x2="780" y2="200" stroke="#334155" strokeWidth="1" strokeDasharray="4 4" />
              <line x1="40" y1="140" x2="780" y2="140" stroke="#334155" strokeWidth="1" strokeDasharray="4 4" />
              <line x1="40" y1="80" x2="780" y2="80" stroke="#334155" strokeWidth="1" strokeDasharray="4 4" />
              <line x1="40" y1="20" x2="780" y2="20" stroke="#334155" strokeWidth="1" strokeDasharray="4 4" />

              {/* Axis labels */}
              <text x="10" y="205" fill="#94a3b8" fontSize="10" fontFamily="monospace">0.0</text>
              <text x="10" y="145" fill="#94a3b8" fontSize="10" fontFamily="monospace">0.3</text>
              <text x="10" y="85" fill="#94a3b8" fontSize="10" fontFamily="monospace">0.6</text>
              <text x="10" y="25" fill="#94a3b8" fontSize="10" fontFamily="monospace">1.0</text>

              {/* Standard Line (Grey) */}
              <polyline
                fill="none"
                stroke="#64748b"
                strokeWidth="2.5"
                points={trend.map((t, idx) => {
                  const x = 40 + (idx * (740 / (trend.length - 1)));
                  const y = 200 - (t.standard * 180);
                  return `${x},${y}`;
                }).join(' ')}
              />

              {/* SmartSession Line (Emerald) */}
              <polyline
                fill="none"
                stroke="#10b981"
                strokeWidth="3.5"
                points={trend.map((t, idx) => {
                  const x = 40 + (idx * (740 / (trend.length - 1)));
                  const y = 200 - (t.smartsession * 180);
                  return `${x},${y}`;
                }).join(' ')}
              />
            </svg>
          </div>

          <div className="flex justify-between items-center text-xs text-slate-400 font-mono mt-3 pt-3 border-t border-slate-800">
            <span>Day 1</span>
            <span>Day 15</span>
            <span>Day 30</span>
          </div>
        </div>
      </div>
    </div>
  );
}
