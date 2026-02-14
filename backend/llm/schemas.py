# CHECKPOINT_6_FUNCTION_CALLING
"""
JSON Schemas for Structured Function Calling
=============================================
Defines JSON schemas for LLM function calls to ensure structured outputs.
"""

from typing import Dict, Any

# ============================================
# Expense Schema
# ============================================

ADD_EXPENSE_SCHEMA = {
    "name": "add_expense",
    "description": "Add a new expense transaction to the database",
    "parameters": {
        "type": "object",
        "properties": {
            "amount": {
                "type": "number",
                "description": "The monetary amount of the expense (positive number)",
                "minimum": 0.01
            },
            "category": {
                "type": "string",
                "description": "Category of the expense",
                "enum": [
                    "food",
                    "transportation",
                    "entertainment",
                    "utilities",
                    "housing",
                    "healthcare",
                    "shopping",
                    "education",
                    "personal",
                    "other"
                ]
            },
            "description": {
                "type": "string",
                "description": "Brief description of the expense",
                "maxLength": 500
            },
            "date": {
                "type": "string",
                "description": "Date of the expense in ISO format (YYYY-MM-DD)",
                "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
            }
        },
        "required": ["amount", "category", "description", "date"]
    }
}

# ============================================
# Budget Schema
# ============================================

SET_BUDGET_SCHEMA = {
    "name": "set_budget",
    "description": "Set or update a budget limit for a category",
    "parameters": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "Category for the budget",
                "enum": [
                    "food",
                    "transportation",
                    "entertainment",
                    "utilities",
                    "housing",
                    "healthcare",
                    "shopping",
                    "education",
                    "personal",
                    "total"
                ]
            },
            "amount": {
                "type": "number",
                "description": "Budget limit amount (positive number)",
                "minimum": 0
            },
            "period": {
                "type": "string",
                "description": "Time period for the budget",
                "enum": ["daily", "weekly", "monthly", "yearly"],
                "default": "monthly"
            }
        },
        "required": ["category", "amount", "period"]
    }
}

# ============================================
# Extraction Schema (for LLM #1)
# ============================================

EXPENSE_EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {
            "type": "string",
            "enum": ["add_expense", "set_budget", "query_expenses", "unknown"],
            "description": "The user's intent based on their input"
        },
        "extracted_data": {
            "type": "object",
            "description": "Data extracted from user input",
            "properties": {
                "amount": {
                    "type": ["number", "null"],
                    "description": "Extracted monetary amount"
                },
                "category": {
                    "type": ["string", "null"],
                    "description": "Extracted or inferred category"
                },
                "description": {
                    "type": ["string", "null"],
                    "description": "Extracted description"
                },
                "date": {
                    "type": ["string", "null"],
                    "description": "Extracted date in ISO format"
                },
                "confidence": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Confidence score of extraction (0-1)"
                }
            }
        }
    },
    "required": ["intent", "extracted_data"]
}

# ============================================
# Validation Schema (for LLM #2)
# ============================================

EXPENSE_VALIDATION_SCHEMA = {
    "type": "object",
    "properties": {
        "is_valid": {
            "type": "boolean",
            "description": "Whether the extracted data is valid"
        },
        "validated_data": {
            "type": "object",
            "description": "Cleaned and validated data",
            "properties": {
                "amount": {
                    "type": "number",
                    "description": "Validated amount"
                },
                "category": {
                    "type": "string",
                    "description": "Normalized category"
                },
                "description": {
                    "type": "string",
                    "description": "Cleaned description"
                },
                "date": {
                    "type": "string",
                    "description": "Validated date in YYYY-MM-DD format"
                }
            },
            "required": ["amount", "category", "description", "date"]
        },
        "errors": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "List of validation errors (if any)"
        },
        "suggestions": {
            "type": "object",
            "description": "Suggested corrections or improvements",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Suggested category if current is unclear"
                },
                "description": {
                    "type": "string",
                    "description": "Suggested improved description"
                }
            }
        }
    },
    "required": ["is_valid", "validated_data", "errors"]
}

# ============================================
# Schema Registry
# ============================================

SCHEMAS: Dict[str, Dict[str, Any]] = {
    "add_expense": ADD_EXPENSE_SCHEMA,
    "set_budget": SET_BUDGET_SCHEMA,
    "extraction": EXPENSE_EXTRACTION_SCHEMA,
    "validation": EXPENSE_VALIDATION_SCHEMA
}


def get_schema(name: str) -> Dict[str, Any]:
    """Get a schema by name"""
    if name not in SCHEMAS:
        raise ValueError(f"Schema '{name}' not found. Available: {list(SCHEMAS.keys())}")
    return SCHEMAS[name]


def get_all_function_schemas() -> list[Dict[str, Any]]:
    """Get all function schemas for LLM function calling"""
    return [ADD_EXPENSE_SCHEMA, SET_BUDGET_SCHEMA]
