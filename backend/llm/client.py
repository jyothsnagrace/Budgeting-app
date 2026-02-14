# CHECKPOINT_5_LLM_PIPELINE
"""
LLM Client Module
=================
Unified client for different LLM providers (Ollama, Groq, OpenAI).
"""

import json
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import httpx
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger("llm_client")


class LLMClient(ABC):
    """Abstract base class for LLM clients"""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 500,
        json_mode: bool = False
    ) -> str:
        """Generate completion from LLM"""
        pass
    
    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate structured JSON output"""
        pass


class OllamaClient(LLMClient):
    """Client for local Ollama LLM"""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model_extraction = settings.OLLAMA_MODEL_EXTRACTION
        self.model_validation = settings.OLLAMA_MODEL_VALIDATION
        logger.info(f"Initialized Ollama client: {self.base_url}")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 500,
        json_mode: bool = False,
        model: Optional[str] = None
    ) -> str:
        """Generate completion from Ollama"""
        async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT) as client:
            payload = {
                "model": model or self.model_extraction,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            if json_mode:
                payload["format"] = "json"
            
            try:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")
            except Exception as e:
                logger.error(f"Ollama generation error: {e}")
                raise
    
    async def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate structured JSON output from Ollama"""
        # Add JSON instruction to prompt
        full_prompt = f"{prompt}\n\nRespond with valid JSON only."
        
        if schema:
            full_prompt += f"\n\nJSON Schema:\n{json.dumps(schema, indent=2)}"
        
        response = await self.generate(
            prompt=full_prompt,
            system_prompt=system_prompt,
            json_mode=True,
            model=model
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {response}")
            raise ValueError(f"Invalid JSON response from LLM: {e}")


class GroqClient(LLMClient):
    """Client for Groq cloud API"""
    
    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not configured")
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        self.base_url = "https://api.groq.com/openai/v1"
        logger.info(f"Initialized Groq client with model: {self.model}")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 500,
        json_mode: bool = False
    ) -> str:
        """Generate completion from Groq"""
        async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT) as client:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            if json_mode:
                payload["response_format"] = {"type": "json_object"}
            
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
            except Exception as e:
                logger.error(f"Groq generation error: {e}")
                raise
    
    async def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate structured JSON output from Groq"""
        full_prompt = f"{prompt}\n\nRespond with valid JSON only."
        if schema:
            full_prompt += f"\n\nJSON Schema:\n{json.dumps(schema, indent=2)}"
        
        response = await self.generate(
            prompt=full_prompt,
            system_prompt=system_prompt,
            json_mode=True
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {response}")
            raise ValueError(f"Invalid JSON response from LLM: {e}")


# ============================================
# Client Factory
# ============================================

def get_llm_client() -> LLMClient:
    """
    Factory function to get the appropriate LLM client based on configuration.
    """
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "ollama":
        return OllamaClient()
    elif provider == "groq":
        return GroqClient()
    elif provider == "openai":
        # TODO: Implement OpenAI client
        raise NotImplementedError("OpenAI client not yet implemented")
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


# ============================================
# Convenience Functions
# ============================================

async def generate_text(
    prompt: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.1
) -> str:
    """Convenience function to generate text"""
    client = get_llm_client()
    return await client.generate(prompt, system_prompt, temperature)


async def generate_json(
    prompt: str,
    system_prompt: Optional[str] = None,
    schema: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Convenience function to generate structured JSON"""
    client = get_llm_client()
    return await client.generate_structured(prompt, system_prompt, schema)
