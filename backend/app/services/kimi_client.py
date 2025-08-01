import httpx
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class KimiK2Client:
    def __init__(self):
        self.api_key = os.getenv("KIMI_API_KEY")
        self.api_url = os.getenv("KIMI_API_URL", "https://api.moonshot.cn/v1")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def chat_completion(
        self, 
        messages: list, 
        model: str = "moonshot-v1-8k",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Send a chat completion request to Kimi K2 API"""
        if not self.is_configured():
            raise Exception("Kimi K2 API key is not configured. Please set KIMI_API_KEY in your environment.")
        
        if not messages:
            raise ValueError("Messages list cannot be empty")
        
        if not 0.0 <= temperature <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        
        async with httpx.AsyncClient() as client:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature
            }
            
            if max_tokens and max_tokens > 0:
                payload["max_tokens"] = max_tokens
            
            try:
                response = await client.post(
                    f"{self.api_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.TimeoutException:
                raise Exception("Request to Kimi K2 API timed out. Please try again.")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    raise Exception("Invalid Kimi K2 API key. Please check your KIMI_API_KEY.")
                elif e.response.status_code == 429:
                    raise Exception("Rate limit exceeded for Kimi K2 API. Please try again later.")
                elif e.response.status_code >= 500:
                    raise Exception("Kimi K2 API server error. Please try again later.")
                else:
                    error_detail = e.response.text if hasattr(e.response, 'text') else str(e)
                    raise Exception(f"Kimi K2 API error ({e.response.status_code}): {error_detail}")
            except httpx.RequestError as e:
                raise Exception(f"Network error connecting to Kimi K2 API: {str(e)}")
            except Exception as e:
                raise Exception(f"Unexpected error with Kimi K2 API: {str(e)}")
    
    async def generate_response(
        self, 
        prompt: str, 
        system_message: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate a response using Kimi K2"""
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        messages = []
        
        if system_message and system_message.strip():
            messages.append({"role": "system", "content": system_message.strip()})
        
        messages.append({"role": "user", "content": prompt.strip()})
        
        result = await self.chat_completion(messages, **kwargs)
        
        if not result or "choices" not in result or not result["choices"]:
            raise Exception("Invalid response from Kimi K2 API - no choices returned")
        
        if "message" not in result["choices"][0] or "content" not in result["choices"][0]["message"]:
            raise Exception("Invalid response format from Kimi K2 API")
        
        return result["choices"][0]["message"]["content"]
    
    def is_configured(self) -> bool:
        """Check if the API key is configured"""
        return bool(self.api_key and self.api_key != "your_kimi_k2_api_key_here")