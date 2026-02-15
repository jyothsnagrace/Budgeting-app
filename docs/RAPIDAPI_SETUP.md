# RapidAPI Configuration Guide

## How to Get Real Cost-of-Living Data

By default, the app uses **mock data** for city cost-of-living information. To get **real-time data**, follow these steps:

---

## Step 1: Sign Up for RapidAPI

1. Go to [RapidAPI](https://rapidapi.com/)
2. Click **"Sign Up"** (it's FREE!)
3. Create an account using email or social login

---

## Step 2: Subscribe to Cost of Living API

1. Go to: [Cost of Living and Prices API](https://rapidapi.com/traveltables/api/cost-of-living-and-prices)
2. Click **"Subscribe to Test"**
3. Choose the **FREE tier**:
   - ✅ **Basic Plan**: Free forever
   - 💰 **0 requests per month** (check current limits)
   - 📊 Sufficient for personal use

---

## Step 3: Get Your API Key

1. After subscribing, you'll see your **API Key** on the API page
2. Look for: `X-RapidAPI-Key: your-key-here`
3. Copy the entire key (looks like: `abc123xyz456...`)

---

## Step 4: Configure Your App

### Option A: Using Environment Variables (Recommended)

1. Create a `.env` file in the project root:
   ```bash
   # In: C:\Users\jyoth\Downloads\Project_0210\Budgeting app\.env
   ```

2. Add your API key:
   ```env
   RAPIDAPI_KEY=your-actual-api-key-here
   ```

3. The app will automatically load it from `backend/config.py`

### Option B: Direct Configuration

1. Open `backend/config.py`
2. Find the `Settings` class
3. Add your key:
   ```python
   class Settings:
       # ... other settings ...
       RAPIDAPI_KEY: Optional[str] = "your-actual-api-key-here"
   ```

---

## Step 5: Restart Backend Server

```powershell
# Stop current backend
Get-Process | Where-Object {$_.ProcessName -eq "python"} | Stop-Process -Force

# Start backend with new API key
python -m backend.main
```

---

## Verification

After configuration, test the API:

```python
# Test script
import requests

response = requests.get(
    'http://localhost:8000/api/v1/cost-of-living/city/Seattle',
    timeout=5
)

data = response.json()
print(f"Source: {data['source']}")  # Should show 'rapidapi' instead of 'mock_data'
print(f"City: {data['city']}")
print(f"Cost Index: {data['cost_index']}")
```

---

## Benefits of Real Data

✅ **Live Updates**: Cost indices updated regularly  
✅ **More Cities**: Access to 4000+ cities worldwide  
✅ **Detailed Breakdown**: Restaurant prices, transportation costs, utilities  
✅ **Currency Conversion**: Automatic local currency support  

---

## Fallback Behavior

If the API key is invalid or quota exceeded:
- ⚠️ App **automatically falls back** to mock data
- 📝 Check logs: `backend.log` for error details
- 💡 Mock data remains accurate for major US cities

---

## Current Mock Cities

The app includes accurate mock data for:
- **USA**: NYC, San Francisco, LA, Chicago, Seattle, Austin, Boston
- **World**: London, Paris, Tokyo, Singapore, Sydney, Toronto
- **Asia**: Bangalore, Mumbai, Delhi

---

## Troubleshooting

### Issue: Still seeing "mock_data" source

**Solution:**
1. Verify API key is correct (no extra spaces)
2. Check you're subscribed to the API
3. Restart backend server
4. Check backend logs for errors

### Issue: API requests failing

**Solution:**
1. Check your RapidAPI quota (free tier limits)
2. Verify API endpoint is correct
3. Test API directly on RapidAPI dashboard

### Issue: "401 Unauthorized"

**Solution:**
- Your API key is incorrect or expired
- Re-copy from RapidAPI dashboard
- Ensure no quotes in `.env` file

---

## Cost Breakdown

- **Free Tier**: $0/month (limited requests)
- **Basic Tier**: ~$10/month (500+ requests)
- **Pro Tier**: ~$30/month (5000+ requests)

💡 **Tip**: For personal use, the free tier is usually sufficient!

---

## API Response Example

```json
{
  "city": "Seattle",
  "country": "United States",
  "cost_index": 86.2,
  "rent_index": 83.4,
  "groceries_index": 89.1,
  "restaurant_index": 81.7,
  "purchasing_power": 74.2,
  "currency": "USD",
  "source": "rapidapi",
  "updated_at": "2026-02-15T10:30:00"
}
```

---

## Need Help?

- 📚 [RapidAPI Documentation](https://docs.rapidapi.com/)
- 💬 [RapidAPI Community Forum](https://community.rapidapi.com/)
- 🐛 Check `backend.log` for error messages
