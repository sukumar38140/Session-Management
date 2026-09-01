import React from 'react';
import { Brain, Zap, Compass, CheckCircle2, AlertCircle, Info, ArrowUpRight, ArrowDownRight } from 'lucide-react';

export default function IntentResult({ result }) {
  if (!result) {
    return (
      <div className="glass-panel rounded-2xl p-10 text-center border border-slate-800 flex flex-col items-center justify-center">
        <Brain className="w-12 h-12 text-slate-600 mb-3 animate-pulse-slow" />
        <h3 className="text-base font-semibold text-slate-400">No Intent Prediction Yet</h3>
        <p className="text-xs text-slate-500 max-w-sm mt-1">Configure session parameters in Panel 1 and click "Detect Session Intent" to see real-time predictions and SHAP explainability.</p>
      </div>
    );
  }

  const isAct = result.intent_label === 'act';
  const confidence = result.confidence || 90.0;
  const score = result.intent_score || 0.85;

  return (
    <div className={`glass-panel rounded-2xl p-6 shadow-2xl border transition-all duration-500 ${isAct ? 'border-emerald-500/30 glow-emerald' : 'border-indigo-500/30 glow-indigo'}`}>
      <div className="flex items-center justify-between pb-5 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className={`p-2.5 rounded-xl border ${isAct ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20'}`}>
            {isAct ? <Zap className="w-5 h-5" /> : <Compass className="w-5 h-5" />}
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">Panel 2 — Intent Prediction & SHAP Explainability</h2>
            <p className="text-xs text-slate-400">Classified within first 30 seconds of session</p>
          </div>
        </div>

        {/* Intent Badge */}
        <div className={`px-4 py-2 rounded-xl text-sm font-extrabold flex items-center gap-2 border shadow-lg ${isAct ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50' : 'bg-indigo-500/20 text-indigo-400 border-indigo-500/50'}`}>
          {isAct ? (
            <>
              <Zap className="w-4 h-4 fill-current animate-bounce" />
              <span>ACT MODE</span>
            </>
          ) : (
            <>
              <Compass className="w-4 h-4 animate-spin-slow" />
              <span>BROWSE MODE</span>
            </>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
        {/* Confidence & Score Metrics */}
        <div className="glass-card p-5 rounded-xl space-y-4">
          <div>
            <div className="flex justify-between items-center text-xs font-semibold mb-1">
              <span className="text-slate-400">Model Confidence</span>
              <span className="text-white font-mono">{confidence}%</span>
            </div>
            <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-1000 ${isAct ? 'bg-emerald-500' : 'bg-indigo-500'}`}
                style={{ width: `${confidence}%` }}
              ></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center text-xs font-semibold mb-1">
              <span className="text-slate-400">Intent Score (Probability of Act)</span>
              <span className="text-white font-mono">{score}</span>
            </div>
            <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-indigo-500 to-emerald-500 rounded-full transition-all duration-1000"
                style={{ width: `${score * 100}%` }}
              ></div>
            </div>
          </div>

          <div className="p-3 bg-slate-900/80 rounded-lg border border-slate-800 text-xs text-slate-300">
            <div className="font-semibold text-slate-200 mb-0.5">Adaptation Strategy:</div>
            {isAct ? (
              <span className="text-emerald-400">Surface primary action items immediately. Reduce steps to conversion.</span>
            ) : (
              <span className="text-indigo-400">Surplace rich discovery feed with depth filters and immersive content previews.</span>
            )}
          </div>
        </div>

        {/* Top 3 SHAP Drivers */}
        <div className="glass-card p-5 rounded-xl md:col-span-2 space-y-3">
          <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
            <Info className="w-3.5 h-3.5 text-indigo-400" /> Top 3 SHAP Feature Drivers
          </h4>

          <div className="space-y-2.5">
            {result.explanation && result.explanation.map((item, idx) => (
              <div key={idx} className="p-3 bg-slate-900/60 rounded-xl border border-slate-800/80 flex items-start gap-3 hover:border-slate-700 transition-all">
                <div className={`p-1.5 rounded-lg mt-0.5 ${item.direction === 'toward_act' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-indigo-500/10 text-indigo-400'}`}>
                  {item.direction === 'toward_act' ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between text-xs mb-0.5">
                    <span className="font-bold text-white capitalize">{item.feature.replace(/_/g, ' ')}</span>
                    <span className="font-mono text-indigo-400 font-bold">{item.weight_pct ? `${item.weight_pct}% weight` : item.impact}</span>
                  </div>
                  <p className="text-xs text-slate-300">{item.plain_english}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Full Plain English Summary Box */}
      <div className="mt-5 p-4 bg-slate-900/90 rounded-xl border border-slate-800">
        <div className="flex items-center gap-2 text-xs font-bold text-indigo-400 mb-1">
          <Brain className="w-3.5 h-3.5" /> Plain-English SHAP Summary
        </div>
        <p className="text-xs text-slate-200 leading-relaxed font-mono">
          "{result.summary}"
        </p>
      </div>
    </div>
  );
}
