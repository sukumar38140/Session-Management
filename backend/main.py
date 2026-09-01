"""
backend/main.py
FastAPI Web Application for SmartSession.
Serves real-time intent classification, adaptive content ranking, friction heatmap tracking, and SVS analytics.
Supports dynamic cloud PORT environment variables and auto-model training on deployment.
"""

import os
import sys
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Local imports
from backend.content_ranker import rank_content, DEFAULT_CONTENT_POOL
from backend.friction_tracker import FrictionTracker
from backend.session_value_score import generate_svs_trend

app = FastAPI(
    title="SmartSession API",
    description="Real-time session intent detection & adaptive content ranking engine API.",
    version="1.0.0"
)

# CORS Middleware setup - Allow all origins for production cloud deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines on startup
explainer_engine = None
friction_tracker = FrictionTracker()

# Absolute path base directory for serverless environments
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def ensure_model_exists():
    """Checks if trained model exists, if not, runs data generator & model training pipeline."""
    model_path = os.path.join(BASE_DIR, 'backend', 'models', 'intent_model.pkl')
    data_path = os.path.join(BASE_DIR, 'backend', 'data', 'sessions.csv')
    
    if not os.path.exists(data_path):
        print("Dataset missing on server. Generating synthetic dataset...")
        from backend.synthetic_data import generate_dataset
        df = generate_dataset(n_samples=10000, random_seed=42)
        os.makedirs(os.path.join(BASE_DIR, 'backend', 'data'), exist_ok=True)
        df.to_csv(data_path, index=False)
        
    if not os.path.exists(model_path):
        print("Trained model missing on server. Training LightGBM model...")
        from backend.train_model import train_intent_model
        train_intent_model()

@app.on_event("startup")
def startup_event():
    global explainer_engine
    try:
        ensure_model_exists()
        from backend.explainer import IntentExplainer
        explainer_engine = IntentExplainer()
        print("IntentExplainer engine successfully initialized.")
    except Exception as e:
        print(f"Warning during model initialization: {e}")

# Pydantic Schemas
class SessionFeatures(BaseModel):
    entry_point: str = Field(..., description="'push', 'organic', or 'widget'")
    time_of_day: int = Field(..., ge=0, le=23, description="Hour of day (0-23)")
    day_of_week: int = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday")
    is_weekend: bool = Field(..., description="True if weekend session")
    network_type: str = Field(..., description="'wifi' or 'cellular'")
    scroll_velocity: float = Field(..., ge=0.0, le=500.0, description="Pixels/sec in first 10s")
    first_tap_depth: int = Field(..., ge=1, le=5, description="First tap UI depth level (1-5)")
    session_gap_hours: float = Field(..., ge=0.0, le=168.0, description="Hours since last session")
    previous_session_converted: bool = Field(..., description="True if previous session converted")
    regional_event_active: bool = Field(..., description="True if regional live event active")
    user_cohort: str = Field(default="regular", description="'new', 'casual', 'regular', or 'power'")

class ContentItem(BaseModel):
    content_id: str
    title: str
    category: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    discovery_score: float = Field(..., ge=0.0, le=1.0)
    tap_to_action: int = Field(..., ge=1, le=5)
    content_depth: int = Field(..., ge=1, le=5)
    thumbnail: Optional[str] = "🎬"
    description: Optional[str] = ""

class RankContentRequest(BaseModel):
    intent_label: str = Field(..., description="'act' or 'browse'")
    content_list: Optional[List[ContentItem]] = None

class EventLogRequest(BaseModel):
    session_id: str
    step: str
    action: str
    dwell_seconds: float = Field(..., ge=0.0)

# Endpoints
@app.get("/", summary="Root API info endpoint")
def root_endpoint():
    return {
        "service": "SmartSession Real-Time Engine API",
        "status": "online",
        "docs_url": "/docs",
        "endpoints": ["/predict-intent", "/rank-content", "/log-event", "/friction-heatmap", "/session-value-score"]
    }

@app.get("/health", summary="Health check endpoint")
def health_check():
    model_loaded = explainer_engine is not None
    return {
        "status": "ok",
        "model_loaded": model_loaded,
        "service": "SmartSession Real-Time Engine"
    }

@app.post("/predict-intent", summary="Predict user session intent (Act vs Browse) with SHAP explanation")
def predict_intent(features: SessionFeatures):
    global explainer_engine
    if explainer_engine is None:
        try:
            ensure_model_exists()
            from backend.explainer import IntentExplainer
            explainer_engine = IntentExplainer()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Model engine not loaded: {str(e)}"
            )
            
    feat_dict = features.dict()
    try:
        explanation_result = explainer_engine.explain_prediction(feat_dict)
        return explanation_result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Inference error: {str(e)}"
        )

@app.post("/rank-content", summary="Re-rank content items based on detected intent")
def rank_content_endpoint(req: RankContentRequest):
    intent_label = req.intent_label.lower().strip()
    if intent_label not in ['act', 'browse']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="intent_label must be either 'act' or 'browse'"
        )
        
    items = [item.dict() for item in req.content_list] if req.content_list and len(req.content_list) > 0 else DEFAULT_CONTENT_POOL
    
    result = rank_content(intent_label, items)
    return result

@app.post("/log-event", summary="Log in-session friction event telemetry")
def log_event_endpoint(req: EventLogRequest):
    friction_tracker.log_event(
        session_id=req.session_id,
        step=req.step,
        action=req.action,
        dwell_seconds=req.dwell_seconds
    )
    return {"status": "logged", "session_id": req.session_id}

@app.get("/friction-heatmap", summary="Get session funnel friction metrics")
def get_friction_heatmap_endpoint():
    return friction_tracker.get_friction_map()

@app.get("/session-value-score", summary="Get 30-day Session Value Score (SVS) comparative trend")
def get_session_value_score_endpoint():
    return generate_svs_trend()

@app.get("/content-pool", summary="Get default entertainment content pool")
def get_content_pool():
    return DEFAULT_CONTENT_POOL

if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
