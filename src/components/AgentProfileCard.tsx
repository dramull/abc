import React from 'react';
import { AgentProfile, AgentType } from '@/types';
import { 
  Search, 
  PenTool, 
  Code, 
  Target, 
  BarChart3,
  Sparkles,
  Plus
} from 'lucide-react';

interface AgentProfileCardProps {
  profile: AgentProfile;
  onSelect: (profileId: string) => void;
  className?: string;
  disabled?: boolean;
}

const typeIcons = {
  [AgentType.RESEARCH]: Search,
  [AgentType.WRITING]: PenTool,
  [AgentType.CODE]: Code,
  [AgentType.PLANNING]: Target,
  [AgentType.ANALYSIS]: BarChart3,
  [AgentType.CUSTOM]: Sparkles
};

const typeColors = {
  [AgentType.RESEARCH]: 'text-blue-600 bg-blue-100',
  [AgentType.WRITING]: 'text-purple-600 bg-purple-100',
  [AgentType.CODE]: 'text-green-600 bg-green-100',
  [AgentType.PLANNING]: 'text-orange-600 bg-orange-100',
  [AgentType.ANALYSIS]: 'text-indigo-600 bg-indigo-100',
  [AgentType.CUSTOM]: 'text-pink-600 bg-pink-100'
};

export default function AgentProfileCard({ 
  profile, 
  onSelect, 
  className = "",
  disabled = false 
}: AgentProfileCardProps) {
  const TypeIcon = typeIcons[profile.type];
  const typeColorClass = typeColors[profile.type];

  const handleSelect = () => {
    if (!disabled) {
      onSelect(profile.id);
    }
  };

  return (
    <div 
      className={`agent-card ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:shadow-lg'} ${className}`}
      onClick={handleSelect}
    >
      <div className="flex items-start gap-4 mb-4">
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${typeColorClass}`}>
          <TypeIcon className="w-6 h-6" />
        </div>
        
        <div className="flex-1">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-secondary-900">{profile.name}</h3>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${typeColorClass}`}>
              {profile.type}
            </span>
          </div>
          
          <p className="text-sm text-secondary-600 mb-3 leading-relaxed">
            {profile.description}
          </p>
        </div>
      </div>

      <div className="mb-4">
        <h4 className="text-sm font-medium text-secondary-800 mb-2">Capabilities:</h4>
        <div className="flex flex-wrap gap-2">
          {profile.capabilities.slice(0, 4).map((capability, index) => (
            <span 
              key={index}
              className="px-2 py-1 bg-secondary-100 text-secondary-700 rounded-md text-xs"
            >
              {capability}
            </span>
          ))}
          {profile.capabilities.length > 4 && (
            <span className="px-2 py-1 bg-secondary-100 text-secondary-700 rounded-md text-xs">
              +{profile.capabilities.length - 4} more
            </span>
          )}
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs text-secondary-500">
          <span>Model: {profile.model_config?.model || 'N/A'}</span>
          <span>•</span>
          <span>Temp: {profile.model_config?.temperature || 'N/A'}</span>
        </div>
        
        <button
          onClick={handleSelect}
          disabled={disabled}
          className="flex items-center gap-2 btn-primary text-sm px-3 py-1.5"
        >
          <Plus className="w-3 h-3" />
          Add Agent
        </button>
      </div>
    </div>
  );
}