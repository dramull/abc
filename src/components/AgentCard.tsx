import React from 'react';
import { AgentInstance, AgentStatus } from '@/types';
import { 
  Brain, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  Trash2,
  Play,
  MessageSquare
} from 'lucide-react';

interface AgentCardProps {
  agent: AgentInstance;
  onDelete?: (agentId: string) => void;
  onChat?: (agentId: string) => void;
  className?: string;
}

const statusConfig = {
  [AgentStatus.IDLE]: {
    icon: Clock,
    label: 'Idle',
    className: 'status-idle'
  },
  [AgentStatus.RUNNING]: {
    icon: Play,
    label: 'Running',
    className: 'status-running'
  },
  [AgentStatus.COMPLETED]: {
    icon: CheckCircle,
    label: 'Completed',
    className: 'status-completed'
  },
  [AgentStatus.ERROR]: {
    icon: AlertCircle,
    label: 'Error',
    className: 'status-error'
  }
};

export default function AgentCard({ 
  agent, 
  onDelete, 
  onChat,
  className = "" 
}: AgentCardProps) {
  const statusInfo = statusConfig[agent.status];
  const StatusIcon = statusInfo.icon;

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (agent.id !== 'base_agent_instance' && onDelete) {
      onDelete(agent.id);
    }
  };

  const handleChat = () => {
    if (onChat) {
      onChat(agent.id);
    }
  };

  return (
    <div className={`agent-card ${className}`} onClick={handleChat}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
            <Brain className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <h3 className="font-semibold text-secondary-900">{agent.name}</h3>
            <div className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${statusInfo.className}`}>
              <StatusIcon className="w-3 h-3" />
              {statusInfo.label}
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={handleChat}
            className="p-2 text-secondary-500 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
            title="Chat with agent"
          >
            <MessageSquare className="w-4 h-4" />
          </button>
          
          {agent.id !== 'base_agent_instance' && onDelete && (
            <button
              onClick={handleDelete}
              className="p-2 text-secondary-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              title="Delete agent"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {agent.current_task && (
        <div className="mb-3">
          <p className="text-sm text-secondary-600 mb-1">Current Task:</p>
          <p className="text-sm text-secondary-800 bg-secondary-50 rounded-md p-2">
            {agent.current_task}
          </p>
        </div>
      )}

      {agent.status === AgentStatus.RUNNING && (
        <div className="mb-3">
          <div className="flex justify-between text-sm text-secondary-600 mb-1">
            <span>Progress</span>
            <span>{Math.round(agent.progress * 100)}%</span>
          </div>
          <div className="w-full bg-secondary-200 rounded-full h-2">
            <div 
              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${agent.progress * 100}%` }}
            />
          </div>
        </div>
      )}

      <div className="text-xs text-secondary-500">
        Created: {new Date(agent.created_at).toLocaleDateString()}
        {agent.last_activity && (
          <span className="ml-2">
            Last active: {new Date(agent.last_activity).toLocaleString()}
          </span>
        )}
      </div>
    </div>
  );
}