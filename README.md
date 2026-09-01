# SmartSession — Real-Time Session Intent Detection & Adaptive Ranking Engine

SmartSession detects user intent within the first 30 seconds of an app session and adaptively reshapes the content experience in real time. It surfaces action-ready primary items for **Act Mode** users and rich discovery feeds for **Browse Mode** users — **with zero dark patterns, no nudging, and no pressure tactics**.

---

## 🌟 Key Architecture & Layers

1. **Layer 1 — Intent Classifier**: LightGBM binary classifier trained on 10,000 synthetic session records. Uses `shap.TreeExplainer` to return plain-English explanations for every prediction.
2. **Layer 2 — Adaptive Content Ranker**: Re-ranks candidate items dynamically based on detected intent:
   - **Act Mode**: Sorted by `relevance_score` DESC, `tap_to_action` ASC.
   - **Browse Mode**: Sorted by `discovery_score` DESC, `content_depth` DESC.
   - **Cold Start Handling**: Assigns new users (`user_cohort == 'new'`) a prior intent score of `0.35`.
3. **Layer 3 — Friction Heatmap Engine**: Tracks session telemetry across 6 funnel steps (`home`, `browse`, `content_detail`, `action_prompt`, `confirm`, `complete`) and generates friction drop-off insights.
4. **Session Value Score (SVS)**: Continuous session quality metric tracking dwell, exploration depth, conversion outcome, and 24h return rate. Demonstrates a **+78.6% SVS lift** over standard static ranking.

---

## 📁 Repository Structure

```
smartsession/
├── backend/
│   ├── data/
│   │   └── sessions.csv          ← Synthetic dataset (10,000 records)
│   ├── models/
│   │   ├── intent_model.pkl      ← Trained LightGBM model
│   │   ├── encoders.pkl          ← Saved LabelEncoders
│   │   └── metadata.json         ← Feature names & metrics
│   ├── synthetic_data.py         ← Step 1: Synthetic data generator
│   ├── train_model.py            ← Step 2: Model trainer & evaluation
│   ├── content_ranker.py         ← Layer 2: Adaptive content ranker
│   ├── friction_tracker.py       ← Layer 3: Friction heatmap tracker
│   ├── session_value_score.py    ← SVS computation & 30-day simulator
│   ├── explainer.py              ← SHAP TreeExplainer & cold-start engine
│   └── main.py                   ← FastAPI Application
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SessionSimulator.jsx    ← Panel 1: Session simulator
│   │   │   ├── IntentResult.jsx        ← Panel 2: Intent & SHAP result
│   │   │   ├── ContentExperience.jsx    ← Panel 3: Split-screen UI
│   │   │   └── AnalyticsDashboard.jsx  ← Panel 4: Heatmap & SVS trend
│   │   ├── App.jsx               ← Tabbed UI orchestrator
│   │   ├── api.js                ← FastAPI client functions (fetch)
│   │   └── index.css             ← Tailwind CSS directives
│   ├── package.json
│   └── vite.config.js
├── requirements.txt
└── README.md
```

---

## 🚀 Setup and Run Instructions

### 1. Install Backend Dependencies & Train Model

```bash
# 1. Install backend requirements
pip install -r requirements.txt

# 2. Generate 10,000 session records
python backend/synthetic_data.py

# 3. Train LightGBM model and verify evaluation metrics (Acc >= 82%, F1 >= 0.80, AUC >= 0.88)
python backend/train_model.py

# 4. Start FastAPI backend server on port 8000
python -m uvicorn backend.main:app --reload --port 8000
```

The FastAPI server interactive API documentation will be available at: `http://localhost:8000/docs`

---

### 2. Start React Frontend Demo UI

Open a new terminal window:

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install Node dependencies
npm install

# 3. Start Vite dev server on port 3000
npm run dev
```

Open your browser and navigate to `http://localhost:3000`.

---

## 🏆 Demo Flow for Hackathon Judges

1. **Step 1: Session Simulator Panel**
   - Click the preset button **"⚡ Action Push"** (Entry point: `push`, Time: 20:00, Previous converted: `true`, Live regional event: `true`).
   - Click **"Detect Session Intent"**.

2. **Step 2: Intent Result Panel**
   - View real-time classification: **ACT MODE** badge (Emerald glow).
   - View confidence score (e.g. 99.5%) and SHAP feature drivers in plain English: *"First 10s scroll velocity of 85.0 px/sec (70% weight)..."*

3. **Step 3: Content Experience Panel**
   - Observe the live **split-screen comparison**:
     - *Left*: Standard static ranking (unadapted).
     - *Right*: SmartSession adaptive ranking surfacing **1-click direct action items** first.
   - Note the **Kendall Tau Layout Shift Score**.

4. **Step 4: Analytics Dashboard Panel**
   - View the **Friction Heatmap**: see how SmartSession reduces high drop-off at `content_detail` from 60% down to 22%.
   - View the **30-Day SVS Performance Chart**: demonstrate the **+78.6% SVS value lift**.

5. **Step 5: Browse Mode Scenario**
   - Return to Panel 1 and click **"🏄 Weekend Browse"** (Entry point: `organic`, Time: 14:00, Weekend: `true`).
   - Click **"Detect Session Intent"** and observe how the engine instantly adapts to **BROWSE MODE**, re-ordering content for rich discovery and depth exploration.

---

## 📡 FastAPI API Endpoints Reference

| Endpoint | Method | Input | Description |
| :--- | :--- | :--- | :--- |
| `/predict-intent` | `POST` | `SessionFeatures` JSON | Returns `intent_label`, `intent_score`, `confidence`, top 3 SHAP drivers, and plain-English summary. |
| `/rank-content` | `POST` | `{ intent_label, content_list }` | Re-ranks content items and computes Kendall Tau distance `diff_score`. |
| `/log-event` | `POST` | `{ session_id, step, action, dwell_seconds }` | Logs in-session telemetry event. |
| `/friction-heatmap` | `GET` | None | Returns funnel step drop-off rates, dwell seconds, and friction insights. |
| `/session-value-score` | `GET` | None | Returns 30-day SVS time-series comparison data. |
| `/content-pool` | `GET` | None | Returns candidate content pool items. |
| `/health` | `GET` | None | Health check & model status. |
