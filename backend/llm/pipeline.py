# CHECKPOINT_5_LLM_PIPELINE
"""
Two-LLM Pipeline
================
Implements the dual-LLM architecture:
- LLM #1: Extract structured data from user input
- LLM #2: Validate and normalize the extracted data
"""

from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from backend.llm.client import get_llm_client
from backend.llm.prompts import build_extraction_prompt, build_validation_prompt
from backend.llm.schemas import EXPENSE_EXTRACTION_SCHEMA, EXPENSE_VALIDATION_SCHEMA
from backend.utils.logger import get_logger

logger = get_logger("llm_pipeline")


class TwoLLMPipeline:
    """
    Two-stage LLM pipeline for expense processing:
    1. Extraction LLM - extracts structured data from raw input
    2. Validation LLM - validates and normalizes extracted data
    """
    
    def __init__(self):
        self.llm_client = get_llm_client()
        logger.info("Initialized Two-LLM Pipeline")
    
    async def extract_expense_data(
        self,
        user_input: str,
        input_method: str = "text"
    ) -> Dict[str, Any]:
        """
        Stage 1: Extract expense information from user input using LLM #1
        
        Args:
            user_input: Raw text input from user
            input_method: 'text' or 'voice'
        
        Returns:
            Extracted data with confidence scores
        """
        logger.info(f"Stage 1 - Extracting data from input: {user_input[:50]}...")
        
        try:
            # Build prompts
            prompts = build_extraction_prompt(user_input)
            
            # Call LLM #1 for extraction
            extracted = await self.llm_client.generate_structured(
                prompt=prompts["user"],
                system_prompt=prompts["system"],
                schema=EXPENSE_EXTRACTION_SCHEMA
            )
            
            logger.info(f"Stage 1 - Extracted: {extracted}")
            
            # Enrich with metadata
            extracted["metadata"] = {
                "input_method": input_method,
                "original_input": user_input,
                "extracted_at": datetime.now().isoformat(),
                "stage": "extraction"
            }
            
            return extracted
            
        except Exception as e:
            logger.error(f"Stage 1 - Extraction failed: {e}")
            raise ValueError(f"Failed to extract expense data: {e}")
    
    async def validate_expense_data(
        self,
        extracted_data: Dict[str, Any],
        original_input: str
    ) -> Dict[str, Any]:
        """
        Stage 2: Validate and normalize extracted data using LLM #2
        
        Args:
            extracted_data: Data from extraction stage
            original_input: Original user input for context
        
        Returns:
            Validated and normalized expense data
        """
        logger.info("Stage 2 - Validating and normalizing extracted data...")
        
        try:
            # Build validation prompts
            prompts = build_validation_prompt(
                extracted_data.get("extracted_data", {}),
                original_input
            )
            
            # Call LLM #2 for validation
            validated = await self.llm_client.generate_structured(
                prompt=prompts["user"],
                system_prompt=prompts["system"],
                schema=EXPENSE_VALIDATION_SCHEMA
            )
            
            logger.info(f"Stage 2 - Validated: {validated}")
            
            # Enrich with metadata
            validated["metadata"] = {
                "validated_at": datetime.now().isoformat(),
                "stage": "validation",
                "extraction_confidence": extracted_data.get("extracted_data", {}).get("confidence", 0)
            }
            
            return validated
            
        except Exception as e:
            logger.error(f"Stage 2 - Validation failed: {e}")
            raise ValueError(f"Failed to validate expense data: {e}")
    
    async def process_expense_input(
        self,
        user_input: str,
        input_method: str = "text"
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Complete two-stage pipeline: extract and validate
        
        Args:
            user_input: Raw user input (text or transcribed voice)
            input_method: 'text' or 'voice'
        
        Returns:
            Tuple of (success, validated_data, error_message)
        """
        logger.info(f"Processing expense input via {input_method}: {user_input[:50]}...")
        
        try:
            # Stage 1: Extraction
            extracted = await self.extract_expense_data(user_input, input_method)
            
            # Check if extraction found valid intent
            intent = extracted.get("intent", "unknown")
            if intent == "unknown":
                return False, None, "Could not determine intent from input"
            
            if intent != "add_expense":
                return False, None, f"This pipeline only handles expenses, got intent: {intent}"
            
            # Stage 2: Validation
            validated = await self.validate_expense_data(extracted, user_input)
            
            # Check validation result
            if not validated.get("is_valid", False):
                errors = validated.get("errors", ["Unknown validation error"])
                error_msg = "Validation failed: " + "; ".join(errors)
                return False, None, error_msg
            
            # Prepare final result
            result = {
                "raw_input": user_input,
                "input_method": input_method,
                "extracted_data": extracted.get("extracted_data", {}),
                "validated_data": validated.get("validated_data", {}),
                "suggestions": validated.get("suggestions", {}),
                "confidence": extracted.get("extracted_data", {}).get("confidence", 0),
                "processed_at": datetime.now().isoformat()
            }
            
            logger.info("✓ Pipeline completed successfully")
            return True, result, None
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
            return False, None, str(e)


# ============================================
# Convenience Functions
# ============================================

async def process_text_expense(text: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """Process text expense input through the pipeline"""
    pipeline = TwoLLMPipeline()
    return await pipeline.process_expense_input(text, "text")


async def process_voice_expense(text: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """Process voice expense input (already transcribed) through the pipeline"""
    pipeline = TwoLLMPipeline()
    return await pipeline.process_expense_input(text, "voice")
