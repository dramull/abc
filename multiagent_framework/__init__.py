"""
Multiagent Framework

A robust, modular multiagent framework using Kimi K2 and Qwen3 APIs.
Supports parallel and serial execution with easy configuration.
"""

__version__ = "1.0.0"
__author__ = "ABC Team"

from .core.framework import MultiAgentFramework
from .core.agent_base import AgentBase
from .core.config_manager import ConfigManager

__all__ = ["MultiAgentFramework", "AgentBase", "ConfigManager"]