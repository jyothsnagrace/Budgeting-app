# CHECKPOINT_7_API_ENDPOINTS
"""
Budget API Endpoints
====================
REST endpoints for budget management.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from backend.database.client import get_database
from backend.utils.logger import get_logger

logger = get_logger("budget_api")
router = APIRouter(prefix="/budgets", tags=["budgets"])


# ============================================
# Request/Response Models
# ============================================

class SetBudgetRequest(BaseModel):
    """Request to set or update a budget"""
    user_id: str
    category: str
    amount: float = Field(..., gt=0)
    period: str = Field(default="monthly", description="daily, weekly, monthly, yearly")
    
    @validator("category")
    def validate_category(cls, v):
        valid_categories = [
            "food", "transportation", "entertainment", "utilities",
            "housing", "healthcare", "shopping", "education", "personal", "total", "other"
        ]
        if v.lower() not in valid_categories:
            raise ValueError(f"Category must be one of: {', '.join(valid_categories)}")
        return v.lower()
    
    @validator("period")
    def validate_period(cls, v):
        valid_periods = ["daily", "weekly", "monthly", "yearly"]
        if v.lower() not in valid_periods:
            raise ValueError(f"Period must be one of: {', '.join(valid_periods)}")
        return v.lower()


class BudgetResponse(BaseModel):
    """Response model for budget"""
    id: str
    user_id: str
    category: str
    amount: float
    period: str
    start_date: str
    created_at: datetime


class BudgetStatus(BaseModel):
    """Budget status with spending information"""
    budget: BudgetResponse
    spent: float
    remaining: float
    percentage_used: float
    is_exceeded: bool


class BudgetListResponse(BaseModel):
    """Response model for budget list"""
    budgets: List[BudgetStatus]
    total_budget: float
    total_spent: float


# ============================================
# Budget Endpoints
# ============================================

@router.post("/set", response_model=BudgetResponse)
async def set_budget(request: SetBudgetRequest):
    """
    Set or update a budget for a category.
    
    If a budget already exists for the user/category/period, it will be updated.
    """
    logger.info(f"Setting budget: {request.category} = ${request.amount} ({request.period})")
    
    try:
        db = await get_database()
        
        budget = await db.set_budget(
            user_id=request.user_id,
            category=request.category,
            amount=request.amount,
            period=request.period
        )
        
        logger.info(f"✓ Budget set: {budget['id']}")
        
        return BudgetResponse(
            id=str(budget["id"]),
            user_id=str(budget["user_id"]),
            category=budget["category"],
            amount=budget["amount"],
            period=budget["period"],
            start_date=budget["start_date"],
            created_at=budget["created_at"]
        )
        
    except Exception as e:
        logger.error(f"Failed to set budget: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=BudgetListResponse)
async def list_budgets(user_id: str):
    """
    Get all budgets for a user with spending status.
    """
    logger.info(f"Fetching budgets for user: {user_id}")
    
    try:
        db = await get_database()
        
        # Get budgets
        budgets = await db.get_user_budgets(user_id)
        
        # Get expenses to calculate spending
        expenses = await db.get_user_expenses(user_id, limit=1000)
        
        # Calculate spending by category
        spending_by_category = {}
        for exp in expenses:
            cat = exp["category"]
            spending_by_category[cat] = spending_by_category.get(cat, 0) + exp["amount"]
        
        total_spent = sum(spending_by_category.values())
        
        # Build budget statuses
        budget_statuses = []
        total_budget = 0
        
        for budget in budgets:
            cat = budget["category"]
            budget_amount = budget["amount"]
            spent = spending_by_category.get(cat, 0)
            remaining = budget_amount - spent
            percentage = (spent / budget_amount * 100) if budget_amount > 0 else 0
            
            total_budget += budget_amount
            
            budget_statuses.append(BudgetStatus(
                budget=BudgetResponse(
                    id=str(budget["id"]),
                    user_id=str(budget["user_id"]),
                    category=budget["category"],
                    amount=budget["amount"],
                    period=budget["period"],
                    start_date=budget["start_date"],
                    created_at=budget["created_at"]
                ),
                spent=spent,
                remaining=remaining,
                percentage_used=percentage,
                is_exceeded=spent > budget_amount
            ))
        
        return BudgetListResponse(
            budgets=budget_statuses,
            total_budget=total_budget,
            total_spent=total_spent
        )
        
    except Exception as e:
        logger.error(f"Failed to fetch budgets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{category}", response_model=BudgetStatus)
async def get_budget_status(user_id: str, category: str, period: str = "monthly"):
    """
    Get budget status for a specific category.
    """
    logger.info(f"Fetching budget status: {category} ({period})")
    
    try:
        db = await get_database()
        
        # Get all budgets and find the matching one
        budgets = await db.get_user_budgets(user_id)
        budget = next(
            (b for b in budgets if b["category"] == category and b["period"] == period),
            None
        )
        
        if not budget:
            raise HTTPException(
                status_code=404,
                detail=f"No budget found for {category} ({period})"
            )
        
        # Get expenses for this category
        expenses = await db.get_user_expenses(user_id, limit=1000)
        spent = sum(
            exp["amount"]
            for exp in expenses
            if exp["category"] == category
        )
        
        budget_amount = budget["amount"]
        remaining = budget_amount - spent
        percentage = (spent / budget_amount * 100) if budget_amount > 0 else 0
        
        return BudgetStatus(
            budget=BudgetResponse(
                id=str(budget["id"]),
                user_id=str(budget["user_id"]),
                category=budget["category"],
                amount=budget["amount"],
                period=budget["period"],
                start_date=budget["start_date"],
                created_at=budget["created_at"]
            ),
            spent=spent,
            remaining=remaining,
            percentage_used=percentage,
            is_exceeded=spent > budget_amount
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch budget status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{budget_id}")
async def delete_budget(budget_id: str, user_id: str):
    """
    Delete a budget.
    """
    # TODO: Implement delete operation
    logger.info(f"Deleting budget: {budget_id}")
    raise HTTPException(status_code=501, detail="Delete operation not yet implemented")
