"""
train_intent_classifier.py
Trains the SmartSession Intent Classifier using LightGBM / XGBoost.
Computes evaluation metrics (AUC-ROC, Accuracy, Precision, Recall).
Initializes SHAP TreeExplainer and saves all artifacts to 'models/'.
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, classification_report, confusion_matrix

try:
    import lightgbm as lgb
    USE_LIGHTGBM = True
except ImportError:
    import xgboost as xgb
    USE_LIGHTGBM = False

import shap

def train_model():
    data_path = 'synthetic_sessions.csv'
    if not os.path.exists(data_path):
        raise FileNotFoundError("synthetic_sessions.csv not found! Run synthetic_data_generator.py first.")
        
    df = pd.read_csv(data_path)
    
    # Feature columns specification
    feature_cols = [
        'entry_point',
        'time_of_day',
        'day_of_week',
        'is_weekend',
        'network_type',
        'scroll_velocity',
        'first_tap_depth',
        'session_gap_hours',
        'previous_session_converted',
        'regional_event_active'
    ]
    
    X = df[feature_cols].copy()
    
    # Convert booleans to int 0/1
    bool_cols = ['is_weekend', 'previous_session_converted', 'regional_event_active']
    for c in bool_cols:
        X[c] = X[c].astype(int)
        
    # Target: 1 for 'act', 0 for 'browse'
    y = (df['intent_label'] == 'act').astype(int)
    
    cat_cols = ['entry_point', 'network_type']
    num_cols = [c for c in feature_cols if c not in cat_cols]
    
    # Preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'), cat_cols),
            ('num', 'passthrough', num_cols)
        ],
        remainder='drop'
    )
    
    X_trans = preprocessor.fit_transform(X)
    
    # Extract feature names after OneHotEncoding
    ohe_feature_names = preprocessor.named_transformers_['cat'].get_feature_names_out(cat_cols).tolist()
    transformed_feature_names = ohe_feature_names + num_cols
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_trans, y, test_size=0.2, random_state=42, stratify=y
    )
    
    os.makedirs('models', exist_ok=True)
    
    print(f"Training set shape: {X_train.shape}, Test set shape: {X_test.shape}")
    
    if USE_LIGHTGBM:
        print("Using LightGBM Classifier...")
        clf = lgb.LGBMClassifier(
            n_estimators=150,
            max_depth=5,
            learning_rate=0.05,
            num_leaves=31,
            random_state=42,
            verbose=-1
        )
    else:
        print("Using XGBoost Classifier...")
        clf = xgb.XGBClassifier(
            n_estimators=150,
            max_depth=5,
            learning_rate=0.05,
            random_state=42,
            eval_metric='logloss'
        )
        
    clf.fit(X_train, y_train)
    
    # Evaluation
    y_pred_proba = clf.predict_proba(X_test)[:, 1]
    y_pred = (y_pred_proba >= 0.5).astype(int)
    
    auc = roc_auc_score(y_test, y_pred_proba)
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    
    print("\n--- MODEL PERFORMANCE METRICS ---")
    print(f"ROC-AUC  : {auc:.4f}")
    print(f"Accuracy : {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall   : {rec:.4f}")
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['browse (0)', 'act (1)']))
    
    # SHAP Explainer Setup
    print("Building SHAP TreeExplainer...")
    explainer = shap.TreeExplainer(clf)
    
    # Test SHAP explanation on a sample prediction
    sample_df = X.iloc[:1]
    sample_trans = preprocessor.transform(sample_df)
    shap_vals = explainer.shap_values(sample_trans)
    
    # Depending on LightGBM/XGBoost SHAP output structure
    if isinstance(shap_vals, list):
        # Multi-class or binary list format
        vals = shap_vals[1][0] if len(shap_vals) > 1 else shap_vals[0][0]
    elif len(np.shape(shap_vals)) == 3:
        vals = shap_vals[0, :, 1]
    else:
        vals = shap_vals[0]
        
    print("\nSample SHAP Feature Contributions for row 0:")
    for feat, val in sorted(zip(transformed_feature_names, vals), key=lambda x: abs(x[1]), reverse=True)[:5]:
        print(f"  {feat:30s}: {val:+.4f}")
        
    # Save artifacts
    joblib.dump(clf, 'models/intent_model.pkl')
    joblib.dump(preprocessor, 'models/preprocessor.pkl')
    joblib.dump(explainer, 'models/explainer.pkl')
    
    meta_info = {
        'feature_cols': feature_cols,
        'cat_cols': cat_cols,
        'num_cols': num_cols,
        'transformed_feature_names': transformed_feature_names,
        'metrics': {
            'auc': float(auc),
            'accuracy': float(acc),
            'precision': float(prec),
            'recall': float(rec)
        }
    }
    with open('models/metadata.json', 'w') as f:
        json.dump(meta_info, f, indent=2)
        
    print("\nAll model artifacts successfully saved in 'models/' directory.")

if __name__ == '__main__':
    train_model()
