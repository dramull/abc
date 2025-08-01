# ABC Multi-Agent Framework

A world-class multi-agent framework with optimized user experience, featuring intelligent agents powered by Kimi K2 API.

## ✨ Features

### 🎯 Optimized User Experience
- **One-Click Agent Deployment**: Choose from 5 predefined agent profiles
- **Intelligent Base Agent**: Always-available coordinator for project guidance
- **Simplified Agent Creation**: Describe what you need, let AI create the agent
- **Modern Web Interface**: Clean, responsive React/Next.js frontend
- **Real-time Chat Interface**: Interactive communication with all agents

### 🤖 Predefined Agent Profiles

1. **Research Agent** - Information gathering and comprehensive analysis
2. **Writing Agent** - Content creation and technical documentation  
3. **Code Agent** - Programming assistance and development support
4. **Planning Agent** - Project planning and task management
5. **Analysis Agent** - Data analysis and insights generation

### 🏗️ Architecture

- **Backend**: FastAPI with async support
- **Frontend**: Next.js 14 with TypeScript and Tailwind CSS
- **AI Integration**: Kimi K2 API with configurable model parameters
- **Agent Management**: Sophisticated orchestration and workflow coordination

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- Kimi K2 API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd abc
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies**
   ```bash
   npm install
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your Kimi K2 API key
   ```

### Running the Application

1. **Start the backend server**
   ```bash
   cd backend
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend (in a new terminal)**
   ```bash
   npm run dev
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📖 Usage Guide

### Getting Started

1. **Configure Your API Key**: Add your Kimi K2 API key to the `.env` file
2. **Access the Interface**: Open http://localhost:3000 in your browser
3. **Chat with Base Agent**: Click the base agent to get started with project guidance
4. **Deploy Agents**: Choose from predefined profiles or create custom agents
5. **Collaborate**: Use multiple agents in parallel or sequential workflows

### Agent Profiles

Each predefined agent comes with:
- Specialized instructions and capabilities
- Optimized model parameters (temperature, max tokens)
- One-click deployment
- Interactive chat interface

### Custom Agent Creation

1. Click "Create Custom Agent"
2. Provide a name and description
3. The Base Agent will generate specialized instructions
4. Deploy and start using immediately

### Project Workflows

The Base Agent can recommend optimal workflows:
- **Research → Analysis → Writing**: For content projects
- **Planning → Code → Testing**: For development projects
- **Research → Planning → Analysis**: For strategic initiatives

## 🔧 Configuration

### Environment Variables

```bash
# Kimi K2 API Configuration
KIMI_API_KEY=your_kimi_k2_api_key_here
KIMI_API_URL=https://api.moonshot.cn/v1

# Application Configuration
BACKEND_PORT=8000
FRONTEND_PORT=3000
ENVIRONMENT=development

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Model Configuration

Each agent profile includes configurable parameters:
- **Temperature**: Controls creativity vs consistency (0.2-0.7)
- **Max Tokens**: Maximum response length (typically 4000)
- **Model**: Kimi K2 model variant (moonshot-v1-8k)

## 🏗️ Development

### Project Structure

```
abc/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── agents/         # Agent definitions
│   │   ├── api/            # API routes
│   │   ├── models/         # Pydantic models
│   │   └── services/       # Business logic
│   └── main.py            # Application entry point
├── src/                    # Next.js frontend
│   ├── app/               # App router pages
│   ├── components/        # React components
│   ├── lib/              # Utilities and API client
│   └── types/            # TypeScript definitions
├── package.json          # Node.js dependencies
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

### API Endpoints

- `GET /api/agents/profiles` - List all agent profiles
- `GET /api/agents/instances` - List active agent instances
- `POST /api/agents/create-from-profile/{profile_id}` - Create agent from profile
- `POST /api/agents/create-custom` - Create custom agent
- `POST /api/agents/execute-task` - Execute task with agent
- `GET /api/agents/status` - System status

### Adding New Agent Profiles

1. Define the profile in `backend/app/agents/predefined.py`
2. Include specialized instructions and capabilities
3. Configure appropriate model parameters
4. Test through the API and frontend

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built with FastAPI, Next.js, and Tailwind CSS
- Powered by Kimi K2 AI technology
- Designed for maximum user experience and productivity