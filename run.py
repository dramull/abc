#!/usr/bin/env python3
"""
Main entry point for the MultiAgent Framework.
"""

import sys
import os
import click
import asyncio
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from multiagent_framework.core.framework import MultiAgentFramework
from multiagent_framework.utils.helpers import setup_logging


@click.group()
@click.option('--config-dir', default='config', help='Configuration directory path')
@click.option('--log-level', default='INFO', help='Logging level')
@click.pass_context
def cli(ctx, config_dir, log_level):
    """MultiAgent Framework CLI."""
    ctx.ensure_object(dict)
    ctx.obj['config_dir'] = config_dir
    ctx.obj['log_level'] = log_level
    
    # Setup logging
    setup_logging(log_level)


@cli.command()
@click.option('--host', default='localhost', help='Host to bind to')
@click.option('--port', default=8501, help='Port to bind to')
@click.pass_context
def ui(ctx, host, port):
    """Launch the Streamlit UI."""
    import subprocess
    
    # Get the path to the Streamlit app
    app_path = Path(__file__).parent / "multiagent_framework" / "ui" / "streamlit_app.py"
    
    # Launch Streamlit
    cmd = [
        sys.executable, "-m", "streamlit", "run", str(app_path),
        "--server.address", host,
        "--server.port", str(port),
        "--browser.gatherUsageStats", "false"
    ]
    
    click.echo(f"Starting UI at http://{host}:{port}")
    subprocess.run(cmd)


@cli.command()
@click.pass_context
def init(ctx):
    """Initialize the framework and create default configuration."""
    config_dir = ctx.obj['config_dir']
    
    click.echo("Initializing MultiAgent Framework...")
    
    # Create configuration directory
    Path(config_dir).mkdir(exist_ok=True)
    
    # Initialize framework
    framework = MultiAgentFramework(config_dir)
    
    async def initialize():
        success = await framework.initialize()
        if success:
            click.echo("Framework initialized successfully!")
            click.echo(f"Configuration directory: {config_dir}")
            click.echo(f"Available agents: {', '.join(framework.get_agents())}")
        else:
            click.echo("Failed to initialize framework")
            return False
        
        await framework.shutdown()
        return True
    
    # Run initialization
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    success = loop.run_until_complete(initialize())
    
    if success:
        click.echo("\nNext steps:")
        click.echo("1. Add your API keys to config/agents_config.yaml")
        click.echo("2. Run 'python run.py ui' to start the web interface")
        click.echo("3. Or use 'python run.py test' to run a quick test")


@cli.command()
@click.option('--agent', default='text_processor', help='Agent to test')
@click.option('--text', default='Hello, this is a test message.', help='Test text')
@click.pass_context
def test(ctx, agent, text):
    """Test the framework with a simple task."""
    config_dir = ctx.obj['config_dir']
    
    click.echo(f"Testing agent '{agent}' with text: {text}")
    
    # Initialize framework
    framework = MultiAgentFramework(config_dir)
    
    async def run_test():
        success = await framework.initialize()
        if not success:
            click.echo("Failed to initialize framework")
            return
        
        # Execute test task
        result = await framework.execute_single(
            agent_name=agent,
            input_data=text,
            task_type="general"
        )
        
        if result.get("success"):
            click.echo("✅ Test successful!")
            click.echo(f"Response: {result.get('response', 'No response')}")
            click.echo(f"Execution time: {result.get('execution_time', 0):.2f}s")
        else:
            click.echo("❌ Test failed!")
            click.echo(f"Error: {result.get('error', 'Unknown error')}")
        
        await framework.shutdown()
    
    # Run test
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_test())


@cli.command()
@click.pass_context
def status(ctx):
    """Show framework status."""
    config_dir = ctx.obj['config_dir']
    
    # Initialize framework
    framework = MultiAgentFramework(config_dir)
    
    async def show_status():
        success = await framework.initialize()
        if not success:
            click.echo("Failed to initialize framework")
            return
        
        # Get framework info
        info = framework.get_framework_info()
        
        click.echo("📊 Framework Status")
        click.echo(f"Version: {info['version']}")
        click.echo(f"Total agents: {info['total_agents']}")
        click.echo(f"Active agents: {', '.join(info['agents']) if info['agents'] else 'None'}")
        click.echo(f"Available projects: {len(info['available_projects'])}")
        click.echo(f"Current project: {info['current_project'] or 'None'}")
        click.echo(f"Config directory: {info['config_dir']}")
        
        # Health check
        health = await framework.health_check()
        click.echo(f"\n🏥 Health Status: {health.get('framework_status', 'unknown').upper()}")
        
        if 'agent_health' in health:
            for agent_name, is_healthy in health['agent_health'].items():
                status_icon = "🟢" if is_healthy else "🔴"
                click.echo(f"  {status_icon} {agent_name}")
        
        await framework.shutdown()
    
    # Run status check
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(show_status())


@cli.command()
@click.option('--name', required=True, help='Agent name')
@click.option('--model', required=True, type=click.Choice(['kimi', 'qwen']), help='Model type')
@click.option('--description', default='', help='Agent description')
@click.option('--api-key', default='', help='API key')
@click.pass_context
def add_agent(ctx, name, model, description, api_key):
    """Add a new agent to the framework."""
    config_dir = ctx.obj['config_dir']
    
    from multiagent_framework.core.agent_base import AgentConfig
    
    # Create agent configuration
    config = AgentConfig(
        name=name,
        description=description,
        model_type=model,
        api_key=api_key,
        max_tokens=1000,
        temperature=0.7
    )
    
    # Initialize framework and add agent
    framework = MultiAgentFramework(config_dir)
    
    async def add_agent_async():
        await framework.initialize()
        
        if framework.add_agent(config):
            click.echo(f"✅ Agent '{name}' added successfully!")
        else:
            click.echo(f"❌ Failed to add agent '{name}'")
        
        await framework.shutdown()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(add_agent_async())


@cli.command()
@click.option('--name', required=True, help='Project name')
@click.option('--description', default='', help='Project description')
@click.option('--agents', help='Comma-separated list of agent names')
@click.pass_context
def create_project(ctx, name, description, agents):
    """Create a new project."""
    config_dir = ctx.obj['config_dir']
    
    agent_list = []
    if agents:
        agent_list = [a.strip() for a in agents.split(',')]
    
    # Initialize framework and create project
    framework = MultiAgentFramework(config_dir)
    
    async def create_project_async():
        await framework.initialize()
        
        if framework.create_project(name, description, agent_list):
            click.echo(f"✅ Project '{name}' created successfully!")
        else:
            click.echo(f"❌ Failed to create project '{name}'")
        
        await framework.shutdown()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(create_project_async())


if __name__ == "__main__":
    cli()