"""
backend/synthetic_data.py
Generates 10,000 realistic session records for SmartSession Intent Classifier.
Strictly adheres to Master Data Schema, Rule-based labeling, Noise Injection, and SVS Formula.
"""

import os
import uuid
import random
import numpy as np
import pandas as pd

def generate_dataset(n_samples=10000, random_seed=42):
    np.random.seed(random_seed)
    random.seed(random_seed)
    
    # 1. User Pool (e.g., 2,500 distinct users assigned to cohorts)
    user_ids = [str(uuid.uuid4()) for _ in range(2500)]
    cohort_types = ['new', 'casual', 'regular', 'power']
    user_cohort_map = {uid: np.random.choice(cohort_types, p=[0.15, 0.40, 0.30, 0.15]) for uid in user_ids}
    
    entry_points = ['push', 'organic', 'widget']
    entry_probs = [0.35, 0.45, 0.20]
    
    network_types = ['wifi', 'cellular']
    network_probs = [0.60, 0.40]
    
    rows = []
    
    for _ in range(n_samples):
        session_id = str(uuid.uuid4())
        user_id = random.choice(user_ids)
        user_cohort = user_cohort_map[user_id]
        
        entry_point = str(np.random.choice(entry_points, p=entry_probs))
        network_type = str(np.random.choice(network_types, p=network_probs))
        
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
        
        session_gap_hours = round(float(np.random.lognormal(mean=2.5, sigma=1.2)), 1)
        session_gap_hours = float(min(max(session_gap_hours, 0.1), 168.0))
        
        previous_session_converted = bool(np.random.rand() < 0.35)
        regional_event_active = bool(np.random.rand() < 0.15)
        
        # Base Rule Evaluation for ACT vs BROWSE
        # ACT if 2+ of these conditions are true:
        cond1 = (entry_point == "push")
        cond2 = (18 <= time_of_day <= 23)
        cond3 = (is_weekend is False)
        cond4 = (previous_session_converted is True)
        cond5 = (regional_event_active is True)
        
        active_conditions_count = sum([cond1, cond2, cond3, cond4, cond5])
        is_act_rule = (cond1 and (cond2 or cond4 or cond5)) or (active_conditions_count >= 3)
        base_intent = 'act' if is_act_rule else 'browse'
        
        # Correlated behavioral features
        if base_intent == 'act':
            scroll_velocity = float(np.random.normal(loc=85.0, scale=30.0))
            first_tap_depth = int(np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.25, 0.45, 0.20, 0.05]))
            converted = bool(np.random.rand() < 0.82)
            dwell_seconds = float(np.random.uniform(30.0, 300.0))
            exploration_depth = int(np.random.randint(1, 6))
            returned_within_24h = bool(np.random.rand() < 0.72)
        else:
            scroll_velocity = float(np.random.normal(loc=310.0, scale=65.0))
            first_tap_depth = int(np.random.choice([1, 2, 3, 4, 5], p=[0.70, 0.20, 0.07, 0.02, 0.01]))
            converted = bool(np.random.rand() < 0.15)
            dwell_seconds = float(np.random.uniform(60.0, 550.0))
            exploration_depth = int(np.random.randint(4, 11))
            returned_within_24h = bool(np.random.rand() < 0.40)
            
        scroll_velocity = round(float(min(max(scroll_velocity, 0.0), 500.0)), 1)
        dwell_seconds = round(float(min(max(dwell_seconds, 0.0), 600.0)), 1)
        
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
            'user_cohort': user_cohort,
            'intent_label': base_intent,
            'converted': converted,
            'dwell_seconds': dwell_seconds,
            'exploration_depth': exploration_depth,
            'returned_within_24h': returned_within_24h
        })
        
    df = pd.DataFrame(rows)
    
    # Apply Noise Injection (8% random flip for realistic noise with high AUC)
    noise_mask = np.random.random(len(df)) < 0.08
    df.loc[noise_mask, 'intent_label'] = df.loc[noise_mask, 'intent_label'].map({'act': 'browse', 'browse': 'act'})
    
    # Calculate exact SVS score per row
    # SVS = (min(dwell_seconds/600, 1.0) * 0.3) + (min(exploration_depth/10, 1.0) * 0.2) + (float(converted) * 0.3) + (float(returned_within_24h) * 0.2)
    df['session_value_score'] = (
        (df['dwell_seconds'] / 600.0).clip(upper=1.0) * 0.3 +
        (df['exploration_depth'] / 10.0).clip(upper=1.0) * 0.2 +
        df['converted'].astype(float) * 0.3 +
        df['returned_within_24h'].astype(float) * 0.2
    ).round(4)
    
    return df

if __name__ == '__main__':
    df_sessions = generate_dataset(n_samples=10000, random_seed=42)
    
    out_dir = os.path.join('backend', 'data')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'sessions.csv')
    
    df_sessions.to_csv(out_path, index=False)
    
    print("=" * 60)
    print("SYNTHETIC DATASET GENERATION COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print(f"Output File  : {out_path}")
    print(f"Dataset Shape: {df_sessions.shape}")
    print("\n--- CLASS DISTRIBUTION ---")
    print(df_sessions['intent_label'].value_counts(normalize=True))
    print(df_sessions['intent_label'].value_counts())
    print("\n--- SVS MEAN BY INTENT LABEL ---")
    print(df_sessions.groupby('intent_label')['session_value_score'].mean())
    print("=" * 60)
