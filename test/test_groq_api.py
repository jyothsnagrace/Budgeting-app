#!/usr/bin/env python3
"""Direct test of Groq API"""

import os
from dotenv import load_dotenv

load_dotenv()

print("Testing Groq API directly...")
print("=" * 50)

groq_key = os.getenv("GROQ_API_KEY")
print(f"API Key: {groq_key[:20]}..." if groq_key else "Missing")

try:
    from groq import Groq
    print("✓ Groq package imported")
    
    # Try different initialization methods
    print("\n1. Testing simple initialization:")
    try:
        client = Groq(api_key=groq_key)
        print("   ✓ Success with simple init")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        
    print("\n2. Testing with explicit parameters:")
    try:
        # Try without any extra params
        from groq import Groq as GroqClient
        client = GroqClient(api_key=groq_key)
        print("   ✓ Success with explicit client")
        
        # Test a simple completion
        print("\n3. Testing API call:")
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": "Say hello"}],
                max_tokens=10
            )
            print(f"   ✓ API call successful: {completion.choices[0].message.content}")
        except Exception as e:
            print(f"   ✗ API call failed: {e}")
            
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
