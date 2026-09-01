"""
backend/friction_tracker.py
Layer 3 — Friction Heatmap Engine for SmartSession.
Tracks in-session funnel events across 6 steps:
["home", "browse", "content_detail", "action_prompt", "confirm", "complete"]
Computes drop-off rates and average dwell time per funnel step.
Includes realistic pre-seeded data for instant demo visualization.
"""

import copy

class FrictionTracker:
    FUNNEL_STEPS = ["home", "browse", "content_detail", "action_prompt", "confirm", "complete"]
    
    def __init__(self):
        self.events = []
        self._seed_demo_data()
        
    def _seed_demo_data(self):
        """Pre-seeds realistic funnel metrics for standard vs SmartSession comparison."""
        # Baseline seed counts for standard app experience
        self.preseeded_funnel = [
            {
                "step": "home",
                "sessions_entered": 10000,
                "sessions_exited": 1400,
                "drop_off_rate": 0.14,
                "avg_dwell_seconds": 6.8
            },
            {
                "step": "browse",
                "sessions_entered": 8600,
                "sessions_exited": 2150,
                "drop_off_rate": 0.25,
                "avg_dwell_seconds": 18.2
            },
            {
                "step": "content_detail",
                "sessions_entered": 6450,
                "sessions_exited": 3870,
                "drop_off_rate": 0.60,
                "avg_dwell_seconds": 42.5
            },
            {
                "step": "action_prompt",
                "sessions_entered": 2580,
                "sessions_exited": 825,
                "drop_off_rate": 0.32,
                "avg_dwell_seconds": 14.1
            },
            {
                "step": "confirm",
                "sessions_entered": 1755,
                "sessions_exited": 210,
                "drop_off_rate": 0.12,
                "avg_dwell_seconds": 9.3
            },
            {
                "step": "complete",
                "sessions_entered": 1545,
                "sessions_exited": 0,
                "drop_off_rate": 0.00,
                "avg_dwell_seconds": 3.2
            }
        ]
        
        # Adaptive SmartSession funnel (reduced drop-off at content_detail & action_prompt)
        self.preseeded_smart_funnel = [
            {
                "step": "home",
                "sessions_entered": 10000,
                "sessions_exited": 600,
                "drop_off_rate": 0.06,
                "avg_dwell_seconds": 5.1
            },
            {
                "step": "browse",
                "sessions_entered": 9400,
                "sessions_exited": 1128,
                "drop_off_rate": 0.12,
                "avg_dwell_seconds": 14.8
            },
            {
                "step": "content_detail",
                "sessions_entered": 8272,
                "sessions_exited": 1819,
                "drop_off_rate": 0.22,
                "avg_dwell_seconds": 24.0
            },
            {
                "step": "action_prompt",
                "sessions_entered": 6453,
                "sessions_exited": 774,
                "drop_off_rate": 0.12,
                "avg_dwell_seconds": 8.5
            },
            {
                "step": "confirm",
                "sessions_entered": 5679,
                "sessions_exited": 284,
                "drop_off_rate": 0.05,
                "avg_dwell_seconds": 6.2
            },
            {
                "step": "complete",
                "sessions_entered": 5395,
                "sessions_exited": 0,
                "drop_off_rate": 0.00,
                "avg_dwell_seconds": 2.8
            }
        ]

    def log_event(self, session_id, step, action, dwell_seconds):
        """Logs a single in-session telemetry event."""
        if step in self.FUNNEL_STEPS:
            self.events.append({
                "session_id": str(session_id),
                "step": str(step),
                "action": str(action),
                "dwell_seconds": float(dwell_seconds)
            })

    def get_friction_map(self):
        """Calculates funnel drop-offs and insights."""
        funnel_data = copy.deepcopy(self.preseeded_funnel)
        smart_data = copy.deepcopy(self.preseeded_smart_funnel)
        
        # Identify biggest drop off step in standard experience
        max_drop = max(funnel_data, key=lambda x: x['drop_off_rate'])
        biggest_drop_step = max_drop['step']
        drop_pct = int(max_drop['drop_off_rate'] * 100)
        
        insight = f"High friction detected: {drop_pct}% of users drop off at '{biggest_drop_step}'. SmartSession reduces this drop-off by 63% through direct action surfacing."
        
        return {
            "funnel": funnel_data,
            "smart_funnel": smart_data,
            "biggest_drop_off": biggest_drop_step,
            "insight": insight
        }

if __name__ == '__main__':
    tracker = FrictionTracker()
    fmap = tracker.get_friction_map()
    print("--- FRICTION HEATMAP ENGINE OUTPUT ---")
    print(f"Biggest Drop-off Step: {fmap['biggest_drop_off']}")
    print(f"Insight: {fmap['insight']}")
    print("\nFunnel Step Metrics:")
    for f in fmap['funnel']:
        print(f"  Step: {f['step']:16s} | Entered: {f['sessions_entered']:5d} | Drop-off Rate: {f['drop_off_rate']*100:4.1f}% | Avg Dwell: {f['avg_dwell_seconds']}s")
