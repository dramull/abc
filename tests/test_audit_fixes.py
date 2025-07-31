"""
Test file to validate critical fixes for the MultiAgent Framework audit.
"""

import pytest
import asyncio
import yaml
import json
from pathlib import Path
from multiagent_framework.core.framework import MultiAgentFramework
from multiagent_framework.core.agent_base import AgentConfig
from multiagent_framework.utils.helpers import validate_agent_config, sanitize_input, is_valid_api_key


class TestCriticalFixes:
    """Test critical fixes implemented during the audit."""

    @pytest.fixture
    def temp_config_dir(self, tmp_path):
        """Create a temporary config directory for testing."""
        return str(tmp_path / "config")

    @pytest.mark.asyncio
    async def test_resource_cleanup(self, temp_config_dir):
        """Test that resources are properly cleaned up."""
        framework = MultiAgentFramework(temp_config_dir)
        await framework.initialize()
        
        # Add agents to test cleanup (use empty API key for simulation mode)
        config = AgentConfig(
            name="cleanup_test_agent",
            model_type="kimi",
            api_key="",  # Empty for simulation mode
            timeout=10
        )
        
        success = await framework.add_agent_async(config)
        assert success
        
        # Verify agent was added
        assert "cleanup_test_agent" in framework.get_agents()
        
        # Test shutdown cleans up resources
        await framework.shutdown()
        
        # Verify framework is properly shut down
        assert len(framework.agents) == 0

    @pytest.mark.asyncio
    async def test_async_agent_management(self, temp_config_dir):
        """Test async agent management functions properly."""
        framework = MultiAgentFramework(temp_config_dir)
        await framework.initialize()
        
        initial_count = len(framework.get_agents())
        
        # Test async agent addition
        config = AgentConfig(
            name="async_test_agent",
            model_type="qwen",
            api_key="",  # Empty for simulation mode
            timeout=15
        )
        
        success = await framework.add_agent_async(config)
        assert success
        
        # Verify agent was added immediately
        assert len(framework.get_agents()) == initial_count + 1
        assert "async_test_agent" in framework.get_agents()
        
        # Test agent removal
        success = framework.remove_agent("async_test_agent")
        assert success
        
        # Verify agent was removed
        assert len(framework.get_agents()) == initial_count
        assert "async_test_agent" not in framework.get_agents()
        
        await framework.shutdown()

    def test_config_validation(self):
        """Test configuration validation functions."""
        # Test valid agent config
        valid_config = {
            "name": "test_agent",
            "model_type": "kimi",
            "max_tokens": 1000,
            "temperature": 0.7,
            "timeout": 30,
            "retry_attempts": 3
        }
        
        is_valid, error = validate_agent_config(valid_config)
        assert is_valid
        assert error == ""
        
        # Test invalid model type
        invalid_config = valid_config.copy()
        invalid_config["model_type"] = "invalid_model"
        
        is_valid, error = validate_agent_config(invalid_config)
        assert not is_valid
        assert "Invalid model_type" in error
        
        # Test missing required field
        incomplete_config = {"name": "test"}
        
        is_valid, error = validate_agent_config(incomplete_config)
        assert not is_valid
        assert "Missing required field" in error
        
        # Test invalid numeric values
        invalid_numeric = valid_config.copy()
        invalid_numeric["temperature"] = 2.0  # Out of range
        
        is_valid, error = validate_agent_config(invalid_numeric)
        assert not is_valid
        assert "must be between" in error

    def test_input_sanitization(self):
        """Test input sanitization functions."""
        # Test normal text
        normal_text = "This is normal text with numbers 123."
        sanitized = sanitize_input(normal_text)
        assert sanitized == normal_text
        
        # Test text with control characters
        control_text = "Text with\x00control\x01characters"
        sanitized = sanitize_input(control_text)
        assert "\x00" not in sanitized
        assert "\x01" not in sanitized
        
        # Test preserving newlines and tabs
        formatted_text = "Line 1\nLine 2\tTabbed"
        sanitized = sanitize_input(formatted_text)
        assert "\n" in sanitized
        assert "\t" in sanitized
        
        # Test empty input
        empty_sanitized = sanitize_input("")
        assert empty_sanitized == ""
        
        # Test None input
        none_sanitized = sanitize_input(None)
        assert none_sanitized == ""

    def test_api_key_validation(self):
        """Test API key validation."""
        # Valid API keys
        assert is_valid_api_key("sk-1234567890abcdef")
        assert is_valid_api_key("api_key_with_underscores_123")
        assert is_valid_api_key("LONG_API_KEY_WITH_MIXED_CASE_123456789")
        
        # Invalid API keys
        assert not is_valid_api_key("")
        assert not is_valid_api_key(None)
        assert not is_valid_api_key("short")
        assert not is_valid_api_key("   ")  # Only whitespace
        assert not is_valid_api_key("!@#$%^&*()")  # Only special chars

    @pytest.mark.asyncio
    async def test_error_handling_in_config_loading(self, temp_config_dir):
        """Test error handling when loading malformed configurations."""
        config_dir = Path(temp_config_dir)
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Create malformed YAML file
        malformed_yaml = config_dir / "framework_config.yaml"
        malformed_yaml.write_text("invalid: yaml: content: [unclosed")
        
        # Framework should handle malformed config gracefully
        framework = MultiAgentFramework(temp_config_dir)
        config = framework.config_manager.load_framework_config()
        
        # Should fall back to default config
        assert config.version == "1.0.0"
        assert config.default_timeout == 30

    @pytest.mark.asyncio 
    async def test_multiple_concurrent_operations(self, temp_config_dir):
        """Test framework handles multiple concurrent operations safely."""
        framework = MultiAgentFramework(temp_config_dir)
        await framework.initialize()
        
        # Create multiple agent configs
        configs = []
        for i in range(3):
            config = AgentConfig(
                name=f"concurrent_agent_{i}",
                model_type="kimi",
                api_key="",  # Empty for simulation
                timeout=10
            )
            configs.append(config)
        
        # Add agents concurrently
        tasks = [framework.add_agent_async(config) for config in configs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should succeed
        assert all(result is True for result in results if not isinstance(result, Exception))
        
        # Verify all agents were added
        agents = framework.get_agents()
        for i in range(3):
            assert f"concurrent_agent_{i}" in agents
        
        await framework.shutdown()

    @pytest.mark.asyncio
    async def test_graceful_shutdown_with_active_agents(self, temp_config_dir):
        """Test graceful shutdown even with active agents."""
        framework = MultiAgentFramework(temp_config_dir)
        await framework.initialize()
        
        # Add some agents
        for i in range(2):
            config = AgentConfig(
                name=f"shutdown_test_agent_{i}",
                model_type="qwen",
                api_key="",
                timeout=5
            )
            await framework.add_agent_async(config)
        
        # Verify agents are active
        assert len(framework.get_agents()) >= 2
        
        # Shutdown should complete without errors
        await framework.shutdown()
        
        # Verify clean shutdown
        assert len(framework.agents) == 0

    def test_path_handling_cross_platform(self, temp_config_dir):
        """Test that path handling works across platforms."""
        framework = MultiAgentFramework(temp_config_dir)
        
        # Test that config directory was created
        config_path = Path(temp_config_dir)
        assert config_path.exists()
        
        # Test project directory creation
        projects_path = Path("projects")
        assert projects_path.exists()

    @pytest.mark.asyncio
    async def test_agent_lifecycle_management(self, temp_config_dir):
        """Test complete agent lifecycle (create, use, shutdown)."""
        framework = MultiAgentFramework(temp_config_dir)
        await framework.initialize()
        
        # Create agent
        config = AgentConfig(
            name="lifecycle_test_agent",
            model_type="kimi",
            api_key="",  # Simulation mode
            timeout=10
        )
        
        # Add agent
        success = await framework.add_agent_async(config)
        assert success
        
        # Use agent
        result = await framework.execute_single(
            "lifecycle_test_agent",
            "Test message",
            task_type="general"
        )
        assert result["success"]
        
        # Check agent status
        status = framework.get_agent_status("lifecycle_test_agent")
        assert status is not None
        assert status["is_active"]
        
        # Remove agent
        success = framework.remove_agent("lifecycle_test_agent")
        assert success
        
        # Verify agent is gone
        assert "lifecycle_test_agent" not in framework.get_agents()
        
        await framework.shutdown()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])