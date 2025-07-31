"""
Tests for the core framework functionality.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path

from multiagent_framework.core.framework import MultiAgentFramework
from multiagent_framework.core.agent_base import AgentConfig


@pytest.fixture
def temp_config_dir():
    """Create a temporary configuration directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def framework_instance(temp_config_dir):
    """Create a framework instance for testing."""
    return MultiAgentFramework(temp_config_dir)


class TestMultiAgentFramework:
    """Test cases for MultiAgentFramework."""
    
    @pytest.mark.asyncio
    async def test_framework_initialization(self, temp_config_dir):
        """Test framework initialization."""
        framework = MultiAgentFramework(temp_config_dir)
        success = await framework.initialize()
        
        assert success
        assert len(framework.get_agents()) > 0
        
        await framework.shutdown()
    
    @pytest.mark.asyncio
    async def test_agent_management(self, framework_instance):
        """Test adding and removing agents."""
        framework = framework_instance
        await framework.initialize()
        
        initial_count = len(framework.get_agents())
        
        # Add a new agent
        config = AgentConfig(
            name="test_agent",
            description="Test agent",
            model_type="kimi",
            api_key="",  # Empty for testing
            max_tokens=500,
            temperature=0.5
        )
        
        success = await framework.add_agent_async(config)
        assert success
        
        # Check agent was added
        agents = framework.get_agents()
        assert len(agents) == initial_count + 1
        assert "test_agent" in agents
        
        # Remove the agent
        success = framework.remove_agent("test_agent")
        assert success
        
        # Check agent was removed
        agents = framework.get_agents()
        assert len(agents) == initial_count
        assert "test_agent" not in agents
        
        await framework.shutdown()
    
    @pytest.mark.asyncio
    async def test_project_management(self, framework_instance):
        """Test project creation and management."""
        framework = framework_instance
        await framework.initialize()
        
        # Create a project
        success = framework.create_project(
            "test_project",
            "Test project description",
            ["text_processor"]
        )
        assert success
        
        # Check project was created
        projects = framework.get_projects()
        assert "test_project" in projects
        
        # Load the project
        success = framework.load_project("test_project")
        assert success
        
        # Delete the project
        success = framework.delete_project("test_project")
        assert success
        
        # Check project was deleted
        projects = framework.get_projects()
        assert "test_project" not in projects
        
        await framework.shutdown()
    
    @pytest.mark.asyncio
    async def test_single_task_execution(self, framework_instance):
        """Test executing a single task."""
        framework = framework_instance
        await framework.initialize()
        
        result = await framework.execute_single(
            agent_name="text_processor",
            input_data="Hello, world!",
            task_type="general"
        )
        
        assert result["success"] == True
        assert "response" in result
        assert "execution_time" in result
        assert result["execution_time"] > 0
        
        await framework.shutdown()
    
    @pytest.mark.asyncio
    async def test_multiple_task_execution(self, framework_instance):
        """Test executing multiple tasks."""
        framework = framework_instance
        await framework.initialize()
        
        tasks = [
            {
                "agent_name": "text_processor",
                "input_data": "Task 1",
                "parameters": {"task_type": "general"}
            },
            {
                "agent_name": "code_analyzer",
                "input_data": "def hello(): pass",
                "parameters": {"task_type": "code_analysis"}
            }
        ]
        
        # Test serial execution
        result = await framework.execute_tasks(tasks, mode="serial")
        assert result["success"] == True
        assert len(result["results"]) == 2
        
        # Test parallel execution
        result = await framework.execute_tasks(tasks, mode="parallel")
        assert result["success"] == True
        assert len(result["results"]) == 2
        
        await framework.shutdown()
    
    @pytest.mark.asyncio
    async def test_health_check(self, framework_instance):
        """Test health check functionality."""
        framework = framework_instance
        await framework.initialize()
        
        health_status = await framework.health_check()
        
        assert "framework_status" in health_status
        assert "total_agents" in health_status
        assert "agent_health" in health_status
        
        # Framework should be healthy
        assert health_status["framework_status"] == "healthy"
        
        # All agents should be healthy (even in simulation mode)
        for agent_name, is_healthy in health_status["agent_health"].items():
            assert is_healthy == True
        
        await framework.shutdown()
    
    @pytest.mark.asyncio
    async def test_framework_info(self, framework_instance):
        """Test getting framework information."""
        framework = framework_instance
        await framework.initialize()
        
        info = framework.get_framework_info()
        
        assert "version" in info
        assert "total_agents" in info
        assert "agents" in info
        assert "available_projects" in info
        assert "config_dir" in info
        
        assert info["version"] == "1.0.0"
        assert info["total_agents"] > 0
        
        await framework.shutdown()