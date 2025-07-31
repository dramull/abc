"""
Main multiagent framework class that coordinates all components.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from .agent_base import AgentBase, AgentConfig
from .config_manager import ConfigManager, ProjectConfig
from .executor import ExecutionEngine, ExecutionTask, ExecutionMode, ExecutionResult


class MultiAgentFramework:
    """
    Main framework class for managing multiple AI agents.
    
    Provides a unified interface for configuring, managing, and executing
    multiple agents using different AI models (Kimi K2, Qwen3, etc.).
    """
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize the multiagent framework.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_manager = ConfigManager(config_dir)
        self.execution_engine = ExecutionEngine()
        self.agents: Dict[str, AgentBase] = {}
        self.current_project: Optional[str] = None
        
        # Setup logging
        self._setup_logging()
        
        # Load framework configuration
        self.framework_config = self.config_manager.load_framework_config()
        
    def _setup_logging(self) -> None:
        """Setup logging for the framework."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> bool:
        """
        Initialize the framework and load default agents.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.logger.info("Initializing MultiAgent Framework...")
            
            # Load agent configurations
            agents_config = self.config_manager.load_agents_config()
            
            # Initialize agents based on their model types
            for agent_name, agent_config in agents_config.items():
                agent = await self._create_agent(agent_config)
                if agent:
                    self.agents[agent_name] = agent
                    self.execution_engine.register_agent(agent)
                    self.logger.info(f"Initialized agent: {agent_name}")
                else:
                    self.logger.warning(f"Failed to initialize agent: {agent_name}")
            
            self.logger.info(f"Framework initialized with {len(self.agents)} agents")
            return True
            
        except Exception as e:
            self.logger.error(f"Framework initialization failed: {str(e)}")
            return False
    
    async def _create_agent(self, config: AgentConfig) -> Optional[AgentBase]:
        """
        Create an agent instance based on its configuration.
        
        Args:
            config: Agent configuration
            
        Returns:
            Agent instance if successful, None otherwise
        """
        try:
            # Import agent classes dynamically
            if config.model_type == "kimi":
                from ..agents.kimi_agent import KimiAgent
                agent = KimiAgent(config)
            elif config.model_type == "qwen":
                from ..agents.qwen_agent import QwenAgent
                agent = QwenAgent(config)
            else:
                from ..agents.custom_agent import CustomAgent
                agent = CustomAgent(config)
            
            # Initialize the agent
            if await agent.initialize():
                return agent
            else:
                self.logger.error(f"Failed to initialize agent: {config.name}")
                return None
                
        except ImportError as e:
            self.logger.error(f"Failed to import agent class for {config.model_type}: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Error creating agent {config.name}: {str(e)}")
            return None
    
    async def add_agent_async(self, agent_config: AgentConfig) -> bool:
        """
        Asynchronously add a new agent to the framework.
        
        Args:
            agent_config: Configuration for the new agent
            
        Returns:
            True if agent added successfully, False otherwise
        """
        try:
            # Save configuration
            self.config_manager.add_agent_config(agent_config)
            
            # Create and register agent
            agent = await self._create_agent(agent_config)
            if agent:
                self.agents[agent_config.name] = agent
                self.execution_engine.register_agent(agent)
                self.logger.info(f"Added agent: {agent_config.name}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to add agent {agent_config.name}: {str(e)}")
            return False
    
    def add_agent(self, agent_config: AgentConfig) -> bool:
        """
        Add a new agent to the framework (synchronous wrapper).
        
        Args:
            agent_config: Configuration for the new agent
            
        Returns:
            True if agent added successfully, False otherwise
        """
        try:
            # Save configuration
            self.config_manager.add_agent_config(agent_config)
            
            # Note: For synchronous usage, configuration is saved immediately
            # Agent will be created on next framework operation or via add_agent_async
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add agent {agent_config.name}: {str(e)}")
            return False
    
    def remove_agent(self, agent_name: str) -> bool:
        """
        Remove an agent from the framework.
        
        Args:
            agent_name: Name of the agent to remove
            
        Returns:
            True if agent removed successfully, False otherwise
        """
        try:
            # Remove from execution engine
            self.execution_engine.unregister_agent(agent_name)
            
            # Shutdown and remove agent
            if agent_name in self.agents:
                # Schedule shutdown for next event loop cycle
                agent = self.agents[agent_name]
                del self.agents[agent_name]
                
                # Attempt to shutdown the agent if possible
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Schedule shutdown for later
                        asyncio.create_task(agent.shutdown())
                    else:
                        # Run shutdown immediately
                        loop.run_until_complete(agent.shutdown())
                except Exception as e:
                    self.logger.warning(f"Could not properly shutdown agent {agent_name}: {str(e)}")
            
            # Remove configuration
            self.config_manager.remove_agent_config(agent_name)
            
            self.logger.info(f"Removed agent: {agent_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove agent {agent_name}: {str(e)}")
            return False
    
    def get_agents(self) -> List[str]:
        """
        Get list of available agent names.
        
        Returns:
            List of agent names
        """
        return list(self.agents.keys())
    
    def get_agent_status(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Agent status dictionary or None if not found
        """
        if agent_name in self.agents:
            return self.agents[agent_name].get_status()
        return None
    
    async def execute_single(
        self,
        agent_name: str,
        input_data: str,
        timeout: Optional[int] = None,
        **kwargs
    ) -> dict:
        """
        Execute a single task on a specific agent.
        
        Args:
            agent_name: Name of the agent to use
            input_data: Input data for processing
            timeout: Optional timeout in seconds
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing the result
        """
        result = await self.execution_engine.execute_single_task(
            agent_name, input_data, timeout, **kwargs
        )
        return result.model_dump()
    
    async def execute_tasks(
        self,
        tasks: List[Dict[str, Any]],
        mode: str = "serial",
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute multiple tasks.
        
        Args:
            tasks: List of task dictionaries with agent_name, input_data, and parameters
            mode: Execution mode ("serial" or "parallel")
            timeout: Optional timeout in seconds
            
        Returns:
            Dictionary containing execution results
        """
        # Convert task dictionaries to ExecutionTask objects
        execution_tasks = []
        for task_dict in tasks:
            task = ExecutionTask(
                agent_name=task_dict["agent_name"],
                input_data=task_dict["input_data"],
                parameters=task_dict.get("parameters", {}),
                priority=task_dict.get("priority", 1)
            )
            execution_tasks.append(task)
        
        # Execute tasks
        execution_mode = ExecutionMode.SERIAL if mode == "serial" else ExecutionMode.PARALLEL
        result = await self.execution_engine.execute_tasks(execution_tasks, execution_mode, timeout)
        
        return result.model_dump()
    
    def create_project(self, project_name: str, description: str = "", agents: List[str] = None) -> bool:
        """
        Create a new project.
        
        Args:
            project_name: Name of the project
            description: Project description
            agents: List of agent names to include in the project
            
        Returns:
            True if project created successfully, False otherwise
        """
        try:
            if agents is None:
                agents = []
            
            project_config = ProjectConfig(
                name=project_name,
                description=description,
                agents=agents,
                execution_mode="serial"
            )
            
            self.config_manager.save_project_config(project_config)
            self.logger.info(f"Created project: {project_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create project {project_name}: {str(e)}")
            return False
    
    def load_project(self, project_name: str) -> bool:
        """
        Load an existing project.
        
        Args:
            project_name: Name of the project to load
            
        Returns:
            True if project loaded successfully, False otherwise
        """
        try:
            project_config = self.config_manager.load_project_config(project_name)
            if project_config:
                self.current_project = project_name
                self.logger.info(f"Loaded project: {project_name}")
                return True
            else:
                self.logger.warning(f"Project not found: {project_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to load project {project_name}: {str(e)}")
            return False
    
    def get_projects(self) -> List[str]:
        """
        Get list of available projects.
        
        Returns:
            List of project names
        """
        return self.config_manager.list_projects()
    
    def delete_project(self, project_name: str) -> bool:
        """
        Delete a project.
        
        Args:
            project_name: Name of the project to delete
            
        Returns:
            True if project deleted successfully, False otherwise
        """
        try:
            success = self.config_manager.delete_project(project_name)
            if success:
                if self.current_project == project_name:
                    self.current_project = None
                self.logger.info(f"Deleted project: {project_name}")
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to delete project {project_name}: {str(e)}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the framework and all agents.
        
        Returns:
            Dictionary containing health status
        """
        try:
            agent_health = await self.execution_engine.health_check_all()
            
            return {
                "framework_status": "healthy",
                "total_agents": len(self.agents),
                "active_agents": list(self.agents.keys()),
                "agent_health": agent_health,
                "current_project": self.current_project
            }
            
        except Exception as e:
            return {
                "framework_status": "error",
                "error": str(e),
                "total_agents": len(self.agents),
                "current_project": self.current_project
            }
    
    async def shutdown(self) -> None:
        """Shutdown the framework and all components."""
        try:
            self.logger.info("Shutting down MultiAgent Framework...")
            await self.execution_engine.shutdown()
            self.agents.clear()
            self.logger.info("Framework shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {str(e)}")
    
    def get_framework_info(self) -> Dict[str, Any]:
        """
        Get information about the framework.
        
        Returns:
            Dictionary containing framework information
        """
        return {
            "version": "1.0.0",
            "total_agents": len(self.agents),
            "agents": list(self.agents.keys()),
            "current_project": self.current_project,
            "available_projects": self.get_projects(),
            "config_dir": str(self.config_manager.config_dir),
            "framework_config": self.framework_config.model_dump()
        }