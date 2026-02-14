# CHECKPOINT_5_LLM_PIPELINE
"""
LLM Prompt Templates
====================
Prompt templates for the two-LLM pipeline and function calling.
"""

from typing import Dict, Any
from datetime import datetime

# ============================================
# LLM #1: Extraction Prompts
# ============================================

EXTRACTION_SYSTEM_PROMPT = """You are an expense tracking assistant. Your job is to extract expense information from user input.

Extract the following information:
1. Amount: The monetary value (convert words to numbers if needed)
2. Category: Classify into one of: food, transportation, entertainment, utilities, housing, healthcare, shopping, education, personal, other
3. Description: A brief summary of what the expense was for
4. Date: The date of the expense (default to today if not specified)

User input can be text or transcribed speech. Handle colloquialisms and informal language.

Examples:
- "I spent 50 dollars on groceries yesterday" → amount: 50, category: food, description: groceries, date: yesterday
- "Uber to work was fifteen bucks" → amount: 15, category: transportation, description: Uber to work, date: today
- "Movie tickets twenty five" → amount: 25, category: entertainment, description: movie tickets, date: today

Always respond with valid JSON matching the schema provided.
"""

EXTRACTION_USER_PROMPT_TEMPLATE = """Extract expense information from this input:

User input: "{user_input}"

Today's date: {today_date}

Extract: amount, category, description, and date. If any information is missing or unclear, make your best guess based on context and set confidence accordingly.

Respond with valid JSON only."""


# ============================================
# LLM #2: Validation Prompts
# ============================================

VALIDATION_SYSTEM_PROMPT = """You are a data validation assistant for an expense tracking system.

Your job is to:
1. Verify that extracted expense data is accurate and reasonable
2. Normalize categories to standard values
3. Clean and improve descriptions
4. Validate date formats
5. Check that amounts are realistic

Standard categories: food, transportation, entertainment, utilities, housing, healthcare, shopping, education, personal, other

If data is invalid, explain why. If valid, provide the cleaned version.

Always respond with valid JSON matching the schema provided.
"""

VALIDATION_USER_PROMPT_TEMPLATE = """Validate and clean this extracted expense data:

Extracted data:
- Amount: {amount}
- Category: {category}
- Description: {description}
- Date: {date}

Original input: "{original_input}"

Check if:
1. Amount is a positive number and reasonable (not too large or small)
2. Category matches one of the standard categories
3. Description is clear and concise
4. Date is in valid ISO format (YYYY-MM-DD)

If valid, return cleaned data. If invalid, list errors and provide suggestions.

Respond with valid JSON only."""


# ============================================
# Function Calling Prompts
# ============================================

FUNCTION_CALLING_SYSTEM_PROMPT = """You are an expense tracking assistant with function calling capabilities.

You have access to these functions:
1. add_expense(amount, category, description, date) - Add a new expense
2. set_budget(category, amount, period) - Set a budget limit

When a user provides expense information, call the appropriate function with the correct parameters.

Always use the exact schema provided for function calls."""

FUNCTION_CALLING_USER_PROMPT_TEMPLATE = """User said: "{user_input}"

Determine which function to call and extract the parameters. Call the function with valid arguments.

Available functions: add_expense, set_budget

Today's date: {today_date}"""


# ============================================
# Categorization Prompt
# ============================================

CATEGORIZATION_PROMPT_TEMPLATE = """Categorize this expense description into one of these categories:
- food (groceries, restaurants, food delivery, snacks)
- transportation (uber, taxi, gas, parking, public transit)
- entertainment (movies, concerts, games, subscriptions)
- utilities (electricity, water, internet, phone)
- housing (rent, mortgage, repairs, furniture)
- healthcare (doctor, medicine, insurance, pharmacy)
- shopping (clothes, electronics, household items)
- education (books, courses, tuition, supplies)
- personal (haircut, gym, hobbies, gifts)
- other (anything that doesn't fit above)

Description: "{description}"

Category:"""


# ============================================
# Prompt Builders
# ============================================

def build_extraction_prompt(user_input: str) -> Dict[str, str]:
    """Build prompt for extraction LLM"""
    today = datetime.now().strftime("%Y-%m-%d")
    return {
        "system": EXTRACTION_SYSTEM_PROMPT,
        "user": EXTRACTION_USER_PROMPT_TEMPLATE.format(
            user_input=user_input,
            today_date=today
        )
    }


def build_validation_prompt(
    extracted_data: Dict[str, Any],
    original_input: str
) -> Dict[str, str]:
    """Build prompt for validation LLM"""
    return {
        "system": VALIDATION_SYSTEM_PROMPT,
        "user": VALIDATION_USER_PROMPT_TEMPLATE.format(
            amount=extracted_data.get("amount", "unknown"),
            category=extracted_data.get("category", "unknown"),
            description=extracted_data.get("description", "unknown"),
            date=extracted_data.get("date", "unknown"),
            original_input=original_input
        )
    }


def build_function_calling_prompt(user_input: str) -> Dict[str, str]:
    """Build prompt for function calling"""
    today = datetime.now().strftime("%Y-%m-%d")
    return {
        "system": FUNCTION_CALLING_SYSTEM_PROMPT,
        "user": FUNCTION_CALLING_USER_PROMPT_TEMPLATE.format(
            user_input=user_input,
            today_date=today
        )
    }


def build_categorization_prompt(description: str) -> str:
    """Build prompt for simple categorization"""
    return CATEGORIZATION_PROMPT_TEMPLATE.format(description=description)
