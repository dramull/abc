from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    COMPLETED = "completed"

class AgentType(str, Enum):
    RESEARCH = "research"
    WRITING = "writing"
    CODE = "code"
    PLANNING = "planning"
    ANALYSIS = "analysis"
    CUSTOM = "custom"

class ModelConfig(BaseModel):
    temperature: float = 0.7
    max_tokens: int = 4000
    model: str = "moonshot-v1-8k"

class AgentProfile(BaseModel):
    id: str
    name: str
    type: AgentType
    description: str
    instructions: str
    capabilities: List[str]
    llm_config: ModelConfig = Field(default_factory=ModelConfig, alias="model_config")
    is_active: bool = True
    created_at: Optional[str] = None

    class Config:
        populate_by_name = True

class AgentInstance(BaseModel):
    id: str
    profile_id: str
    name: str
    status: AgentStatus
    current_task: Optional[str] = None
    progress: float = 0.0
    created_at: str
    last_activity: Optional[str] = None

class TaskRequest(BaseModel):
    agent_id: str = Field(..., min_length=1, description="Agent ID must not be empty")
    instruction: str = Field(..., min_length=1, max_length=8000, description="Task instruction must not be empty")
    context: Optional[str] = Field(None, max_length=4000, description="Optional context information")
    parameters: Optional[Dict[str, Any]] = None

class TaskResponse(BaseModel):
    task_id: str
    agent_id: str
    status: AgentStatus
    result: Optional[str] = None
    error: Optional[str] = None
    progress: float = 0.0

class ProjectConfig(BaseModel):
    id: str
    name: str
    description: str
    active_agents: List[str]
    workflow_template: Optional[str] = None
    created_at: str
    updated_at: str

class CreateAgentRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Agent name must not be empty")
    description: str = Field(..., min_length=10, max_length=1000, description="Agent description must be at least 10 characters")
    agent_type: Optional[AgentType] = AgentType.CUSTOM
    instructions: Optional[str] = Field(None, max_length=2000, description="Optional additional instructions")