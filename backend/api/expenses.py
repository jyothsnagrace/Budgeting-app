# CHECKPOINT_7_API_ENDPOINTS
"""
Expense API Endpoints
=====================
REST endpoints for expense operations with LLM integration.
"""

from fastapi import APIRouter, HTTPException, Query, File, UploadFile
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


class ParseExpenseRequest(BaseModel):
    """Request to parse expense from text without saving"""
    input_text: str = Field(..., description="Natural language expense description")


class ParsedExpenseResponse(BaseModel):
    """Parsed expense data without saving to database"""
    amount: float
    category: str
    description: str
    date: str
    confidence: Optional[str] = None
    transcript: str
    extracted_data: Optional[dict] = None
    validated_data: Optional[dict] = None


@router.post("/parse", response_model=ParsedExpenseResponse)
async def parse_expense_from_text(request: ParseExpenseRequest):
    """
    Parse expense from natural language without saving to database.
    
    This endpoint is useful for showing users what was extracted before
    they confirm and save the expense.
    
    Uses Two-LLM pipeline:
    1. LLM #1 extracts structured data
    2. LLM #2 validates and normalizes
    3. Returns parsed data (does NOT save)
    """
    logger.info(f"Parsing expense from text: {request.input_text}")
    
    try:
        # Initialize LLM pipeline
        pipeline = TwoLLMPipeline()
        
        # Stage 1: Extract data
        extracted = await pipeline.extract_expense_data(
            user_input=request.input_text,
            input_method="voice"
        )
        
        # Stage 2: Validate data
        validated = await pipeline.validate_expense_data(
            extracted_data=extracted,
            original_input=request.input_text
        )
        
        # Check if validation passed
        if not validated.get("is_valid", False):
            errors = validated.get('errors', [])
            error_str = ', '.join(errors) if isinstance(errors, list) else str(errors)
            raise ValueError(f"Could not parse expense: {error_str or 'Invalid format'}")
        
        # Extract final data
        final_data = validated.get("validated_data", {})
        
        logger.info(f"✓ Expense parsed successfully")
        
        return ParsedExpenseResponse(
            amount=final_data["amount"],
            category=final_data["category"],
            description=final_data["description"],
            date=final_data["date"],
            confidence=validated.get("confidence", "high"),
            transcript=request.input_text,
            extracted_data=extracted,
            validated_data=validated
        )
        
    except ValueError as e:
        logger.error(f"Parsing error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to parse expense: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to parse expense: {str(e)}")


class ReceiptParseResponse(BaseModel):
    """Parsed receipt data"""
    amount: float
    category: str
    description: str
    date: str
    extracted_text: str
    confidence: Optional[str] = None


@router.post("/parse-receipt", response_model=ReceiptParseResponse)
async def parse_receipt(receipt: UploadFile = File(...)):
    """
    Parse receipt image using OCR/Vision AI.
    
    Extracts expense details from uploaded receipt image:
    - Amount
    - Merchant/Description
    - Date
    - Category (inferred)
    
    Supports: JPG, PNG, WEBP
    """
    import base64
    from groq import Groq
    from backend.config import settings
    
    logger.info(f"Processing receipt: {receipt.filename}")
    
    try:
        # Read image bytes
        image_bytes = await receipt.read()
        
        # Initialize Groq client for LLM parsing
        client = Groq(api_key=settings.GROQ_API_KEY)
        
        # Use text extraction approach with Groq LLM
        # For now, we'll use a simpler approach: ask user to type receipt details
        # or integrate with a proper OCR service
        
        # Alternative: Use Groq's text model to parse receipt data from a description
        # For actual OCR, you would need to integrate:
        # - pytesseract for basic OCR
        # - Google Vision API
        # - AWS Textract
        # - Azure Computer Vision
        
        # For this demo, let's use a mock/manual parsing approach
        # that extracts basic info from the filename or common patterns
        
        import io
        from PIL import Image
        
        # Load image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Try to use pytesseract if available, otherwise return a helpful message
        try:
            import pytesseract
            
            # Try to set tesseract path for Windows
            try:
                pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            except:
                pass
            
            # Extract text from image
            extracted_text = pytesseract.image_to_string(image)
            logger.info(f"OCR extracted text: {extracted_text}")
            
        except (ImportError, pytesseract.TesseractNotFoundError) as e:
            # Pytesseract not installed or Tesseract not found
            logger.warning(f"OCR not available: {e}")
            
            # Fallback: Return a helpful message to manually type receipt info
            raise HTTPException(
                status_code=400,
                detail="Receipt OCR not available. Please install Tesseract OCR:\n\n"
                       "Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki\n"
                       "Mac: brew install tesseract\n"
                       "Linux: sudo apt-get install tesseract-ocr\n\n"
                       "Or manually type the receipt details in the text input field."
            )
        
        # Use Groq LLM to parse the extracted text
        if extracted_text and len(extracted_text.strip()) > 10:
            parse_prompt = f"""Parse this receipt text and extract the following information in JSON format:

Receipt Text:
{extracted_text}

Extract and return ONLY valid JSON in this exact format:
{{
  "merchant": "name of the store/merchant",
  "amount": total amount as a number (just the number, no currency symbol),
  "date": "date in YYYY-MM-DD format",
  "items": "brief description of items purchased"
}}

Rules:
- Use the TOTAL amount, not subtotal
- Convert any date format to YYYY-MM-DD
- If date is not found, use today's date: {datetime.now().strftime('%Y-%m-%d')}
- Be as accurate as possible
- Return ONLY the JSON object, no other text"""

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a receipt parser. Extract structured data from receipt text and return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": parse_prompt
                    }
                ],
                temperature=0.1,
                max_tokens=300,
            )
            
            llm_response = response.choices[0].message.content
            logger.info(f"LLM parsing response: {llm_response}")
            
            # Parse JSON from response
            import json
            import re
            
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                receipt_data = json.loads(json_match.group())
            else:
                raise ValueError("Could not extract JSON from LLM response")
        else:
            raise ValueError("Could not extract text from receipt image. Please install pytesseract or enter details manually.")
        
        # Map merchant to category
        merchant = receipt_data.get("merchant", "").lower()
        items = receipt_data.get("items", "").lower()
        category = "food"  # default
        
        # Check merchant and items for categorization
        combined_text = f"{merchant} {items}"
        
        if any(word in combined_text for word in ["uber", "lyft", "taxi", "gas", "shell", "chevron", "exxon", "bp"]):
            category = "transportation"
        elif any(word in combined_text for word in ["walmart", "target", "amazon", "mall", "store", "shop"]):
            category = "shopping"
        elif any(word in combined_text for word in ["restaurant", "cafe", "pizza", "burger", "food", "starbucks", "mcdonald", "breakfast", "lunch", "dinner", "waffle", "chicken", "meal", "drinks", "bar", "grill"]):
            category = "food"
        elif any(word in combined_text for word in ["pharmacy", "cvs", "walgreens", "hospital", "clinic", "doctor", "medical"]):
            category = "healthcare"
        elif any(word in combined_text for word in ["movie", "theater", "cinema", "concert", "game", "entertainment"]):
            category = "entertainment"
        
        # Create description
        items = receipt_data.get("items", "")
        description = f"{receipt_data.get('merchant', 'Purchase')}"
        if items:
            description += f" - {items}"
        
        return ReceiptParseResponse(
            amount=float(receipt_data.get("amount", 0)),
            category=category,
            description=description[:200],  # Truncate if too long
            date=receipt_data.get("date", ""),
            extracted_text=extracted_text,
            confidence="high"
        )
        
    except Exception as e:
        logger.error(f"Failed to parse receipt: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to parse receipt: {str(e)}")


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
