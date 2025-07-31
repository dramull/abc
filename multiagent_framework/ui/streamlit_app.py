"""
Streamlit web application for the MultiAgent Framework.
"""

import streamlit as st
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import sys
import os

# Add the parent directory to sys.path to import the framework
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from multiagent_framework.core.framework import MultiAgentFramework
from multiagent_framework.core.agent_base import AgentConfig


# Initialize session state
if 'framework' not in st.session_state:
    st.session_state.framework = None
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
if 'current_project' not in st.session_state:
    st.session_state.current_project = None


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="MultiAgent Framework",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🤖 MultiAgent Framework")
    st.markdown("A robust, modular multiagent framework using Kimi K2 and Qwen3 APIs")
    
    # Sidebar for navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox(
            "Select Page",
            ["Dashboard", "Agent Management", "Project Management", "Execute Tasks", "Configuration", "Health Check"]
        )
    
    # Initialize framework if not done
    if not st.session_state.initialized:
        initialize_framework()
    
    # Route to appropriate page
    if page == "Dashboard":
        show_dashboard()
    elif page == "Agent Management":
        show_agent_management()
    elif page == "Project Management":
        show_project_management()
    elif page == "Execute Tasks":
        show_task_execution()
    elif page == "Configuration":
        show_configuration()
    elif page == "Health Check":
        show_health_check()


def initialize_framework():
    """Initialize the multiagent framework."""
    try:
        with st.spinner("Initializing MultiAgent Framework..."):
            # Create framework instance
            framework = MultiAgentFramework()
            
            # Run initialization in async context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(framework.initialize())
            
            if success:
                st.session_state.framework = framework
                st.session_state.initialized = True
                st.success("Framework initialized successfully!")
            else:
                st.error("Failed to initialize framework")
                
    except Exception as e:
        st.error(f"Error initializing framework: {str(e)}")


def show_dashboard():
    """Show the main dashboard."""
    st.header("📊 Dashboard")
    
    if not st.session_state.framework:
        st.warning("Framework not initialized")
        return
    
    framework = st.session_state.framework
    
    # Get framework info
    info = framework.get_framework_info()
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Agents", info["total_agents"])
    
    with col2:
        st.metric("Available Projects", len(info["available_projects"]))
    
    with col3:
        current_proj = info["current_project"] or "None"
        st.metric("Current Project", current_proj)
    
    with col4:
        st.metric("Framework Version", info["version"])
    
    # Display active agents
    st.subheader("Active Agents")
    if info["agents"]:
        for agent_name in info["agents"]:
            status = framework.get_agent_status(agent_name)
            if status:
                with st.expander(f"🤖 {agent_name}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Model Type:** {status.get('model_type', 'Unknown')}")
                        st.write(f"**Status:** {'Active' if status.get('is_active') else 'Inactive'}")
                    with col2:
                        st.write(f"**Total Executions:** {status.get('total_executions', 0)}")
                        last_exec = status.get('last_execution')
                        if last_exec:
                            st.write(f"**Last Execution:** {last_exec}")
    else:
        st.info("No active agents")
    
    # Recent activity (simulated)
    st.subheader("Recent Activity")
    st.info("No recent activity to display")


def show_agent_management():
    """Show agent management interface."""
    st.header("🤖 Agent Management")
    
    if not st.session_state.framework:
        st.warning("Framework not initialized")
        return
    
    framework = st.session_state.framework
    
    # Tabs for different operations
    tab1, tab2, tab3 = st.tabs(["View Agents", "Add Agent", "Configure Agent"])
    
    with tab1:
        st.subheader("Current Agents")
        agents = framework.get_agents()
        
        if agents:
            for agent_name in agents:
                status = framework.get_agent_status(agent_name)
                if status:
                    with st.expander(f"🤖 {agent_name}", expanded=False):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Model Type:** {status.get('model_type', 'Unknown')}")
                            st.write(f"**Status:** {'🟢 Active' if status.get('is_active') else '🔴 Inactive'}")
                            st.write(f"**Total Executions:** {status.get('total_executions', 0)}")
                        
                        with col2:
                            if st.button(f"Remove {agent_name}", key=f"remove_{agent_name}"):
                                if framework.remove_agent(agent_name):
                                    st.success(f"Agent {agent_name} removed successfully!")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to remove agent {agent_name}")
        else:
            st.info("No agents available")
    
    with tab2:
        st.subheader("Add New Agent")
        
        with st.form("add_agent_form"):
            agent_name = st.text_input("Agent Name", placeholder="my_new_agent")
            description = st.text_area("Description", placeholder="Agent description...")
            
            col1, col2 = st.columns(2)
            with col1:
                model_type = st.selectbox("Model Type", ["kimi", "qwen"])
                max_tokens = st.number_input("Max Tokens", min_value=100, max_value=4000, value=1000)
            
            with col2:
                temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
                timeout = st.number_input("Timeout (seconds)", min_value=10, max_value=300, value=30)
            
            api_key = st.text_input("API Key", type="password", placeholder="Enter API key (optional for demo)")
            api_endpoint = st.text_input("API Endpoint (optional)", placeholder="Custom endpoint URL")
            
            submitted = st.form_submit_button("Add Agent")
            
            if submitted:
                if agent_name:
                    config = AgentConfig(
                        name=agent_name,
                        description=description,
                        model_type=model_type,
                        api_key=api_key,
                        api_endpoint=api_endpoint,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        timeout=timeout
                    )
                    
                    if framework.add_agent(config):
                        st.success(f"Agent {agent_name} added successfully!")
                        time.sleep(1)  # Give time for async initialization
                        st.rerun()
                    else:
                        st.error("Failed to add agent")
                else:
                    st.error("Please enter an agent name")
    
    with tab3:
        st.subheader("Configure Existing Agent")
        agents = framework.get_agents()
        
        if agents:
            selected_agent = st.selectbox("Select Agent to Configure", agents)
            
            if selected_agent:
                config = framework.config_manager.get_agent_config(selected_agent)
                if config:
                    with st.form("config_agent_form"):
                        new_description = st.text_area("Description", value=config.description)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            new_max_tokens = st.number_input("Max Tokens", value=config.max_tokens, min_value=100, max_value=4000)
                            new_temperature = st.slider("Temperature", value=config.temperature, min_value=0.0, max_value=1.0, step=0.1)
                        
                        with col2:
                            new_timeout = st.number_input("Timeout", value=config.timeout, min_value=10, max_value=300)
                            new_retry_attempts = st.number_input("Retry Attempts", value=config.retry_attempts, min_value=1, max_value=5)
                        
                        new_api_key = st.text_input("API Key", type="password", placeholder="Leave empty to keep current")
                        
                        if st.form_submit_button("Update Configuration"):
                            # Create updated config
                            updated_config = AgentConfig(
                                name=config.name,
                                description=new_description,
                                model_type=config.model_type,
                                api_key=new_api_key if new_api_key else config.api_key,
                                api_endpoint=config.api_endpoint,
                                max_tokens=new_max_tokens,
                                temperature=new_temperature,
                                timeout=new_timeout,
                                retry_attempts=new_retry_attempts,
                                custom_params=config.custom_params
                            )
                            
                            framework.config_manager.add_agent_config(updated_config)
                            st.success("Agent configuration updated!")
        else:
            st.info("No agents available to configure")


def show_project_management():
    """Show project management interface."""
    st.header("📁 Project Management")
    
    if not st.session_state.framework:
        st.warning("Framework not initialized")
        return
    
    framework = st.session_state.framework
    
    # Tabs for project operations
    tab1, tab2, tab3 = st.tabs(["Current Projects", "Create Project", "Load Project"])
    
    with tab1:
        st.subheader("Available Projects")
        projects = framework.get_projects()
        
        if projects:
            for project in projects:
                with st.expander(f"📁 {project}"):
                    project_config = framework.config_manager.load_project_config(project)
                    if project_config:
                        st.write(f"**Description:** {project_config.description}")
                        st.write(f"**Agents:** {', '.join(project_config.agents)}")
                        st.write(f"**Execution Mode:** {project_config.execution_mode}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"Load {project}", key=f"load_{project}"):
                                if framework.load_project(project):
                                    st.session_state.current_project = project
                                    st.success(f"Project {project} loaded!")
                                    st.rerun()
                        
                        with col2:
                            if st.button(f"Delete {project}", key=f"delete_{project}"):
                                if framework.delete_project(project):
                                    st.success(f"Project {project} deleted!")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete project")
        else:
            st.info("No projects available")
    
    with tab2:
        st.subheader("Create New Project")
        
        with st.form("create_project_form"):
            project_name = st.text_input("Project Name", placeholder="my_project")
            project_description = st.text_area("Description", placeholder="Project description...")
            
            available_agents = framework.get_agents()
            selected_agents = st.multiselect("Select Agents", available_agents)
            
            execution_mode = st.selectbox("Execution Mode", ["serial", "parallel"])
            
            if st.form_submit_button("Create Project"):
                if project_name:
                    if framework.create_project(project_name, project_description, selected_agents):
                        st.success(f"Project {project_name} created successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to create project")
                else:
                    st.error("Please enter a project name")
    
    with tab3:
        st.subheader("Load Existing Project")
        projects = framework.get_projects()
        
        if projects:
            selected_project = st.selectbox("Select Project", projects)
            
            if st.button("Load Selected Project"):
                if framework.load_project(selected_project):
                    st.session_state.current_project = selected_project
                    st.success(f"Project {selected_project} loaded!")
                    st.rerun()
                else:
                    st.error("Failed to load project")
        else:
            st.info("No projects available to load")


def show_task_execution():
    """Show task execution interface."""
    st.header("⚡ Execute Tasks")
    
    if not st.session_state.framework:
        st.warning("Framework not initialized")
        return
    
    framework = st.session_state.framework
    agents = framework.get_agents()
    
    if not agents:
        st.warning("No agents available. Please add agents first.")
        return
    
    # Tabs for different execution modes
    tab1, tab2 = st.tabs(["Single Task", "Multiple Tasks"])
    
    with tab1:
        st.subheader("Execute Single Task")
        
        with st.form("single_task_form"):
            selected_agent = st.selectbox("Select Agent", agents)
            input_text = st.text_area("Input Text", placeholder="Enter your text here...")
            
            col1, col2 = st.columns(2)
            with col1:
                task_type = st.selectbox("Task Type", [
                    "general", "text_analysis", "summarization", "translation",
                    "code_analysis", "code_review", "documentation",
                    "research", "information_gathering"
                ])
                timeout = st.number_input("Timeout (seconds)", min_value=10, max_value=300, value=30)
            
            with col2:
                temperature = st.slider("Temperature Override", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
                max_tokens = st.number_input("Max Tokens Override", min_value=100, max_value=4000, value=1000)
            
            if st.form_submit_button("Execute Task"):
                if input_text and selected_agent:
                    with st.spinner("Executing task..."):
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            result = loop.run_until_complete(
                                framework.execute_single(
                                    selected_agent,
                                    input_text,
                                    timeout=timeout,
                                    task_type=task_type,
                                    temperature=temperature,
                                    max_tokens=max_tokens
                                )
                            )
                            
                            # Display results
                            if result.get("success"):
                                st.success("Task completed successfully!")
                                st.subheader("Result:")
                                st.write(result.get("response", "No response"))
                                
                                with st.expander("Execution Details"):
                                    st.json(result)
                            else:
                                st.error(f"Task failed: {result.get('error', 'Unknown error')}")
                                
                        except Exception as e:
                            st.error(f"Execution error: {str(e)}")
                else:
                    st.error("Please provide input text and select an agent")
    
    with tab2:
        st.subheader("Execute Multiple Tasks")
        
        # Task builder
        if 'tasks' not in st.session_state:
            st.session_state.tasks = []
        
        st.write("**Build Task List:**")
        
        with st.form("add_task_form"):
            col1, col2 = st.columns(2)
            with col1:
                task_agent = st.selectbox("Agent", agents, key="task_agent")
                task_input = st.text_area("Input Text", key="task_input")
            
            with col2:
                task_type = st.selectbox("Task Type", [
                    "general", "text_analysis", "summarization", "translation",
                    "code_analysis", "code_review", "documentation",
                    "research", "information_gathering"
                ], key="task_type")
                task_priority = st.number_input("Priority", min_value=1, max_value=10, value=1, key="task_priority")
            
            if st.form_submit_button("Add Task"):
                if task_input and task_agent:
                    new_task = {
                        "agent_name": task_agent,
                        "input_data": task_input,
                        "parameters": {"task_type": task_type},
                        "priority": task_priority
                    }
                    st.session_state.tasks.append(new_task)
                    st.success("Task added to list!")
                    st.rerun()
        
        # Display current tasks
        if st.session_state.tasks:
            st.write(f"**Current Tasks ({len(st.session_state.tasks)}):**")
            
            for i, task in enumerate(st.session_state.tasks):
                with st.expander(f"Task {i+1}: {task['agent_name']} - {task['parameters']['task_type']}"):
                    st.write(f"**Input:** {task['input_data'][:100]}...")
                    st.write(f"**Priority:** {task['priority']}")
                    
                    if st.button(f"Remove Task {i+1}", key=f"remove_task_{i}"):
                        st.session_state.tasks.pop(i)
                        st.rerun()
            
            # Execution controls
            st.write("**Execute Tasks:**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                execution_mode = st.selectbox("Execution Mode", ["serial", "parallel"])
            
            with col2:
                execution_timeout = st.number_input("Timeout per task", min_value=10, max_value=300, value=30)
            
            with col3:
                if st.button("Execute All Tasks"):
                    if st.session_state.tasks:
                        with st.spinner("Executing tasks..."):
                            try:
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)
                                result = loop.run_until_complete(
                                    framework.execute_tasks(
                                        st.session_state.tasks,
                                        mode=execution_mode,
                                        timeout=execution_timeout
                                    )
                                )
                                
                                # Display results
                                if result.get("success"):
                                    st.success("All tasks completed successfully!")
                                    
                                    st.subheader("Results:")
                                    for i, task_result in enumerate(result.get("results", [])):
                                        with st.expander(f"Task {i+1} Result"):
                                            if task_result.get("success"):
                                                st.write(task_result.get("response", "No response"))
                                            else:
                                                st.error(task_result.get("error", "Unknown error"))
                                    
                                    with st.expander("Execution Summary"):
                                        st.json(result.get("metadata", {}))
                                else:
                                    st.error("Some tasks failed")
                                    st.write("Errors:", result.get("errors", []))
                                
                                # Clear tasks after execution
                                st.session_state.tasks = []
                                
                            except Exception as e:
                                st.error(f"Execution error: {str(e)}")
            
            if st.button("Clear All Tasks"):
                st.session_state.tasks = []
                st.rerun()
        else:
            st.info("No tasks added yet")


def show_configuration():
    """Show configuration interface."""
    st.header("⚙️ Configuration")
    
    if not st.session_state.framework:
        st.warning("Framework not initialized")
        return
    
    framework = st.session_state.framework
    
    # Tabs for different configurations
    tab1, tab2 = st.tabs(["Framework Settings", "Agent Templates"])
    
    with tab1:
        st.subheader("Framework Configuration")
        
        config = framework.framework_config
        
        with st.form("framework_config_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_timeout = st.number_input("Default Timeout", value=config.default_timeout, min_value=10, max_value=300)
                new_max_parallel = st.number_input("Max Parallel Agents", value=config.max_parallel_agents, min_value=1, max_value=20)
            
            with col2:
                new_log_level = st.selectbox("Log Level", ["DEBUG", "INFO", "WARNING", "ERROR"], index=["DEBUG", "INFO", "WARNING", "ERROR"].index(config.log_level))
            
            if st.form_submit_button("Update Framework Configuration"):
                config.default_timeout = new_timeout
                config.max_parallel_agents = new_max_parallel
                config.log_level = new_log_level
                
                framework.config_manager.save_framework_config(config)
                st.success("Framework configuration updated!")
    
    with tab2:
        st.subheader("Agent Templates")
        st.info("Agent templates allow you to quickly create agents with predefined configurations.")
        
        # Display current agent configs as templates
        agents_config = framework.config_manager.load_agents_config()
        
        if agents_config:
            for agent_name, config in agents_config.items():
                with st.expander(f"Template: {agent_name}"):
                    st.write(f"**Model Type:** {config.model_type}")
                    st.write(f"**Description:** {config.description}")
                    st.write(f"**Max Tokens:** {config.max_tokens}")
                    st.write(f"**Temperature:** {config.temperature}")
                    st.write(f"**Timeout:** {config.timeout}")


def show_health_check():
    """Show health check interface."""
    st.header("🏥 Health Check")
    
    if not st.session_state.framework:
        st.warning("Framework not initialized")
        return
    
    framework = st.session_state.framework
    
    if st.button("Run Health Check"):
        with st.spinner("Running health check..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                health_status = loop.run_until_complete(framework.health_check())
                
                st.subheader("Health Check Results")
                
                # Framework status
                framework_status = health_status.get("framework_status", "unknown")
                if framework_status == "healthy":
                    st.success("🟢 Framework Status: Healthy")
                else:
                    st.error(f"🔴 Framework Status: {framework_status}")
                    if "error" in health_status:
                        st.error(f"Error: {health_status['error']}")
                
                # Agent health
                st.subheader("Agent Health Status")
                agent_health = health_status.get("agent_health", {})
                
                if agent_health:
                    for agent_name, is_healthy in agent_health.items():
                        if is_healthy:
                            st.success(f"🟢 {agent_name}: Healthy")
                        else:
                            st.error(f"🔴 {agent_name}: Unhealthy")
                else:
                    st.info("No agents to check")
                
                # System info
                with st.expander("System Information"):
                    st.json(health_status)
                    
            except Exception as e:
                st.error(f"Health check failed: {str(e)}")
    
    # System status
    st.subheader("System Status")
    info = framework.get_framework_info()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Active Agents", len(info["agents"]))
        st.metric("Available Projects", len(info["available_projects"]))
    
    with col2:
        st.metric("Framework Version", info["version"])
        current_proj = info["current_project"] or "None"
        st.metric("Current Project", current_proj)


if __name__ == "__main__":
    main()