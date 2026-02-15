#!/usr/bin/env python3
"""Test voice transcription service"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("=" * 50)
print("🎤 VOICE TRANSCRIPTION TEST")
print("=" * 50)

# Check configuration
print("\n1️⃣ Configuration Check:")
groq_key = os.getenv("GROQ_API_KEY")
llm_provider = os.getenv("LLM_PROVIDER")
print(f"   LLM_PROVIDER: {llm_provider}")
print(f"   GROQ_API_KEY: {'✓ Set (' + groq_key[:20] + '...)' if groq_key else '✗ Missing'}")

# Test Groq package
print("\n2️⃣ Package Test:")
try:
    import groq
    print("   ✓ Groq package imported")
    
    # Try to create client
    try:
        client = groq.Groq(api_key=groq_key)
        print("   ✓ Groq client created successfully")
    except Exception as e:
        print(f"   ✗ Failed to create Groq client: {e}")
        
except ImportError as e:
    print(f"   ✗ Groq package not found: {e}")

# Test voice service
print("\n3️⃣ Voice Service Test:")
try:
    from backend.api.voice import get_voice_service
    
    # Get voice service (should auto-detect Groq)
    service = get_voice_service()
    print(f"   ✓ Voice service initialized")
    print(f"   Mode: {service.mode}")
    
    if service.mode == "groq" and groq_key:
        print("   ✓ Using Groq API for transcription")
        print("\n✅ Voice service is ready!")
        print("\nTo test in app:")
        print("   1. Open app → 'Add New Expense'")
        print("   2. Click 'Voice Input' button")
        print("   3. Speak: 'I spent 25 dollars on pizza'")
        print("   4. Click 'Stop'")
    elif service.mode == "local":
        print("   ⚠ Using local Whisper (requires model download)")
        print("   💡 Tip: Use Groq API for faster transcription")
    else:
        print(f"   ⚠ Unknown mode: {service.mode}")
        
except Exception as e:
    print(f"   ✗ Voice service error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
