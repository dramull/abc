# MultiAgent Framework

A robust, modular multiagent framework using Kimi K2 and Qwen3 APIs for parallel and serial agent execution.

## 🚀 Features

- **Multi-Model Support**: Seamlessly integrate Kimi K2 and Qwen3 APIs
- **Flexible Execution**: Run agents in parallel or serial mode
- **Modular Architecture**: Easy to add, configure, and manage agents
- **Project Management**: Organize agents into projects with custom configurations
- **User-Friendly UI**: Streamlit-based web interface for easy interaction
- **Configuration Management**: YAML-based configuration system
- **Health Monitoring**: Built-in health checks and status monitoring
- **Extensible Design**: Easy to add new agent types and capabilities

## 🏗️ Architecture

```
MultiAgent Framework
├── Core Framework
│   ├── Agent Base Classes
│   ├── Execution Engine
│   ├── Configuration Manager
│   └── Project Manager
├── API Integration Layer
│   ├── Kimi K2 API Client
│   └── Qwen3 API Client
├── Pre-built Agents
│   ├── Text Processing Agent (Kimi)
│   ├── Code Analysis Agent (Qwen)
│   └── Research Agent (Custom)
└── User Interface
    ├── Streamlit Web App
    └── CLI Tools
```

## 🎯 Agent Types

### 1. Text Processing Agent (Kimi K2)
- **Purpose**: General text analysis and processing
- **Capabilities**:
  - Text analysis and summarization
  - Language translation
  - Content writing and generation
  - Question answering
- **Ideal for**: Content creation, text analysis, general NLP tasks

### 2. Code Analysis Agent (Qwen3)
- **Purpose**: Code review and technical documentation
- **Capabilities**:
  - Code analysis and review
  - Documentation generation
  - Bug detection and debugging assistance
  - Architecture design suggestions
- **Ideal for**: Software development, code quality, technical writing

### 3. Research Agent (Custom)
- **Purpose**: Information gathering and synthesis
- **Capabilities**:
  - Research and information gathering
  - Data synthesis and analysis
  - Domain-specific expertise
  - Custom workflow execution
- **Ideal for**: Research tasks, data analysis, domain-specific applications

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Kimi K2 API key (optional for demo mode)
- Qwen3 API key (optional for demo mode)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd abc
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the framework**:
   ```bash
   python run.py init
   ```

4. **Configure API keys** (optional):
   Edit `config/agents_config.yaml` and add your API keys:
   ```yaml
   agents:
     text_processor:
       api_key: "your-kimi-api-key"
     code_analyzer:
       api_key: "your-qwen-api-key"
     research_agent:
       api_key: "your-api-key"
   ```

## 🚀 Quick Start

### Using the Web Interface

1. **Start the UI**:
   ```bash
   python run.py ui
   ```

2. **Open your browser** to `http://localhost:8501`

3. **Navigate through the interface**:
   - **Dashboard**: Overview of agents and system status
   - **Agent Management**: Add, configure, and manage agents
   - **Project Management**: Create and organize projects
   - **Execute Tasks**: Run single or multiple tasks
   - **Configuration**: Adjust framework settings
   - **Health Check**: Monitor system health

### Using the CLI

1. **Test the framework**:
   ```bash
   python run.py test --agent text_processor --text "Analyze this sample text"
   ```

2. **Check status**:
   ```bash
   python run.py status
   ```

3. **Add a new agent**:
   ```bash
   python run.py add-agent --name my_agent --model kimi --description "My custom agent"
   ```

4. **Create a project**:
   ```bash
   python run.py create-project --name my_project --description "My project" --agents text_processor,code_analyzer
   ```

## 📖 Usage Examples

### Single Task Execution

```python
import asyncio
from multiagent_framework import MultiAgentFramework

async def main():
    # Initialize framework
    framework = MultiAgentFramework()
    await framework.initialize()
    
    # Execute a single task
    result = await framework.execute_single(
        agent_name="text_processor",
        input_data="Summarize the benefits of artificial intelligence",
        task_type="summarization"
    )
    
    print("Result:", result["response"])
    await framework.shutdown()

asyncio.run(main())
```

### Multiple Tasks (Parallel)

```python
tasks = [
    {
        "agent_name": "text_processor",
        "input_data": "Analyze market trends in AI",
        "parameters": {"task_type": "analysis"}
    },
    {
        "agent_name": "code_analyzer", 
        "input_data": "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
        "parameters": {"task_type": "code_review"}
    },
    {
        "agent_name": "research_agent",
        "input_data": "Latest developments in machine learning",
        "parameters": {"task_type": "research", "domain": "technical"}
    }
]

result = await framework.execute_tasks(tasks, mode="parallel")
```

## 🔧 Configuration

### Framework Configuration (`config/framework_config.yaml`)

```yaml
version: "1.0.0"
default_timeout: 30
max_parallel_agents: 5
log_level: "INFO"

ui_config:
  title: "MultiAgent Framework"
  theme: "light"
  auto_refresh: true

api_config:
  rate_limiting:
    enabled: true
    requests_per_minute: 60
  retry_config:
    max_retries: 3
    backoff_factor: 2
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_framework.py -v
```

## 🚀 Deployment

### Local Development
```bash
python run.py ui --host localhost --port 8501
```

### Windows Environment
The framework is fully compatible with Windows and can be run locally with the Streamlit UI.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

**Note**: This framework runs in simulation mode when API keys are not provided, making it perfect for testing and development without requiring actual API access.