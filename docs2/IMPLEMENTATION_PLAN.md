# LLM-Powered Expense Tracking App - Implementation Plan

## 🎯 Project Overview
A lightweight, Python-based expense tracking system with LLM integration, multimodal input, and structured function calling.

---

## 📋 Implementation Plan (Step-by-Step)

### Phase 1: Project Setup (CHECKPOINT_1)
**Objective**: Set up project structure, dependencies, and basic configuration

1. Create folder structure
2. Install Python dependencies
3. Set up environment variables
4. Configure Supabase connection
5. Create basic configuration module
6. Verify imports work

**Deliverables**:
- Folder structure created
- `requirements.txt` created
- `.env.example` created
- Basic config module working

---

### Phase 2: Authentication (CHECKPOINT_2)
**Objective**: Implement username-only authentication

1. Create user schema in Supabase
2. Implement username validation
3. Create authentication module
4. Add session management
5. Test user creation and login

**Deliverables**:
- User table in Supabase
- `auth.py` module
- Username validation working
- Simple login endpoint

---

### Phase 3: Database Schema & Integration (CHECKPOINT_3)
**Objective**: Set up complete database schema and connection layer

1. Design all database tables
2. Create SQL migration scripts
3. Implement database client wrapper
4. Add CRUD operations
5. Test all database operations

**Deliverables**:
- Complete SQL schema
- `database.py` module
- Migration scripts
- CRUD operations tested

---

### Phase 4: Multimodal Input (CHECKPOINT_4)
**Objective**: Implement text and voice input processing

1. Set up Whisper for speech-to-text (local)
2. Create audio input handler
3. Implement text input handler
4. Create unified input processor
5. Test both input modes

**Deliverables**:
- `voice_input.py` module
- Whisper integration working
- Audio → text conversion tested
- Unified input interface

---

### Phase 5: Two-LLM Pipeline (CHECKPOINT_5)
**Objective**: Implement dual-LLM architecture for extraction and validation

1. Set up LLM client (Ollama/free API)
2. Implement LLM #1: Data extraction
3. Implement LLM #2: Validation/categorization
4. Create prompt templates
5. Test pipeline end-to-end

**Deliverables**:
- `llm_client.py` module
- `llm_pipeline.py` module
- Prompt templates
- Two-stage processing working

---

### Phase 6: Structured Function Calling (CHECKPOINT_6)
**Objective**: Implement JSON schema-based structured outputs

1. Define JSON schemas for functions
2. Implement schema validation
3. Create function dispatcher
4. Add error handling for invalid outputs
5. Test schema enforcement

**Deliverables**:
- `schemas.py` with JSON schemas
- `function_calling.py` module
- Schema validation working
- Error handling tested

---

### Phase 7: Cost-of-Living API Integration (CHECKPOINT_7)
**Objective**: Integrate external cost-of-living data

1. Research and select free COL API
2. Implement API client with rate limiting
3. Create data fetch and cache logic
4. Store COL data in database
5. Test API integration with fallbacks

**Deliverables**:
- `cost_of_living.py` module
- API client with error handling
- Caching mechanism
- Database storage for COL data

---

### Phase 8: Calendar Integration (CHECKPOINT_8)
**Objective**: Add expense entries to calendar

1. Create calendar table schema
2. Implement calendar entry creation
3. Link expenses to calendar
4. Add date parsing logic
5. Test calendar functionality

**Deliverables**:
- Calendar table in database
- `calendar_manager.py` module
- Automatic entry creation
- Date handling tested

---

### Phase 9: API Endpoints & Integration (CHECKPOINT_9)
**Objective**: Create REST API for frontend integration

1. Set up FastAPI server
2. Create all REST endpoints
3. Add request/response validation
4. Implement error handling
5. Test all endpoints

**Deliverables**:
- `api.py` with FastAPI app
- All CRUD endpoints
- API documentation
- Integration tested

---

### Phase 10: Final Validation & Documentation (CHECKPOINT_10)
**Objective**: Complete testing, documentation, and milestone validation

1. End-to-end testing
2. Complete README documentation
3. Add usage examples
4. Validate all milestones
5. Create deployment guide

**Deliverables**:
- Complete README.md
- Usage examples
- Milestone checklist
- Deployment instructions

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                        │
│                   [Existing Budgeting App]                   │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/REST API
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    PYTHON BACKEND                            │
│  ┌────────────────────────────────────────────────────┐     │
│  │              FastAPI Server                        │     │
│  │  - Authentication endpoints                        │     │
│  │  - Expense CRUD endpoints                          │     │
│  │  - Voice input endpoint                            │     │
│  │  - Budget management                               │     │
│  └──────┬─────────────────────────────────────────────┘     │
│         │                                                    │
│  ┌──────▼──────────────────────────────────────────────┐   │
│  │         Input Processing Layer                      │   │
│  │  ┌──────────────┐        ┌──────────────┐          │   │
│  │  │ Text Input   │        │ Voice Input  │          │   │
│  │  │ Handler      │        │ (Whisper)    │          │   │
│  │  └──────┬───────┘        └──────┬───────┘          │   │
│  │         └────────┬───────────────┘                  │   │
│  └──────────────────┼────────────────────────────────┘    │
│                     │                                       │
│  ┌──────────────────▼────────────────────────────────┐    │
│  │          Two-LLM Pipeline                          │    │
│  │  ┌───────────────────────────────────────────┐    │    │
│  │  │  LLM #1: Extraction                       │    │    │
│  │  │  - Parse expense details                  │    │    │
│  │  │  - Extract: amount, category, date, desc │    │    │
│  │  └──────────────┬────────────────────────────┘    │    │
│  │                 │                                  │    │
│  │  ┌──────────────▼────────────────────────────┐    │    │
│  │  │  LLM #2: Validation & Categorization      │    │    │
│  │  │  - Validate extracted data                │    │    │
│  │  │  - Normalize categories                   │    │    │
│  │  │  - Enrich with context                    │    │    │
│  │  └──────────────┬────────────────────────────┘    │    │
│  └─────────────────┼───────────────────────────────┘     │
│                    │                                       │
│  ┌─────────────────▼───────────────────────────────────┐  │
│  │      Structured Function Calling                    │  │
│  │  - JSON Schema Validation                           │  │
│  │  - Function: add_expense(...)                       │  │
│  │  - Function: set_budget(...)                        │  │
│  │  - Schema enforcement & error handling              │  │
│  └─────────────────┬───────────────────────────────────┘  │
│                    │                                       │
│  ┌─────────────────▼───────────────────────────────────┐  │
│  │         Business Logic Layer                        │  │
│  │  - Expense manager                                  │  │
│  │  - Budget manager                                   │  │
│  │  - Calendar manager                                 │  │
│  │  - Cost-of-living analyzer                          │  │
│  └─────────────────┬───────────────────────────────────┘  │
└────────────────────┼───────────────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────────────┐
│                  DATA LAYER                                 │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │   Supabase DB    │         │  External APIs   │         │
│  │  - users         │         │ - Cost of Living │         │
│  │  - expenses      │         │ - (Numbeo API)   │         │
│  │  - budgets       │         │                  │         │
│  │  - calendar      │         └──────────────────┘         │
│  │  - cost_index    │                                      │
│  └──────────────────┘                                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    LLM BACKEND                               │
│  ┌──────────────────────────────────────────────────┐       │
│  │  Ollama (Local) OR Free API                      │       │
│  │  - Model: LLaMA 3.2 / Mistral / GPT-4o-mini     │       │
│  │  - Structured output support                     │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Folder Structure

```
Budgeting app/
├── backend/                    # Python backend
│   ├── __init__.py
│   ├── main.py                # FastAPI entry point
│   ├── config.py              # Configuration management
│   │
│   ├── api/                   # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication endpoints
│   │   ├── expenses.py       # Expense CRUD endpoints
│   │   ├── budgets.py        # Budget endpoints
│   │   ├── voice.py          # Voice input endpoint
│   │   └── cost_of_living.py # COL endpoints
│   │
│   ├── core/                  # Core business logic
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication logic
│   │   ├── expense_manager.py
│   │   ├── budget_manager.py
│   │   ├── calendar_manager.py
│   │   └── cost_analyzer.py
│   │
│   ├── llm/                   # LLM integration
│   │   ├── __init__.py
│   │   ├── client.py         # LLM client wrapper
│   │   ├── pipeline.py       # Two-LLM pipeline
│   │   ├── prompts.py        # Prompt templates
│   │   └── schemas.py        # JSON schemas for function calling
│   │
│   ├── input/                 # Input processing
│   │   ├── __init__.py
│   │   ├── text_input.py
│   │   ├── voice_input.py    # Whisper integration
│   │   └── input_processor.py
│   │
│   ├── database/              # Database layer
│   │   ├── __init__.py
│   │   ├── client.py         # Supabase client
│   │   ├── models.py         # Data models
│   │   └── migrations/       # SQL migration scripts
│   │       ├── 001_create_users.sql
│   │       ├── 002_create_expenses.sql
│   │       ├── 003_create_budgets.sql
│   │       ├── 004_create_calendar.sql
│   │       └── 005_create_cost_index.sql
│   │
│   ├── external/              # External API integrations
│   │   ├── __init__.py
│   │   └── cost_of_living_api.py
│   │
│   └── utils/                 # Utilities
│       ├── __init__.py
│       ├── validators.py
│       ├── logger.py
│       └── cache.py
│
├── src/                       # Frontend (existing React app)
├── scripts/                   # Utility scripts
│   ├── setup_database.py
│   ├── test_llm_pipeline.py
│   └── test_voice_input.py
│
├── tests/                     # Tests
│   ├── test_auth.py
│   ├── test_llm_pipeline.py
│   ├── test_expenses.py
│   └── test_voice_input.py
│
├── .env.example              # Environment variables template
├── requirements.txt          # Python dependencies
├── README.md                 # Main documentation
├── IMPLEMENTATION_PLAN.md    # This file
└── CHECKPOINTS.md            # Checkpoint tracking
```

---

## 🔧 Technology Stack (All Free/Open Source)

### Backend
- **Python 3.10+**: Main language
- **FastAPI**: REST API framework
- **Supabase**: PostgreSQL database (free tier)
- **Ollama**: Local LLM runtime (free)
- **Whisper.cpp**: Speech-to-text (local, free)

### LLM Options (Choose one)
1. **Ollama + LLaMA 3.2** (local, completely free)
2. **Groq API** (fast inference, generous free tier)
3. **OpenAI GPT-4o-mini** (very cheap, $0.15/1M input tokens)

### External APIs
- **Numbeo API**: Cost-of-living data (free tier available)
- Alternative: **Teleport API** (free)

### Storage
- **Supabase**: 500MB free, 50MB file uploads

---

## ✅ Milestone Coverage Checklist

This implementation satisfies all required milestones:

- [x] **LLM Integration**: Two-LLM pipeline with Ollama/Groq
- [x] **Prompt Design**: Template-based prompts in `prompts.py`
- [x] **Structured Outputs**: JSON schema validation
- [x] **Function Calling**: Schema-enforced `add_expense`, `set_budget`
- [x] **Multimodal Input**: Text + Voice (Whisper)
- [x] **External API Integration**: Cost-of-living API
- [x] **Persistent Storage**: Supabase PostgreSQL
- [x] **Basic Authentication**: Username-only auth
- [x] **Modular Architecture**: Clean separation of concerns
- [x] **Error Handling**: Try-catch, validation, fallbacks
- [x] **Deployment Feasibility**: Docker-ready, lightweight

---

## 🚀 Next Steps

1. Review this plan
2. Confirm technology choices
3. Set up Supabase account
4. Install Ollama (if using local LLM)
5. Begin CHECKPOINT_1 implementation

---

## 📝 Notes

- Each checkpoint must be verified before proceeding
- Keep all API usage within free tiers
- Test thoroughly at each stage
- Document any deviations from plan
