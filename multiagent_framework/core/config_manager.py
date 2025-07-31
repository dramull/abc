"""
Configuration manager for the multiagent framework.
"""

import yaml
import json
import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from pydantic import BaseModel, Field
from .agent_base import AgentConfig


class ProjectConfig(BaseModel):
    """Configuration model for projects."""
    name: str
    description: str = ""
    agents: List[str] = Field(default_factory=list)
    execution_mode: str = "serial"  # "serial" or "parallel"
    global_config: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""


class FrameworkConfig(BaseModel):
    """Main framework configuration."""
    version: str = "1.0.0"
    default_timeout: int = 30
    max_parallel_agents: int = 5
    log_level: str = "INFO"
    ui_config: Dict[str, Any] = Field(default_factory=dict)
    api_config: Dict[str, Any] = Field(default_factory=dict)


class ConfigManager:
    """
    Manages configuration for the multiagent framework.
    
    Handles loading, saving, and validation of configurations for
    the framework, projects, and agents.
    """
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize the configuration manager.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.framework_config_path = self.config_dir / "framework_config.yaml"
        self.agents_config_path = self.config_dir / "agents_config.yaml"
        self.projects_dir = Path("projects")
        self.projects_dir.mkdir(exist_ok=True)
        
        self._framework_config: Optional[FrameworkConfig] = None
        self._agents_config: Dict[str, AgentConfig] = {}
        
        # Setup logger
        self.logger = logging.getLogger(__name__)
        
    def load_framework_config(self) -> FrameworkConfig:
        """
        Load the main framework configuration.
        
        Returns:
            FrameworkConfig object
        """
        if self._framework_config is None:
            if self.framework_config_path.exists():
                try:
                    with open(self.framework_config_path, 'r') as f:
                        config_data = yaml.safe_load(f)
                    
                    # Validate configuration
                    if not isinstance(config_data, dict):
                        raise ValueError("Invalid configuration format: expected dictionary")
                    
                    self._framework_config = FrameworkConfig(**config_data)
                except (yaml.YAMLError, TypeError, ValueError) as e:
                    self.logger.error(f"Error loading framework config: {str(e)}")
                    # Fallback to default configuration
                    self._framework_config = FrameworkConfig()
                    self.save_framework_config(self._framework_config)
            else:
                # Create default configuration
                self._framework_config = FrameworkConfig()
                self.save_framework_config(self._framework_config)
        
        return self._framework_config
    
    def save_framework_config(self, config: FrameworkConfig) -> None:
        """
        Save the framework configuration.
        
        Args:
            config: FrameworkConfig to save
        """
        with open(self.framework_config_path, 'w') as f:
            yaml.dump(config.model_dump(), f, default_flow_style=False)
        self._framework_config = config
    
    def load_agents_config(self) -> Dict[str, AgentConfig]:
        """
        Load all agent configurations.
        
        Returns:
            Dictionary mapping agent names to AgentConfig objects
        """
        if not self._agents_config:
            if self.agents_config_path.exists():
                try:
                    with open(self.agents_config_path, 'r') as f:
                        config_data = yaml.safe_load(f)
                    
                    # Validate configuration structure
                    if not isinstance(config_data, dict) or 'agents' not in config_data:
                        raise ValueError("Invalid agents configuration format")
                    
                    for name, agent_data in config_data.get('agents', {}).items():
                        try:
                            self._agents_config[name] = AgentConfig(name=name, **agent_data)
                        except Exception as e:
                            self.logger.error(f"Invalid configuration for agent '{name}': {str(e)}")
                            
                except (yaml.YAMLError, TypeError, ValueError) as e:
                    self.logger.error(f"Error loading agents config: {str(e)}")
                    # Fallback to default configurations
                    self._create_default_agents_config()
            else:
                # Create default agent configurations
                self._create_default_agents_config()
        
        return self._agents_config
    
    def save_agents_config(self, agents_config: Dict[str, AgentConfig]) -> None:
        """
        Save agent configurations.
        
        Args:
            agents_config: Dictionary of agent configurations
        """
        config_data = {
            'agents': {
                name: config.model_dump(exclude={'name'})
                for name, config in agents_config.items()
            }
        }
        
        with open(self.agents_config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)
        
        self._agents_config = agents_config
    
    def get_agent_config(self, agent_name: str) -> Optional[AgentConfig]:
        """
        Get configuration for a specific agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            AgentConfig if found, None otherwise
        """
        agents = self.load_agents_config()
        return agents.get(agent_name)
    
    def add_agent_config(self, agent_config: AgentConfig) -> None:
        """
        Add or update an agent configuration.
        
        Args:
            agent_config: AgentConfig to add/update
        """
        agents = self.load_agents_config()
        agents[agent_config.name] = agent_config
        self.save_agents_config(agents)
    
    def remove_agent_config(self, agent_name: str) -> bool:
        """
        Remove an agent configuration.
        
        Args:
            agent_name: Name of the agent to remove
            
        Returns:
            True if removed, False if not found
        """
        agents = self.load_agents_config()
        if agent_name in agents:
            del agents[agent_name]
            self.save_agents_config(agents)
            return True
        return False
    
    def load_project_config(self, project_name: str) -> Optional[ProjectConfig]:
        """
        Load configuration for a specific project.
        
        Args:
            project_name: Name of the project
            
        Returns:
            ProjectConfig if found, None otherwise
        """
        project_path = self.projects_dir / project_name / "project_config.yaml"
        if project_path.exists():
            with open(project_path, 'r') as f:
                config_data = yaml.safe_load(f)
            return ProjectConfig(**config_data)
        return None
    
    def save_project_config(self, project_config: ProjectConfig) -> None:
        """
        Save a project configuration.
        
        Args:
            project_config: ProjectConfig to save
        """
        project_dir = self.projects_dir / project_config.name
        project_dir.mkdir(exist_ok=True)
        
        project_path = project_dir / "project_config.yaml"
        with open(project_path, 'w') as f:
            yaml.dump(project_config.model_dump(), f, default_flow_style=False)
    
    def list_projects(self) -> List[str]:
        """
        List all available projects.
        
        Returns:
            List of project names
        """
        projects = []
        for project_dir in self.projects_dir.iterdir():
            if project_dir.is_dir() and (project_dir / "project_config.yaml").exists():
                projects.append(project_dir.name)
        return projects
    
    def delete_project(self, project_name: str) -> bool:
        """
        Delete a project and its configuration.
        
        Args:
            project_name: Name of the project to delete
            
        Returns:
            True if deleted, False if not found
        """
        project_dir = self.projects_dir / project_name
        if project_dir.exists():
            import shutil
            shutil.rmtree(project_dir)
            return True
        return False
    
    def _create_default_agents_config(self) -> None:
        """Create default agent configurations."""
        default_agents = {
            "text_processor": AgentConfig(
                name="text_processor",
                description="General text processing and analysis agent",
                model_type="kimi",
                max_tokens=1500,
                temperature=0.7
            ),
            "code_analyzer": AgentConfig(
                name="code_analyzer",
                description="Code analysis and documentation agent",
                model_type="qwen",
                max_tokens=2000,
                temperature=0.3
            ),
            "research_agent": AgentConfig(
                name="research_agent",
                description="Information gathering and synthesis agent",
                model_type="kimi",
                max_tokens=2500,
                temperature=0.8
            )
        }
        
        self.save_agents_config(default_agents)