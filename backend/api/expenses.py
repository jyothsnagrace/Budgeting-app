# CHECKPOINT_7_API_ENDPOINTS
"""
Expense API Endpoints
=====================
REST endpoints for expense operations with LLM integration.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID

from backend.database.client import get_database
from backend.llm.pipeline import TwoLLMPipeline
from backend.utils.logger import get_logger

logger = get_logger("expense_api")
router = APIRouter(prefix="/expenses", tags=["expenses"])


# ============================================
# Request/Response Models
# ============================================

class AddExpenseRequest(BaseModel):
    """Request to add expense via natural language"""
    user_id: str
    input_text: str = Field(..., description="Natural language expense description")
    input_method: str = Field(default="text", description="text or voice")
    
    @validator("input_method")
    def validate_input_method(cls, v):
        if v not in ["text", "voice"]:
            raise ValueError("input_method must be 'text' or 'voice'")
        return v


class AddExpenseDirectRequest(BaseModel):
    """Request to add expense with structured data"""
    user_id: str
    amount: float = Field(..., gt=0)
    category: str
    description: str
    date: str = Field(..., description="ISO format: YYYY-MM-DD")
    
    @validator("category")
    def validate_category(cls, v):
        valid_categories = [
            "food", "transportation", "entertainment", "utilities",
            "housing", "healthcare", "shopping", "education", "personal", "other"
        ]
        if v.lower() not in valid_categories:
            raise ValueError(f"Category must be one of: {', '.join(valid_categories)}")
        return v.lower()


class ExpenseResponse(BaseModel):
    """Response model for expense"""
    id: str
    user_id: str
    amount: float
    category: str
    description: str
    date: str
    input_method: str
    created_at: datetime
    llm_extracted: Optional[dict] = None
    llm_validated: Optional[dict] = None


class ExpenseListResponse(BaseModel):
    """Response model for expense list"""
    expenses: List[ExpenseResponse]
    total: int
    page: int
    limit: int


class ExpenseSummary(BaseModel):
    """Summary statistics for expenses"""
    total_amount: float
    expense_count: int
    category_breakdown: dict
    date_range: dict


# ============================================
# Expense Endpoints
# ============================================

@router.post("/add", response_model=ExpenseResponse)
async def add_expense_from_text(request: AddExpenseRequest):
    """
    Add expense from natural language input.
    
    Uses Two-LLM pipeline:
    1. LLM #1 extracts structured data
    2. LLM #2 validates and normalizes
    3. Saves to database
    """
    logger.info(f"Adding expense from text: {request.input_text}")
    
    try:
        # Initialize LLM pipeline
        pipeline = TwoLLMPipeline()
        
        # Stage 1: Extract data
        extracted = await pipeline.extract_expense_data(
            user_input=request.input_text,
            input_method=request.input_method
        )
        
        # Stage 2: Validate data
        validated = await pipeline.validate_expense_data(
            extracted_data=extracted,
            original_input=request.input_text
        )
        
        # Check if validation passed
        if not validated.get("is_valid", False):
            raise ValueError(f"Validation failed: {validated.get('errors', [])}")
        
        # Extract final data
        final_data = validated.get("validated_data", {})
        
        # Save to database
        db = await get_database()
        expense = await db.add_expense(
            user_id=request.user_id,
            amount=final_data["amount"],
            category=final_data["category"],
            description=final_data["description"],
            expense_date=final_data["date"],
            input_method=request.input_method,
            raw_input=request.input_text,
            llm_extracted=extracted,
            llm_validated=validated
        )
        
        # Also add to calendar
        await db.add_calendar_entry(
            user_id=request.user_id,
            expense_id=expense["id"],
            entry_date=final_data["date"],
            title=f"{final_data['category']}: ${final_data['amount']}",
            description=final_data["description"],
            amount=final_data["amount"],
            category=final_data["category"]
        )
        
        logger.info(f"✓ Expense added: {expense['id']}")
        
        return ExpenseResponse(
            id=str(expense["id"]),
            user_id=str(expense["user_id"]),
            amount=expense["amount"],
            category=expense["category"],
            description=expense["description"],
            date=expense["expense_date"],
            input_method=expense["input_method"],
            created_at=expense["created_at"],
            llm_extracted=extracted,
            llm_validated=validated
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to add expense: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add expense: {str(e)}")


@router.post("/add-direct", response_model=ExpenseResponse)
async def add_expense_direct(request: AddExpenseDirectRequest):
    """
    Add expense with pre-structured data (no LLM processing).
    
    Use this endpoint when you already have structured data.
    """
    logger.info(f"Adding expense directly: {request.amount} for {request.category}")
    
    try:
        db = await get_database()
        
        expense = await db.add_expense(
            user_id=request.user_id,
            amount=request.amount,
            category=request.category,
            description=request.description,
            expense_date=request.date,
            input_method="direct",
            raw_input=None,
            llm_extracted=None,
            llm_validated=None
        )
        
        # Also add to calendar
        await db.add_calendar_entry(
            user_id=request.user_id,
            expense_id=expense["id"],
            entry_date=request.date,
            title=f"{request.category}: ${request.amount}",
            description=request.description,
            amount=request.amount,
            category=request.category
        )
        
        logger.info(f"✓ Expense added directly: {expense['id']}")
        
        return ExpenseResponse(
            id=str(expense["id"]),
            user_id=str(expense["user_id"]),
            amount=expense["amount"],
            category=expense["category"],
            description=expense["description"],
            date=expense["expense_date"],
            input_method="direct",
            created_at=expense["created_at"]
        )
        
    except Exception as e:
        logger.error(f"Failed to add expense: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=ExpenseListResponse)
async def list_expenses(
    user_id: str,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Get list of expenses for a user with optional filters.
    """
    logger.info(f"Fetching expenses for user: {user_id}")
    
    try:
        db = await get_database()
        expenses = await db.get_user_expenses(user_id, limit, offset)
        
        # Convert to response models
        expense_responses = [
            ExpenseResponse(
                id=str(exp["id"]),
                user_id=str(exp["user_id"]),
                amount=exp["amount"],
                category=exp["category"],
                description=exp["description"],
                date=exp["expense_date"],
                input_method=exp.get("input_method", "text"),
                created_at=exp["created_at"],
                llm_extracted=exp.get("llm_extracted"),
                llm_validated=exp.get("llm_validated")
            )
            for exp in expenses
        ]
        
        return ExpenseListResponse(
            expenses=expense_responses,
            total=len(expense_responses),
            page=offset // limit,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Failed to fetch expenses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary", response_model=ExpenseSummary)
async def get_expense_summary(
    user_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Get expense summary with category breakdown.
    """
    logger.info(f"Generating expense summary for user: {user_id}")
    
    try:
        db = await get_database()
        expenses = await db.get_user_expenses(user_id, limit=1000)
        
        # Calculate summary
        total_amount = sum(exp["amount"] for exp in expenses)
        
        # Category breakdown
        category_breakdown = {}
        for exp in expenses:
            cat = exp["category"]
            category_breakdown[cat] = category_breakdown.get(cat, 0) + exp["amount"]
        
        # Date range
        dates = [exp["expense_date"] for exp in expenses]
        date_range = {
            "start": min(dates) if dates else None,
            "end": max(dates) if dates else None
        }
        
        return ExpenseSummary(
            total_amount=total_amount,
            expense_count=len(expenses),
            category_breakdown=category_breakdown,
            date_range=date_range
        )
        
    except Exception as e:
        logger.error(f"Failed to generate summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{expense_id}")
async def delete_expense(expense_id: str, user_id: str):
    """
    Delete an expense.
    """
    # TODO: Implement delete operation
    logger.info(f"Deleting expense: {expense_id}")
    raise HTTPException(status_code=501, detail="Delete operation not yet implemented")
