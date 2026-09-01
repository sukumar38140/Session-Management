/**
 * frontend/src/api.js
 * Central API client module for SmartSession FastAPI backend.
 * Dynamically supports production Vercel deployment (same origin relative URLs) & local dev fallback.
 */

const isLocalDev = typeof window !== 'undefined' && window.location.hostname === 'localhost' && window.location.port === '3000';
const BASE_URL = import.meta.env.VITE_API_URL || (isLocalDev ? 'http://localhost:8000' : '');

async function handleResponse(response) {
  if (!response.ok) {
    let errorMsg = `HTTP Error ${response.status}`;
    try {
      const errData = await response.json();
      errorMsg = errData.detail || JSON.stringify(errData);
    } catch (e) {
      // fallback
    }
    throw new Error(errorMsg);
  }
  return await response.json();
}

export async function predictIntent(features) {
  const response = await fetch(`${BASE_URL}/predict-intent`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(features)
  });
  return await handleResponse(response);
}

export async function rankContent(intentLabel, contentList = null) {
  const response = await fetch(`${BASE_URL}/rank-content`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      intent_label: intentLabel,
      content_list: contentList
    })
  });
  return await handleResponse(response);
}

export async function logEvent(sessionId, step, action, dwellSeconds) {
  const response = await fetch(`${BASE_URL}/log-event`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      step: step,
      action: action,
      dwell_seconds: dwellSeconds
    })
  });
  return await handleResponse(response);
}

export async function getFrictionHeatmap() {
  const response = await fetch(`${BASE_URL}/friction-heatmap`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });
  return await handleResponse(response);
}

export async function getSessionValueScore() {
  const response = await fetch(`${BASE_URL}/session-value-score`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });
  return await handleResponse(response);
}

export async function getContentPool() {
  const response = await fetch(`${BASE_URL}/content-pool`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });
  return await handleResponse(response);
}
