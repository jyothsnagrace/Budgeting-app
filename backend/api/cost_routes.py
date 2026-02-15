# CHECKPOINT_8_EXTERNAL_API
"""
Cost of Living API Endpoints
=============================
REST endpoints for cost-of-living data.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict

from backend.api.cost_of_living import get_cost_service
from backend.database.client import get_database
from backend.utils.logger import get_logger

logger = get_logger("cost_api")
router = APIRouter(prefix="/cost-of-living", tags=["cost-of-living"])


# ============================================
# Request/Response Models
# ============================================

class CityDataResponse(BaseModel):
    """Response model for city cost data"""
    city: str
    country: str
    cost_index: float
    rent_index: float
    groceries_index: float
    restaurant_index: float
    purchasing_power: float
    currency: str
    updated_at: str
    source: str
    note: Optional[str] = None


class ComparisonResponse(BaseModel):
    """Response model for spending comparison"""
    city: str
    cost_index: float
    comparisons: Dict
    insights: List[str]
    overall_status: str


# ============================================
# Cost of Living Endpoints
# ============================================

@router.get("/city/{city_name}", response_model=CityDataResponse)
async def get_city_cost_data(
    city_name: str,
    country: Optional[str] = None
):
    """
    Get cost-of-living data for a city.
    
    Parameters:
        city_name: Name of the city
        country: Optional country name for disambiguation
    """
    logger.info(f"Fetching cost data for: {city_name}")
    
    try:
        service = get_cost_service()
        data = await service.get_city_data(city_name, country)
        
        return CityDataResponse(**data)
        
    except Exception as e:
        logger.error(f"Failed to fetch city data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch cost data: {str(e)}"
        )


@router.get("/compare", response_model=ComparisonResponse)
async def compare_user_spending(
    user_id: str,
    city_name: str,
    country: Optional[str] = None,
    months: int = Query(default=1, ge=1, le=12)
):
    """
    Compare user's spending to city average.
    
    Parameters:
        user_id: User ID
        city_name: City to compare against
        country: Optional country name
        months: Number of months to analyze (1-12)
    """
    logger.info(f"Comparing spending for user {user_id} in {city_name}")
    
    try:
        # Get user expenses
        db = await get_database()
        expenses = await db.get_user_expenses(user_id, limit=1000)
        
        # Get cost service and compare
        service = get_cost_service()
        comparison = await service.compare_user_spending(
            user_expenses=expenses,
            city_name=city_name,
            country_name=country
        )
        
        return ComparisonResponse(**comparison)
        
    except Exception as e:
        logger.error(f"Failed to compare spending: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compare spending: {str(e)}"
        )


@router.get("/insights/{user_id}")
async def get_spending_insights(
    user_id: str,
    city_name: str,
    country: Optional[str] = None
):
    """
    Get personalized spending insights based on cost-of-living data.
    """
    logger.info(f"Generating insights for user {user_id}")
    
    try:
        # Get comparison
        db = await get_database()
        expenses = await db.get_user_expenses(user_id, limit=1000)
        
        service = get_cost_service()
        comparison = await service.compare_user_spending(
            user_expenses=expenses,
            city_name=city_name,
            country_name=country
        )
        
        # Generate additional insights
        insights = comparison["insights"]
        
        # Add more insights based on data
        city_data = await service.get_city_data(city_name, country)
        
        if city_data["cost_index"] > 90:
            insights.append(
                f"{city_name} is an expensive city (cost index: {city_data['cost_index']}). "
                "Consider budgeting carefully."
            )
        elif city_data["cost_index"] < 50:
            insights.append(
                f"{city_name} is relatively affordable (cost index: {city_data['cost_index']})."
            )
        
        return {
            "user_id": user_id,
            "city": city_name,
            "insights": insights,
            "overall_status": comparison["overall_status"],
            "city_cost_index": city_data["cost_index"]
        }
        
    except Exception as e:
        logger.error(f"Failed to generate insights: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate insights: {str(e)}"
        )
