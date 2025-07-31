"""
Base agent class for all agents in the multiagent framework.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import asyncio
import uuid
from datetime import datetime


class AgentConfig(BaseModel):
    """Configuration model for agents."""
    model_config = {"protected_namespaces": ()}
    
    name: str
    description: str = ""
    model_type: str  # "kimi" or "qwen"
    api_key: str = ""
    api_endpoint: str = ""
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 30
    retry_attempts: int = 3
    custom_params: Dict[str, Any] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    """Standard response model for agent operations."""
    agent_id: str
    success: bool
    response: str = ""
    error: Optional[str] = None
    execution_time: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentBase(ABC):
    """
    Abstract base class for all agents in the multiagent framework.
    
    This class provides the standard interface and common functionality
    that all agents must implement.
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize the agent with configuration.
        
        Args:
            config: Agent configuration containing model type, API keys, etc.
        """
        self.config = config
        self.agent_id = str(uuid.uuid4())
        self.is_active = False
        self.execution_history: List[AgentResponse] = []
    
    @abstractmethod
    async def process(self, input_data: str, **kwargs) -> AgentResponse:
        """
        Process input data and return a response.
        
        Args:
            input_data: The input text/data to process
            **kwargs: Additional parameters for processing
            
        Returns:
            AgentResponse containing the result
        """
        pass
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the agent and establish API connections.
        
        Returns:
            True if initialization successful, False otherwise
        """
        pass
    
    async def shutdown(self) -> None:
        """Clean up resources and shutdown the agent."""
        self.is_active = False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the agent.
        
        Returns:
            Dictionary containing agent status information
        """
        return {
            "agent_id": self.agent_id,
            "name": self.config.name,
            "model_type": self.config.model_type,
            "is_active": self.is_active,
            "total_executions": len(self.execution_history),
            "last_execution": self.execution_history[-1].timestamp if self.execution_history else None
        }
    
    def get_history(self, limit: Optional[int] = None) -> List[AgentResponse]:
        """
        Get execution history for this agent.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of AgentResponse objects
        """
        history = self.execution_history
        if limit:
            history = history[-limit:]
        return history
    
    async def health_check(self) -> bool:
        """
        Perform a health check on the agent.
        
        Returns:
            True if agent is healthy, False otherwise
        """
        try:
            # Simple test to verify agent is responsive
            test_response = await self.process("health_check_test")
            return test_response.success
        except Exception:
            return False