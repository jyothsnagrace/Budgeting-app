# 🚀 LLM-Powered Expense Tracker - Complete Setup Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Database Setup (Supabase)](#database-setup)
4. [LLM Configuration](#llm-configuration)
5. [Running the Application](#running-the-application)
6. [Testing the API](#testing-the-api)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)

---

## 📦 Prerequisites

### Required
- **Python 3.9+** (3.10 or 3.11 recommended)
- **pip** (Python package manager)
- **Git**
- **Supabase Account** (free tier)

### Optional
- **Docker** (for containerized deployment)
- **Groq API Key** (for faster LLM inference)
- **RapidAPI Key** (for real cost-of-living data)

---

## 🔧 Initial Setup

### Step 1: Clone or Navigate to Project

```bash
cd "c:\Users\jyoth\Downloads\Project_0210\Budgeting app"
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Core Dependencies:**
```
fastapi==0.115.0
uvicorn[standard]==0.32.0
supabase==2.9.0
ollama==0.3.3
openai-whisper==20240930
jsonschema==4.23.0
pydantic==2.9.0
httpx==0.27.2
sounddevice==0.5.1
soundfile==0.12.1
numpy==1.26.4
torch==2.5.1
torchaudio==2.5.1
PyJWT==2.8.0
python-multipart==0.0.12
```

### Step 4: Create Environment File

Create a `.env` file in the project root:

```env
# Application Settings
APP_NAME="LLM Expense Tracker"
APP_VERSION="0.1.0"
ENVIRONMENT="development"
DEBUG=True

# API Settings
API_HOST="0.0.0.0"
API_PORT=8000

# Supabase Configuration
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_KEY="your-anon-key-here"
SUPABASE_SERVICE_KEY="your-service-key-here"  # Optional

# LLM Configuration
LLM_PROVIDER="ollama"  # Options: ollama, groq, openai
LLM_TIMEOUT=30

# Ollama Settings (Local)
OLLAMA_BASE_URL="http://localhost:11434"
OLLAMA_MODEL_EXTRACTION="llama3.2"
OLLAMA_MODEL_VALIDATION="llama3.2"

# Groq Settings (Optional - FREE tier)
# GROQ_API_KEY="your-groq-api-key"
# GROQ_MODEL="llama3-8b-8192"

# OpenAI Settings (Optional - Paid)
# OPENAI_API_KEY="your-openai-key"

# Whisper Settings
WHISPER_MODEL_SIZE="base"  # Options: tiny, base, small, medium, large

# Cost of Living API (Optional)
# RAPIDAPI_KEY="your-rapidapi-key"

# Logging
LOG_LEVEL="INFO"
```

---

## 🗄️ Database Setup (Supabase)

### Step 1: Create Supabase Project

1. Go to https://supabase.com
2. Sign up / Login
3. Create new project
4. Wait for database provisioning (~2 minutes)

### Step 2: Get Credentials

1. Go to **Settings → API**
2. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **anon/public key** → `SUPABASE_KEY`

### Step 3: Run Database Schema

1. Open **SQL Editor** in Supabase dashboard
2. Copy contents from `database_schema.sql`
3. Run the SQL script

**Verify tables created:**
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';
```

You should see:
- `users`
- `expenses`
- `budgets`
- `calendar_entries`
- `cost_of_living`

---

## 🤖 LLM Configuration

### Option 1: Ollama (Recommended - Local, FREE, Unlimited)

**Install Ollama:**

Windows:
```bash
# Download from https://ollama.ai/download
# Or use PowerShell:
iwr https://ollama.ai/install.ps1 -useb | iex
```

Linux/Mac:
```bash
curl https://ollama.ai/install.sh | sh
```

**Pull Model:**
```bash
ollama pull llama3.2
```

**Verify:**
```bash
ollama list
ollama run llama3.2 "Hello"
```

**Configure in .env:**
```env
LLM_PROVIDER="ollama"
OLLAMA_BASE_URL="http://localhost:11434"
OLLAMA_MODEL_EXTRACTION="llama3.2"
OLLAMA_MODEL_VALIDATION="llama3.2"
```

### Option 2: Groq (Cloud, FREE tier - 1M tokens/day)

**Get API Key:**
1. Go to https://console.groq.com
2. Sign up
3. Create API key

**Configure in .env:**
```env
LLM_PROVIDER="groq"
GROQ_API_KEY="your-key-here"
GROQ_MODEL="llama3-8b-8192"
```

### Option 3: OpenAI (Paid)

**Configure in .env:**
```env
LLM_PROVIDER="openai"
OPENAI_API_KEY="your-key-here"
```

---

## ▶️ Running the Application

### Development Mode

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Start server
python -m backend.main

# Or with uvicorn directly
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Access Points

- **API Docs (Swagger):** http://localhost:8000/docs
- **Alternative Docs (ReDoc):** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

---

## 🧪 Testing the API

### 1. Test Authentication

```bash
# Login/Create User
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser"}'

# Response:
# {
#   "user_id": "uuid-here",
#   "username": "testuser",
#   "access_token": "jwt-token-here",
#   "token_type": "bearer"
# }
```

### 2. Test Expense Addition (Text Input)

```bash
curl -X POST "http://localhost:8000/api/v1/expenses/add" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "your-user-id",
    "input_text": "I spent 45 dollars on pizza last night",
    "input_method": "text"
  }'
```

### 3. Test Voice Transcription

```bash
# Upload audio file
curl -X POST "http://localhost:8000/api/v1/voice/transcribe" \
  -F "audio_file=@recording.wav" \
  -F "mode=local"
```

### 4. Test Budget Setting

```bash
curl -X POST "http://localhost:8000/api/v1/budgets/set" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "your-user-id",
    "category": "food",
    "amount": 500,
    "period": "monthly"
  }'
```

### 5. Test Cost-of-Living Comparison

```bash
curl -X GET "http://localhost:8000/api/v1/cost-of-living/compare?user_id=your-user-id&city_name=New%20York"
```

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Login
response = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "testuser"
})
data = response.json()
user_id = data["user_id"]
token = data["access_token"]

# Add expense
response = requests.post(f"{BASE_URL}/expenses/add", json={
    "user_id": user_id,
    "input_text": "Spent 30 bucks on lunch today",
    "input_method": "text"
})
print(response.json())

# Get expenses
response = requests.get(f"{BASE_URL}/expenses/list", params={
    "user_id": user_id,
    "limit": 10
})
print(response.json())
```

---

## 🌐 Deployment

### Option 1: Railway (FREE tier)

**Setup:**
1. Create account at https://railway.app
2. Connect GitHub repo
3. Add environment variables
4. Deploy

**railway.json:**
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn backend.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Option 2: Render (FREE tier)

**Setup:**
1. Create account at https://render.com
2. New → Web Service
3. Connect repo
4. Configure:
   - **Build:** `pip install -r requirements.txt`
   - **Start:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### Option 3: Docker

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and Run:**
```bash
docker build -t expense-tracker .
docker run -p 8000:8000 --env-file .env expense-tracker
```

### Option 4: Local Production

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn (better for production)
gunicorn backend.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

---

## 🔧 Troubleshooting

### Issue: Import Errors

```bash
# Solution: Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Issue: Supabase Connection Failed

```bash
# Verify credentials
python -c "from backend.config import settings; print(settings.SUPABASE_URL)"

# Test connection
python -c "from backend.database.client import get_db; client = get_db(); print(client)"
```

### Issue: Ollama Not Running

```bash
# Start Ollama
ollama serve

# In another terminal
ollama pull llama3.2
```

### Issue: Whisper Too Slow

```bash
# Use smaller model
WHISPER_MODEL_SIZE="tiny"  # In .env

# Or use Groq API for faster transcription
```

### Issue: Port Already in Use

```bash
# Find process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Linux/Mac:
lsof -i :8000
kill -9 <pid>

# Or use different port
uvicorn backend.main:app --port 8001
```

---

## 📊 System Requirements

### Minimum
- **CPU:** 2 cores
- **RAM:** 2GB (4GB for local Whisper)
- **Storage:** 2GB (5GB if using local Ollama models)

### Recommended
- **CPU:** 4+ cores
- **RAM:** 8GB
- **Storage:** 10GB
- **GPU:** Optional (speeds up Whisper/Ollama)

---

## 🎯 Quick Start Summary

```bash
# 1. Setup
cd "c:\Users\jyoth\Downloads\Project_0210\Budgeting app"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure .env
# (Copy .env.example and fill in Supabase credentials)

# 3. Setup Ollama
ollama pull llama3.2

# 4. Run
python -m backend.main

# 5. Test
# Open http://localhost:8000/docs
```

---

## 🔗 Useful Links

- **Supabase Dashboard:** https://app.supabase.com
- **Ollama Models:** https://ollama.ai/library
- **Groq Console:** https://console.groq.com
- **API Documentation:** http://localhost:8000/docs
- **Project Repository:** (your-repo-url)

---

## 📧 Support

For issues or questions:
1. Check troubleshooting section
2. Review API docs at `/docs`
3. Check logs in `logs/` directory
4. Open GitHub issue (if applicable)

---

**Last Updated:** February 2026
**Version:** 0.1.0
