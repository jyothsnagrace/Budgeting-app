# CHECKPOINT_AI_ADVISOR
"""
AI Financial Advisor
====================
LLM-powered financial advisor with location context.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json

from backend.config import settings
from backend.llm.client import get_llm_client
from backend.api.cost_of_living import get_cost_service
from backend.utils.logger import get_logger

logger = get_logger("ai_advisor")
router = APIRouter(prefix="/advisor", tags=["advisor"])


# ============================================
# Models
# ============================================

class AdvisorRequest(BaseModel):
    """Request for AI financial advice"""
    question: str
    city: Optional[str] = None
    country: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    friendship_level: Optional[int] = 0  # 0-100
    mood: Optional[str] = "happy"  # happy, worried, excited
    pet_type: Optional[str] = "penguin"  # penguin, dragon, cat, capybara


class AdvisorResponse(BaseModel):
    """Response from AI financial advisor"""
    answer: str
    city_data: Optional[Dict[str, Any]] = None
    related_insights: Optional[List[str]] = None


# ============================================
# Advisor Endpoint
# ============================================

@router.post("/ask", response_model=AdvisorResponse)
async def ask_advisor(request: AdvisorRequest):
    """
    Ask the AI financial advisor a location-aware money question.
    
    Examples:
    - "Which is budget friendly restaurant in Seattle?"
    - "Is it smarter to buy or rent in Seattle?"
    - "What's the average cost of housing in Austin?"
    - "Should I move to Portland or Denver for better savings?"
    """
    logger.info(f"AI Advisor question: {request.question} (city: {request.city})")
    
    try:
        # Get city data if specified
        city_data = None
        if request.city:
            cost_service = get_cost_service()
            city_data = await cost_service.get_city_data(request.city, request.country)
        
        # Build personality based on pet type and friendship
        personality = _build_personality(
            request.pet_type,
            request.friendship_level,
            request.mood
        )
        
        # Build context for LLM
        llm_context = _build_llm_context(
            request.question,
            city_data,
            request.context,
            personality
        )
        
        # Get LLM response
        llm = get_llm_client()
        answer = await llm.generate(
            prompt=llm_context,
            temperature=0.8,
            max_tokens=200  # Keep responses brief and cute
        )
        
        # Generate related insights
        insights = []
        if city_data:
            insights = _generate_insights(city_data, request.context)
        
        return AdvisorResponse(
            answer=answer,
            city_data=city_data,
            related_insights=insights
        )
        
    except Exception as e:
        logger.error(f"AI Advisor error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get advice: {str(e)}"
        )


# ============================================
# Helper Functions
# ============================================

def _build_personality(pet_type: str, friendship_level: int, mood: str) -> str:
    """Build personality traits based on avatar and friendship"""
    
    # Base personalities
    base_personalities = {
        "penguin": {
            "name": "Penny the Penguin 🐧",
            "style": "cheerful and bubbly",
            "tone": "Super upbeat! Loves celebrating wins with penguin waddles! Uses ice/water puns! 🧊❄️"
        },
        "dragon": {
            "name": "Esper the Dragon 🐉",
            "style": "wise guardian of treasure",
            "tone": "Mystical and protective! Calls money 'treasure hoard'. Breathes wisdom fire! 💎🔥"
        },
        "cat": {
            "name": "Mochi the Cat 🐱",
            "style": "sassy but adorable",
            "tone": "Playfully sassy! Purrs when happy, swishes tail when concerned! 😸✨"
        },
        "capybara": {
            "name": "Capy the Capybara 🦫",
            "style": "zen master of chill",
            "tone": "Ultra relaxed! Everything's gonna be okay vibes! Promotes mindful spending! 🌿☮️"
        }
    }
    
    base = base_personalities.get(pet_type, base_personalities["penguin"])
    
    # Adjust based on friendship level
    if friendship_level < 20:
        relationship = "Just becoming friends! Be warm but professional. 👋"
    elif friendship_level < 50:
        relationship = "Friends now! Show personality, care about their goals! 😊💕"
    elif friendship_level < 80:
        relationship = "Good friends! Celebrate wins, give gentle guidance! 🎉🤗"
    else:
        relationship = "BEST FRIENDS FOREVER! Be super enthusiastic, inside jokes welcome! 🎈✨💖"
    
    # Adjust based on mood
    mood_adjustments = {
        "happy": "They're crushing it! 🌟 Celebrate and cheer!",
        "worried": "Budget's getting tight! 😅 Be supportive, quick tips!",
        "excited": "Uh oh, over budget! 😬 Kind but firm, actionable help!"
    }
    
    return f"""You are {base['name']}, a {base['style']} financial advisor.

Your vibe: {base['tone']}

Friendship level: {relationship}

Current mood: {mood_adjustments.get(mood, mood_adjustments['happy'])}

⚠️ SUPER IMPORTANT: Keep answers SHORT and CUTE! Maximum 2-3 sentences. Use emojis! Be adorable but helpful! Get to the point fast! 🚀
"""


def _build_llm_context(
    question: str,
    city_data: Optional[Dict],
    user_context: Optional[Dict],
    personality: str
) -> str:
    """Build complete context for LLM"""
    
    prompt = f"""{personality}

USER QUESTION: {question}
"""
    
    if city_data:
        prompt += f"""

LOCATION DATA ({city_data['city']}):
- Cost of Living Index: {city_data['cost_index']} (baseline: NYC = 100)
- Rent Index: {city_data['rent_index']}
- Groceries Index: {city_data['groceries_index']}
- Restaurant Index: {city_data['restaurant_index']}
- Local Purchasing Power: {city_data['purchasing_power']}
- Source: {city_data['source']}
"""
        if city_data.get('note'):
            prompt += f"\nNote: {city_data['note']}\n"
    
    if user_context:
        prompt += f"""

USER BUDGET CONTEXT:
{json.dumps(user_context, indent=2)}
"""
    
    prompt += """

Provide a helpful, location-aware answer. Be specific and practical.
If the question is about buying vs renting, provide a comparison table.
If about restaurants or businesses, suggest specific types or areas known for value.
"""
    
    return prompt


def _generate_insights(city_data: Dict, user_context: Optional[Dict]) -> List[str]:
    """Generate additional insights based on city data"""
    insights = []
    
    cost_idx = city_data['cost_index']
    rent_idx = city_data['rent_index']
    
    # Cost insights
    if cost_idx > 90:
        insights.append(f"{city_data['city']} is an expensive city. Budget carefully!")
    elif cost_idx < 50:
        insights.append(f"{city_data['city']} is very affordable. Your money goes further here!")
    
    # Rent insights
    if rent_idx > 100:
        insights.append(f"Rent in {city_data['city']} is above average. Consider roommates or suburbs.")
    elif rent_idx < 60:
        insights.append(f"Rent in {city_data['city']} is relatively affordable.")
    
    # Purchasing power
    if city_data['purchasing_power'] > 90:
        insights.append(f"High purchasing power in {city_data['city']} means better value for your income.")
    
    return insights
