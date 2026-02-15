# 💡 SAMPLE CODE SNIPPETS & USAGE EXAMPLES

## 📚 Quick Reference Guide

This document provides copy-paste ready code examples for using the LLM Expense Tracker API.

---

## 🔐 1. Authentication

### Python Client

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

def login(username: str):
    """Login and get access token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username}
    )
    data = response.json()
    return data["user_id"], data["access_token"]

# Usage
user_id, token = login("alice")
print(f"User ID: {user_id}")
print(f"Token: {token[:20]}...")
```

### JavaScript/TypeScript

```javascript
const BASE_URL = "http://localhost:8000/api/v1";

async function login(username) {
  const response = await fetch(`${BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username })
  });
  const data = await response.json();
  return { userId: data.user_id, token: data.access_token };
}

// Usage
const { userId, token } = await login("alice");
```

### cURL

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "alice"}'
```

---

## 💰 2. Adding Expenses (Natural Language)

### Text Input

```python
def add_expense_text(user_id: str, text: str):
    """Add expense from natural language text"""
    response = requests.post(
        f"{BASE_URL}/expenses/add",
        json={
            "user_id": user_id,
            "input_text": text,
            "input_method": "text"
        }
    )
    return response.json()

# Usage Examples
expense1 = add_expense_text(user_id, "I spent 45 dollars on pizza last night")
expense2 = add_expense_text(user_id, "Uber to work was fifteen bucks")
expense3 = add_expense_text(user_id, "Bought groceries for fifty dollars")
expense4 = add_expense_text(user_id, "Movie tickets twenty five")

print(f"Added expense: ${expense1['amount']} for {expense1['category']}")
```

### Voice Input

```python
def add_expense_voice(user_id: str, audio_file_path: str):
    """Add expense from voice recording"""
    # Step 1: Transcribe audio
    with open(audio_file_path, 'rb') as f:
        files = {'audio_file': f}
        data = {'mode': 'local'}
        response = requests.post(
            f"{BASE_URL}/voice/transcribe",
            files=files,
            data=data
        )
    
    transcription = response.json()
    text = transcription['text']
    print(f"Transcribed: {text}")
    
    # Step 2: Add expense from transcription
    return add_expense_text(user_id, text)

# Usage
expense = add_expense_voice(user_id, "recording.wav")
```

### Direct Structured Input

```python
def add_expense_direct(user_id: str, amount: float, category: str, 
                       description: str, date: str):
    """Add expense with structured data (no LLM)"""
    response = requests.post(
        f"{BASE_URL}/expenses/add-direct",
        json={
            "user_id": user_id,
            "amount": amount,
            "category": category,
            "description": description,
            "date": date
        }
    )
    return response.json()

# Usage
from datetime import date
expense = add_expense_direct(
    user_id=user_id,
    amount=35.50,
    category="food",
    description="Lunch at cafe",
    date=date.today().isoformat()
)
```

---

## 📊 3. Listing and Querying Expenses

### Get All Expenses

```python
def get_expenses(user_id: str, limit: int = 50, offset: int = 0):
    """Get list of expenses"""
    response = requests.get(
        f"{BASE_URL}/expenses/list",
        params={
            "user_id": user_id,
            "limit": limit,
            "offset": offset
        }
    )
    return response.json()

# Usage
expenses = get_expenses(user_id, limit=10)
for exp in expenses['expenses']:
    print(f"{exp['date']}: ${exp['amount']} - {exp['description']}")
```

### Get Expense Summary

```python
def get_expense_summary(user_id: str):
    """Get expense summary with category breakdown"""
    response = requests.get(
        f"{BASE_URL}/expenses/summary",
        params={"user_id": user_id}
    )
    return response.json()

# Usage
summary = get_expense_summary(user_id)
print(f"Total spent: ${summary['total_amount']}")
print(f"Total expenses: {summary['expense_count']}")
print("\nBy category:")
for category, amount in summary['category_breakdown'].items():
    print(f"  {category}: ${amount}")
```

---

## 💵 4. Budget Management

### Set Budget

```python
def set_budget(user_id: str, category: str, amount: float, period: str = "monthly"):
    """Set or update budget for a category"""
    response = requests.post(
        f"{BASE_URL}/budgets/set",
        json={
            "user_id": user_id,
            "category": category,
            "amount": amount,
            "period": period
        }
    )
    return response.json()

# Usage
budget1 = set_budget(user_id, "food", 500, "monthly")
budget2 = set_budget(user_id, "transportation", 200, "monthly")
budget3 = set_budget(user_id, "entertainment", 150, "monthly")

print(f"Set {budget1['category']} budget to ${budget1['amount']}/{budget1['period']}")
```

### Get Budget Status

```python
def get_budgets(user_id: str):
    """Get all budgets with spending status"""
    response = requests.get(
        f"{BASE_URL}/budgets/list",
        params={"user_id": user_id}
    )
    return response.json()

# Usage
budgets = get_budgets(user_id)
print(f"Total budget: ${budgets['total_budget']}")
print(f"Total spent: ${budgets['total_spent']}")
print("\nBudget status:")
for budget in budgets['budgets']:
    b = budget['budget']
    print(f"\n{b['category'].upper()}")
    print(f"  Budget: ${b['amount']}")
    print(f"  Spent: ${budget['spent']}")
    print(f"  Remaining: ${budget['remaining']}")
    print(f"  Used: {budget['percentage_used']:.1f}%")
    if budget['is_exceeded']:
        print(f"  ⚠️ BUDGET EXCEEDED!")
```

### Get Specific Category Status

```python
def get_category_budget(user_id: str, category: str, period: str = "monthly"):
    """Get budget status for specific category"""
    response = requests.get(
        f"{BASE_URL}/budgets/status/{category}",
        params={
            "user_id": user_id,
            "period": period
        }
    )
    return response.json()

# Usage
food_budget = get_category_budget(user_id, "food")
print(f"Food budget: ${food_budget['budget']['amount']}")
print(f"Spent: ${food_budget['spent']}")
print(f"Percentage: {food_budget['percentage_used']:.1f}%")
```

---

## 🌍 5. Cost of Living Comparison

### Get City Data

```python
def get_city_cost(city: str, country: str = None):
    """Get cost-of-living data for a city"""
    params = {"city_name": city}
    if country:
        params["country"] = country
    
    response = requests.get(
        f"{BASE_URL}/cost-of-living/city/{city}",
        params=params
    )
    return response.json()

# Usage
nyc = get_city_cost("New York")
print(f"{nyc['city']}, {nyc['country']}")
print(f"Cost Index: {nyc['cost_index']}")
print(f"Rent Index: {nyc['rent_index']}")
print(f"Groceries Index: {nyc['groceries_index']}")
```

### Compare User Spending

```python
def compare_spending(user_id: str, city: str, country: str = None):
    """Compare user's spending to city average"""
    params = {"user_id": user_id, "city_name": city}
    if country:
        params["country"] = country
    
    response = requests.get(
        f"{BASE_URL}/cost-of-living/compare",
        params=params
    )
    return response.json()

# Usage
comparison = compare_spending(user_id, "New York")
print(f"Comparing to: {comparison['city']}")
print(f"Cost Index: {comparison['cost_index']}")
print(f"\nOverall: {comparison['overall_status']}")
print("\nInsights:")
for insight in comparison['insights']:
    print(f"  • {insight}")
```

### Get Spending Insights

```python
def get_insights(user_id: str, city: str):
    """Get personalized spending insights"""
    response = requests.get(
        f"{BASE_URL}/cost-of-living/insights/{user_id}",
        params={"city_name": city}
    )
    return response.json()

# Usage
insights = get_insights(user_id, "San Francisco")
print(f"Insights for {insights['city']}:")
for insight in insights['insights']:
    print(f"  📊 {insight}")
```

---

## 🎤 6. Voice Processing

### Transcribe Audio File

```python
def transcribe_audio(audio_file_path: str, mode: str = "local"):
    """Transcribe audio file to text"""
    with open(audio_file_path, 'rb') as f:
        files = {'audio_file': f}
        data = {'mode': mode}
        response = requests.post(
            f"{BASE_URL}/voice/transcribe",
            files=files,
            data=data
        )
    return response.json()

# Usage
result = transcribe_audio("recording.wav")
print(f"Transcription: {result['text']}")
print(f"Processing time: {result['processing_time_ms']:.0f}ms")
```

### Record and Transcribe (Server-side)

```python
def record_and_transcribe(duration: int = 5, mode: str = "local"):
    """Record audio on server and transcribe"""
    response = requests.post(
        f"{BASE_URL}/voice/record-and-transcribe",
        params={
            "duration": duration,
            "mode": mode
        }
    )
    return response.json()

# Usage (only works if server has microphone)
result = record_and_transcribe(duration=5)
print(f"Transcription: {result['text']}")
```

---

## 🔄 7. Complete Workflow Examples

### Example 1: Daily Expense Tracking

```python
import requests
from datetime import date

BASE_URL = "http://localhost:8000/api/v1"

# Login
user_id, token = login("alice")

# Add multiple expenses
expenses = [
    "Spent 12 dollars on coffee this morning",
    "Lunch was 25 bucks",
    "Bought groceries for 85 dollars",
    "Gas station 40 dollars"
]

for text in expenses:
    exp = add_expense_text(user_id, text)
    print(f"✓ Added: ${exp['amount']} - {exp['description']}")

# Check summary
summary = get_expense_summary(user_id)
print(f"\nToday's total: ${summary['total_amount']}")
```

### Example 2: Budget Management

```python
# Set monthly budgets
categories = {
    "food": 600,
    "transportation": 200,
    "entertainment": 150,
    "shopping": 300
}

for category, amount in categories.items():
    set_budget(user_id, category, amount, "monthly")
    print(f"✓ Set {category} budget: ${amount}")

# Check status
budgets = get_budgets(user_id)
for budget in budgets['budgets']:
    b = budget['budget']
    status = "✓" if not budget['is_exceeded'] else "⚠️"
    print(f"{status} {b['category']}: ${budget['spent']}/${b['amount']}")
```

### Example 3: Cost-of-Living Analysis

```python
# Get user expenses
summary = get_expense_summary(user_id)

# Compare to city
comparison = compare_spending(user_id, "San Francisco")

print("Cost of Living Analysis")
print("=" * 50)
print(f"Your total spending: ${summary['total_amount']}")
print(f"City: {comparison['city']}")
print(f"Cost Index: {comparison['cost_index']}")
print(f"\nStatus: {comparison['overall_status']}")

print("\nInsights:")
for insight in comparison['insights']:
    print(f"  • {insight}")
```

### Example 4: Voice-Powered Expense Tracking

```python
import sounddevice as sd
import soundfile as sf
import numpy as np

def record_voice_expense(user_id: str, duration: int = 5):
    """Record voice, transcribe, and add expense"""
    print(f"🎤 Recording for {duration} seconds...")
    
    # Record audio
    sample_rate = 16000
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='float32'
    )
    sd.wait()
    
    # Save to temp file
    temp_file = "temp_recording.wav"
    sf.write(temp_file, audio, sample_rate)
    
    print("🔄 Transcribing...")
    
    # Transcribe
    with open(temp_file, 'rb') as f:
        files = {'audio_file': f}
        response = requests.post(
            f"{BASE_URL}/voice/transcribe",
            files=files,
            data={'mode': 'local'}
        )
    
    text = response.json()['text']
    print(f"📝 Heard: {text}")
    
    # Add expense
    print("💰 Adding expense...")
    expense = add_expense_text(user_id, text)
    
    print(f"✓ Added: ${expense['amount']} for {expense['category']}")
    return expense

# Usage
expense = record_voice_expense(user_id, duration=5)
```

---

## 🔌 8. Integration Examples

### Flask Integration

```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
BASE_URL = "http://localhost:8000/api/v1"

@app.route('/add-expense', methods=['POST'])
def add_expense():
    data = request.json
    user_id = data['user_id']
    text = data['text']
    
    response = requests.post(
        f"{BASE_URL}/expenses/add",
        json={
            "user_id": user_id,
            "input_text": text,
            "input_method": "text"
        }
    )
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(port=5000)
```

### React Integration

```javascript
import React, { useState } from 'react';

const ExpenseForm = ({ userId }) => {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);

  const addExpense = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/expenses/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          input_text: text,
          input_method: 'text'
        })
      });
      const data = await response.json();
      alert(`Added: $${data.amount} for ${data.category}`);
      setText('');
    } catch (error) {
      alert('Error adding expense');
    }
    setLoading(false);
  };

  return (
    <div>
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="E.g., Spent 20 dollars on lunch"
      />
      <button onClick={addExpense} disabled={loading}>
        {loading ? 'Adding...' : 'Add Expense'}
      </button>
    </div>
  );
};
```

---

## 🧪 9. Testing Examples

### Unit Test Example (pytest)

```python
import pytest
from backend.llm.pipeline import TwoLLMPipeline

@pytest.mark.asyncio
async def test_expense_extraction():
    pipeline = TwoLLMPipeline()
    
    result = await pipeline.extract_expense_data(
        user_input="I spent 45 dollars on pizza",
        input_method="text"
    )
    
    assert result['extracted_data']['amount'] == 45.0
    assert result['extracted_data']['category'] == 'food'
    assert 'pizza' in result['extracted_data']['description'].lower()
```

### Integration Test Example

```python
def test_add_expense_flow():
    # Login
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "testuser"}
    )
    user_id = response.json()["user_id"]
    
    # Add expense
    response = requests.post(
        f"{BASE_URL}/expenses/add",
        json={
            "user_id": user_id,
            "input_text": "Spent 30 on groceries",
            "input_method": "text"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data['amount'] == 30.0
    assert data['category'] == 'food'
```

---

## 📱 10. Mobile App Example (React Native)

```javascript
// ExpenseTracker.js
import React, { useState } from 'react';
import { View, TextInput, Button, Text } from 'react-native';
import AudioRecord from 'react-native-audio-record';

const ExpenseTracker = () => {
  const [userId, setUserId] = useState('');
  const [text, setText] = useState('');
  const [expenses, setExpenses] = useState([]);

  const addExpense = async (inputText) => {
    const response = await fetch('http://your-api.com/api/v1/expenses/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userId,
        input_text: inputText,
        input_method: 'text'
      })
    });
    const data = await response.json();
    setExpenses([...expenses, data]);
  };

  return (
    <View>
      <TextInput
        placeholder="Describe your expense"
        value={text}
        onChangeText={setText}
      />
      <Button title="Add Expense" onPress={() => addExpense(text)} />
      
      {expenses.map(exp => (
        <Text key={exp.id}>
          ${exp.amount} - {exp.description}
        </Text>
      ))}
    </View>
  );
};
```

---

## 🎯 Key Patterns

### 1. Error Handling

```python
def safe_add_expense(user_id: str, text: str):
    try:
        response = requests.post(
            f"{BASE_URL}/expenses/add",
            json={
                "user_id": user_id,
                "input_text": text,
                "input_method": "text"
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.Timeout:
        return {"error": "Request timed out"}
    except requests.HTTPError as e:
        return {"error": f"HTTP {e.response.status_code}"}
    except Exception as e:
        return {"error": str(e)}
```

### 2. Retry Logic

```python
from time import sleep

def add_expense_with_retry(user_id: str, text: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            return add_expense_text(user_id, text)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            sleep(2 ** attempt)  # Exponential backoff
```

### 3. Batch Operations

```python
def add_multiple_expenses(user_id: str, expense_texts: list):
    results = []
    for text in expense_texts:
        try:
            result = add_expense_text(user_id, text)
            results.append(result)
        except Exception as e:
            results.append({"error": str(e), "text": text})
    return results
```

---

**For more examples, see:**
- API Documentation: http://localhost:8000/docs
- Architecture: ARCHITECTURE.md
- Setup Guide: SETUP_GUIDE.md
