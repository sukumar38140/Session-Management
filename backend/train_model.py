"""
backend/train_model.py
Trains the Intent Classifier for SmartSession.
Supports LightGBM with automatic scikit-learn GradientBoostingClassifier fallback for cloud environments without libgomp.so.1.
Encodes categoricals with LabelEncoder, evaluates against success criteria (Acc >= 82%, F1 >= 0.80, AUC >= 0.88),
and saves trained model and encoders to backend/models/.
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, classification_report, confusion_matrix
from sklearn.ensemble import GradientBoostingClassifier

# Try importing LightGBM, fallback to GradientBoostingClassifier if libgomp.so.1 is missing
USE_LIGHTGBM = False
try:
    import lightgbm as lgb
    # Verify binary load
    _dummy = lgb.LGBMClassifier(n_estimators=1)
    USE_LIGHTGBM = True
    print("LightGBM successfully loaded.")
except (ImportError, OSError) as e:
    print(f"LightGBM unavailable ({e}). Using scikit-learn GradientBoostingClassifier fallback...")
    USE_LIGHTGBM = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def train_intent_model():
    data_path = os.path.join(BASE_DIR, 'backend', 'data', 'sessions.csv')
    if not os.path.exists(data_path):
        from backend.synthetic_data import generate_dataset
        df_gen = generate_dataset(10000, random_seed=42)
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        df_gen.to_csv(data_path, index=False)
        
    df = pd.read_csv(data_path)
    
    # Target encoding: browse=0, act=1
    df['target'] = (df['intent_label'] == 'act').astype(int)
    
    # Categoricals & Numericals
    cat_cols = ['entry_point', 'network_type', 'user_cohort']
    
    exclude_cols = [
        'session_id', 'user_id', 'intent_label', 'target',
        'converted', 'dwell_seconds', 'exploration_depth',
        'returned_within_24h', 'session_value_score'
    ]
    
    feature_cols = [c for c in df.columns if c not in exclude_cols]
    
    X = df[feature_cols].copy()
    y = df['target'].copy()
    
    # Convert booleans to int (0/1)
    bool_cols = ['is_weekend', 'previous_session_converted', 'regional_event_active']
    for b in bool_cols:
        if b in X.columns:
            X[b] = X[b].astype(int)
            
    # Fit LabelEncoders for categorical columns
    encoders = {}
    for col in cat_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le
        
    # Train / Test split (80/20, stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    
    print(f"Training set: {X_train.shape}, Test set: {X_test.shape}")
    
    if USE_LIGHTGBM:
        print("Training LightGBM Classifier...")
        clf = lgb.LGBMClassifier(
            n_estimators=300,
            learning_rate=0.1,
            max_depth=6,
            num_leaves=31,
            class_weight='balanced',
            random_state=42,
            verbose=-1
        )
    else:
        print("Training Scikit-Learn GradientBoostingClassifier (libgomp-safe)...")
        clf = GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.08,
            max_depth=5,
            random_state=42
        )
        
    clf.fit(X_train, y_train)
    
    # Predictions
    y_pred_proba = clf.predict_proba(X_test)[:, 1]
    y_pred = clf.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')
    auc = roc_auc_score(y_test, y_pred_proba)
    
    print("\n" + "=" * 60)
    print("MODEL TRAINING & EVALUATION METRICS")
    print("=" * 60)
    print(f"Accuracy  : {acc:.4f}  (Target >= 0.82) {'PASSED' if acc >= 0.82 else 'WARNING'}")
    print(f"F1-Score  : {f1:.4f}  (Target >= 0.80) {'PASSED' if f1 >= 0.80 else 'WARNING'}")
    print(f"AUC-ROC   : {auc:.4f}  (Target >= 0.88) {'PASSED' if auc >= 0.88 else 'WARNING'}")
    
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Top 5 Feature Importances
    importances = clf.feature_importances_
    feat_imp = sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)
    
    print("\nTop 5 Feature Importances:")
    for feat, imp in feat_imp[:5]:
        print(f"  {feat:30s}: {imp:.4f}")
        
    # Save Model Artifacts
    models_dir = os.path.join(BASE_DIR, 'backend', 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    model_path = os.path.join(models_dir, 'intent_model.pkl')
    encoders_path = os.path.join(models_dir, 'encoders.pkl')
    meta_path = os.path.join(models_dir, 'metadata.json')
    
    joblib.dump(clf, model_path)
    joblib.dump(encoders, encoders_path)
    
    metadata = {
        'feature_cols': feature_cols,
        'cat_cols': cat_cols,
        'model_type': 'LightGBM' if USE_LIGHTGBM else 'GradientBoostingClassifier',
        'metrics': {
            'accuracy': float(acc),
            'f1_weighted': float(f1),
            'auc_roc': float(auc)
        },
        'feature_importances': {feat: float(imp) for feat, imp in feat_imp}
    }
    with open(meta_path, 'w') as f:
        json.dump(metadata, f, indent=2)
        
    print("\nSaved artifacts:")
    print(f"  Model   : {model_path}")
    print(f"  Encoders: {encoders_path}")
    print(f"  Metadata: {meta_path}")
    print("=" * 60)

if __name__ == '__main__':
    train_intent_model()
