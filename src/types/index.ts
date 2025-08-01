export interface AgentProfile {
  id: string;
  name: string;
  type: AgentType;
  description: string;
  instructions: string;
  capabilities: string[];
  model_config: {
    temperature: number;
    max_tokens: number;
    model: string;
  };
  is_active: boolean;
  created_at?: string;
}

export interface AgentInstance {
  id: string;
  profile_id: string;
  name: string;
  status: AgentStatus;
  current_task?: string;
  progress: number;
  created_at: string;
  last_activity?: string;
}

export interface TaskRequest {
  agent_id: string;
  instruction: string;
  context?: string;
  parameters?: Record<string, any>;
}

export interface TaskResponse {
  task_id: string;
  agent_id: string;
  status: AgentStatus;
  result?: string;
  error?: string;
  progress: number;
}

export interface CreateAgentRequest {
  name: string;
  description: string;
  agent_type?: AgentType;
  instructions?: string;
}

export interface ProjectConfig {
  id: string;
  name: string;
  description: string;
  active_agents: string[];
  workflow_template?: string;
  created_at: string;
  updated_at: string;
}

export interface SystemStatus {
  kimi_configured: boolean;
  active_agents: number;
  available_profiles: number;
  status: string;
}

export enum AgentStatus {
  IDLE = "idle",
  RUNNING = "running",
  ERROR = "error",
  COMPLETED = "completed"
}

export enum AgentType {
  RESEARCH = "research",
  WRITING = "writing",
  CODE = "code",
  PLANNING = "planning",
  ANALYSIS = "analysis",
  CUSTOM = "custom"
}