# 📁 PROJECT STRUCTURE

## Complete Folder Structure

```
Budgeting app/
│
├── 📄 README.md                    # Project overview
├── 📄 ARCHITECTURE.md              # System architecture & design
├── 📄 SETUP_GUIDE.md               # Complete setup instructions
├── 📄 IMPLEMENTATION_PLAN.md       # Step-by-step implementation plan
├── 📄 PROJECT_EVALUATION.md        # Milestone coverage & evaluation
├── 📄 CODE_SAMPLES.md              # Usage examples & snippets
├── 📄 CHECKPOINTS.md               # Development checkpoints
├── 📄 ATTRIBUTIONS.md              # Credits & licenses
│
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env.example                 # Environment variables template
├── 📄 .gitignore                   # Git ignore rules
├── 📄 package.json                 # Node.js dependencies (frontend)
├── 📄 vite.config.ts               # Vite configuration
├── 📄 postcss.config.mjs           # PostCSS configuration
│
├── 📄 database_schema.sql          # Complete database schema
│
├── 🐍 backend/                     # Python backend
│   ├── __init__.py
│   ├── 📄 main.py                  # FastAPI application entry point
│   ├── 📄 config.py                # Configuration management
│   │
│   ├── 🔐 api/                     # REST API endpoints
│   │   ├── __init__.py
│   │   ├── 📄 auth.py              # Authentication endpoints (JWT)
│   │   ├── 📄 expenses.py          # Expense CRUD endpoints
│   │   ├── 📄 budgets.py           # Budget management endpoints
│   │   ├── 📄 voice.py             # Voice service (Whisper STT)
│   │   ├── 📄 voice_routes.py      # Voice API endpoints
│   │   ├── 📄 cost_of_living.py    # Cost-of-living service
│   │   └── 📄 cost_routes.py       # Cost-of-living endpoints
│   │
│   ├── 🗄️ database/                # Database layer
│   │   ├── __init__.py
│   │   └── 📄 client.py            # Supabase client wrapper
│   │
│   ├── 🤖 llm/                     # LLM integration
│   │   ├── __init__.py
│   │   ├── 📄 client.py            # LLM client (Ollama/Groq/OpenAI)
│   │   ├── 📄 pipeline.py          # Two-LLM pipeline orchestration
│   │   ├── 📄 prompts.py           # Prompt templates
│   │   └── 📄 schemas.py           # JSON schemas for function calling
│   │
│   └── 🛠️ utils/                   # Utilities
│       ├── __init__.py
│       └── 📄 logger.py            # Logging configuration
│
├── 🎨 src/                         # Frontend source (React)
│   ├── 📄 main.tsx                 # Entry point
│   │
│   ├── 📱 app/                     # Application components
│   │   ├── 📄 App.tsx              # Main app component
│   │   │
│   │   └── components/             # UI components
│   │       ├── 📄 BudgetBuddy.tsx
│   │       ├── 📄 BudgetSettings.tsx
│   │       ├── 📄 BudgetSummary.tsx
│   │       ├── 📄 CompanionSelector.tsx
│   │       ├── 📄 ExpenseList.tsx
│   │       ├── 📄 FriendshipStatus.tsx
│   │       ├── 📄 SpendingCalendar.tsx
│   │       ├── 📄 SpendingForm.tsx
│   │       ├── 📄 SpendingGraph.tsx
│   │       │
│   │       ├── figma/              # Figma-imported components
│   │       │   └── 📄 ImageWithFallback.tsx
│   │       │
│   │       └── ui/                 # Reusable UI components (shadcn)
│   │           ├── 📄 button.tsx
│   │           ├── 📄 input.tsx
│   │           ├── 📄 card.tsx
│   │           ├── 📄 dialog.tsx
│   │           ├── 📄 form.tsx
│   │           ├── 📄 calendar.tsx
│   │           ├── 📄 chart.tsx
│   │           └── ... (40+ components)
│   │
│   ├── 🎨 styles/                  # Stylesheets
│   │   ├── 📄 index.css            # Main styles
│   │   ├── 📄 tailwind.css         # Tailwind imports
│   │   ├── 📄 theme.css            # Theme variables
│   │   └── 📄 fonts.css            # Font definitions
│   │
│   └── 📦 assets/                  # Static assets
│
├── 🗄️ supabase/                    # Supabase configuration
│   └── functions/
│       └── server/
│           ├── 📄 index.tsx
│           └── 📄 kv_store.tsx
│
├── 🧪 tests/                       # Test files (to be created)
│   ├── __init__.py
│   ├── 📄 test_auth.py
│   ├── 📄 test_expenses.py
│   ├── 📄 test_budgets.py
│   ├── 📄 test_llm_pipeline.py
│   └── 📄 test_voice.py
│
├── 📝 logs/                        # Application logs (created at runtime)
│   └── app.log
│
├── 🐳 docker/                      # Docker configuration (optional)
│   ├── 📄 Dockerfile
│   └── 📄 docker-compose.yml
│
└── 📖 guidelines/                  # Development guidelines
    └── 📄 Guidelines.md
```

---

## 📋 File-by-File Description

### Root Level

| File | Purpose | Status |
|------|---------|--------|
| `README.md` | Project overview and quick start | ✅ |
| `ARCHITECTURE.md` | System architecture diagrams | ✅ |
| `SETUP_GUIDE.md` | Complete setup instructions | ✅ |
| `IMPLEMENTATION_PLAN.md` | Development roadmap | ✅ |
| `PROJECT_EVALUATION.md` | Milestone checklist | ✅ |
| `CODE_SAMPLES.md` | Usage examples | ✅ |
| `requirements.txt` | Python dependencies | ✅ |
| `.env.example` | Environment template | ⚠️ To create |
| `database_schema.sql` | PostgreSQL schema | ✅ |

### Backend (`backend/`)

#### Core Files
- **`main.py`**: FastAPI application, route registration, middleware
- **`config.py`**: Environment variable loading, settings management

#### API Layer (`backend/api/`)
- **`auth.py`**: Username-only login, JWT token generation
- **`expenses.py`**: Expense CRUD with LLM processing
- **`budgets.py`**: Budget management endpoints
- **`voice.py`**: Whisper STT service
- **`voice_routes.py`**: Voice API endpoints
- **`cost_of_living.py`**: Cost-of-living API integration
- **`cost_routes.py`**: Cost-of-living endpoints

#### Database Layer (`backend/database/`)
- **`client.py`**: Supabase client wrapper, CRUD operations

#### LLM Layer (`backend/llm/`)
- **`client.py`**: Multi-provider LLM client (Ollama/Groq/OpenAI)
- **`pipeline.py`**: Two-stage LLM pipeline (extraction → validation)
- **`prompts.py`**: Prompt templates with examples
- **`schemas.py`**: JSON schemas for structured outputs

#### Utils (`backend/utils/`)
- **`logger.py`**: Centralized logging configuration

### Frontend (`src/`)

#### React Application
- **`main.tsx`**: React entry point
- **`App.tsx`**: Main application component

#### Components (`src/app/components/`)
- Budget tracking UI components
- Expense input forms
- Calendar views
- Graph visualizations
- AI companion interface

#### Styles (`src/styles/`)
- Tailwind CSS configuration
- Custom theme variables
- Font imports

---

## 🔑 Key Modules & Their Responsibilities

### 1. Authentication Module
```
backend/api/auth.py
├── POST /auth/login          # Username-only login
├── GET /auth/me              # Get current user
├── POST /auth/logout         # Logout
└── GET /auth/validate        # Validate token
```

### 2. Expense Management
```
backend/api/expenses.py
├── POST /expenses/add        # Add via natural language
├── POST /expenses/add-direct # Add structured data
├── GET /expenses/list        # List with filters
├── GET /expenses/summary     # Category breakdown
└── DELETE /expenses/{id}     # Delete expense
```

### 3. Budget Management
```
backend/api/budgets.py
├── POST /budgets/set         # Set/update budget
├── GET /budgets/list         # List all with status
├── GET /budgets/status/{cat} # Specific category
└── DELETE /budgets/{id}      # Delete budget
```

### 4. Voice Input
```
backend/api/voice.py + voice_routes.py
├── POST /voice/transcribe           # Upload audio file
├── POST /voice/record-and-transcribe # Server recording
└── GET /voice/health                # Service health check
```

### 5. Cost of Living
```
backend/api/cost_of_living.py + cost_routes.py
├── GET /cost-of-living/city/{name}      # City data
├── GET /cost-of-living/compare          # User comparison
└── GET /cost-of-living/insights/{user}  # Spending insights
```

### 6. LLM Pipeline
```
backend/llm/pipeline.py
├── extract_expense_data()    # LLM #1: Extract structured data
└── validate_expense_data()   # LLM #2: Validate & normalize
```

---

## 📦 Dependencies by Category

### Core Framework (FastAPI)
```
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic==2.9.0
python-multipart==0.0.12
```

### Database (Supabase)
```
supabase==2.9.0
postgrest==0.16.11
```

### LLM Integration
```
ollama==0.3.3              # Local LLM
groq==0.11.0               # Groq API (optional)
openai==1.54.0             # OpenAI API (optional)
httpx==0.27.2              # HTTP client
jsonschema==4.23.0         # Schema validation
```

### Voice (Whisper)
```
openai-whisper==20240930   # Speech-to-text
sounddevice==0.5.1         # Audio recording
soundfile==0.12.1          # Audio file handling
numpy==1.26.4              # Array processing
torch==2.5.1               # PyTorch (Whisper backend)
torchaudio==2.5.1          # Audio processing
```

### Authentication
```
PyJWT==2.8.0               # JWT tokens
python-dotenv==1.0.1       # Environment variables
```

### Development
```
pytest==8.3.3              # Testing
black==24.10.0             # Code formatting
mypy==1.13.0               # Type checking
```

---

## 🚀 Getting Started

### 1. Clone/Navigate to Project
```bash
cd "c:\Users\jyoth\Downloads\Project_0210\Budgeting app"
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with your Supabase credentials
```

### 5. Run Database Schema
```bash
# Copy contents of database_schema.sql
# Paste in Supabase SQL Editor
```

### 6. Start Backend
```bash
python -m backend.main
# API available at http://localhost:8000
```

### 7. Access Documentation
```
http://localhost:8000/docs        # Swagger UI
http://localhost:8000/redoc       # ReDoc
```

---

## 📊 Code Statistics

| Metric | Count |
|--------|-------|
| **Python Files** | 15+ |
| **Lines of Code** | ~3,500+ |
| **API Endpoints** | 20+ |
| **Database Tables** | 5 |
| **Documentation Pages** | 6 |
| **JSON Schemas** | 4 |
| **Prompt Templates** | 6 |

---

## 🎯 Module Dependencies

```
main.py
  ├── config.py
  ├── api/
  │   ├── auth.py → database/client.py
  │   ├── expenses.py → llm/pipeline.py → llm/client.py
  │   │                → database/client.py
  │   ├── budgets.py → database/client.py
  │   ├── voice_routes.py → api/voice.py
  │   └── cost_routes.py → api/cost_of_living.py
  │                      → database/client.py
  └── utils/logger.py
```

---

## 🔐 Environment Variables Required

```env
# Critical
SUPABASE_URL=           # From Supabase dashboard
SUPABASE_KEY=           # From Supabase dashboard

# LLM (choose one)
LLM_PROVIDER=ollama     # or groq, openai
OLLAMA_BASE_URL=        # For local Ollama
GROQ_API_KEY=           # For Groq API
OPENAI_API_KEY=         # For OpenAI

# Optional
RAPIDAPI_KEY=           # For real cost-of-living data
WHISPER_MODEL_SIZE=base # tiny, base, small, medium, large
```

---

## 📖 Documentation Map

| Document | Audience | Purpose |
|----------|----------|---------|
| `README.md` | All | Quick overview |
| `ARCHITECTURE.md` | Developers | System design |
| `SETUP_GUIDE.md` | Operators | Installation |
| `IMPLEMENTATION_PLAN.md` | Developers | Development roadmap |
| `PROJECT_EVALUATION.md` | Evaluators | Milestone coverage |
| `CODE_SAMPLES.md` | Users | Usage examples |

---

**Last Updated:** February 2026  
**Project Structure Version:** 1.0
