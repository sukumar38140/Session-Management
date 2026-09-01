import React from 'react';
import { Sliders, Zap, Compass, UserCheck, Smartphone, Clock, Calendar, Wifi, MousePointer, Layers, Repeat, Radio } from 'lucide-react';

export default function SessionSimulator({ features, setFeatures, onDetectIntent, loading }) {
  
  const handleChange = (field, value) => {
    setFeatures(prev => ({ ...prev, [field]: value }));
  };

  const applyPreset = (presetType) => {
    if (presetType === 'action_push') {
      setFeatures({
        entry_point: 'push',
        time_of_day: 20,
        day_of_week: 4,
        is_weekend: false,
        network_type: 'wifi',
        scroll_velocity: 85.0,
        first_tap_depth: 4,
        session_gap_hours: 1.5,
        previous_session_converted: true,
        regional_event_active: true,
        user_cohort: 'regular'
      });
    } else if (presetType === 'weekend_browse') {
      setFeatures({
        entry_point: 'organic',
        time_of_day: 14,
        day_of_week: 6,
        is_weekend: true,
        network_type: 'wifi',
        scroll_velocity: 320.0,
        first_tap_depth: 1,
        session_gap_hours: 36.0,
        previous_session_converted: false,
        regional_event_active: false,
        user_cohort: 'casual'
      });
    } else if (presetType === 'cold_start') {
      setFeatures({
        entry_point: 'organic',
        time_of_day: 11,
        day_of_week: 2,
        is_weekend: false,
        network_type: 'cellular',
        scroll_velocity: 240.0,
        first_tap_depth: 1,
        session_gap_hours: 0.0,
        previous_session_converted: false,
        regional_event_active: false,
        user_cohort: 'new'
      });
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 shadow-2xl border border-slate-800">
      <div className="flex items-center justify-between pb-5 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-indigo-500/10 text-indigo-400 rounded-xl border border-indigo-500/20">
            <Sliders className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">Panel 1 — Session Simulator</h2>
            <p className="text-xs text-slate-400">Configure real-time context telemetry within the first 30s</p>
          </div>
        </div>

        {/* Preset quick buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => applyPreset('action_push')}
            className="text-xs px-3 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/20 transition-all flex items-center gap-1.5"
          >
            <Zap className="w-3.5 h-3.5" /> Action Push
          </button>
          <button
            onClick={() => applyPreset('weekend_browse')}
            className="text-xs px-3 py-1.5 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/30 hover:bg-indigo-500/20 transition-all flex items-center gap-1.5"
          >
            <Compass className="w-3.5 h-3.5" /> Weekend Browse
          </button>
          <button
            onClick={() => applyPreset('cold_start')}
            className="text-xs px-3 py-1.5 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/30 hover:bg-amber-500/20 transition-all flex items-center gap-1.5"
          >
            <UserCheck className="w-3.5 h-3.5" /> New User Cold Start
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 mt-6">
        {/* Entry Point */}
        <div className="glass-card p-4 rounded-xl">
          <label className="text-xs font-semibold text-slate-300 mb-2 flex items-center gap-1.5">
            <Smartphone className="w-3.5 h-3.5 text-indigo-400" /> Entry Point
          </label>
          <select
            value={features.entry_point}
            onChange={(e) => handleChange('entry_point', e.target.value)}
            className="w-full bg-slate-900 text-white text-sm rounded-lg p-2.5 border border-slate-700 focus:border-indigo-500 focus:outline-none"
          >
            <option value="push">push_notification</option>
            <option value="organic">organic_app_launch</option>
            <option value="widget">home_screen_widget</option>
          </select>
        </div>

        {/* User Cohort */}
        <div className="glass-card p-4 rounded-xl">
          <label className="text-xs font-semibold text-slate-300 mb-2 flex items-center gap-1.5">
            <UserCheck className="w-3.5 h-3.5 text-indigo-400" /> User Cohort
          </label>
          <select
            value={features.user_cohort}
            onChange={(e) => handleChange('user_cohort', e.target.value)}
            className="w-full bg-slate-900 text-white text-sm rounded-lg p-2.5 border border-slate-700 focus:border-indigo-500 focus:outline-none"
          >
            <option value="regular">regular (Full ML model)</option>
            <option value="casual">casual (Full ML model)</option>
            <option value="power">power (Full ML model)</option>
            <option value="new">new (Cold Start Prior: 0.35)</option>
          </select>
        </div>

        {/* Network Type */}
        <div className="glass-card p-4 rounded-xl">
          <label className="text-xs font-semibold text-slate-300 mb-2 flex items-center gap-1.5">
            <Wifi className="w-3.5 h-3.5 text-indigo-400" /> Network Type
          </label>
          <select
            value={features.network_type}
            onChange={(e) => handleChange('network_type', e.target.value)}
            className="w-full bg-slate-900 text-white text-sm rounded-lg p-2.5 border border-slate-700 focus:border-indigo-500 focus:outline-none"
          >
            <option value="wifi">wifi</option>
            <option value="cellular">cellular</option>
          </select>
        </div>

        {/* Time of Day */}
        <div className="glass-card p-4 rounded-xl">
          <div className="flex justify-between items-center mb-2">
            <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-indigo-400" /> Time of Day
            </label>
            <span className="text-xs font-mono font-bold text-indigo-400">{features.time_of_day}:00 ({features.time_of_day >= 18 ? 'Evening' : features.time_of_day >= 12 ? 'Afternoon' : 'Morning'})</span>
          </div>
          <input
            type="range"
            min="0"
            max="23"
            value={features.time_of_day}
            onChange={(e) => handleChange('time_of_day', parseInt(e.target.value))}
            className="w-full accent-indigo-500 bg-slate-800 rounded-lg cursor-pointer"
          />
        </div>

        {/* Scroll Velocity */}
        <div className="glass-card p-4 rounded-xl">
          <div className="flex justify-between items-center mb-2">
            <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
              <MousePointer className="w-3.5 h-3.5 text-indigo-400" /> Scroll Velocity
            </label>
            <span className="text-xs font-mono font-bold text-indigo-400">{features.scroll_velocity} px/sec</span>
          </div>
          <input
            type="range"
            min="10"
            max="500"
            step="5"
            value={features.scroll_velocity}
            onChange={(e) => handleChange('scroll_velocity', parseFloat(e.target.value))}
            className="w-full accent-indigo-500 bg-slate-800 rounded-lg cursor-pointer"
          />
        </div>

        {/* First Tap Depth */}
        <div className="glass-card p-4 rounded-xl">
          <div className="flex justify-between items-center mb-2">
            <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-indigo-400" /> First Tap Depth
            </label>
            <span className="text-xs font-mono font-bold text-indigo-400">Level {features.first_tap_depth}</span>
          </div>
          <input
            type="range"
            min="1"
            max="5"
            value={features.first_tap_depth}
            onChange={(e) => handleChange('first_tap_depth', parseInt(e.target.value))}
            className="w-full accent-indigo-500 bg-slate-800 rounded-lg cursor-pointer"
          />
        </div>

        {/* Session Gap Hours */}
        <div className="glass-card p-4 rounded-xl col-span-1 md:col-span-2 lg:col-span-1">
          <div className="flex justify-between items-center mb-2">
            <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
              <Repeat className="w-3.5 h-3.5 text-indigo-400" /> Session Gap
            </label>
            <span className="text-xs font-mono font-bold text-indigo-400">{features.session_gap_hours} hrs</span>
          </div>
          <input
            type="range"
            min="0"
            max="168"
            step="0.5"
            value={features.session_gap_hours}
            onChange={(e) => handleChange('session_gap_hours', parseFloat(e.target.value))}
            className="w-full accent-indigo-500 bg-slate-800 rounded-lg cursor-pointer"
          />
        </div>

        {/* Boolean Toggles */}
        <div className="glass-card p-4 rounded-xl col-span-1 md:col-span-2 lg:col-span-2 flex flex-wrap items-center justify-between gap-4">
          <label className="flex items-center gap-2 text-xs font-medium cursor-pointer text-slate-300 hover:text-white">
            <input
              type="checkbox"
              checked={features.is_weekend}
              onChange={(e) => handleChange('is_weekend', e.target.checked)}
              className="rounded accent-indigo-500 w-4 h-4"
            />
            <span>Is Weekend</span>
          </label>

          <label className="flex items-center gap-2 text-xs font-medium cursor-pointer text-slate-300 hover:text-white">
            <input
              type="checkbox"
              checked={features.previous_session_converted}
              onChange={(e) => handleChange('previous_session_converted', e.target.checked)}
              className="rounded accent-indigo-500 w-4 h-4"
            />
            <span>Previous Converted</span>
          </label>

          <label className="flex items-center gap-2 text-xs font-medium cursor-pointer text-slate-300 hover:text-white">
            <input
              type="checkbox"
              checked={features.regional_event_active}
              onChange={(e) => handleChange('regional_event_active', e.target.checked)}
              className="rounded accent-indigo-500 w-4 h-4"
            />
            <span className="flex items-center gap-1 text-emerald-400">
              <Radio className="w-3.5 h-3.5 animate-pulse" /> Live Regional Event
            </span>
          </label>
        </div>
      </div>

      {/* Submit button */}
      <div className="mt-6 flex justify-end">
        <button
          onClick={onDetectIntent}
          disabled={loading}
          className="w-full md:w-auto px-8 py-3.5 bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-500 hover:from-indigo-600 hover:to-emerald-600 text-white font-bold rounded-xl shadow-lg shadow-indigo-500/25 transition-all flex items-center justify-center gap-2 text-sm disabled:opacity-50"
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Analyzing Intent...</span>
            </>
          ) : (
            <>
              <Zap className="w-4 h-4 fill-current" />
              <span>Detect Session Intent</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
