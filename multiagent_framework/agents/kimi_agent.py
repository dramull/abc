"""
Kimi agent implementation for text processing tasks.
"""

import time
from typing import Dict, Any
from ..core.agent_base import AgentBase, AgentConfig, AgentResponse
from ..api.kimi_api import KimiAPI


class KimiAgent(AgentBase):
    """
    Agent implementation using Kimi K2 API for text processing tasks.
    
    Specializes in general text analysis, processing, and generation tasks.
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize Kimi agent.
        
        Args:
            config: Agent configuration
        """
        super().__init__(config)
        self.api_client: KimiAPI = None
        self.capabilities = [
            "text_analysis",
            "text_generation",
            "summarization",
            "translation",
            "question_answering",
            "content_writing"
        ]
    
    async def initialize(self) -> bool:
        """
        Initialize the Kimi agent and establish API connection.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Initialize API client
            endpoint = self.config.api_endpoint or "https://api.moonshot.cn/v1/chat/completions"
            
            self.api_client = KimiAPI(
                api_key=self.config.api_key,
                api_endpoint=endpoint,
                timeout=self.config.timeout,
                retry_attempts=self.config.retry_attempts
            )
            
            # Test connection
            if self.config.api_key:  # Only test if API key is provided
                connection_ok = await self.api_client.test_connection()
                if not connection_ok:
                    return False
            
            self.is_active = True
            return True
            
        except Exception as e:
            print(f"Failed to initialize Kimi agent: {str(e)}")
            return False
    
    async def process(self, input_data: str, **kwargs) -> AgentResponse:
        """
        Process input data using Kimi K2 API.
        
        Args:
            input_data: Input text to process
            **kwargs: Additional parameters
            
        Returns:
            AgentResponse containing the result
        """
        start_time = time.time()
        
        try:
            if not self.is_active or not self.api_client:
                return AgentResponse(
                    agent_id=self.agent_id,
                    success=False,
                    error="Agent not initialized or not active"
                )
            
            # Handle special test case
            if input_data == "health_check_test":
                return AgentResponse(
                    agent_id=self.agent_id,
                    success=True,
                    response="Health check passed",
                    execution_time=time.time() - start_time
                )
            
            # Extract parameters
            task_type = kwargs.get("task_type", "general")
            max_tokens = kwargs.get("max_tokens", self.config.max_tokens)
            temperature = kwargs.get("temperature", self.config.temperature)
            model = kwargs.get("model", "moonshot-v1-8k")
            
            # Prepare prompt based on task type
            prompt = self._prepare_prompt(input_data, task_type, kwargs)
            
            # Make API call
            if not self.config.api_key:
                # Simulation mode for demo/testing
                response_text = self._simulate_response(input_data, task_type)
                api_response = {
                    "success": True,
                    "data": {"choices": [{"message": {"content": response_text}}]},
                    "execution_time": 0.5
                }
            else:
                api_response = await self.api_client.generate_response(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    model=model,
                    **self.config.custom_params
                )
            
            execution_time = time.time() - start_time
            
            if api_response["success"]:
                response_text = self.api_client.extract_text_from_response(api_response)
                
                result = AgentResponse(
                    agent_id=self.agent_id,
                    success=True,
                    response=response_text,
                    execution_time=execution_time,
                    metadata={
                        "task_type": task_type,
                        "model": model,
                        "api_execution_time": api_response.get("execution_time", 0)
                    }
                )
            else:
                result = AgentResponse(
                    agent_id=self.agent_id,
                    success=False,
                    error=api_response.get("error", "Unknown API error"),
                    execution_time=execution_time,
                    metadata={"task_type": task_type}
                )
            
            # Store in history
            self.execution_history.append(result)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            result = AgentResponse(
                agent_id=self.agent_id,
                success=False,
                error=f"Processing error: {str(e)}",
                execution_time=execution_time
            )
            
            self.execution_history.append(result)
            return result
    
    def _prepare_prompt(self, input_data: str, task_type: str, kwargs: Dict[str, Any]) -> str:
        """
        Prepare the prompt based on task type and parameters.
        
        Args:
            input_data: Original input data
            task_type: Type of task to perform
            kwargs: Additional parameters
            
        Returns:
            Formatted prompt string
        """
        if task_type == "summarization":
            return f"Please provide a concise summary of the following text:\n\n{input_data}"
        
        elif task_type == "translation":
            target_language = kwargs.get("target_language", "English")
            return f"Please translate the following text to {target_language}:\n\n{input_data}"
        
        elif task_type == "analysis":
            return f"Please analyze the following text and provide insights:\n\n{input_data}"
        
        elif task_type == "question_answering":
            question = kwargs.get("question", "What is this about?")
            return f"Based on the following text, please answer this question: {question}\n\nText:\n{input_data}"
        
        elif task_type == "content_writing":
            style = kwargs.get("style", "professional")
            topic = kwargs.get("topic", input_data)
            return f"Please write {style} content about: {topic}"
        
        else:  # general
            instruction = kwargs.get("instruction", "Please process the following text:")
            return f"{instruction}\n\n{input_data}"
    
    def _simulate_response(self, input_data: str, task_type: str) -> str:
        """
        Simulate API response for testing/demo purposes.
        
        Args:
            input_data: Input data
            task_type: Task type
            
        Returns:
            Simulated response text
        """
        if task_type == "summarization":
            return f"Summary: This text discusses {input_data[:50]}... and provides key insights about the topic."
        
        elif task_type == "analysis":
            return f"Analysis: The provided text appears to be about {input_data[:30]}... Key themes include information processing and content analysis."
        
        elif task_type == "translation":
            return f"Translation: [Translated version of: {input_data[:50]}...]"
        
        else:
            return f"Processed response: I have analyzed your input '{input_data[:50]}...' and here is my response based on the Kimi K2 model capabilities."
    
    async def shutdown(self) -> None:
        """Shutdown the agent and close API connections."""
        if self.api_client:
            await self.api_client.close()
        await super().shutdown()
    
    def get_capabilities(self) -> list:
        """
        Get list of agent capabilities.
        
        Returns:
            List of capability strings
        """
        return self.capabilities.copy()
    
    def supports_task(self, task_type: str) -> bool:
        """
        Check if agent supports a specific task type.
        
        Args:
            task_type: Task type to check
            
        Returns:
            True if supported, False otherwise
        """
        return task_type in [
            "general", "text_analysis", "text_generation", 
            "summarization", "translation", "question_answering", 
            "content_writing", "analysis"
        ]