# GenAI-Powered Product Decision & Trade-off Intelligence System

A fully functional, locally runnable full-stack application that provides **structured, explainable decision logic** for product trade-offs.

```
┌──────────────────────────────────────────────────────────┐
│                   Architecture Overview                   │
│                                                          │
│  ┌───────────────┐         ┌───────────────────────────┐ │
│  │  React + Vite │ ──HTTP──│       FastAPI + Uvicorn   │ │
│  │  TypeScript   │         │                           │ │
│  │  Material UI  │         │  ┌─────────────────────┐  │ │
│  │  Recharts     │         │  │  Scoring Engine      │  │ │
│  │  react-hook-  │         │  │  (Deterministic,     │  │ │
│  │   form        │         │  │   Rule-Based)        │  │ │
│  │  Port: 5173   │         │  └─────────────────────┘  │ │
│  └───────────────┘         │  SQLAlchemy 2.x + Alembic │ │
│                            │  JWT Auth + RBAC          │ │
│                            │  Port: 8000               │ │
│                            └────────────┬──────────────┘ │
│                                         │                 │
│                            ┌────────────▼──────────────┐ │
│                            │     PostgreSQL (local)    │ │
│                            │     Port: 5432            │ │
│                            └───────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

## Folder Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app entry point
│   │   ├── config.py               # Pydantic settings
│   │   ├── database.py             # SQLAlchemy engine + session
│   │   ├── seed.py                 # Seed script (3 realistic scenarios)
│   │   ├── models/                 # SQLAlchemy ORM models
│   │   │   ├── user.py             # User, Role (JWT + RBAC)
│   │   │   ├── workspace.py        # Workspace model
│   │   │   ├── decision.py         # Decision, Option, Constraint, Version
│   │   │   ├── criteria.py         # Criterion, Weight, OptionScore
│   │   │   └── collaboration.py    # Comment, AuditLog
│   │   ├── schemas/                # Pydantic v2 schemas
│   │   ├── core/
│   │   │   ├── security.py         # JWT + bcrypt
│   │   │   ├── deps.py             # FastAPI dependencies (auth/RBAC)
│   │   │   └── scoring_engine.py   # 🧠 Deterministic scoring engine
│   │   └── routers/                # FastAPI routers (all endpoints)
│   ├── alembic/                    # DB migrations
│   ├── tests/                      # pytest tests (31 tests)
│   ├── requirements.txt
│   ├── alembic.ini
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── App.tsx                 # React app with routing
    │   ├── main.tsx
    │   ├── api/
    │   │   ├── client.ts           # Axios instance + interceptors
    │   │   ├── endpoints.ts        # All API call functions
    │   │   └── types.ts            # TypeScript interfaces
    │   ├── contexts/
    │   │   └── AuthContext.tsx     # JWT auth context
    │   ├── components/
    │   │   ├── Layout.tsx          # Sidebar + AppBar
    │   │   └── ProtectedRoute.tsx  # Auth guard
    │   ├── pages/
    │   │   ├── LoginPage.tsx       # Login + Register
    │   │   ├── WorkspacesPage.tsx  # Workspace list + create
    │   │   ├── WorkspaceDetailPage.tsx  # Decision list
    │   │   ├── DecisionDetailPage.tsx   # Full decision editor + evaluate
    │   │   ├── PrioritizePage.tsx  # Impact vs Effort quadrant
    │   │   └── SettingsPage.tsx    # Criteria templates + config
    │   └── test/
    │       └── smoke.test.tsx      # React Testing Library (12 tests)
    ├── package.json
    └── vite.config.ts
```

---

## Windows 11 Local Setup (PowerShell)

### 1. Install Prerequisites

```powershell
# Node.js LTS
winget install OpenJS.NodeJS.LTS

# Python 3.11+
winget install Python.Python.3.11

# PostgreSQL 15 or 16
winget install PostgreSQL.PostgreSQL
```

Restart your terminal after installation.

### 2. Create PostgreSQL Database

Open a PowerShell as Administrator and run:

```powershell
# Start PostgreSQL service (if not already running)
Start-Service postgresql*

# Open psql (adjust path to match your PostgreSQL version)
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres
```

In the psql prompt:

```sql
CREATE USER decision_user WITH PASSWORD 'decision_pass';
CREATE DATABASE decision_db OWNER decision_user;
GRANT ALL PRIVILEGES ON DATABASE decision_db TO decision_user;
\q
```

### 3. Backend Setup

```powershell
cd backend

# Create and activate virtual environment
py -m venv .venv
.\.venv\Scripts\Activate.ps1

# If you get an execution policy error:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install dependencies
pip install -r requirements.txt

# Create environment file
Copy-Item .env.example .env
# Edit .env if needed (defaults work with the database created above)

# Run database migrations
alembic upgrade head

# Seed the database with 3 realistic scenarios
py -m app.seed
```

### 4. Run Backend

```powershell
# In backend directory with .venv activated:
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API docs available at: http://localhost:8000/docs

### 5. Frontend Setup

```powershell
# In a new PowerShell window:
cd frontend
npm install
npm run dev
```

Frontend available at: http://localhost:5173

### 6. Login

Use these seeded credentials:

| Email | Password | Role |
|-------|----------|------|
| admin@example.com | Admin123! | Admin |
| pm@example.com | PM123! | PM |
| viewer@example.com | Viewer123! | Viewer |

---

## Features

### 🔐 Authentication & RBAC
- JWT-based auth (no external services)
- Roles: Admin, PM, Viewer
- Protected routes with middleware

### 🗂 Workspace Management
- Create/read/update/delete workspaces
- Workspace context: name, description, goals, context

### 📋 Decision Management
- Decision CRUD with status flow: Draft → Reviewed → Approved
- Problem statement, success metrics
- Constraints editor (time, budget, technical, organizational)
- Multiple options/alternatives (A/B/C)
- Editable criteria weights with sliders

### 🧠 Deterministic Scoring Engine (Core Logic)
- **Weighted scoring** across 8 criteria (1-10 scale per criterion)
- **Explainable outputs**: per-criterion scores with explanations
- **Total weighted score** (normalised 0-100)
- **Ranking** with risks and recommendations
- **Trade-off matrix** for visualization
- **Rule-based narrative** generation
- All inputs, weights, intermediate values persisted in DB (JSON)

**8 Criteria:**
1. User Value
2. Engineering Effort (lower = higher score)
3. Time-to-Market
4. Risk (lower = higher score)
5. Cost (lower = higher score)
6. Maintainability
7. Strategic Alignment
8. Compliance/Privacy

### 📊 Prioritization Dashboard
- Rank multiple decisions by score
- **Impact vs Effort quadrant chart** (scatter plot)
- Suggested MVP scope vs Later phases
- JSON export

### 💬 Collaboration & Audit
- Comments on decisions
- Version history snapshots
- Audit logs (Admin-only endpoint)

---

## Seed Scenarios & Expected Rankings

### 1. Pricing Experiment Rollout
**Options:** A/B Framework | Feature Flags | Manual Rollout  
**Expected Ranking:** Feature Flags 🥇 > Manual Rollout 🥈 > A/B Framework 🥉  
_Feature Flags wins because it's proven, low-risk, uses existing infrastructure, and is cost-effective._

### 2. Search Upgrade Strategy
**Options:** Keyword Enhancement | Semantic Search | Hybrid Search  
**Expected Ranking:** Hybrid Search 🥇 > Keyword Enhancement 🥈 > Semantic Search 🥉  
_Hybrid wins by balancing user value with lower risk than pure semantic and better quality than keyword alone._

### 3. Mobile MVP Scope Definition
**Options:** Core Flows Only | Core + Onboarding | Full Feature Parity  
**Expected Ranking:** Core + Onboarding 🥇 > Core Flows Only 🥈 > Full Feature Parity 🥉  
_Core + Onboarding wins for user value while Full Parity ranks last due to high effort, cost, and risk._

---

## Running Tests

### Backend (31 tests)
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest tests/ -v
```

### Frontend (12 tests)
```powershell
cd frontend
npm test
```

---

## Troubleshooting

### CORS errors
Ensure `CORS_ORIGINS=http://localhost:5173` is set in `backend/.env`.

### Port conflicts
- Backend: Change `--port 8000` in the uvicorn command
- Frontend: Change `port: 5173` in `vite.config.ts`

### PostgreSQL service not running
```powershell
Start-Service postgresql*
# or
net start postgresql-x64-16
```

### Execution policy error for .venv activation
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### psycopg driver issues
```powershell
pip install psycopg[binary]
```

### Missing Python
```powershell
winget install Python.Python.3.11 --force
# Ensure Python is in PATH:
py --version
```

---

## Optional LLM Integration

Set these in `backend/.env`:
```env
LLM_PROVIDER=openai
LLM_API_KEY=sk-...
```

When configured, the narrative text in evaluation results can be enhanced by the LLM. **Numeric scores and rankings are never modified by LLM output.** The UI labels LLM-assisted text with a chip.

Without an API key, the system runs fully with the deterministic scoring engine.
