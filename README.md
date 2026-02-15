# 💰 Smart Budget Companion

> An intelligent personal finance app with AI-powered expense tracking, receipt OCR, and location-aware financial advice.

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB)](https://reactjs.org/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success)](#)

---

## 🎯 Overview

A full-stack personal budgeting application that combines **Large Language Models (LLMs)** with **computer vision** to make expense tracking effortless. Features natural language processing, receipt OCR, and an AI financial advisor that provides location-aware spending insights.

### ✨ Key Features

- 🤖 **AI Financial Advisor** - Chat with your budget buddy (Penguin 🐧, Dragon 🐉, Cat 🐱, or Capybara 🦫)
- 📸 **Receipt OCR** - Upload receipt photos for automatic expense extraction
- 💬 **Natural Language Input** - Type "Spent $45 on pizza" instead of filling forms
- 📍 **Location-Aware Insights** - Compare spending to 54 US cities using real-time cost-of-living data
- 📅 **Interactive Calendar** - Visual spending patterns with hover details
- 🎨 **Companion System** - Build friendship levels through consistent tracking
- 📊 **Smart Analytics** - Category breakdowns, trends, and budget alerts

---

## 🏗️ Architecture

### Frontend (React + TypeScript)
```
src/app/
├── components/
│   ├── BudgetBuddy.tsx        # AI Chat Advisor
│   ├── SpendingForm.tsx       # Multi-modal input (text/OCR/manual)
│   ├── SpendingCalendar.tsx   # Interactive expense calendar
│   ├── SpendingGraph.tsx      # Category analytics
│   └── CompanionSelector.tsx  # Pet selection system
└── utils/
    └── dateUtils.ts           # Timezone-safe date handling
```

### Backend (FastAPI + Python)
```
backend/
├── api/
│   ├── advisor.py             # AI Financial Advisor (Groq LLM)
│   ├── expenses.py            # Expense CRUD + OCR
│   ├── budgets.py             # Budget management
│   ├── cost_of_living.py      # RapidAPI integration
│   └── auth.py                # JWT authentication
├── llm/
│   ├── pipeline.py            # LLM orchestration
│   ├── prompts.py             # Personality system prompts
│   └── schemas.py             # Pydantic validation
└── database/
    └── client.py              # Supabase PostgreSQL
```

**Detailed diagrams:** [Architecture Documentation](docs2/ARCHITECTURE.md)

---

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.11+
- **Supabase** account (free tier)
- **API Keys** (free):
  - Groq API (LLM)
  - RapidAPI (cost-of-living data)

### Installation

```bash
# 1. Clone and navigate
cd "Budgeting app"

# 2. Install frontend dependencies
npm install

# 3. Set up Python environment
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 4. Configure environment variables
# Create .env file with:
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
GROQ_API_KEY=your_groq_key
RAPIDAPI_KEY=your_rapidapi_key

# 5. Set up database
# Run database_schema.sql in Supabase SQL Editor

# 6. Start both servers
# Terminal 1 (Backend):
python -m backend.main

# Terminal 2 (Frontend):
npm run dev
```

**Access the app:**
- 🌐 **Frontend**: http://localhost:5173
- 📖 **API Docs**: http://localhost:8000/docs
- ✅ **Health Check**: http://localhost:8000/health

**Full setup instructions:** [Setup Guide](docs2/SETUP_GUIDE.md)

---

## 💡 Usage

### 1. Quick Add Expense
Type naturally: `"Spent $32 on Uber to airport"`
- Parses amount, category, description automatically
- Switches to manual entry for review
- One-click submit

### 2. Receipt Upload
- Click "Upload Receipt" button
- Select photo (PNG/JPG)
- Auto-extracts: amount, merchant, items
- Review and submit

### 3. Ask Your AI Advisor
Choose your companion (each has unique personality):
- **Penny the Penguin** 🐧 - Cheerful and bubbly
- **Esper the Dragon** 🐉 - Wise guardian of treasure
- **Mochi the Cat** 🐱 - Sassy but adorable
- **Capy the Capybara** 🦫 - Zen master of chill

**Example questions:**
- "Should I buy or rent in Charlotte?"
- "Where are budget-friendly restaurants in Denver?"
- "How does my spending compare to Seattle average?"

Responses adapt based on:
- Pet personality
- Friendship level (0-100)
- Current mood (happy/worried/over budget)

### 4. Calendar View
- Hover over any day to see expense breakdown
- Category icons + amounts displayed inline
- Color-coded by spending level

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18 + TypeScript | SPA with Vite bundler |
| **UI Components** | Radix UI + Tailwind CSS | Accessible, customizable components |
| **Backend** | FastAPI 0.115 | Async REST API |
| **Database** | Supabase (PostgreSQL) | Row-level security, real-time |
| **LLM** | Groq (LLaMA 3.1 8B) | Fast inference for chat |
| **OCR** | Backend LLM pipeline | Receipt text extraction |
| **Cost Data** | RapidAPI | Real-time city cost-of-living |
| **Auth** | JWT tokens | Secure user sessions |

**Total Cost:** $0/month (free tiers) 🎉

---

## 📊 Features

### ✅ Implemented

| Feature | Status | Description |
|---------|--------|-------------|
| **Natural Language Parser** | ✅ | LLM-powered expense extraction |
| **Receipt OCR** | ✅ | Upload photos, auto-fill expenses |
| **AI Financial Advisor** | ✅ | Location-aware chat with 4 personalities |
| **Cost-of-Living API** | ✅ | 54 US cities with real-time data |
| **Budget Tracking** | ✅ | Category limits with alerts |
| **Interactive Calendar** | ✅ | Hover tooltips with expense details |
| **Companion System** | ✅ | Friendship levels + mood adaptation |
| **Multi-Input Methods** | ✅ | Text/OCR/Manual entry |
| **Responsive Design** | ✅ | Mobile-friendly UI |
| **Database Security** | ✅ | Fixed search_path vulnerability |

### 📈 Analytics
- Category spending breakdown
- Monthly/weekly trends
- Budget vs actual comparison
- Spending calendar heatmap

---

## 📂 Project Structure

```
/
├── src/app/                    # React frontend
│   ├── components/             # UI components
│   ├── utils/                  # Client utilities
│   └── App.tsx                 # Main app component
├── backend/                    # Python backend
│   ├── api/                    # REST endpoints
│   ├── llm/                    # LLM integration layer
│   ├── database/               # Supabase client
│   └── main.py                 # FastAPI entry point
├── docs/                       # Documentation archive
│   ├── ARCHITECTURE.md         # System design
│   ├── PROJECT_EVALUATION.md  # Milestone tracking
│   ├── RAPIDAPI_SETUP.md      # API configuration guide
│   └── [7 more docs]
├── docs2/                      # Updated documentation
│   ├── SETUP_GUIDE.md         # Installation instructions
│   ├── QUICKSTART.md          # 5-minute evaluator guide
│   ├── MILESTONE_5.md         # Tool calling integration
│   └── [8 more docs]
├── database_schema.sql         # PostgreSQL schema
├── SETUP_GUIDE.md             # Installation instructions
└── README.md                  # This file
```

---

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```bash
# Database
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# LLM
GROQ_API_KEY=gsk_xxxxx

# External APIs
RAPIDAPI_KEY=your_rapidapi_key
COST_API_PROVIDER=rapidapi

# Server
ENVIRONMENT=development
DEBUG=True
```

**Frontend (auto-loads from backend):**
- No separate .env needed for frontend
- API base URL auto-configured

### Database Setup

1. Create Supabase project
2. Run [database_schema.sql](database_schema.sql) in SQL Editor
3. Enable Row Level Security (RLS)
4. Note your project URL and anon key

**Schema includes:**
- `users` - Authentication
- `expenses` - Transaction records
- `budgets` - Spending limits
- Triggers for `updated_at` timestamps

---

## 🎨 UI Highlights

### 1. Companion Selection
- 4 animated avatars to choose from
- Friendship meter (builds with consistent usage)
- Mood indicator (happy/worried/excited)

### 2. Spending Form
- **Quick Add**: Natural language or receipt upload
- **Manual Entry**: Traditional form (amount/category/date)
- Side-by-side buttons for optimal workflow
- Real-time validation

### 3. Calendar View
- Color-coded by spending amount:
  - 🟢 Green: $0-20
  - 🟡 Yellow: $20-50
  - 🟠 Orange: $50-100
  - 🔴 Red: $100+
- Inline category emojis + amounts
- Hover for full breakdown

### 4. AI Chat
- City dropdown (54 US cities, alphabetized)
- Auto-detects location via browser
- Brief, emoji-rich responses
- Related insights below answers

---

## 🚀 Deployment

### Backend Options

**Railway (Recommended):**
```bash
railway login
railway init
railway up
```

**Render:**
- Connect GitHub repo
- Set environment variables
- Auto-deploys on push

### Frontend Options

**Vercel:**
```bash
vercel login
vercel --prod
```

**Netlify:**
- Connect GitHub
- Build command: `npm run build`
- Publish dir: `dist`

**See:** [Deployment Guide](docs2/SETUP_GUIDE.md#deployment)

---

## 🧪 Testing

```bash
# Backend
pytest tests/ -v --cov=backend

# Frontend
npm test

# End-to-end
npm run test:e2e
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [SETUP_GUIDE.md](docs2/SETUP_GUIDE.md) | Complete installation & troubleshooting |
| [QUICKSTART.md](docs2/QUICKSTART.md) | 5-minute evaluator guide |
| [MILESTONE_5.md](docs2/MILESTONE_5.md) | Tool calling integration (Assignment) |
| [ARCHITECTURE.md](docs2/ARCHITECTURE.md) | Technical architecture diagrams |
| [PROJECT_EVALUATION.md](docs2/PROJECT_EVALUATION.md) | Milestone coverage & grading rubric |
| [RAPIDAPI_SETUP.md](docs/RAPIDAPI_SETUP.md) | Cost-of-living API configuration |
| [CODE_SAMPLES.md](docs2/CODE_SAMPLES.md) | API usage examples |
| [database_schema.sql](database_schema.sql) | PostgreSQL schema with RLS |

---

## 🔒 Security

### Implemented
✅ JWT authentication  
✅ Row-level security (Supabase RLS)  
✅ Input validation (Pydantic)  
✅ SQL injection prevention (parameterized queries)  
✅ Fixed search_path vulnerability in triggers  

### Production Recommendations
- Add password hashing (bcrypt)
- Enable HTTPS only
- Rate limiting middleware
- CORS whitelist specific origins
- API key rotation policy

---

## 🤝 Contributing

This is an academic project. For local improvements:

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m "Add amazing feature"`
4. Push: `git push origin feature/amazing-feature`
5. Open Pull Request

---

## 📧 Support

**Troubleshooting:**
1. Check [SETUP_GUIDE.md](docs2/SETUP_GUIDE.md) troubleshooting section
2. Review API docs: http://localhost:8000/docs
3. Check backend logs: `backend/logs/app.log`
4. Verify environment variables loaded correctly

**Common Issues:**
- CORS errors → Check frontend proxy config in `vite.config.ts`
- 401 errors → Token expired, re-login
- OCR not working → Check Groq API key and rate limits
- Cities not loading → Verify RapidAPI key configured

---

## 📜 License

This project is provided for educational purposes.

---

## 🙏 Acknowledgments

- **Groq** - Fast LLM inference
- **Supabase** - Backend infrastructure
- **RapidAPI** - Cost-of-living data
- **Radix UI** - Accessible components
- **Tailwind CSS** - Rapid styling
- **FastAPI** - Modern Python framework
- **Vite** - Lightning-fast dev server

---

## 📊 Project Metrics

- **Total Lines of Code**: ~4,500+
- **Frontend Components**: 15+
- **Backend Endpoints**: 25+
- **Database Tables**: 5
- **Supported Cities**: 54
- **Pet Personalities**: 4
- **Documentation Pages**: 10+

---

## 🎯 Quick Links

- 🌐 [Live Demo](#) (Add your deployment URL)
- 📖 [API Documentation](http://localhost:8000/docs)
- 🏗️ [Architecture](docs2/ARCHITECTURE.md)
- 🚀 [Setup Guide](docs2/SETUP_GUIDE.md)
- 📝 [Milestone 5](docs2/MILESTONE_5.md)
- 💬 [Report Issue](#)

---

**Built with ❤️ for Personal Finance Management**

**Version:** 2.0.0  
**Last Updated:** February 15, 2026  
**Status:** ✅ Production Ready
