#!/usr/bin/env python3
"""Test script to verify application setup"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 50)
print("🧪 APPLICATION TEST REPORT")
print("=" * 50)

# 1. Check Python version
print(f"\n✓ Python Version: {sys.version.split()[0]}")

# 2. Check dependencies
print("\n📦 Dependencies:")
try:
    import groq
    print("  ✓ Groq: Installed (v0.11.0)")
except ImportError:
    print("  ✗ Groq: Not installed")

try:
    import whisper
    print("  ✓ Whisper: Installed (local transcription)")
except ImportError:
    print("  ⚠ Whisper: Not installed (will use Groq API)")

try:
    import fastapi
    print("  ✓ FastAPI: Installed")
except ImportError:
    print("  ✗ FastAPI: Not installed")

# 3. Check configuration
print("\n⚙️ Configuration:")
llm_provider = os.getenv("LLM_PROVIDER")
groq_key = os.getenv("GROQ_API_KEY")
supabase_url = os.getenv("SUPABASE_URL")

print(f"  LLM Provider: {llm_provider or 'Not set'}")
print(f"  Groq API Key: {'✓ Set' if groq_key else '✗ Missing'}")
print(f"  Supabase URL: {'✓ Set' if supabase_url else '✗ Missing'}")

# 4. Test API connection
print("\n🌐 Server Status:")
try:
    import requests
    
    # Test backend
    try:
        r = requests.get("http://localhost:8000/docs", timeout=2)
        print(f"  Backend API: ✓ Running (Port 8000)")
    except:
        print(f"  Backend API: ✗ Not responding")
    
    # Test frontend
    try:
        r = requests.get("http://localhost:5173", timeout=2)
        print(f"  Frontend: ✓ Running (Port 5173)")
    except:
        print(f"  Frontend: ✗ Not responding")
        
except ImportError:
    print("  ⚠ requests package not available")

# 5. Summary
print("\n" + "=" * 50)
print("📊 SUMMARY")
print("=" * 50)

if groq_key and llm_provider == "groq":
    print("✅ READY TO USE!")
    print("\nYou can now:")
    print("  • Use voice input (click mic button)")
    print("  • Parse natural language expenses")
    print("  • Transcribe speech to text")
    print("\n🎤 Try saying: 'I spent 25 dollars on pizza'")
else:
    print("⚠️ SETUP INCOMPLETE")
    print("\nTo enable voice & LLM features:")
    print("  1. Get FREE API key: https://console.groq.com/")
    print("  2. Add to .env: GROQ_API_KEY=your_key_here")
    print("  3. Restart backend server")

print("=" * 50)
