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
        async with httpx.AsyncClient() as client:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature
            }
            
            if max_tokens:
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
            except httpx.HTTPError as e:
                raise Exception(f"Kimi K2 API error: {str(e)}")
    
    async def generate_response(
        self, 
        prompt: str, 
        system_message: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate a response using Kimi K2"""
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        result = await self.chat_completion(messages, **kwargs)
        return result["choices"][0]["message"]["content"]
    
    def is_configured(self) -> bool:
        """Check if the API key is configured"""
        return bool(self.api_key and self.api_key != "your_kimi_k2_api_key_here")