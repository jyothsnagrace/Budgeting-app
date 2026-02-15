# CHECKPOINT_8_EXTERNAL_API
"""
Cost of Living API Integration
===============================
Integration with free cost-of-living data APIs.
"""

import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger("cost_of_living")


class CostOfLivingService:
    """
    Service for fetching cost-of-living data from free APIs.
    
    Free API Options:
    1. Numbeo API (limited free tier)
    2. Cost of Living API on RapidAPI (free tier)
    3. Custom scraped data (fallback)
    """
    
    def __init__(self):
        self.base_url = "https://cost-of-living-and-prices.p.rapidapi.com"
        self.api_key = getattr(settings, 'RAPIDAPI_KEY', None)
        self.cache = {}  # Simple in-memory cache
        self.cache_duration = timedelta(days=7)  # Cache for 7 days
    
    async def get_city_data(
        self,
        city_name: str,
        country_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get cost-of-living data for a city.
        
        Args:
            city_name: Name of the city
            country_name: Optional country name for disambiguation
        
        Returns:
            Cost data including various indices
        """
        # Check cache first
        cache_key = f"{city_name}:{country_name or 'any'}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_duration:
                logger.info(f"Returning cached data for {city_name}")
                return cached_data
        
        try:
            # Try RapidAPI Cost of Living API
            if self.api_key:
                data = await self._fetch_from_rapidapi(city_name, country_name)
            else:
                # Fallback to mock data
                logger.warning("No RapidAPI key found, using mock data")
                data = self._get_mock_data(city_name, country_name)
            
            # Cache the result
            self.cache[cache_key] = (data, datetime.now())
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to fetch cost data for {city_name}: {e}")
            # Return mock data on error
            return self._get_mock_data(city_name, country_name)
    
    async def _fetch_from_rapidapi(
        self,
        city_name: str,
        country_name: Optional[str]
    ) -> Dict[str, Any]:
        """Fetch data from RapidAPI Cost of Living API"""
        async with httpx.AsyncClient() as client:
            headers = {
                "X-RapidAPI-Key": self.api_key,
                "X-RapidAPI-Host": "cost-of-living-and-prices.p.rapidapi.com"
            }
            
            # Search for city
            search_url = f"{self.base_url}/cities"
            query = {"city_name": city_name}
            if country_name:
                query["country_name"] = country_name
            
            response = await client.get(
                search_url,
                headers=headers,
                params=query,
                timeout=10.0
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Parse and structure the data
            return self._parse_api_response(data, city_name)
    
    def _parse_api_response(self, api_data: Dict, city_name: str) -> Dict[str, Any]:
        """Parse API response into standardized format"""
        # This will depend on the actual API response structure
        return {
            "city": city_name,
            "country": api_data.get("country", "Unknown"),
            "cost_index": api_data.get("cost_of_living_index", 100.0),
            "rent_index": api_data.get("rent_index", 100.0),
            "groceries_index": api_data.get("groceries_index", 100.0),
            "restaurant_index": api_data.get("restaurant_price_index", 100.0),
            "purchasing_power": api_data.get("local_purchasing_power_index", 100.0),
            "currency": api_data.get("currency", "USD"),
            "updated_at": datetime.now().isoformat(),
            "source": "rapidapi"
        }
    
    def _get_mock_data(self, city_name: str, country_name: Optional[str]) -> Dict[str, Any]:
        """
        Get mock cost-of-living data.
        
        Uses approximate real-world indices (baseline = 100 for New York)
        """
        # Mock data for common cities
        mock_data = {
            "new york": {"cost_index": 100, "rent_index": 100, "groceries": 100},
            "san francisco": {"cost_index": 104, "rent_index": 135, "groceries": 108},
            "los angeles": {"cost_index": 82, "rent_index": 85, "groceries": 84},
            "chicago": {"cost_index": 77, "rent_index": 67, "groceries": 76},
            "boston": {"cost_index": 87, "rent_index": 78, "groceries": 86},
            "seattle": {"cost_index": 86, "rent_index": 83, "groceries": 89},
            "austin": {"cost_index": 72, "rent_index": 62, "groceries": 70},
            "london": {"cost_index": 88, "rent_index": 85, "groceries": 82},
            "paris": {"cost_index": 91, "rent_index": 78, "groceries": 90},
            "tokyo": {"cost_index": 92, "rent_index": 68, "groceries": 93},
            "singapore": {"cost_index": 93, "rent_index": 122, "groceries": 88},
            "sydney": {"cost_index": 86, "rent_index": 76, "groceries": 90},
            "toronto": {"cost_index": 75, "rent_index": 65, "groceries": 77},
            "bangalore": {"cost_index": 26, "rent_index": 18, "groceries": 28},
            "mumbai": {"cost_index": 32, "rent_index": 42, "groceries": 34},
            "delhi": {"cost_index": 25, "rent_index": 21, "groceries": 27},
        }
        
        city_key = city_name.lower()
        city_data = mock_data.get(city_key, {
            "cost_index": 60,
            "rent_index": 50,
            "groceries": 60
        })
        
        return {
            "city": city_name.title(),
            "country": country_name or "Unknown",
            "cost_index": city_data["cost_index"],
            "rent_index": city_data["rent_index"],
            "groceries_index": city_data["groceries"],
            "restaurant_index": city_data["cost_index"] * 0.95,
            "purchasing_power": 100 - (city_data["cost_index"] * 0.3),
            "currency": "USD",
            "updated_at": datetime.now().isoformat(),
            "source": "mock_data",
            "note": "This is mock data. Configure RAPIDAPI_KEY for real data."
        }
    
    async def compare_user_spending(
        self,
        user_expenses: List[Dict[str, Any]],
        city_name: str,
        country_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compare user's spending to city average.
        
        Args:
            user_expenses: List of user expense records
            city_name: City to compare against
            country_name: Optional country name
        
        Returns:
            Comparison with insights
        """
        # Get city data
        city_data = await self.get_city_data(city_name, country_name)
        
        # Calculate user spending by category
        user_spending = {}
        for expense in user_expenses:
            cat = expense.get("category", "other")
            amount = expense.get("amount", 0)
            user_spending[cat] = user_spending.get(cat, 0) + amount
        
        # Average monthly spending benchmarks (based on NYC baseline)
        nyc_benchmarks = {
            "food": 600,
            "transportation": 150,
            "entertainment": 200,
            "utilities": 150,
            "housing": 2000,
            "healthcare": 300,
            "shopping": 250,
            "personal": 150
        }
        
        # Adjust benchmarks for this city
        cost_ratio = city_data["cost_index"] / 100.0
        city_benchmarks = {
            cat: amount * cost_ratio
            for cat, amount in nyc_benchmarks.items()
        }
        
        # Compare
        comparisons = {}
        insights = []
        
        for category, user_amount in user_spending.items():
            if category in city_benchmarks:
                benchmark = city_benchmarks[category]
                difference = user_amount - benchmark
                percentage_diff = (difference / benchmark * 100) if benchmark > 0 else 0
                
                comparisons[category] = {
                    "user_spent": user_amount,
                    "city_average": benchmark,
                    "difference": difference,
                    "percentage_diff": percentage_diff
                }
                
                # Generate insight
                if percentage_diff > 20:
                    insights.append(
                        f"Your {category} spending is {abs(percentage_diff):.0f}% "
                        f"higher than {city_name} average"
                    )
                elif percentage_diff < -20:
                    insights.append(
                        f"Your {category} spending is {abs(percentage_diff):.0f}% "
                        f"lower than {city_name} average"
                    )
        
        return {
            "city": city_data["city"],
            "cost_index": city_data["cost_index"],
            "comparisons": comparisons,
            "insights": insights,
            "overall_status": self._get_overall_status(comparisons)
        }
    
    def _get_overall_status(self, comparisons: Dict) -> str:
        """Determine overall spending status"""
        if not comparisons:
            return "No data available"
        
        avg_diff = sum(
            comp["percentage_diff"]
            for comp in comparisons.values()
        ) / len(comparisons)
        
        if avg_diff > 20:
            return "Spending significantly above average"
        elif avg_diff > 5:
            return "Spending slightly above average"
        elif avg_diff < -20:
            return "Spending significantly below average"
        elif avg_diff < -5:
            return "Spending slightly below average"
        else:
            return "Spending around average"


# ============================================
# Singleton Instance
# ============================================

_cost_service: Optional[CostOfLivingService] = None


def get_cost_service() -> CostOfLivingService:
    """Get cost-of-living service singleton"""
    global _cost_service
    if _cost_service is None:
        _cost_service = CostOfLivingService()
    return _cost_service
