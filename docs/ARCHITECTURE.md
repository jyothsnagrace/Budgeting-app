# 🏗️ LLM-Powered Expense Tracking App - Architecture

## 📊 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER (Mobile/Web)                    │
│  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  Text Input     │  │  Voice Input     │  │  Visual UI       │  │
│  │  (Typing)       │  │  (Microphone)    │  │  (React/Native)  │  │
│  └────────┬────────┘  └─────────┬────────┘  └─────────┬────────┘  │
└───────────┼────────────────────────┼─────────────────────┼──────────┘
            │                        │                     │
            └────────────────────────┼─────────────────────┘
                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      API LAYER (FastAPI/Python)                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                     Authentication                            │  │
│  │              (Username-only, No Password)                     │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐   │
│  │   Voice API  │  │ Expense API  │  │   Budget API           │   │
│  │   /voice     │  │ /expenses    │  │   /budgets             │   │
│  └──────┬───────┘  └──────┬───────┘  └───────┬────────────────┘   │
│         │                  │                  │                     │
│         ▼                  ▼                  ▼                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │              MULTIMODAL INPUT PROCESSOR                      │  │
│  │  ┌─────────────────────┐  ┌──────────────────────────────┐  │  │
│  │  │  Whisper STT        │  │  Text Normalizer             │  │  │
│  │  │  (Local/OpenAI)     │  │  (Clean & Standardize)       │  │  │
│  │  └──────────┬──────────┘  └──────────────┬───────────────┘  │  │
│  └─────────────┼────────────────────────────┼──────────────────┘  │
│                │                             │                     │
│                └─────────────┬───────────────┘                     │
│                              ▼                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                 TWO-LLM PIPELINE                            │  │
│  │                                                             │  │
│  │   ┌─────────────────────────────────────────────────────┐  │  │
│  │   │  LLM #1: EXTRACTION                                 │  │  │
│  │   │  - Extract amount, category, description, date     │  │  │
│  │   │  - Handle colloquialisms                           │  │  │
│  │   │  - Assign confidence scores                        │  │  │
│  │   │  Model: Ollama (llama3.2) / Groq (free)            │  │  │
│  │   └──────────────────────┬──────────────────────────────┘  │  │
│  │                          ▼                                  │  │
│  │   ┌─────────────────────────────────────────────────────┐  │  │
│  │   │  LLM #2: VALIDATION & NORMALIZATION                │  │  │
│  │   │  - Validate extracted data                         │  │  │
│  │   │  - Normalize categories                            │  │  │
│  │   │  - Clean descriptions                              │  │  │
│  │   │  - Check reasonableness                            │  │  │
│  │   │  Model: Ollama (llama3.2) / Groq (free)            │  │  │
│  │   └──────────────────────┬──────────────────────────────┘  │  │
│  └──────────────────────────┼──────────────────────────────────┘  │
│                             ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │          STRUCTURED FUNCTION CALLING                        │  │
│  │  - JSON Schema Validation (jsonschema)                      │  │
│  │  - add_expense(amount, category, description, date)         │  │
│  │  - set_budget(category, amount, period)                     │  │
│  │  ✓ Pydantic Models for type safety                          │  │
│  └──────────────────────────┬──────────────────────────────────┘  │
└───────────────────────────────┼──────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   EXTERNAL INTEGRATIONS                              │
│  ┌──────────────────────┐  ┌───────────────────────────────────┐  │
│  │  Cost-of-Living API  │  │  Future: Banking APIs             │  │
│  │  (Numbeo/Free API)   │  │  (Open Banking, Plaid)            │  │
│  └──────────┬───────────┘  └───────────────────────────────────┘  │
└─────────────┼────────────────────────────────────────────────────────┘
              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DATABASE LAYER (Supabase)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │    users     │  │   expenses   │  │   budgets    │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│  ┌──────────────┐  ┌──────────────┐                               │
│  │   calendar   │  │ cost_of_living│                              │
│  └──────────────┘  └──────────────┘                               │
│                                                                      │
│  PostgreSQL (Free Tier: 500MB + 2GB Bandwidth/month)               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Component Architecture

### 1. **Authentication Layer**
```python
AuthService
├── validate_username(username: str) -> bool
├── create_user(username: str) -> User
├── get_user(username: str) -> Optional[User]
└── update_last_login(user_id: UUID)
```

**Design Decisions:**
- ✓ No password for simplicity (username-only)
- ✓ Session management via JWT tokens
- ✓ Username uniqueness enforced at DB level
- ⚠️ Production: Add proper OAuth/password auth

---

### 2. **Multimodal Input Layer**

#### 2a. Voice Input (Whisper)
```python
VoiceInputService
├── record_audio(duration: int) -> AudioFile
├── transcribe_audio(audio_file: AudioFile) -> str
└── process_voice_input(audio: bytes) -> str
```

**Technology Stack:**
- **Whisper** (OpenAI) - FREE options:
  1. **Local**: `openai-whisper` (runs on CPU/GPU)
  2. **Cloud**: Groq API (free tier: 1M tokens/day)
  3. **Alternative**: faster-whisper (optimized version)

**Audio Pipeline:**
```
Microphone → Record Audio → Whisper STT → Transcribed Text → LLM Pipeline
```

#### 2b. Text Input
```python
TextInputService
├── normalize_text(text: str) -> str
├── clean_input(text: str) -> str
└── validate_input(text: str) -> bool
```

---

### 3. **Two-LLM Pipeline**

#### Stage 1: Extraction LLM
```python
ExtractionService
├── extract_expense_data(text: str) -> ExtractedExpense
├── assign_confidence_scores(data: dict) -> dict
└── handle_ambiguities(data: dict) -> dict
```

**Input:** "Spent 45 bucks on pizza last night"
**Output:**
```json
{
  "amount": 45.0,
  "category": "food",
  "description": "pizza",
  "date": "2026-02-12",
  "confidence": {
    "amount": 1.0,
    "category": 0.95,
    "date": 0.9
  }
}
```

#### Stage 2: Validation LLM
```python
ValidationService
├── validate_extracted_data(data: ExtractedExpense) -> ValidationResult
├── normalize_category(category: str) -> str
├── check_reasonableness(amount: float, category: str) -> bool
└── suggest_corrections(data: dict) -> List[str]
```

**Validation Checks:**
- ✓ Amount is positive and reasonable
- ✓ Category matches predefined list
- ✓ Date is valid and not in future
- ✓ Description is meaningful

---

### 4. **Structured Function Calling**

```python
@dataclass
class AddExpenseFunction:
    name: str = "add_expense"
    schema: dict = ADD_EXPENSE_SCHEMA
    
    def validate(self, data: dict) -> ValidationResult:
        """Validate against JSON schema"""
        jsonschema.validate(data, self.schema)
        return ValidationResult(valid=True)
    
    async def execute(self, user_id: UUID, **params) -> Expense:
        """Execute function call"""
        expense = await db.create_expense(user_id, **params)
        await db.create_calendar_entry(expense)
        return expense
```

**Schemas:**
- `add_expense(amount, category, description, date)`
- `set_budget(category, amount, period)`
- `get_expenses(start_date, end_date, category)`
- `get_budget_status(category, period)`

---

### 5. **Database Layer (Supabase)**

#### Schema Design
```sql
-- Users: Minimal auth
users (id UUID, username VARCHAR UNIQUE, created_at TIMESTAMP)

-- Expenses: Core data
expenses (id UUID, user_id UUID, amount DECIMAL, category VARCHAR, 
          description TEXT, date DATE, input_method VARCHAR,
          llm_extracted JSONB, llm_validated JSONB)

-- Budgets: Spending limits
budgets (id UUID, user_id UUID, category VARCHAR, amount DECIMAL,
         period VARCHAR, start_date DATE)

-- Calendar: Visual tracking
calendar_entries (id UUID, user_id UUID, expense_id UUID,
                  event_date DATE, amount DECIMAL, category VARCHAR)

-- Cost of Living: External data cache
cost_of_living (city VARCHAR, country VARCHAR, cost_index FLOAT,
                rent_index FLOAT, updated_at TIMESTAMP)
```

---

### 6. **Cost-of-Living API Integration**

**Free Options:**
1. **Numbeo API** (Limited free tier)
2. **Cost of Living API** (RapidAPI - free tier)
3. **OpenWeatherMap** (city data)

```python
CostOfLivingService
├── fetch_city_data(city: str, country: str) -> CostData
├── cache_cost_data(data: CostData)
├── compare_user_expenses(user_id: UUID, city: str) -> Comparison
└── get_spending_insights(user_id: UUID) -> List[Insight]
```

**Features:**
- Fetch cost indices for user's city
- Compare user spending to city averages
- Provide insights: "Your food spending is 20% higher than average"
- Cache data to avoid API rate limits

---

## 🎯 LLM Configuration

### Free-Tier Options

| Provider | Model | Free Tier | Best For |
|----------|-------|-----------|----------|
| **Ollama** | llama3.2 | ∞ (local) | Privacy, no limits |
| **Groq** | llama3-8b | 1M tokens/day | Speed, structured output |
| **HuggingFace** | Llama-2-7B | Limited API | Experimentation |
| **Together AI** | Various | $25 credit | Testing |

**Recommended Setup:**
- **Development:** Ollama (local, unlimited)
- **Production:** Groq API (fast, free tier)
- **Fallback:** Together AI or HuggingFace

---

## 🔐 Error Handling Strategy

```python
# Layered error handling
try:
    # Layer 1: Input validation
    validated_input = validate_user_input(raw_input)
    
    # Layer 2: LLM extraction
    extracted = await llm_pipeline.extract(validated_input)
    
    # Layer 3: Schema validation
    validated_data = validate_schema(extracted, ADD_EXPENSE_SCHEMA)
    
    # Layer 4: Database operation
    expense = await db.create_expense(validated_data)
    
except ValidationError as e:
    return ErrorResponse(
        code="VALIDATION_ERROR",
        message="Invalid input",
        details=str(e)
    )
except LLMTimeoutError as e:
    return ErrorResponse(
        code="LLM_TIMEOUT",
        message="LLM request timed out",
        fallback_action="retry"
    )
except DatabaseError as e:
    return ErrorResponse(
        code="DATABASE_ERROR",
        message="Failed to save expense",
        rollback_performed=True
    )
```

**Error Categories:**
1. ⚠️ **User Errors**: Invalid input, missing fields
2. 🔴 **System Errors**: LLM timeout, DB connection lost
3. 🟡 **Business Logic Errors**: Budget exceeded, duplicate entry
4. ⚪ **External API Errors**: Cost-of-living API down

**Graceful Degradation:**
- LLM down → Use rule-based parser fallback
- Cost API down → Use cached data
- DB connection lost → Queue operations locally

---

## 📱 Minimal UI Suggestion

### Pages
1. **Login** - Username input
2. **Home** - Quick expense entry (text/voice)
3. **Expenses** - List view with filters
4. **Budgets** - Category-wise limits and status
5. **Calendar** - Visual spending timeline
6. **Insights** - Cost-of-living comparison

### Tech Stack (Frontend)
- **Framework:** React Native (cross-platform)
- **Styling:** Tailwind CSS / NativeWind
- **State:** Zustand / React Context
- **API Client:** Axios / Fetch

---

## 🚀 Deployment Architecture

```
┌─────────────────────────────────────────┐
│  Frontend (Vercel/Netlify - FREE)      │
│  - React/React Native                   │
│  - Static hosting                       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Backend (Railway/Render - FREE)        │
│  - FastAPI Python app                   │
│  - Docker container                     │
│  - 500MB RAM / 512MB storage            │
└──────────────┬──────────────────────────┘
               │
               ├─────► ┌──────────────────────┐
               │       │  Supabase (FREE)     │
               │       │  - PostgreSQL DB     │
               │       │  - 500MB storage     │
               │       └──────────────────────┘
               │
               ├─────► ┌──────────────────────┐
               │       │  Ollama (Self-host)  │
               │       │  OR Groq (FREE API)  │
               │       └──────────────────────┘
               │
               └─────► ┌──────────────────────┐
                       │  Cost API (FREE tier)│
                       └──────────────────────┘
```

**All FREE Services:**
- ✓ Supabase: 500MB DB, 2GB bandwidth
- ✓ Railway/Render: 500MB RAM, 100GB/month bandwidth
- ✓ Vercel: Unlimited static hosting
- ✓ Groq: 1M tokens/day
- ✓ Ollama: Self-hosted (unlimited)

---

## 📊 Data Flow Example

**User:** "I spent thirty dollars on groceries yesterday"

```
1. Input → Voice/Text API
   ↓
2. Whisper STT (if voice) → "I spent thirty dollars on groceries yesterday"
   ↓
3. LLM #1 (Extraction)
   Output: {
     "amount": 30.0,
     "category": "food",
     "description": "groceries",
     "date": "2026-02-12",
     "confidence": {"amount": 1.0, "category": 0.95, "date": 0.9}
   }
   ↓
4. LLM #2 (Validation)
   Output: {
     "valid": true,
     "normalized_category": "food",
     "cleaned_description": "Groceries",
     "suggestions": []
   }
   ↓
5. Schema Validation (JSON Schema)
   ✓ All fields present
   ✓ Types correct
   ✓ Amount > 0
   ↓
6. Function Call: add_expense(30.0, "food", "Groceries", "2026-02-12")
   ↓
7. Database Insert
   - Insert into expenses table
   - Insert into calendar_entries table
   - Update budget status
   ↓
8. Response → User
   "✓ Added $30.00 for groceries on Feb 12"
```

---

## 🔑 Key Design Principles

1. **Modularity**: Each component is independent and testable
2. **Type Safety**: Pydantic models for all data structures
3. **Fail-Safe**: Graceful degradation when services unavailable
4. **Zero Cost**: All services have generous free tiers
5. **Privacy**: Option to run fully local (Ollama + SQLite)
6. **Extensibility**: Easy to add new function calls or features

---

## 📦 Technology Stack Summary

| Layer | Technology | Cost | Why |
|-------|------------|------|-----|
| Backend | FastAPI + Python | FREE | Fast, async, great typing |
| Database | Supabase (PostgreSQL) | FREE | Generous free tier, realtime |
| LLM | Ollama / Groq | FREE | Local or cloud, structured output |
| STT | Whisper (OpenAI) | FREE | State-of-art, multiple options |
| Validation | Pydantic + jsonschema | FREE | Type-safe, schema validation |
| Cost API | Numbeo / RapidAPI | FREE | Cost-of-living data |
| Hosting | Railway / Render | FREE | Easy deploy, Docker support |
| Frontend | React Native | FREE | Cross-platform mobile |

**Total Monthly Cost: $0** 🎉
