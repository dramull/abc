"""
Kimi K2 API integration.
"""

import aiohttp
import asyncio
import json
from typing import Dict, Any, Optional
import time


class KimiAPI:
    """
    API client for Kimi K2 language model.
    
    Provides async interface for communicating with Kimi K2 API endpoints.
    """
    
    def __init__(
        self,
        api_key: str,
        api_endpoint: str = "https://api.moonshot.cn/v1/chat/completions",
        timeout: int = 30,
        retry_attempts: int = 3
    ):
        """
        Initialize Kimi API client.
        
        Args:
            api_key: API key for authentication
            api_endpoint: API endpoint URL
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts for failed requests
        """
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_session(self) -> None:
        """Ensure aiohttp session is created."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def close(self) -> None:
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def generate_response(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        model: str = "moonshot-v1-8k",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response using Kimi K2 API.
        
        Args:
            prompt: Input prompt for the model
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            model: Model name to use
            **kwargs: Additional parameters for the API
            
        Returns:
            Dictionary containing the API response
        """
        await self._ensure_session()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }
        
        for attempt in range(self.retry_attempts):
            try:
                start_time = time.time()
                
                async with self.session.post(
                    self.api_endpoint,
                    headers=headers,
                    json=payload
                ) as response:
                    
                    execution_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "data": data,
                            "execution_time": execution_time,
                            "status_code": response.status
                        }
                    else:
                        error_text = await response.text()
                        if attempt == self.retry_attempts - 1:
                            return {
                                "success": False,
                                "error": f"HTTP {response.status}: {error_text}",
                                "execution_time": execution_time,
                                "status_code": response.status
                            }
                        
                        # Wait before retry
                        await asyncio.sleep(2 ** attempt)
                        
            except asyncio.TimeoutError:
                if attempt == self.retry_attempts - 1:
                    return {
                        "success": False,
                        "error": "Request timed out",
                        "execution_time": self.timeout
                    }
                await asyncio.sleep(2 ** attempt)
                
            except Exception as e:
                if attempt == self.retry_attempts - 1:
                    return {
                        "success": False,
                        "error": f"Request failed: {str(e)}",
                        "execution_time": time.time() - start_time if 'start_time' in locals() else 0
                    }
                await asyncio.sleep(2 ** attempt)
        
        return {
            "success": False,
            "error": "All retry attempts failed",
            "execution_time": 0
        }
    
    async def test_connection(self) -> bool:
        """
        Test the API connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            result = await self.generate_response(
                "Hello, this is a test message.",
                max_tokens=10,
                temperature=0.1
            )
            return result["success"]
        except Exception:
            return False
    
    def extract_text_from_response(self, response: Dict[str, Any]) -> str:
        """
        Extract text content from API response.
        
        Args:
            response: API response dictionary
            
        Returns:
            Extracted text content
        """
        if not response.get("success", False):
            return f"Error: {response.get('error', 'Unknown error')}"
        
        try:
            data = response["data"]
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"].strip()
            else:
                return "No content in response"
        except (KeyError, IndexError, TypeError) as e:
            return f"Error parsing response: {str(e)}"
    
    async def stream_response(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        model: str = "moonshot-v1-8k",
        **kwargs
    ):
        """
        Generate a streaming response using Kimi K2 API.
        
        Args:
            prompt: Input prompt for the model
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            model: Model name to use
            **kwargs: Additional parameters for the API
            
        Yields:
            Chunks of the response as they arrive
        """
        await self._ensure_session()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
            **kwargs
        }
        
        try:
            async with self.session.post(
                self.api_endpoint,
                headers=headers,
                json=payload
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    yield {"error": f"HTTP {response.status}: {error_text}"}
                    return
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        data_str = line[6:]  # Remove 'data: ' prefix
                        if data_str == '[DONE]':
                            break
                        try:
                            data = json.loads(data_str)
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield {"content": delta["content"]}
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            yield {"error": f"Streaming failed: {str(e)}"}
    
    def get_supported_models(self) -> list:
        """
        Get list of supported Kimi models.
        
        Returns:
            List of supported model names
        """
        return [
            "moonshot-v1-8k",
            "moonshot-v1-32k",
            "moonshot-v1-128k"
        ]