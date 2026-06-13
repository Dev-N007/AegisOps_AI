# AegisOps AI — Autonomous Incident Intelligence Platform

> **From Alert to Resolution — Powered by Autonomous SRE Agents**  
> Category: Generative AI + Agentic AI  
> Team: **Prompt Surfers** (Nilesh Raj, Abhinav Kumar Rai, Tarun Khatod)

---

## Architecture Overview

AegisOps AI acts as an autonomous Site Reliability Engineer (SRE) to triage and resolve system incidents. Instead of simple alerts, it models the investigation cycle as a sequential LangGraph workflow.

```
                  [Alert Alert Triggered]
                             │
                             ▼
                    ┌─────────────────┐
                    │   Alert Agent   │ (Anomaly & Severity Triage)
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    Log Agent    │ (Pattern & Error Clustering)
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    RCA Agent    │ (Log-to-Metric Correlation)
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Knowledge Agent │ (ChromaDB runbook lookup)
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │Resolution Agent │ (Risk-assessed SRE actions)
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Comm Agent     │ (Post-Mortem Markdown Report)
                    └────────┬────────┘
                             │
                             ▼
               [Executive Incident Report UI]
```

### Key Technical Specs

- **LangGraph State Orchestration**: LangGraph orchestrates the multi-agent nodes. Nodes communicate only by updating a shared transactional `IncidentState` model. No direct node-to-node routing.
- **Relational & Vector Hybrid DB**: Database state is persisted in PostgreSQL (with local SQLite fallback), and runbook document vectors are indexed in ChromaDB.
- **Custom Hybrid Embeddings**: In the absence of network keys, a zero-dependency local TF-IDF cosine-similarity projection generates embeddings for ChromaDB retrieval, ensuring offline resilience.
- **AI Simulation (What-If Sandbox)**: The What-If Agent runs predictive models (e.g. Monte Carlo or pattern classification) to compute downtime and recovery risks for human operator commands before deployment.

---

## Directory Structure

```
aegisops-ai/
├── backend/                  # Python FastAPI Backend
│   ├── app/
│   │   ├── agents/           # LangGraph Agent Nodes
│   │   │   ├── alert_agent/
│   │   │   ├── log_agent/
│   │   │   ├── root_cause_agent/
│   │   │   ├── knowledge_agent/
│   │   │   ├── resolution_agent/
│   │   │   ├── communication_agent/
│   │   │   └── simulation_agent/ # What-if simulator
│   │   ├── api/              # API Endpoints
│   │   │   ├── routes/
│   │   │   └── controllers/
│   │   ├── database/         # Database models & sessions
│   │   ├── services/         # Incident, Agent & Vector DB services
│   │   ├── langgraph/        # orchestrator.py (StateGraph Definition)
│   │   └── rag/              # Ingestion & retrieval code
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                 # Next.js 15 React Frontend
│   ├── src/
│   │   ├── app/              # App Router Pages (dashboard, incidents, agents, analytics, settings)
│   │   ├── components/       # UI Components (visualizations, timeline, agent network)
│   │   ├── hooks/            # React Hooks
│   │   ├── services/         # API fetchers
│   │   ├── types/            # TypeScript interfaces
│   │   └── lib/              # Styling utilities
│   ├── tailwind.config.ts
│   └── package.json
├── shared/                   # Common configuration and schemas
├── docs/                     # API Docs, Setup Guide & Architecture diagram
├── knowledge/                # Markdown runbooks, logs, and guides for ingestion
└── docker-compose.yml        # Orchestrates Postgres, Chroma, Backend, and Frontend
```

---

## Getting Started (Local Development)

To run the platform immediately on your system, follow the steps below:

### 1. Prerequisites
- **Node.js**: v18+ (tested on v22)
- **Python**: v3.12+

### 2. Backend Setup
1. Open a terminal and navigate to `/backend`.
2. Configure `.env` file (see `.env.example`). You can leave `GEMINI_API_KEY` blank to test in **Simulation Mode** (which loads pre-generated Gemini traces automatically).
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Seed database and ChromaDB knowledge files:
   ```bash
   python app/database/seed.py
   ```
5. Start FastAPI API:
   ```bash
   python main.py
   ```
   The backend will start on `http://localhost:8000`.

### 3. Frontend Setup
1. Navigate to `/frontend`.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Next.js development server:
   ```bash
   npm run dev
   ```
4. Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Production Deployment (Docker)

To run the entire suite under production conditions (including PostgreSQL and dependencies) using Docker Compose:

1. In the root directory, run:
   ```bash
   docker-compose up --build
   ```
2. The services will bind to:
   - **Frontend UI**: `http://localhost:3000`
   - **FastAPI Backend**: `http://localhost:8000`
   - **PostgreSQL Database**: `localhost:5432`
