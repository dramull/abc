"""
Tests for agent implementations.
"""

import pytest
import asyncio

from multiagent_framework.core.agent_base import AgentConfig
from multiagent_framework.agents.kimi_agent import KimiAgent
from multiagent_framework.agents.qwen_agent import QwenAgent
from multiagent_framework.agents.custom_agent import CustomAgent


class TestAgents:
    """Test cases for agent implementations."""
    
    @pytest.mark.asyncio
    async def test_kimi_agent_initialization(self):
        """Test Kimi agent initialization."""
        config = AgentConfig(
            name="test_kimi",
            description="Test Kimi agent",
            model_type="kimi",
            api_key="",  # Empty for testing
            max_tokens=500,
            temperature=0.7
        )
        
        agent = KimiAgent(config)
        success = await agent.initialize()
        
        assert success
        assert agent.is_active
        assert agent.config.name == "test_kimi"
        
        await agent.shutdown()
    
    @pytest.mark.asyncio
    async def test_qwen_agent_initialization(self):
        """Test Qwen agent initialization."""
        config = AgentConfig(
            name="test_qwen",
            description="Test Qwen agent",
            model_type="qwen",
            api_key="",  # Empty for testing
            max_tokens=500,
            temperature=0.3
        )
        
        agent = QwenAgent(config)
        success = await agent.initialize()
        
        assert success
        assert agent.is_active
        assert agent.config.name == "test_qwen"
        
        await agent.shutdown()
    
    @pytest.mark.asyncio
    async def test_custom_agent_initialization(self):
        """Test Custom agent initialization."""
        config = AgentConfig(
            name="test_custom",
            description="Test Custom agent",
            model_type="kimi",  # Custom agent can use either model
            api_key="",  # Empty for testing
            max_tokens=500,
            temperature=0.8
        )
        
        agent = CustomAgent(config)
        success = await agent.initialize()
        
        assert success
        assert agent.is_active
        assert agent.config.name == "test_custom"
        
        await agent.shutdown()
    
    @pytest.mark.asyncio
    async def test_kimi_agent_processing(self):
        """Test Kimi agent text processing."""
        config = AgentConfig(
            name="test_kimi",
            model_type="kimi",
            api_key="",
            max_tokens=500,
            temperature=0.7
        )
        
        agent = KimiAgent(config)
        await agent.initialize()
        
        # Test general processing
        result = await agent.process("Hello, world!")
        assert result.success
        assert result.response
        assert result.execution_time > 0
        
        # Test summarization
        result = await agent.process(
            "This is a long text that needs to be summarized.",
            task_type="summarization"
        )
        assert result.success
        assert "summary" in result.response.lower() or "summariz" in result.response.lower()
        
        await agent.shutdown()
    
    @pytest.mark.asyncio
    async def test_qwen_agent_processing(self):
        """Test Qwen agent code processing."""
        config = AgentConfig(
            name="test_qwen",
            model_type="qwen",
            api_key="",
            max_tokens=500,
            temperature=0.3
        )
        
        agent = QwenAgent(config)
        await agent.initialize()
        
        # Test code analysis
        code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
        """
        
        result = await agent.process(code, task_type="code_analysis")
        assert result.success
        assert result.response
        assert result.execution_time > 0
        
        # Test code review
        result = await agent.process(code, task_type="code_review")
        assert result.success
        
        await agent.shutdown()
    
    @pytest.mark.asyncio
    async def test_custom_agent_processing(self):
        """Test Custom agent research capabilities."""
        config = AgentConfig(
            name="test_custom",
            model_type="kimi",
            api_key="",
            max_tokens=500,
            temperature=0.8
        )
        
        agent = CustomAgent(config)
        await agent.initialize()
        
        # Test research task
        result = await agent.process(
            "Artificial Intelligence in healthcare",
            task_type="research",
            domain="medical"
        )
        assert result.success
        assert result.response
        assert result.execution_time > 0
        
        # Test information gathering
        result = await agent.process(
            "Machine learning algorithms",
            task_type="information_gathering",
            domain="technical"
        )
        assert result.success
        
        await agent.shutdown()
    
    @pytest.mark.asyncio
    async def test_agent_health_check(self):
        """Test agent health check functionality."""
        config = AgentConfig(
            name="test_agent",
            model_type="kimi",
            api_key="",
            max_tokens=500,
            temperature=0.7
        )
        
        agent = KimiAgent(config)
        await agent.initialize()
        
        # Health check should pass
        is_healthy = await agent.health_check()
        assert is_healthy
        
        await agent.shutdown()
    
    @pytest.mark.asyncio
    async def test_agent_capabilities(self):
        """Test agent capabilities and task support."""
        # Test Kimi agent capabilities
        kimi_config = AgentConfig(name="kimi_test", model_type="kimi", api_key="")
        kimi_agent = KimiAgent(kimi_config)
        
        capabilities = kimi_agent.get_capabilities()
        assert "text_analysis" in capabilities
        assert "summarization" in capabilities
        
        assert kimi_agent.supports_task("summarization")
        assert kimi_agent.supports_task("translation")
        
        # Test Qwen agent capabilities
        qwen_config = AgentConfig(name="qwen_test", model_type="qwen", api_key="")
        qwen_agent = QwenAgent(qwen_config)
        
        capabilities = qwen_agent.get_capabilities()
        assert "code_analysis" in capabilities
        assert "code_review" in capabilities
        
        assert qwen_agent.supports_task("code_analysis")
        assert qwen_agent.supports_task("debugging")
        
        # Test Custom agent capabilities
        custom_config = AgentConfig(name="custom_test", model_type="kimi", api_key="")
        custom_agent = CustomAgent(custom_config)
        
        capabilities = custom_agent.get_capabilities()
        assert "research" in capabilities
        assert "information_gathering" in capabilities
        
        assert custom_agent.supports_task("research")
        assert custom_agent.supports_task("data_synthesis")
        
        # Test supported domains
        domains = custom_agent.get_supported_domains()
        assert "medical" in domains
        assert "technical" in domains
    
    def test_agent_status(self):
        """Test agent status reporting."""
        config = AgentConfig(
            name="status_test",
            model_type="kimi",
            api_key="",
            max_tokens=500,
            temperature=0.7
        )
        
        agent = KimiAgent(config)
        
        status = agent.get_status()
        assert status["agent_id"] == agent.agent_id
        assert status["name"] == "status_test"
        assert status["model_type"] == "kimi"
        assert status["is_active"] == False  # Not initialized yet
        assert status["total_executions"] == 0