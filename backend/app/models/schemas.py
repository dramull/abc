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
    agent_id: str
    instruction: str
    context: Optional[str] = None
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
    name: str
    description: str
    agent_type: Optional[AgentType] = AgentType.CUSTOM
    instructions: Optional[str] = None