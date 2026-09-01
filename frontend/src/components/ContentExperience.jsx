import React from 'react';
import { LayoutGrid, ArrowRight, Zap, Compass, CheckCircle, ShieldCheck, Sparkles } from 'lucide-react';

export default function ContentExperience({ rankingResult, intentLabel }) {
  if (!rankingResult) {
    return (
      <div className="glass-panel rounded-2xl p-10 text-center border border-slate-800 flex flex-col items-center justify-center">
        <LayoutGrid className="w-12 h-12 text-slate-600 mb-3 animate-pulse-slow" />
        <h3 className="text-base font-semibold text-slate-400">No Content Ranking Calculated</h3>
        <p className="text-xs text-slate-500 max-w-sm mt-1">Run an intent prediction in Panel 1 to view the side-by-side split-screen comparison between Standard and SmartSession layouts.</p>
      </div>
    );
  }

  const { standard_ranking = [], smart_ranking = [], diff_score = 0.0 } = rankingResult;
  const isAct = intentLabel === 'act';

  return (
    <div className="glass-panel rounded-2xl p-6 shadow-2xl border border-slate-800">
      <div className="flex items-center justify-between pb-5 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-indigo-500/10 text-indigo-400 rounded-xl border border-indigo-500/20">
            <LayoutGrid className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">Panel 3 — Content Experience Comparison</h2>
            <p className="text-xs text-slate-400">Split-screen live demo: Standard Static Layout vs SmartSession Adaptive Layout</p>
          </div>
        </div>

        {/* Diff Score Badge */}
        <div className="flex items-center gap-2 px-3.5 py-1.5 bg-purple-500/10 border border-purple-500/30 rounded-xl">
          <Sparkles className="w-4 h-4 text-purple-400" />
          <span className="text-xs text-purple-300 font-medium">Layout Shift (Kendall Tau):</span>
          <span className="text-xs font-mono font-extrabold text-white">{(diff_score * 100).toFixed(1)}%</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        {/* Left Column: Standard Experience */}
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 bg-slate-900/80 rounded-xl border border-slate-800">
            <div className="flex items-center gap-2 text-slate-300 font-bold text-sm">
              <div className="w-2.5 h-2.5 rounded-full bg-slate-500"></div>
              <span>Standard Experience (Static Fixed Order)</span>
            </div>
            <span className="text-xs text-slate-500 font-mono">Unadapted</span>
          </div>

          <div className="space-y-3">
            {standard_ranking.map((item, idx) => (
              <div key={item.content_id} className="p-4 glass-card rounded-xl opacity-75 hover:opacity-100 transition-all border border-slate-800">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{item.thumbnail || '🎬'}</span>
                    <div>
                      <h4 className="text-sm font-bold text-white">{item.title}</h4>
                      <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">{item.category}</span>
                    </div>
                  </div>
                  <span className="text-xs font-mono text-slate-500">Rank #{idx + 1}</span>
                </div>
                <p className="text-xs text-slate-400 mt-2">{item.description}</p>
                <div className="mt-3 flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800/60">
                  <span>Relevance: {(item.relevance_score * 100).toFixed(0)}%</span>
                  <span>Steps to action: {item.tap_to_action}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: SmartSession Experience */}
        <div className="space-y-4">
          <div className={`flex items-center justify-between p-3 rounded-xl border ${isAct ? 'bg-emerald-950/40 border-emerald-500/30' : 'bg-indigo-950/40 border-indigo-500/30'}`}>
            <div className="flex items-center gap-2 font-bold text-sm">
              <div className={`w-2.5 h-2.5 rounded-full ${isAct ? 'bg-emerald-400 animate-pulse' : 'bg-indigo-400 animate-pulse'}`}></div>
              <span className={isAct ? 'text-emerald-300' : 'text-indigo-300'}>
                SmartSession {isAct ? 'Act-Mode' : 'Browse-Mode'} Adaptive Layout
              </span>
            </div>
            <span className={`text-xs px-2.5 py-0.5 rounded-md font-bold uppercase ${isAct ? 'bg-emerald-500/20 text-emerald-300' : 'bg-indigo-500/20 text-indigo-300'}`}>
              Zero Dark Patterns
            </span>
          </div>

          <div className="space-y-3">
            {smart_ranking.map((item, idx) => (
              <div
                key={item.content_id}
                className={`p-4 rounded-xl border transition-all duration-300 ${
                  idx === 0
                    ? (isAct ? 'bg-gradient-to-r from-emerald-950/50 to-slate-900 border-emerald-500/50 shadow-lg shadow-emerald-500/10' : 'bg-gradient-to-r from-indigo-950/50 to-slate-900 border-indigo-500/50 shadow-lg shadow-indigo-500/10')
                    : 'glass-card border-slate-800'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{item.thumbnail || '🎬'}</span>
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="text-sm font-bold text-white">{item.title}</h4>
                        {idx === 0 && (
                          <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${isAct ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30'}`}>
                            {isAct ? '⚡ Primary Action' : '⭐ Top Discovery'}
                          </span>
                        )}
                      </div>
                      <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">{item.category}</span>
                    </div>
                  </div>
                  <span className={`text-xs font-mono font-bold px-2 py-1 rounded-md ${idx === 0 ? 'bg-indigo-500/20 text-indigo-300' : 'text-slate-400 bg-slate-900'}`}>
                    Rank #{idx + 1}
                  </span>
                </div>

                <p className="text-xs text-slate-300 mt-2">{item.description}</p>

                {/* Adaptive Action / Discovery Bar */}
                <div className="mt-3 pt-3 border-t border-slate-800 flex items-center justify-between">
                  <div className="text-xs text-emerald-400 font-medium flex items-center gap-1">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>{item.rank_reason}</span>
                  </div>

                  {isAct ? (
                    <button className="px-3 py-1.5 bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold rounded-lg text-xs flex items-center gap-1 shadow-md shadow-emerald-500/20 transition-all">
                      <span>Launch Now</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  ) : (
                    <button className="px-3 py-1.5 bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-300 border border-indigo-500/40 font-bold rounded-lg text-xs flex items-center gap-1 transition-all">
                      <span>Explore Media</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
