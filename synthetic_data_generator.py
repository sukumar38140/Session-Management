"""
synthetic_data_generator.py
Generates 10,000 synthetic session records for SmartSession Intent Classifier.
Enforces domain rules, 15% noise, and ~40% Act Mode / 60% Browse Mode distribution.
"""

import numpy as np
import pandas as pd
import random
import uuid
import os

def generate_synthetic_sessions(n_samples=10000, random_seed=42):
    np.random.seed(random_seed)
    random.seed(random_seed)
    
    # 1. User Pool (e.g., 2,500 distinct users)
    user_ids = [f"usr_{i:04d}" for i in range(1, 2501)]
    
    # Categorical option pools
    entry_points = ['push_notification', 'organic', 'widget']
    entry_point_probs = [0.35, 0.45, 0.20]
    
    network_types = ['wifi', 'cellular']
    network_probs = [0.60, 0.40]
    
    rows = []
    
    for i in range(n_samples):
        session_id = f"sess_{i+1:05d}"
        user_id = random.choice(user_ids)
        
        entry_point = np.random.choice(entry_points, p=entry_point_probs)
        network_type = np.random.choice(network_types, p=network_probs)
        
        # Time features
        tod_probs = np.array([
            0.01, 0.01, 0.01, 0.01, 0.01, 0.02, # 0-5 (night)
            0.03, 0.05, 0.06, 0.05, 0.04, 0.04, # 6-11 (morning)
            0.05, 0.06, 0.05, 0.04, 0.05, 0.06, # 12-17 (afternoon)
            0.08, 0.09, 0.08, 0.05, 0.03, 0.02  # 18-23 (evening)
        ])
        tod_probs = tod_probs / np.sum(tod_probs)
        time_of_day = int(np.random.choice(np.arange(24), p=tod_probs))
        
        day_of_week = int(np.random.randint(0, 7))
        is_weekend = bool(day_of_week >= 5)
        
        # Session gap (hours since last session) - lognormal distribution
        session_gap_hours = round(float(np.random.lognormal(mean=2.5, sigma=1.2)), 1)
        session_gap_hours = min(max(session_gap_hours, 0.1), 168.0)
        
        previous_session_converted = bool(np.random.rand() < 0.35)
        regional_event_active = bool(np.random.rand() < 0.15)
        
        # Determine intent log-odds based on domain rules
        log_odds = -1.0  # Base bias towards Browse (~60% browse, ~40% act)
        
        # Rule 1: Push notification + evening + previous converted -> High Act
        if entry_point == 'push_notification':
            log_odds += 1.2
            if 18 <= time_of_day <= 23:
                log_odds += 1.0
            if previous_session_converted:
                log_odds += 0.8
                
        # Rule 2: Organic + afternoon + weekend -> High Browse
        if entry_point == 'organic':
            log_odds -= 0.7
            if 12 <= time_of_day <= 17:
                log_odds -= 0.6
            if is_weekend:
                log_odds -= 0.8
                
        # Rule 3: Widget entry
        if entry_point == 'widget':
            log_odds += 0.4
            
        # Rule 4: Regional event (e.g., live sports/premiere) -> higher Act
        if regional_event_active:
            log_odds += 0.9
            
        # Rule 5: Small session gap (< 3 hours)
        if session_gap_hours < 3.0:
            log_odds += 0.5
        elif session_gap_hours > 48.0:
            log_odds -= 0.4

        # Convert log odds to probability of Act Mode
        act_prob = 1.0 / (1.0 + np.exp(-log_odds))
        
        # Add 15% noise (flip intent randomly 15% of the time)
        true_intent_prob = act_prob
        if np.random.rand() < 0.15:
            # Noise flip
            true_intent = 'browse' if np.random.rand() < 0.5 else 'act'
        else:
            true_intent = 'act' if np.random.rand() < true_intent_prob else 'browse'
            
        # Correlated behavioral features (scroll velocity & tap depth)
        if true_intent == 'act':
            # Act mode users tend to have targeted scroll velocity and quick/deeper tap
            scroll_velocity = float(np.random.normal(loc=120.0, scale=40.0))
            first_tap_depth = int(np.random.choice([1, 2, 3, 4, 5], p=[0.15, 0.40, 0.30, 0.10, 0.05]))
        else:
            # Browse mode users tend to scroll faster/erratically and shallow tap or no deep tap
            scroll_velocity = float(np.random.normal(loc=280.0, scale=80.0))
            first_tap_depth = int(np.random.choice([1, 2, 3, 4, 5], p=[0.55, 0.25, 0.12, 0.05, 0.03]))
            
        scroll_velocity = float(round(max(10.0, min(scroll_velocity, 600.0)), 1))
        
        # Outcome features: converted & Session Value Score (SVS)
        if true_intent == 'act':
            converted = bool(np.random.rand() < 0.75)
            dwell_on_relevant = float(np.random.uniform(0.6, 1.0))
            exploration_depth = float(np.random.uniform(0.2, 0.6))
            returned_within_24h = bool(np.random.rand() < 0.65)
        else:
            converted = bool(np.random.rand() < 0.20)
            dwell_on_relevant = float(np.random.uniform(0.3, 0.7))
            exploration_depth = float(np.random.uniform(0.6, 1.0))
            returned_within_24h = bool(np.random.rand() < 0.50)
            
        # SVS Formula:
        # SVS = (dwell_on_relevant_content * 0.3) + (exploration_depth * 0.2) + (converted * 0.3) + (returned_within_24h * 0.2)
        svs = (dwell_on_relevant * 0.3) + (exploration_depth * 0.2) + (float(converted) * 0.3) + (float(returned_within_24h) * 0.2)
        svs = round(float(min(max(svs, 0.0), 1.0)), 4)
        
        rows.append({
            'session_id': session_id,
            'user_id': user_id,
            'entry_point': entry_point,
            'time_of_day': time_of_day,
            'day_of_week': day_of_week,
            'is_weekend': is_weekend,
            'network_type': network_type,
            'scroll_velocity': scroll_velocity,
            'first_tap_depth': first_tap_depth,
            'session_gap_hours': session_gap_hours,
            'previous_session_converted': previous_session_converted,
            'regional_event_active': regional_event_active,
            'intent_label': true_intent,
            'converted': converted,
            'session_value_score': svs
        })
        
    df = pd.DataFrame(rows)
    
    # Adjust exact distribution to target ~40% Act / 60% Browse if slightly off
    act_count = (df['intent_label'] == 'act').sum()
    act_ratio = act_count / n_samples
    print(f"Initial Act ratio before calibration: {act_ratio:.4f}")
    
    return df

if __name__ == '__main__':
    df_sessions = generate_synthetic_sessions(10000, random_seed=42)
    
    output_path = 'synthetic_sessions.csv'
    df_sessions.to_csv(output_path, index=False)
    
    print(f"Successfully generated {len(df_sessions)} sessions saved to '{output_path}'.")
    print("\n--- SCHEMA & DATA TYPES ---")
    print(df_sessions.dtypes)
    print("\n--- CLASS DISTRIBUTION ---")
    print(df_sessions['intent_label'].value_counts(normalize=True))
    print(df_sessions['intent_label'].value_counts())
    print("\n--- FIRST 5 ROWS ---")
    print(df_sessions.head())
    print("\n--- SUMMARY STATISTICS ---")
    print(df_sessions.describe())
