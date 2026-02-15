# 🎓 Quick Start for Evaluators

This guide helps instructors and evaluators quickly set up and test the application.

## ⚡ 5-Minute Setup

### 1. Prerequisites Check
```powershell
# Verify installations
python --version  # Should be 3.11+
node --version    # Should be 18+
npm --version
```

### 2. Environment Configuration
Create `.env` file in project root:
```env
# Database (Supabase)
SUPABASE_URL=https://csrqjkxfqnrhfpnvowba.supabase.co
SUPABASE_KEY=your_anon_key_here

# LLM (Groq - free tier)
GROQ_API_KEY=gsk_your_key_here

# Cost Data (RapidAPI - free tier)
RAPIDAPI_KEY=your_rapidapi_key
COST_API_PROVIDER=rapidapi
```

**Get free API keys:**
- Supabase: https://supabase.com (run `database_schema.sql` in SQL Editor)
- Groq: https://console.groq.com
- RapidAPI: https://rapidapi.com/asaniczka/api/world-cost-of-living-and-prices

### 3. Install & Run
```powershell
# Backend setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
npm install

# Start both (2 terminals)
# Terminal 1:
python -m backend.main

# Terminal 2:
npm run dev
```

### 4. Access Application
- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 🧪 Quick Feature Test

### Test 1: Natural Language Expense
1. Go to http://localhost:5173
2. Login with any username
3. In "Quick Add" tab, type: `"Spent $45 on pizza last night"`
4. Click "Parse & Fill"
5. Verify it populates amount ($45) and category (Food)
6. Click "Add Expense"

### Test 2: Receipt OCR
1. Click "Upload Receipt" button
2. Select any receipt image
3. Wait for auto-extraction
4. Verify extracted data in manual entry form
5. Submit expense

### Test 3: AI Financial Advisor
1. Select a pet companion (Penguin/Dragon/Cat/Capybara)
2. Choose a city from dropdown (54 US cities available)
3. Ask: "Should I buy or rent in [city]?"
4. Verify personalized response based on:
   - Pet personality
   - Friendship level
   - Selected city's cost-of-living data

### Test 4: Calendar View
1. Add multiple expenses on different dates
2. View calendar in main dashboard
3. Hover over days with expenses
4. Verify tooltip shows:
   - Category icons
   - Individual amounts
   - Descriptions

---

## 📊 Key Features to Evaluate

### LLM Integration ✅
- **Natural Language Parsing**: `backend/llm/pipeline.py`
  - Uses Groq LLaMA 3.1 8B
  - Two-stage extraction + validation
  - Pydantic schema validation

- **AI Advisor**: `backend/api/advisor.py`
  - 4 distinct personalities
  - Friendship level adaptation (0-100)
  - Mood-based responses (happy/worried/excited)
  - Location-aware insights

### Computer Vision ✅
- **Receipt OCR**: `backend/api/expenses.py` (line 200+)
  - Multipart file upload
  - LLM-based text extraction
  - Auto-fills expense form

### External APIs ✅
- **Cost-of-Living**: `backend/api/cost_of_living.py`
  - RapidAPI integration
  - 54 US cities
  - Real-time data with mock fallback

### Database ✅
- **Supabase PostgreSQL**: `database_schema.sql`
  - Row-Level Security (RLS)
  - JWT authentication
  - Fixed search_path vulnerability

### Frontend ✅
- **React + TypeScript**: `src/app/components/`
  - 15+ reusable components
  - Radix UI + Tailwind CSS
  - Vite build system

---

## 📖 Documentation Structure

```
/
├── README.md                  # Main project overview
├── SETUP_GUIDE.md            # Detailed installation (this file)
├── docs/
│   ├── README.md             # Documentation index
│   ├── ARCHITECTURE.md       # System design diagrams
│   ├── PROJECT_EVALUATION.md # Milestone coverage matrix
│   ├── RAPIDAPI_SETUP.md     # API configuration guide
│   └── [7 more technical docs]
└── database_schema.sql       # PostgreSQL schema
```

---

## 🔍 Code Highlights

### Backend Highlights
```python
# LLM Pipeline with validation
from backend.llm.pipeline import extract_and_validate_expense
result = await extract_and_validate_expense("Spent $45 on pizza")

# AI Advisor with personality
from backend.api.advisor import _build_personality
personality = _build_personality("penguin", friendship_level=75, mood="happy")

# Cost-of-living comparison
from backend.api.cost_of_living import get_city_data
data = await get_city_data("Charlotte", "United States")
```

### Frontend Highlights
```typescript
// Location-aware AI chat
<BudgetBuddy totalSpent={500} budget={1000} />

// Multi-modal expense input
<SpendingForm onAddExpense={handleAdd} />

// Interactive calendar with hover details
<SpendingCalendar expenses={expenses} />
```

---

## ⚠️ Common Issues

### Backend won't start
```powershell
# Check dependencies
pip list | findstr fastapi
pip list | findstr groq

# Verify environment
Get-Content .env | Select-String "GROQ_API_KEY"
```

### Frontend compilation errors
```powershell
# Clear cache and reinstall
Remove-Item node_modules -Recurse -Force
Remove-Item package-lock.json
npm install
```

### API returns 401 Unauthorized
- Token expires after inactivity
- Re-login from frontend
- Check JWT token in localStorage

### AI Advisor not responding
- Verify GROQ_API_KEY in .env
- Check rate limits (free tier: 14,400/day)
- View backend logs: `backend/logs/app.log`

---

## 📊 Evaluation Checklist

- [ ] **LLM Integration**
  - [ ] Natural language parsing works
  - [ ] AI advisor responds with personality
  - [ ] Structured JSON outputs validated
  
- [ ] **External APIs**
  - [ ] RapidAPI returns cost-of-living data
  - [ ] 54 US cities available in dropdown
  
- [ ] **Database**
  - [ ] Supabase connected
  - [ ] Expenses persist across sessions
  - [ ] RLS policies working
  
- [ ] **Frontend**
  - [ ] Responsive design on mobile
  - [ ] Calendar hover tooltips work
  - [ ] Receipt upload functional
  
- [ ] **Documentation**
  - [ ] README clear and comprehensive
  - [ ] Setup guide complete
  - [ ] Code samples accurate

---

## 📞 Support

**Quick References:**
- API Docs: http://localhost:8000/docs
- Backend Logs: `backend/logs/app.log`
- Database Schema: [database_schema.sql](database_schema.sql)
- Architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

**For detailed troubleshooting:** See [SETUP_GUIDE.md](SETUP_GUIDE.md#troubleshooting)

---

**Estimated evaluation time:** 15-30 minutes for full feature testing

**Project metrics:**
- Lines of Code: ~4,500+
- Components: 15+ (Frontend) + 25+ API endpoints (Backend)
- Documentation: 12 markdown files
- Test Coverage: Infrastructure ready
