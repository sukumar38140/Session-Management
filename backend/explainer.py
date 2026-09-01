"""
backend/explainer.py
SHAP TreeExplainer engine for SmartSession.
Computes feature attribution and formats plain-English explanations for Model predictions.
Supports LightGBM and GradientBoostingClassifier natively with zero system library requirements.
Handles cold start users ('new' cohort prior).
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
import shap

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class IntentExplainer:
    def __init__(self, models_dir=None):
        if models_dir is None:
            models_dir = os.path.join(BASE_DIR, 'backend', 'models')
            
        model_path = os.path.join(models_dir, 'intent_model.pkl')
        encoders_path = os.path.join(models_dir, 'encoders.pkl')
        meta_path = os.path.join(models_dir, 'metadata.json')
        
        if not os.path.exists(model_path):
            from backend.train_model import train_intent_model
            train_intent_model()
            
        self.clf = joblib.load(model_path)
        self.encoders = joblib.load(encoders_path)
        
        with open(meta_path, 'r') as f:
            self.metadata = json.load(f)
            
        self.feature_cols = self.metadata['feature_cols']
        self.cat_cols = self.metadata['cat_cols']
        
        # Initialize SHAP TreeExplainer
        self.explainer = shap.TreeExplainer(self.clf)
        
    def _preprocess_row(self, raw_dict):
        """Converts raw input dictionary into encoded DataFrame row matching training feature order."""
        row_dict = {}
        for col in self.feature_cols:
            val = raw_dict.get(col, 0)
            if col in self.cat_cols:
                le = self.encoders[col]
                val_str = str(val)
                if val_str in le.classes_:
                    row_dict[col] = le.transform([val_str])[0]
                else:
                    row_dict[col] = 0
            elif col in ['is_weekend', 'previous_session_converted', 'regional_event_active']:
                row_dict[col] = int(bool(val))
            else:
                row_dict[col] = float(val)
                
        df_row = pd.DataFrame([row_dict], columns=self.feature_cols)
        return df_row

    def explain_prediction(self, features_dict):
        user_cohort = str(features_dict.get('user_cohort', 'regular')).lower()
        
        # Handle Cold Start for 'new' cohort
        if user_cohort == 'new':
            intent_score = 0.35
            intent_label = 'browse'
            confidence = 65.0
            
            explanation = [
                {
                    "feature": "user_cohort",
                    "value": "new",
                    "impact": "medium",
                    "direction": "toward_browse",
                    "plain_english": "New user with no history — assigned cohort prior (0.35). Defaulting to Browse Mode."
                }
            ]
            summary = "Predicted Browse Mode (Cohort Prior) because: New user assigned prior intent score of 0.35."
            
            return {
                "intent_label": intent_label,
                "intent_score": intent_score,
                "confidence": confidence,
                "explanation": explanation,
                "summary": summary
            }
            
        # Standard Prediction for regular / casual / power cohorts
        df_row = self._preprocess_row(features_dict)
        
        # Predict probability of Act Mode (class 1)
        probas = self.clf.predict_proba(df_row)[0]
        act_prob = float(probas[1])
        
        intent_score = round(act_prob, 4)
        intent_label = 'act' if act_prob >= 0.5 else 'browse'
        confidence = round(float(max(probas) * 100.0), 1)
        
        # Calculate SHAP values safely
        shap_vals = self.explainer.shap_values(df_row)
        
        if isinstance(shap_vals, list):
            vals = shap_vals[1][0] if len(shap_vals) > 1 else shap_vals[0][0]
        elif len(np.shape(shap_vals)) == 3:
            vals = shap_vals[0, :, 1]
        elif len(np.shape(shap_vals)) == 2:
            vals = shap_vals[0]
        else:
            vals = shap_vals
            
        # Calculate percentage contributions of top features
        abs_vals = np.abs(vals)
        sum_abs = np.sum(abs_vals) if np.sum(abs_vals) > 0 else 1.0
        
        # Rank features by absolute SHAP impact
        ranked_feats = sorted(zip(self.feature_cols, vals, abs_vals), key=lambda x: x[2], reverse=True)
        top_3 = ranked_feats[:3]
        
        explanation = []
        summary_parts = []
        
        friendly_names = {
            "entry_point": "Entry Point",
            "time_of_day": "Time of Day",
            "day_of_week": "Day of Week",
            "is_weekend": "Weekend Session",
            "network_type": "Network Connection",
            "scroll_velocity": "Scroll Velocity",
            "first_tap_depth": "First Tap Depth",
            "session_gap_hours": "Session Gap",
            "previous_session_converted": "Previous Conversion",
            "regional_event_active": "Regional Live Event",
            "user_cohort": "User Cohort"
        }
        
        for feat, shap_val, abs_v in top_3:
            raw_val = features_dict.get(feat, "")
            pct = int(round((abs_v / sum_abs) * 100.0))
            direction = "toward_act" if shap_val > 0 else "toward_browse"
            
            # Plain English generator
            if feat == "entry_point":
                pe = f"Opened via '{raw_val}' entry point ({pct}% weight)"
            elif feat == "time_of_day":
                pe = f"Session started at {raw_val}:00 hours ({pct}% weight)"
            elif feat == "scroll_velocity":
                pe = f"First 10s scroll velocity of {raw_val} px/sec ({pct}% weight)"
            elif feat == "first_tap_depth":
                pe = f"First tap at UI depth level {raw_val} ({pct}% weight)"
            elif feat == "session_gap_hours":
                pe = f"{raw_val} hours gap since last session ({pct}% weight)"
            elif feat == "previous_session_converted":
                pe = f"Converted in previous session: {raw_val} ({pct}% weight)"
            elif feat == "regional_event_active":
                pe = f"Live regional event active: {raw_val} ({pct}% weight)"
            else:
                pe = f"{friendly_names.get(feat, feat)} = {raw_val} ({pct}% weight)"
                
            impact_level = "high" if pct >= 30 else ("medium" if pct >= 15 else "low")
            
            explanation.append({
                "feature": feat,
                "value": str(raw_val),
                "impact": impact_level,
                "direction": direction,
                "plain_english": pe,
                "weight_pct": pct
            })
            
            summary_parts.append(f"{friendly_names.get(feat, feat)} ({raw_val}) contributed {pct}%")
            
        summary = f"Predicted {intent_label.upper()} Mode because: " + ", ".join(summary_parts) + "."
        
        return {
            "intent_label": intent_label,
            "intent_score": intent_score,
            "confidence": confidence,
            "explanation": explanation,
            "summary": summary
        }

if __name__ == '__main__':
    explainer = IntentExplainer()
    sample_act = {
        "entry_point": "push",
        "time_of_day": 20,
        "day_of_week": 4,
        "is_weekend": False,
        "network_type": "wifi",
        "scroll_velocity": 85.0,
        "first_tap_depth": 3,
        "session_gap_hours": 1.5,
        "previous_session_converted": True,
        "regional_event_active": True,
        "user_cohort": "regular"
    }
    res = explainer.explain_prediction(sample_act)
    print("\n--- SAMPLE EXPLAINER OUTPUT ---")
    print(json.dumps(res, indent=2))
