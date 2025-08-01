from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import (
    AgentProfile, AgentInstance, TaskRequest, TaskResponse, CreateAgentRequest
)
from app.services.agent_manager import AgentManager

router = APIRouter()
agent_manager = AgentManager()

@router.get("/profiles", response_model=List[AgentProfile])
async def get_agent_profiles():
    """Get all available agent profiles"""
    return agent_manager.get_agent_profiles()

@router.get("/instances", response_model=List[AgentInstance])
async def get_active_agents():
    """Get all active agent instances"""
    return agent_manager.get_active_agents()

@router.post("/create-from-profile/{profile_id}", response_model=AgentInstance)
async def create_agent_from_profile(profile_id: str):
    """Create an agent instance from a predefined profile"""
    try:
        return await agent_manager.create_agent_from_profile(profile_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-custom", response_model=AgentInstance)
async def create_custom_agent(request: CreateAgentRequest):
    """Create a custom agent from description"""
    try:
        return await agent_manager.create_custom_agent(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute-task", response_model=TaskResponse)
async def execute_task(task_request: TaskRequest):
    """Execute a task with the specified agent"""
    try:
        return await agent_manager.execute_task(task_request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/instances/{agent_id}", response_model=AgentInstance)
async def get_agent_instance(agent_id: str):
    """Get a specific agent instance"""
    agent = agent_manager.get_agent_instance(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.delete("/instances/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent instance"""
    if agent_id == "base_agent_instance":
        raise HTTPException(status_code=400, detail="Cannot delete base agent")
    
    success = agent_manager.delete_agent(agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {"message": "Agent deleted successfully"}

@router.get("/status")
async def get_system_status():
    """Get system status and configuration"""
    return {
        "kimi_configured": agent_manager.is_kimi_configured(),
        "active_agents": len(agent_manager.get_active_agents()),
        "available_profiles": len(agent_manager.get_agent_profiles()),
        "status": "operational"
    }