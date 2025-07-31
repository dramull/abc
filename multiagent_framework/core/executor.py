"""
Execution engine for running agents in parallel or serial mode.
"""

import asyncio
import time
from typing import List, Dict, Any, Optional, Union
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from pydantic import BaseModel
from .agent_base import AgentBase, AgentResponse


class ExecutionMode(Enum):
    """Execution modes for agent processing."""
    SERIAL = "serial"
    PARALLEL = "parallel"


class ExecutionTask(BaseModel):
    """Represents a task to be executed by an agent."""
    agent_name: str
    input_data: str
    parameters: Dict[str, Any] = {}
    priority: int = 1


class ExecutionResult(BaseModel):
    """Result of executing a set of tasks."""
    success: bool
    execution_time: float
    results: List[AgentResponse]
    errors: List[str] = []
    metadata: Dict[str, Any] = {}


class ExecutionEngine:
    """
    Engine for executing agents in parallel or serial mode.
    
    Handles task scheduling, execution monitoring, and result aggregation.
    """
    
    def __init__(self, max_parallel_agents: int = 5):
        """
        Initialize the execution engine.
        
        Args:
            max_parallel_agents: Maximum number of agents to run in parallel
        """
        self.max_parallel_agents = max_parallel_agents
        self.active_agents: Dict[str, AgentBase] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_parallel_agents)
        
    def register_agent(self, agent: AgentBase) -> None:
        """
        Register an agent with the execution engine.
        
        Args:
            agent: Agent instance to register
        """
        self.active_agents[agent.config.name] = agent
        
    def unregister_agent(self, agent_name: str) -> bool:
        """
        Unregister an agent from the execution engine.
        
        Args:
            agent_name: Name of the agent to unregister
            
        Returns:
            True if unregistered, False if not found
        """
        if agent_name in self.active_agents:
            del self.active_agents[agent_name]
            return True
        return False
    
    async def execute_tasks(
        self,
        tasks: List[ExecutionTask],
        mode: ExecutionMode = ExecutionMode.SERIAL,
        timeout: Optional[int] = None
    ) -> ExecutionResult:
        """
        Execute a list of tasks using the specified mode.
        
        Args:
            tasks: List of tasks to execute
            mode: Execution mode (serial or parallel)
            timeout: Optional timeout for the entire execution
            
        Returns:
            ExecutionResult containing all results and metadata
        """
        start_time = time.time()
        results = []
        errors = []
        
        try:
            if mode == ExecutionMode.SERIAL:
                results, errors = await self._execute_serial(tasks, timeout)
            else:
                results, errors = await self._execute_parallel(tasks, timeout)
                
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                success=len(errors) == 0,
                execution_time=execution_time,
                results=results,
                errors=errors,
                metadata={
                    "mode": mode.value,
                    "total_tasks": len(tasks),
                    "successful_tasks": len([r for r in results if r.success]),
                    "failed_tasks": len(errors)
                }
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                execution_time=execution_time,
                results=results,
                errors=[f"Execution engine error: {str(e)}"],
                metadata={"mode": mode.value, "total_tasks": len(tasks)}
            )
    
    async def _execute_serial(
        self,
        tasks: List[ExecutionTask],
        timeout: Optional[int] = None
    ) -> tuple[List[AgentResponse], List[str]]:
        """
        Execute tasks serially (one after another).
        
        Args:
            tasks: List of tasks to execute
            timeout: Optional timeout for each task
            
        Returns:
            Tuple of (results, errors)
        """
        results = []
        errors = []
        
        for task in tasks:
            try:
                if task.agent_name not in self.active_agents:
                    errors.append(f"Agent '{task.agent_name}' not found")
                    continue
                
                agent = self.active_agents[task.agent_name]
                
                # Execute task with timeout
                if timeout:
                    result = await asyncio.wait_for(
                        agent.process(task.input_data, **task.parameters),
                        timeout=timeout
                    )
                else:
                    result = await agent.process(task.input_data, **task.parameters)
                
                results.append(result)
                
                if not result.success and result.error:
                    errors.append(f"Agent '{task.agent_name}': {result.error}")
                    
            except asyncio.TimeoutError:
                errors.append(f"Agent '{task.agent_name}' timed out")
            except Exception as e:
                errors.append(f"Agent '{task.agent_name}' error: {str(e)}")
        
        return results, errors
    
    async def _execute_parallel(
        self,
        tasks: List[ExecutionTask],
        timeout: Optional[int] = None
    ) -> tuple[List[AgentResponse], List[str]]:
        """
        Execute tasks in parallel.
        
        Args:
            tasks: List of tasks to execute
            timeout: Optional timeout for each task
            
        Returns:
            Tuple of (results, errors)
        """
        results = []
        errors = []
        
        # Create coroutines for all tasks
        coroutines = []
        task_info = []
        
        for task in tasks:
            if task.agent_name not in self.active_agents:
                errors.append(f"Agent '{task.agent_name}' not found")
                continue
            
            agent = self.active_agents[task.agent_name]
            
            # Create coroutine with timeout if specified
            if timeout:
                coro = asyncio.wait_for(
                    agent.process(task.input_data, **task.parameters),
                    timeout=timeout
                )
            else:
                coro = agent.process(task.input_data, **task.parameters)
            
            coroutines.append(coro)
            task_info.append(task)
        
        # Execute all coroutines in parallel
        if coroutines:
            try:
                # Use asyncio.gather to run all tasks concurrently
                parallel_results = await asyncio.gather(*coroutines, return_exceptions=True)
                
                for i, result in enumerate(parallel_results):
                    task = task_info[i]
                    
                    if isinstance(result, Exception):
                        if isinstance(result, asyncio.TimeoutError):
                            errors.append(f"Agent '{task.agent_name}' timed out")
                        else:
                            errors.append(f"Agent '{task.agent_name}' error: {str(result)}")
                    else:
                        results.append(result)
                        if not result.success and result.error:
                            errors.append(f"Agent '{task.agent_name}': {result.error}")
                            
            except Exception as e:
                errors.append(f"Parallel execution error: {str(e)}")
        
        return results, errors
    
    async def execute_single_task(
        self,
        agent_name: str,
        input_data: str,
        timeout: Optional[int] = None,
        **kwargs
    ) -> AgentResponse:
        """
        Execute a single task on a specific agent.
        
        Args:
            agent_name: Name of the agent to use
            input_data: Input data for the agent
            timeout: Optional timeout for the task
            **kwargs: Additional parameters for the agent
            
        Returns:
            AgentResponse from the agent
        """
        if agent_name not in self.active_agents:
            return AgentResponse(
                agent_id="unknown",
                success=False,
                error=f"Agent '{agent_name}' not found"
            )
        
        agent = self.active_agents[agent_name]
        
        try:
            if timeout:
                result = await asyncio.wait_for(
                    agent.process(input_data, **kwargs),
                    timeout=timeout
                )
            else:
                result = await agent.process(input_data, **kwargs)
            
            return result
            
        except asyncio.TimeoutError:
            return AgentResponse(
                agent_id=agent.agent_id,
                success=False,
                error=f"Agent '{agent_name}' timed out"
            )
        except Exception as e:
            return AgentResponse(
                agent_id=agent.agent_id,
                success=False,
                error=f"Agent '{agent_name}' error: {str(e)}"
            )
    
    def get_active_agents(self) -> List[str]:
        """
        Get list of currently active agent names.
        
        Returns:
            List of active agent names
        """
        return list(self.active_agents.keys())
    
    async def health_check_all(self) -> Dict[str, bool]:
        """
        Perform health checks on all active agents.
        
        Returns:
            Dictionary mapping agent names to health status
        """
        health_status = {}
        
        for agent_name, agent in self.active_agents.items():
            try:
                health_status[agent_name] = await agent.health_check()
            except Exception:
                health_status[agent_name] = False
        
        return health_status
    
    async def shutdown(self) -> None:
        """Shutdown the execution engine and all agents."""
        for agent in self.active_agents.values():
            await agent.shutdown()
        
        self.active_agents.clear()
        self.executor.shutdown(wait=True)