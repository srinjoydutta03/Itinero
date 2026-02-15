# 🌍 Itinero — AI-Powered Multi-Agent Travel Planner

Itinero is a full-stack travel planning application that uses **Claude as an orchestrator** to coordinate five specialized AI sub-agents — each backed by real-time APIs — to produce structured, interactive travel plans with weather forecasts, flights, hotels, local discoveries, and budget optimization.

![Architecture](https://img.shields.io/badge/Architecture-Multi--Agent-blue)
![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)
![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB)
![AI](https://img.shields.io/badge/AI-Claude%20Agent%20SDK-7C3AED)

---

## ✨ Features

- **Multi-Agent Orchestration** — Claude coordinates 5 specialized sub-agents in parallel, each with its own MCP tools and real-time API access
- **Real-Time Data** — Live weather forecasts, flight prices, hotel rates, and local recommendations via OpenWeatherMap and SerpAPI
- **Interactive Dashboard** — Day-by-day itinerary, weather cards, flight options, hotel comparisons, and a discoveries tab with attractions, hidden gems, and restaurants
- **Conversational Plan Editing** — Chat with the AI to modify any aspect of your plan ("I only want Indian restaurants", "Find me a cheaper hotel") — the dashboard updates in real time
- **Smart Budget System** — Travel style multipliers (affordable / standard / premium / luxury) with automatic food and activity allocation derived from your budget
- **Airport Autocomplete** — 200+ airports with IATA code badges and keyboard navigation
- **Climate Fallback** — When trip dates exceed the 5-day forecast window, generates latitude-adjusted climate estimates labeled clearly

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   Frontend (React + Vite)                     │
│                     localhost:3001                            │
│  ┌──────────┐  ┌────────────┐  ┌───────────────────────────┐ │
│  │  Home    │→ │ Dashboard  │  │  Chat Sidebar             │ │
│  │  (Form)  │  │ (5 Tabs)   │  │  (modifies plan live)     │ │
│  └──────────┘  └────────────┘  └───────────────────────────┘ │
│         │              ▲               ▲                     │
│         │    POST /api/plan     POST /api/chat               │
└─────────┼──────────────┼───────────────┼─────────────────────┘
          │              │               │
          ▼              │               │
┌──────────────────────────────────────────────────────────────┐
│                 Backend (FastAPI + Uvicorn)                   │
│                     localhost:8000                            │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                  Orchestrator Agent                      │ │
│  │               (Claude Sonnet — via Task tool)            │ │
│  │                                                         │ │
│  │  Phase 1 (parallel):        Phase 2 (sequential):       │ │
│  │  ┌──────────┐               ┌───────────┐              │ │
│  │  │ Weather  │               │  Budget   │              │ │
│  │  │ Agent    │               │  Agent    │              │ │
│  │  ├──────────┤               └─────┬─────┘              │ │
│  │  │Transport │                     │                     │ │
│  │  │ Agent    │              Uses real costs              │ │
│  │  ├──────────┤              from Phase 1                 │ │
│  │  │ Hotel   │                                            │ │
│  │  │ Agent    │                                           │ │
│  │  ├──────────┤                                           │ │
│  │  │Discovery │                                           │ │
│  │  │ Agent    │                                           │ │
│  │  └──────────┘                                           │ │
│  └─────────────────────────────────────────────────────────┘ │
│         │         │         │         │         │            │
│    MCP Tools  MCP Tools  MCP Tools  MCP Tools  MCP Tools     │
│         │         │         │         │         │            │
│   OpenWeather  SerpAPI   SerpAPI   SerpAPI   Budget          │
│    Map API    Flights    Hotels   Maps/Web  Calculator       │
└──────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Itinero/
├── backend/                        # FastAPI Python backend
│   ├── main.py                     # App entry, CORS, lifespan
│   ├── routes/
│   │   ├── plan.py                 # POST /api/plan
│   │   ├── chat.py                 # POST /api/chat
│   │   ├── replan.py               # POST /api/replan
│   │   └── session.py              # GET /api/session/:id
│   ├── agents/
│   │   ├── orchestrator.py         # Central brain — coordinates all agents
│   │   ├── weather_agent.py        # Weather forecasts + climate fallback
│   │   ├── transport_agent.py      # Flight search + IATA resolution
│   │   ├── hotel_agent.py          # Hotel search + value scoring
│   │   ├── discovery_agent.py      # Attractions, restaurants, hidden gems
│   │   ├── budget_agent.py         # Budget optimization by travel style
│   │   ├── agent_tracker.py        # Tracks tool calls across agents
│   │   └── tools/                  # MCP tool definitions
│   │       ├── weather_tools.py
│   │       ├── transport_tools.py
│   │       ├── hotel_tools.py
│   │       ├── discovery_tools.py
│   │       └── budget_tools.py
│   ├── prompts/                    # System prompts (loaded at startup)
│   │   ├── orchestrator.txt
│   │   ├── weather.txt
│   │   ├── transport.txt
│   │   ├── hotel.txt
│   │   ├── discovery.txt
│   │   └── budget.txt
│   ├── models/
│   │   └── model.py                # All Pydantic data models
│   └── utils/
│       ├── client_manager.py       # Claude SDK client pooling + TTL
│       ├── prompt_loader.py        # Loads .txt prompts from disk
│       ├── session_store.py        # In-memory session persistence
│       └── serp_fetch.py           # SerpAPI HTTP wrapper with retries
│
├── client/                         # React + TypeScript frontend
│   └── src/
│       ├── App.tsx                 # Router setup
│       ├── pages/
│       │   ├── home.tsx            # Landing page with trip form
│       │   └── dashboard.tsx       # Plan results + chat + tabs
│       ├── components/
│       │   ├── airport-combobox.tsx # Autocomplete with IATA codes
│       │   ├── layout.tsx          # Page shell
│       │   └── ui/                 # shadcn/ui components
│       └── lib/
│           ├── api.ts              # fetch wrapper → localhost:8000
│           ├── types.ts            # TypeScript interfaces
│           ├── airports.ts         # 200+ airport dataset
│           └── utils.ts            # cn() + helpers
│
├── server/                         # Express dev server
│   └── index.ts                    # Serves Vite build in production
│
└── package.json
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.13+** with `venv`
- **Node.js 18+** with `npm`
- **API Keys:**
  - `ANTHROPIC_API_KEY` — [Anthropic Console](https://console.anthropic.com/)
  - `SERPAPI_API_KEY` — [SerpAPI](https://serpapi.com/)
  - `OPENWEATHERMAP_API_KEY` — [OpenWeatherMap](https://openweathermap.org/api)

### Setup

```bash
# Clone
git clone https://github.com/srinjoydutta03/Itinero.git
cd Itinero

# Backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Frontend
npm install

# Environment
cp .env.example .env
# Fill in your API keys in .env
```

### Run

```bash
# Terminal 1 — Backend (port 8000)
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 — Frontend (port 3001)
npm run dev
```

Open **http://localhost:3001** in your browser.

---

## 🔄 Request Lifecycle

### Initial Plan (`POST /api/plan`)

1. **Frontend** sends `PlanRequest` with destination, origin, dates, budget, travel style, preferences
2. **Orchestrator** builds a prompt and creates a `ClaudeSDKClient` with 5 sub-agent definitions
3. **Phase 1** — Claude delegates to 4 agents **in parallel** via the `Task` tool:
   - **Weather Agent** → OpenWeatherMap API (or climate estimate fallback)
   - **Transport Agent** → SerpAPI Google Flights (with IATA code resolution)
   - **Hotel Agent** → SerpAPI Google Hotels (ranked by value score)
   - **Discovery Agent** → SerpAPI Google Maps + Reddit (attractions, restaurants, hidden gems)
4. **Phase 2** — Claude delegates to the **Budget Agent** sequentially (needs real transport/hotel costs from Phase 1)
5. **Hooks** capture every tool call and result via `AgentTracker`
6. **Extraction** parses raw JSON responses into Pydantic models
7. **Session** is saved with all structured data + the LLM summary
8. **Response** is serialized as `TravelPlanResponse` and returned to the frontend

### Chat Modifications (`POST /api/chat`)

1. Frontend sends `ChatRequest` with `session_id` and user message
2. `run_chat_turn()` resets the tracker, loads the persistent SDK client (or creates one with injected plan context)
3. Claude processes the message — if it's a modification request, it re-invokes relevant sub-agents via `Task`
4. Hooks capture the new tool results, session is updated with fresh data
5. `ChatResponse` includes:
   - `reply` — the conversational response (shown in chat)
   - `updated_plan` — full `TravelPlanResponse` with updated data (triggers dashboard re-render)
6. The **original AI summary is preserved** — chat replies don't overwrite it

---

## 🤖 Agent Details

| Agent | API | Key Capability |
|-------|-----|----------------|
| **Weather** | OpenWeatherMap | 5-day forecast + latitude-based climate estimate fallback for distant dates |
| **Transport** | SerpAPI Google Flights | IATA code resolution (80+ cities), tags cheapest/fastest/best value |
| **Hotel** | SerpAPI Google Hotels | Value scoring (rating / price × 100), top 5 ranked options |
| **Discovery** | SerpAPI Google Maps + Web | Attractions (≥4.0★), restaurants (cuisine filter), hidden gems (Reddit-sourced, 2+ mentions) |
| **Budget** | Pure calculation | Style multipliers: affordable (0.80×), standard (1.00×), premium (1.20×), luxury (uncapped). Food=60%, Activities=40% of discretionary |

---

## 🖥️ Frontend

### Home Page
- Two-row responsive form with airport autocomplete (200+ airports, IATA badges, keyboard navigation)
- Date picker, guest count, budget input, travel style selector (affordable / standard / premium / luxury)

### Dashboard
- **AI Summary** — Markdown-rendered travel overview (persisted across chat updates)
- **Budget Overview** — 4 cost cards (transport, hotel, food, activities) + progress bar + tips
- **5 Tabs:**
  - **Itinerary** — Day-by-day plan built client-side from weather + flights + hotels + discoveries
  - **Weather** — Daily forecast cards with temperature, conditions, rain probability
  - **Flights** — Option cards with recommended badge, airlines, stops, duration
  - **Hotels** — Cards with rating, price, amenities, booking links
  - **Discoveries** — Clickable attractions + hidden gems (detail dialogs) + restaurants
- **Chat Sidebar** — Conversational follow-up that triggers real agent re-runs and live dashboard updates

---

## 🧩 Key Design Decisions

### Why Multi-Agent Instead of One Big Prompt?
Each agent has a **focused system prompt** and **dedicated API tools**. This means:
- Parallel execution — 4 agents run simultaneously, cutting latency
- Separation of concerns — each agent is testable in isolation
- Targeted re-runs — chat modifications only re-invoke the relevant agent(s)

### Why MCP Tools Instead of Function Calling?
The Claude Agent SDK's MCP integration provides:
- Standardized tool schemas with automatic validation
- Hook system for intercepting every tool call (tracking, logging, progress events)
- Sub-agent isolation — each agent sees only its own tools

### Why Client-Side Itinerary?
The backend returns raw data (weather, flights, hotels, discoveries). The **Itinerary tab builds the day-by-day plan client-side** by combining the best options:
- Morning/afternoon attractions from discovery
- Daily restaurant assignment (cycled through available)
- Weather overlay per day
- Flight info on first/last day

This approach means any data update (via chat) automatically reflects in the itinerary without backend re-computation.

---

## 🐛 Notable Challenges Solved

| Challenge | Symptom | Solution |
|-----------|---------|----------|
| SDK hook signature mismatch | `'NoneType' object has no attribute 'items'` | Rewrote hooks to accept `(input_data, tool_use_id, context)` |
| SerpAPI requires IATA codes | Every flight search returned 400 | Built 80+ city→IATA lookup with `_resolve_iata()` |
| Parallel agent interleaving | Tool results attached to wrong agent | Backwards search matching on `tool_use_id` |
| CORS + credentials conflict | Silent `Failed to fetch` with no error | Removed `credentials: "include"`, set `allow_credentials=False` |
| Weather API 5-day limit | Empty weather for future trips | Climate estimate fallback using latitude + hemisphere + seasonality |
| Chat context loss | LLM asks "where are you going?" after planning | `_build_plan_context()` injects full plan state into new chat client |
| Chat didn't update frontend | LLM replied conversationally, no agent calls | Added `<chat_mode>` prompt section + `tracker.reset()` + `updated_plan` field |
| Discovery ignored cuisine type | "I want Indian food" → still showed Italian | Added `cuisine_preferences` param to discovery tool + search query |
| Budget used hardcoded city tiers | Same food cost for $2K and $10K trips | Replaced with travel style multipliers derived from actual budget |
| Chat overwrote AI summary | Original travel summary replaced by chat reply | Stored `llm_summary` in `SessionState`, stopped overwriting on chat turns |

---

## 📝 Environment Variables

```env
ANTHROPIC_API_KEY=sk-ant-...
SERPAPI_API_KEY=...
OPENWEATHERMAP_API_KEY=...
ORCHESTRATOR_MODEL=sonnet       # optional, default: sonnet
SUBAGENT_MODEL=haiku            # optional, default: haiku
```

---

## 📄 License

MIT

---

Built with [Claude Agent SDK](https://docs.anthropic.com/), [FastAPI](https://fastapi.tiangolo.com/), [React](https://react.dev/), [Vite](https://vitejs.dev/), [shadcn/ui](https://ui.shadcn.com/), and [SerpAPI](https://serpapi.com/).
