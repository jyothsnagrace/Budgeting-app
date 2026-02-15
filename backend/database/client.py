# CHECKPOINT_3_DATABASE
"""
Supabase Database Client
=========================
Wrapper for Supabase operations.
"""

from typing import Dict, Any, List, Optional
from supabase import create_client, Client
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger("database")


class SupabaseClient:
    """Wrapper for Supabase database operations"""
    
    _instance: Optional['SupabaseClient'] = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Supabase client"""
        try:
            self._client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY
            )
            logger.info("✓ Supabase client initialized")
        except Exception as e:
            logger.error(f"✗ Failed to initialize Supabase client: {e}")
            raise
    
    @property
    def client(self) -> Client:
        """Get the Supabase client"""
        if self._client is None:
            self._initialize_client()
        return self._client
    
    # ============================================
    # User Operations
    # ============================================
    
    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        try:
            response = self.client.table("users").select("*").eq("username", username).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error fetching user: {e}")
            return None
    
    async def create_user(self, username: str, display_name: Optional[str] = None) -> Dict[str, Any]:
        """Create a new user"""
        try:
            data = {"username": username}
            if display_name:
                data["display_name"] = display_name
            
            response = self.client.table("users").insert(data).execute()
            logger.info(f"✓ Created user: {username}")
            return response.data[0]
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            response = self.client.table("users").select("*").eq("id", user_id).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error fetching user by ID: {e}")
            return None
    
    async def update_user_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        try:
            from datetime import datetime
            self.client.table("users").update({
                "last_login": datetime.now().isoformat()
            }).eq("id", user_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error updating last login: {e}")
            return False
    
    #============================================
    # Expense Operations
    # ============================================
    
    async def add_expense(
        self,
        user_id: str,
        amount: float,
        category: str,
        description: str,
        expense_date: str,
        input_method: str = "text",
        raw_input: Optional[str] = None,
        llm_extracted: Optional[Dict] = None,
        llm_validated: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Add a new expense"""
        try:
            data = {
                "user_id": user_id,
                "amount": amount,
                "category": category,
                "description": description,
                "expense_date": expense_date,
                "input_method": input_method,
                "raw_input": raw_input,
                "llm_extracted": llm_extracted,
                "llm_validated": llm_validated
            }
            
            response = self.client.table("expenses").insert(data).execute()
            logger.info(f"✓ Added expense: {amount} for {category}")
            return response.data[0]
        except Exception as e:
            logger.error(f"Error adding expense: {e}")
            raise
    
    async def get_user_expenses(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get expenses for a user"""
        try:
            response = (
                self.client.table("expenses")
                .select("*")
                .eq("user_id", user_id)
                .order("expense_date", desc=True)
                .limit(limit)
                .offset(offset)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Error fetching expenses: {e}")
            return []
    
    # ============================================
    # Budget Operations
    # ============================================
    
    async def set_budget(
        self,
        user_id: str,
        category: str,
        amount: float,
        period: str = "monthly"
    ) -> Dict[str, Any]:
        """Set or update a budget"""
        try:
            # Check if budget exists
            existing = (
                self.client.table("budgets")
                .select("*")
                .eq("user_id", user_id)
                .eq("category", category)
                .eq("period", period)
                .execute()
            )
            
            data = {
                "user_id": user_id,
                "category": category,
                "amount": amount,
                "period": period
            }
            
            if existing.data and len(existing.data) > 0:
                # Update existing
                response = (
                    self.client.table("budgets")
                    .update({"amount": amount})
                    .eq("id", existing.data[0]["id"])
                    .execute()
                )
                logger.info(f"✓ Updated budget: {category} to {amount}")
            else:
                # Create new
                response = self.client.table("budgets").insert(data).execute()
                logger.info(f"✓ Created budget: {category} = {amount}")
            
            return response.data[0]
        except Exception as e:
            logger.error(f"Error setting budget: {e}")
            raise
    
    async def get_user_budgets(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all budgets for a user"""
        try:
            response = (
                self.client.table("budgets")
                .select("*")
                .eq("user_id", user_id)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Error fetching budgets: {e}")
            return []
    
    # ============================================
    # Calendar Operations
    # ============================================
    
    async def add_calendar_entry(
        self,
        user_id: str,
        expense_id: str,
        entry_date: str,
        title: str,
        description: Optional[str] = None,
        amount: Optional[float] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add a calendar entry linked to an expense"""
        try:
            data = {
                "user_id": user_id,
                "expense_id": expense_id,
                "entry_date": entry_date,
                "title": title,
                "description": description,
                "amount": amount,
                "category": category
            }
            
            response = self.client.table("calendar_entries").insert(data).execute()
            logger.info(f"✓ Added calendar entry: {title}")
            return response.data[0]
        except Exception as e:
            logger.error(f"Error adding calendar entry: {e}")
            raise


# ============================================
# Singleton Instance
# ============================================

def get_db() -> SupabaseClient:
    """Get database client singleton"""
    return SupabaseClient()


async def get_database() -> SupabaseClient:
    """Get database client singleton (async version for FastAPI dependency)"""
    return SupabaseClient()
