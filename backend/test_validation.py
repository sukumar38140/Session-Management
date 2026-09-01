"""
backend/test_validation.py
Comprehensive End-to-End Validation Suite for SmartSession Engine.
Tests Data Generation, Model Metrics, SHAP Explainer, Cold Start Handling,
Content Ranking, Friction Heatmap, SVS Calculation, and FastAPI Endpoints.
"""

import os
import json
import pandas as pd
import numpy as np
from fastapi.testclient import TestClient

from backend.main import app
from backend.explainer import IntentExplainer
from backend.content_ranker import rank_content, DEFAULT_CONTENT_POOL
from backend.friction_tracker import FrictionTracker
from backend.session_value_score import calculate_svs, generate_svs_trend

def validate_all():
    print("=" * 70)
    print("SMARTSESSION SYSTEM END-TO-END VALIDATION SUITE")
    print("=" * 70)
    
    passed_tests = 0
    total_tests = 0

    # -------------------------------------------------------------
    # Test 1: Synthetic Dataset Schema & Class Distribution
    # -------------------------------------------------------------
    total_tests += 1
    print("\n[TEST 1] Synthetic Dataset Schema & Distribution...")
    csv_path = os.path.join('backend', 'data', 'sessions.csv')
    assert os.path.exists(csv_path), f"Dataset missing at {csv_path}"
    df = pd.read_csv(csv_path)
    
    assert len(df) == 10000, f"Expected 10,000 rows, got {len(df)}"
    required_cols = [
        'session_id', 'user_id', 'entry_point', 'time_of_day', 'day_of_week',
        'is_weekend', 'network_type', 'scroll_velocity', 'first_tap_depth',
        'session_gap_hours', 'previous_session_converted', 'regional_event_active',
        'user_cohort', 'intent_label', 'converted', 'dwell_seconds',
        'exploration_depth', 'returned_within_24h', 'session_value_score'
    ]
    for col in required_cols:
        assert col in df.columns, f"Missing column: {col}"
        
    counts = df['intent_label'].value_counts(normalize=True)
    print(f"  Rows: {len(df)} | Columns: {len(df.columns)}")
    print(f"  Distribution: Browse={counts.get('browse', 0):.2%}, Act={counts.get('act', 0):.2%}")
    print("  --> PASSED")
    passed_tests += 1

    # -------------------------------------------------------------
    # Test 2: Trained LightGBM Model & Success Criteria
    # -------------------------------------------------------------
    total_tests += 1
    print("\n[TEST 2] Model Evaluation Metrics & Artifacts...")
    meta_path = os.path.join('backend', 'models', 'metadata.json')
    assert os.path.exists(meta_path), "Model metadata missing"
    with open(meta_path, 'r') as f:
        meta = json.load(f)
        
    metrics = meta['metrics']
    acc = metrics['accuracy']
    f1 = metrics['f1_weighted']
    auc = metrics['auc_roc']
    
    print(f"  Accuracy : {acc:.4f} (Target >= 0.82)")
    print(f"  F1-Score : {f1:.4f} (Target >= 0.80)")
    print(f"  AUC-ROC  : {auc:.4f} (Target >= 0.88)")
    
    assert acc >= 0.82, f"Accuracy {acc} below target"
    assert f1 >= 0.80, f"F1 {f1} below target"
    assert auc >= 0.88, f"AUC {auc} below target"
    print("  --> PASSED")
    passed_tests += 1

    # -------------------------------------------------------------
    # Test 3: SHAP Explainer & Cold Start Handling
    # -------------------------------------------------------------
    total_tests += 1
    print("\n[TEST 3] SHAP Explainer Engine & Cold Start Logic...")
    explainer = IntentExplainer()
    
    # 3a. Standard Regular User (Act Mode)
    sample_act = {
        "entry_point": "push", "time_of_day": 20, "day_of_week": 4, "is_weekend": False,
        "network_type": "wifi", "scroll_velocity": 85.0, "first_tap_depth": 4,
        "session_gap_hours": 1.5, "previous_session_converted": True,
        "regional_event_active": True, "user_cohort": "regular"
    }
    res_act = explainer.explain_prediction(sample_act)
    assert res_act['intent_label'] in ['act', 'browse'], "Invalid intent label"
    assert len(res_act['explanation']) == 3, "Explanation should contain top 3 features"
    assert "summary" in res_act, "Missing plain English summary"
    
    # 3b. New User Cold Start
    sample_new = {
        "entry_point": "organic", "time_of_day": 12, "day_of_week": 2, "is_weekend": False,
        "network_type": "wifi", "scroll_velocity": 250.0, "first_tap_depth": 1,
        "session_gap_hours": 0.0, "previous_session_converted": False,
        "regional_event_active": False, "user_cohort": "new"
    }
    res_new = explainer.explain_prediction(sample_new)
    assert res_new['intent_score'] == 0.35, "Cold start score should be cohort prior 0.35"
    assert res_new['intent_label'] == 'browse', "Cold start prior should default to browse"
    print(f"  Regular User Prediction: {res_act['intent_label'].upper()} (Score: {res_act['intent_score']})")
    print(f"  Cold Start Prediction  : {res_new['intent_label'].upper()} (Prior Score: {res_new['intent_score']})")
    print("  --> PASSED")
    passed_tests += 1

    # -------------------------------------------------------------
    # Test 4: Adaptive Content Ranker & Kendall Tau Distance
    # -------------------------------------------------------------
    total_tests += 1
    print("\n[TEST 4] Layer 2 Content Ranker & Kendall Tau Distance...")
    act_rank = rank_content('act', DEFAULT_CONTENT_POOL)
    browse_rank = rank_content('browse', DEFAULT_CONTENT_POOL)
    
    assert len(act_rank['smart_ranking']) == len(DEFAULT_CONTENT_POOL)
    assert act_rank['diff_score'] > 0.0, "Kendall Tau diff score should be > 0"
    assert 'rank_reason' in act_rank['smart_ranking'][0], "Missing rank_reason"
    print(f"  Act Mode Top Item   : [{act_rank['smart_ranking'][0]['content_id']}] {act_rank['smart_ranking'][0]['title']}")
    print(f"  Browse Mode Top Item: [{browse_rank['smart_ranking'][0]['content_id']}] {browse_rank['smart_ranking'][0]['title']}")
    print(f"  Kendall Tau Diff    : Act={act_rank['diff_score']}, Browse={browse_rank['diff_score']}")
    print("  --> PASSED")
    passed_tests += 1

    # -------------------------------------------------------------
    # Test 5: Session Value Score (SVS) & Funnel Metrics
    # -------------------------------------------------------------
    total_tests += 1
    print("\n[TEST 5] SVS Formula & Funnel Metrics...")
    # Exact SVS check
    svs_val = calculate_svs(dwell_seconds=300, exploration_depth=5, converted=True, returned_within_24h=True)
    # (0.5 * 0.3) + (0.5 * 0.2) + (1.0 * 0.3) + (1.0 * 0.2) = 0.15 + 0.10 + 0.30 + 0.20 = 0.75
    assert abs(svs_val - 0.75) < 0.001, f"Expected SVS 0.75, got {svs_val}"
    
    svs_trend = generate_svs_trend()
    assert svs_trend['improvement_pct'] > 50.0, "SmartSession SVS should show significant improvement"
    assert len(svs_trend['trend']) == 30, "Trend should contain 30 days of data"
    print(f"  Calculated SVS Test : {svs_val}")
    print(f"  SVS Improvement     : +{svs_trend['improvement_pct']}% (Standard: {svs_trend['standard_avg_svs']} -> SmartSession: {svs_trend['smartsession_avg_svs']})")
    print("  --> PASSED")
    passed_tests += 1

    # -------------------------------------------------------------
    # Test 6: FastAPI Endpoints via TestClient
    # -------------------------------------------------------------
    total_tests += 1
    print("\n[TEST 6] FastAPI Server Endpoints...")
    client = TestClient(app)
    
    # 6a. GET /health
    r_health = client.get("/health")
    assert r_health.status_code == 200 and r_health.json()["status"] == "ok"
    
    # 6b. POST /predict-intent
    r_pred = client.post("/predict-intent", json=sample_act)
    assert r_pred.status_code == 200 and "intent_label" in r_pred.json()
    
    # 6c. POST /rank-content
    r_rank = client.post("/rank-content", json={"intent_label": "act", "content_list": DEFAULT_CONTENT_POOL})
    assert r_rank.status_code == 200 and "smart_ranking" in r_rank.json()
    
    # 6d. GET /friction-heatmap
    r_frict = client.get("/friction-heatmap")
    assert r_frict.status_code == 200 and "funnel" in r_frict.json()
    
    # 6e. GET /session-value-score
    r_svs = client.get("/session-value-score")
    assert r_svs.status_code == 200 and "trend" in r_svs.json()
    
    print("  /health              --> 200 OK")
    print("  /predict-intent      --> 200 OK")
    print("  /rank-content        --> 200 OK")
    print("  /friction-heatmap    --> 200 OK")
    print("  /session-value-score --> 200 OK")
    print("  --> PASSED")
    passed_tests += 1

    print("\n" + "=" * 70)
    print(f"SUCCESS: {passed_tests}/{total_tests} VALIDATION TESTS PASSED (100%)")
    print("=" * 70)

if __name__ == '__main__':
    validate_all()
