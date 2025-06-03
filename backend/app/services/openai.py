"""OpenAI service module for interacting with OpenAI API."""
import os
from typing import Optional, Dict, Any
import httpx
from openai import AsyncOpenAI
from fastapi import HTTPException, status
from loguru import logger
from app.core.config import settings


class OpenAIService:
    """Service for interacting with OpenAI API."""
    
    def __init__(self):
        """Initialize OpenAI service."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            raise ValueError("OPENAI_API_KEY environment variable is required")
            
        # Initialize AsyncOpenAI client with timeout settings
        self.client = AsyncOpenAI(
            api_key=api_key,
            timeout=httpx.Timeout(60.0, read=30.0, write=10.0, connect=5.0),
            max_retries=3
        )
        
        # Default model (can be overridden in .env)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        
    async def generate_completion(
        self, 
        prompt: str,
        max_tokens: Optional[int] = 2000,
        temperature: Optional[float] = 0.7,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate a completion from OpenAI.
        
        Args:
            prompt: The user prompt
            max_tokens: Maximum tokens in response
            temperature: Temperature for randomness (0-2)
            system_prompt: Optional system prompt
            
        Returns:
            Generated text content
            
        Raises:
            HTTPException: If OpenAI API call fails
        """
        try:
            # Prepare messages
            messages = []
            
            # Add system prompt if provided
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            else:
                # Default system prompt for Vibe Coding
                messages.append({
                    "role": "system",
                    "content": (
                        "Eres un asistente experto en desarrollo de software, "
                        "especializado en el estilo 'Vibe Coding'. Tu objetivo es "
                        "generar código y documentación de alta calidad siguiendo "
                        "las mejores prácticas de desarrollo."
                    )
                })
            
            # Add user prompt
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Make API call
            logger.info(f"Sending request to OpenAI API with model: {self.model}")
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Extract generated content
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                logger.info(f"Successfully generated completion, length: {len(content)}")
                return content
            else:
                logger.error("No choices returned from OpenAI API")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="No response generated from OpenAI"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating completion from OpenAI: {type(e).__name__}: {str(e)}")
            
            # Handle specific OpenAI errors
            error_message = str(e)
            if "rate_limit" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="OpenAI API rate limit exceeded. Please try again later."
                )
            elif "api_key" in error_message.lower() or "authentication" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid OpenAI API key"
                )
            elif "timeout" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="OpenAI API request timed out"
                )
            elif "model" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid model: {self.model}"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"OpenAI API error: {error_message}"
                )


# Create singleton instance
openai_service = OpenAIService()
