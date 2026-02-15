/**
 * API client for the Itinero backend (FastAPI).
 *
 * All requests go to /api/* on the same origin. The Express server
 * proxies these to the FastAPI backend running on port 8000.
 */

import type {
  PlanRequest,
  TravelPlanResponse,
  ChatRequest,
  ChatResponse,
  ReplanRequest,
} from "./types";

const API_BASE = "http://localhost:8000/api";

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    method,
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const text = (await res.text()) || res.statusText;
    throw new Error(`${res.status}: ${text}`);
  }

  return res.json();
}

// ─── Plan ───────────────────────────────────────────────────────────────────

/**
 * Create a full travel plan. Runs all agents (weather, transport, hotel,
 * discovery, budget) and returns a complete itinerary.
 */
export async function createPlan(
  req: PlanRequest,
): Promise<TravelPlanResponse> {
  return request<TravelPlanResponse>("POST", "/plan", req);
}

// ─── Chat ───────────────────────────────────────────────────────────────────

/**
 * Send a chat message to the orchestrator. If session_id is null/omitted,
 * a new chat session is created.
 */
export async function sendChatMessage(
  req: ChatRequest,
): Promise<ChatResponse> {
  return request<ChatResponse>("POST", "/chat", req);
}

/**
 * End a chat session and release server-side resources.
 */
export async function endChatSession(
  sessionId: string,
): Promise<{ status: string; message: string }> {
  return request("DELETE", `/chat/${sessionId}`);
}

// ─── Replan ─────────────────────────────────────────────────────────────────

/**
 * Selectively re-plan parts of an existing travel plan.
 * Only agents affected by the changed fields are re-run.
 */
export async function replan(
  req: ReplanRequest,
): Promise<TravelPlanResponse> {
  return request<TravelPlanResponse>("POST", "/replan", req);
}

// ─── Session ────────────────────────────────────────────────────────────────

/**
 * Retrieve a stored session state by ID.
 */
export async function getSession(sessionId: string) {
  return request("GET", `/session/${sessionId}`);
}

// ─── Health ─────────────────────────────────────────────────────────────────

/**
 * Check if the backend API is reachable.
 */
export async function healthCheck(): Promise<{
  status: string;
  service: string;
  version: string;
}> {
  return request("GET", "/health");
}
