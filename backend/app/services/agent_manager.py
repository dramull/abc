import uuid
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from app.models.schemas import (
    AgentProfile, AgentInstance, AgentStatus, AgentType,
    TaskRequest, TaskResponse, CreateAgentRequest, ModelConfig
)
from app.services.kimi_client import KimiK2Client
from app.agents.predefined import get_predefined_agent, get_all_predefined_agents

class AgentManager:
    def __init__(self):
        self.kimi_client = KimiK2Client()
        self.active_agents: Dict[str, AgentInstance] = {}
        self.agent_profiles: Dict[str, AgentProfile] = {}
        self.task_history: Dict[str, TaskResponse] = {}
        
        # Load predefined agents
        self._load_predefined_agents()
        
        # Initialize base agent
        self._initialize_base_agent()
    
    def _load_predefined_agents(self):
        """Load all predefined agent profiles"""
        for agent in get_all_predefined_agents():
            self.agent_profiles[agent.id] = agent
    
    def _initialize_base_agent(self):
        """Initialize the base agent that's always available"""
        base_agent = AgentProfile(
            id="base_agent",
            name="Base Agent",
            type=AgentType.CUSTOM,
            description="Intelligent base agent for project setup, agent creation, and workflow guidance",
            instructions="""You are the Base Agent - the central coordinator for this multi-agent framework. Your primary responsibilities:

1. **New User Onboarding**: Help users understand and navigate the agent system
2. **Project Setup**: Analyze user objectives and recommend appropriate workflows
3. **Agent Creation**: Generate new custom agents based on user descriptions
4. **Workflow Coordination**: Orchestrate multi-agent tasks and workflows
5. **System Guidance**: Provide help and guidance on using the framework

When a user describes a project or objective:
- Analyze the requirements carefully
- Recommend appropriate existing agents from the available profiles
- Suggest optimal workflows (parallel vs sequential agent usage)
- Create custom agents if needed for specialized tasks
- Provide step-by-step guidance for project execution

Available predefined agents you can recommend:
- Research Agent: Information gathering and analysis
- Writing Agent: Content creation and editing
- Code Agent: Programming and development
- Planning Agent: Project planning and task breakdown
- Analysis Agent: Data analysis and insights

Always prioritize user experience and provide clear, actionable guidance.""",
            capabilities=[
                "User onboarding",
                "Project analysis",
                "Agent recommendation",
                "Workflow design",
                "Custom agent creation",
                "System coordination"
            ],
            llm_config=ModelConfig(
                temperature=0.6,
                max_tokens=4000,
                model="moonshot-v1-8k"
            )
        )
        
        self.agent_profiles["base_agent"] = base_agent
        
        # Create base agent instance
        base_instance = AgentInstance(
            id="base_agent_instance",
            profile_id="base_agent",
            name="Base Agent",
            status=AgentStatus.IDLE,
            created_at=datetime.now().isoformat()
        )
        
        self.active_agents["base_agent_instance"] = base_instance
    
    async def create_agent_from_profile(self, profile_id: str) -> AgentInstance:
        """Create an agent instance from a predefined profile"""
        if profile_id not in self.agent_profiles:
            raise ValueError(f"Agent profile {profile_id} not found")
        
        profile = self.agent_profiles[profile_id]
        instance_id = str(uuid.uuid4())
        
        instance = AgentInstance(
            id=instance_id,
            profile_id=profile_id,
            name=f"{profile.name} - {instance_id[:8]}",
            status=AgentStatus.IDLE,
            created_at=datetime.now().isoformat()
        )
        
        self.active_agents[instance_id] = instance
        return instance
    
    async def create_custom_agent(self, request: CreateAgentRequest) -> AgentInstance:
        """Create a custom agent using the base agent's intelligence"""
        # Use base agent to generate custom agent profile
        prompt = f"""Create a custom agent profile for the following request:

Name: {request.name}
Description: {request.description}
Type: {request.agent_type}
Additional Instructions: {request.instructions or 'None provided'}

Generate detailed instructions for this agent that include:
1. Clear role definition and responsibilities
2. Specific capabilities and expertise areas
3. Approach to handling tasks
4. Communication style and methods
5. Any specialized knowledge or focus areas

The instructions should be comprehensive but focused on the specific purpose described."""

        try:
            instructions = await self.kimi_client.generate_response(
                prompt,
                system_message="You are an expert at designing AI agent profiles. Create detailed, specific instructions that will guide an agent to excel at their designated role."
            )
            
            # Create custom profile
            profile_id = str(uuid.uuid4())
            custom_profile = AgentProfile(
                id=profile_id,
                name=request.name,
                type=request.agent_type,
                description=request.description,
                instructions=instructions,
                capabilities=["Custom capabilities based on description"],
                llm_config=ModelConfig(
                    temperature=0.6,
                    max_tokens=4000,
                    model="moonshot-v1-8k"
                ),
                created_at=datetime.now().isoformat()
            )
            
            self.agent_profiles[profile_id] = custom_profile
            
            # Create instance
            return await self.create_agent_from_profile(profile_id)
            
        except Exception as e:
            raise Exception(f"Failed to create custom agent: {str(e)}")
    
    async def execute_task(self, task_request: TaskRequest) -> TaskResponse:
        """Execute a task with the specified agent"""
        if task_request.agent_id not in self.active_agents:
            raise ValueError(f"Agent {task_request.agent_id} not found")
        
        agent_instance = self.active_agents[task_request.agent_id]
        agent_profile = self.agent_profiles[agent_instance.profile_id]
        
        # Update agent status
        agent_instance.status = AgentStatus.RUNNING
        agent_instance.current_task = task_request.instruction
        
        task_id = str(uuid.uuid4())
        
        try:
            # Prepare the prompt with agent instructions and context
            system_message = agent_profile.instructions
            
            user_prompt = task_request.instruction
            if task_request.context:
                user_prompt = f"Context: {task_request.context}\n\nTask: {task_request.instruction}"
            
            # Execute with Kimi K2
            result = await self.kimi_client.generate_response(
                user_prompt,
                system_message=system_message,
                temperature=agent_profile.llm_config.temperature,
                max_tokens=agent_profile.llm_config.max_tokens
            )
            
            # Update agent status
            agent_instance.status = AgentStatus.COMPLETED
            agent_instance.current_task = None
            agent_instance.last_activity = datetime.now().isoformat()
            
            response = TaskResponse(
                task_id=task_id,
                agent_id=task_request.agent_id,
                status=AgentStatus.COMPLETED,
                result=result,
                progress=1.0
            )
            
            self.task_history[task_id] = response
            return response
            
        except Exception as e:
            # Update agent status on error
            agent_instance.status = AgentStatus.ERROR
            agent_instance.current_task = None
            
            response = TaskResponse(
                task_id=task_id,
                agent_id=task_request.agent_id,
                status=AgentStatus.ERROR,
                error=str(e),
                progress=0.0
            )
            
            self.task_history[task_id] = response
            return response
    
    def get_agent_profiles(self) -> List[AgentProfile]:
        """Get all available agent profiles"""
        return list(self.agent_profiles.values())
    
    def get_active_agents(self) -> List[AgentInstance]:
        """Get all active agent instances"""
        return list(self.active_agents.values())
    
    def get_agent_instance(self, agent_id: str) -> Optional[AgentInstance]:
        """Get a specific agent instance"""
        return self.active_agents.get(agent_id)
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent instance"""
        if agent_id in self.active_agents and agent_id != "base_agent_instance":
            del self.active_agents[agent_id]
            return True
        return False
    
    def is_kimi_configured(self) -> bool:
        """Check if Kimi K2 is properly configured"""
        return self.kimi_client.is_configured()