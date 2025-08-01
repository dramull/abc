'use client';

import React, { useState, useEffect } from 'react';
import { 
  AgentProfile, 
  AgentInstance, 
  SystemStatus,
  CreateAgentRequest,
  AgentType 
} from '@/types';
import { agentAPI } from '@/lib/api';
import AgentCard from '@/components/AgentCard';
import AgentProfileCard from '@/components/AgentProfileCard';
import ChatInterface from '@/components/ChatInterface';
import { 
  Brain, 
  Plus, 
  Settings, 
  AlertCircle, 
  CheckCircle,
  Sparkles,
  Zap,
  Users,
  MessageSquare,
  Layout,
  Star,
  ArrowRight,
  Lightbulb,
  Rocket
} from 'lucide-react';

export default function Home() {
  const [profiles, setProfiles] = useState<AgentProfile[]>([]);
  const [instances, setInstances] = useState<AgentInstance[]>([]);
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeChat, setActiveChat] = useState<AgentInstance | null>(null);
  const [showCustomAgent, setShowCustomAgent] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [customAgentForm, setCustomAgentForm] = useState<CreateAgentRequest>({
    name: '',
    description: '',
    agent_type: AgentType.CUSTOM
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [profilesData, instancesData, statusData] = await Promise.all([
        agentAPI.getProfiles(),
        agentAPI.getInstances(),
        agentAPI.getStatus()
      ]);
      
      setProfiles(profilesData);
      setInstances(instancesData);
      setStatus(statusData);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateFromProfile = async (profileId: string) => {
    try {
      const newInstance = await agentAPI.createFromProfile(profileId);
      setInstances(prev => [...prev, newInstance]);
      
      // Automatically open chat with new agent
      setActiveChat(newInstance);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create agent');
    }
  };

  const handleCreateCustomAgent = async () => {
    if (!customAgentForm.name.trim() || !customAgentForm.description.trim()) {
      setError('Name and description are required');
      return;
    }

    try {
      const newInstance = await agentAPI.createCustom(customAgentForm);
      setInstances(prev => [...prev, newInstance]);
      setShowCustomAgent(false);
      setCustomAgentForm({
        name: '',
        description: '',
        agent_type: AgentType.CUSTOM
      });
      
      // Automatically open chat with new agent
      setActiveChat(newInstance);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create custom agent');
    }
  };

  const handleDeleteAgent = async (agentId: string) => {
    try {
      await agentAPI.deleteAgent(agentId);
      setInstances(prev => prev.filter(agent => agent.id !== agentId));
      
      // Close chat if the deleted agent was active
      if (activeChat?.id === agentId) {
        setActiveChat(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete agent');
    }
  };

  const handleChatWithAgent = (agentId: string) => {
    const agent = instances.find(a => a.id === agentId);
    if (agent) {
      setActiveChat(agent);
    }
  };

  const predefinedProfiles = profiles.filter(p => p.type !== AgentType.CUSTOM && p.id !== 'base_agent');
  const baseAgent = instances.find(a => a.id === 'base_agent_instance');
  const otherAgents = instances.filter(a => a.id !== 'base_agent_instance');

  return (
    <div className="flex h-screen bg-secondary-50 overflow-hidden">
      {/* Sidebar - Agent Library */}
      <div className={`${sidebarCollapsed ? 'w-16' : 'w-80'} transition-all duration-300 bg-white border-r border-secondary-200 flex flex-col`}>
        {/* Sidebar Header */}
        <div className="p-4 border-b border-secondary-200">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            {!sidebarCollapsed && (
              <div>
                <h1 className="text-lg font-bold text-secondary-900">ABC Framework</h1>
                <p className="text-xs text-secondary-600">Multi-Agent Intelligence</p>
              </div>
            )}
            <button
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="ml-auto p-1 hover:bg-secondary-100 rounded"
            >
              <Layout className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="p-4 border-b border-secondary-200">
          {!sidebarCollapsed && (
            <div className="space-y-2">
              <button
                onClick={() => {
                  const baseAgent = instances.find(a => a.id === 'base_agent_instance');
                  if (baseAgent) setActiveChat(baseAgent);
                }}
                className="w-full btn-primary text-left flex items-center gap-2"
              >
                <Rocket className="w-4 h-4" />
                Start with Base Agent
              </button>
              <button
                onClick={() => setShowCustomAgent(true)}
                className="w-full btn-outline text-left flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                Create Custom Agent
              </button>
            </div>
          )}
        </div>

        {/* Agent Profiles */}
        <div className="flex-1 overflow-y-auto p-4">
          {!sidebarCollapsed && (
            <>
              <h3 className="text-sm font-semibold text-secondary-900 mb-3 flex items-center gap-2">
                <Star className="w-4 h-4" />
                Agent Profiles
              </h3>
              <div className="space-y-3">
                {profiles.filter(p => p.type !== AgentType.CUSTOM && p.id !== 'base_agent').map((profile) => (
                  <div
                    key={profile.id}
                    className="sidebar-agent-card"
                    onClick={() => handleCreateFromProfile(profile.id)}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                        profile.type === 'research' ? 'bg-blue-100 text-blue-600' :
                        profile.type === 'writing' ? 'bg-purple-100 text-purple-600' :
                        profile.type === 'code' ? 'bg-green-100 text-green-600' :
                        profile.type === 'planning' ? 'bg-orange-100 text-orange-600' :
                        'bg-indigo-100 text-indigo-600'
                      }`}>
                        {profile.type === 'research' && <Lightbulb className="w-4 h-4" />}
                        {profile.type === 'writing' && <Zap className="w-4 h-4" />}
                        {profile.type === 'code' && <Brain className="w-4 h-4" />}
                        {profile.type === 'planning' && <ArrowRight className="w-4 h-4" />}
                        {profile.type === 'analysis' && <Users className="w-4 h-4" />}
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-secondary-900">{profile.name}</h4>
                        <p className="text-xs text-secondary-600 truncate">{profile.description}</p>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-secondary-500">Click to deploy</span>
                      <Plus className="w-3 h-3 text-secondary-400" />
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>

        {/* Status */}
        <div className="p-4 border-t border-secondary-200">
          {status && !sidebarCollapsed && (
            <div className="flex items-center gap-2 text-sm">
              {status.kimi_configured ? (
                <div className="flex items-center gap-1 text-green-600">
                  <CheckCircle className="w-4 h-4" />
                  <span>API Ready</span>
                </div>
              ) : (
                <div className="flex items-center gap-1 text-red-600">
                  <AlertCircle className="w-4 h-4" />
                  <span>Setup needed</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Action Bar */}
        <div className="bg-white border-b border-secondary-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-secondary-900">
                {activeChat ? `Chatting with ${activeChat.name}` : 'Choose Your Starting Point'}
              </h2>
              <p className="text-sm text-secondary-600">
                {activeChat ? 'Ask questions or give instructions to your agent' : 'Start with the Base Agent for guidance, or deploy a specialized agent'}
              </p>
            </div>
            <div className="flex items-center gap-3">
              {instances.filter(a => a.id !== 'base_agent_instance').length > 0 && (
                <div className="flex items-center gap-2">
                  <Users className="w-4 h-4 text-secondary-500" />
                  <span className="text-sm text-secondary-600">
                    {instances.filter(a => a.id !== 'base_agent_instance').length} active agents
                  </span>
                </div>
              )}
              <button className="btn-secondary flex items-center gap-2">
                <Settings className="w-4 h-4" />
                Settings
              </button>
            </div>
          </div>
        </div>

        {/* Welcome Hero Section (when no active chat) */}
        {!activeChat && (
          <div className="flex-1 flex items-center justify-center p-8">
            <div className="max-w-2xl text-center">
              <div className="w-20 h-20 bg-gradient-to-r from-primary-600 to-primary-700 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Sparkles className="w-10 h-10 text-white" />
              </div>
              <h1 className="text-3xl font-bold text-secondary-900 mb-4">
                Welcome to ABC Framework
              </h1>
              <p className="text-lg text-secondary-600 mb-8 leading-relaxed">
                Your intelligent multi-agent workspace. Start with the Base Agent for project guidance, 
                or jump directly to specialized agents for focused tasks.
              </p>
              
              <div className="grid md:grid-cols-2 gap-4 mb-8">
                <button
                  onClick={() => {
                    const baseAgent = instances.find(a => a.id === 'base_agent_instance');
                    if (baseAgent) setActiveChat(baseAgent);
                  }}
                  className="hero-action-card p-6 bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl text-white hover:from-primary-700 hover:to-primary-800"
                >
                  <MessageSquare className="w-8 h-8 mx-auto mb-3" />
                  <h3 className="font-semibold mb-2">Chat with Base Agent</h3>
                  <p className="text-sm text-primary-100">Get project guidance and workflow recommendations</p>
                </button>
                
                <button
                  onClick={() => setShowCustomAgent(true)}
                  className="hero-action-card p-6 bg-white border-2 border-primary-200 rounded-xl hover:border-primary-400"
                >
                  <Plus className="w-8 h-8 mx-auto mb-3 text-primary-600" />
                  <h3 className="font-semibold mb-2 text-secondary-900">Create Custom Agent</h3>
                  <p className="text-sm text-secondary-600">Describe your needs and get a specialized agent</p>
                </button>
              </div>

              {/* Quick Deploy Agents */}
              <div className="text-left">
                <h3 className="text-lg font-semibold text-secondary-900 mb-2">Quick Deploy Agents</h3>
                <p className="text-sm text-secondary-600 mb-4">One-click deployment for common workflows</p>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                  {profiles.filter(p => p.type !== AgentType.CUSTOM && p.id !== 'base_agent').map((profile) => (
                    <button
                      key={profile.id}
                      onClick={() => handleCreateFromProfile(profile.id)}
                      disabled={!status?.kimi_configured}
                      className="quick-deploy-card p-3 bg-white rounded-lg border border-secondary-200 hover:border-primary-300 hover:shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <div className={`w-10 h-10 rounded-lg mx-auto mb-2 flex items-center justify-center ${
                        profile.type === 'research' ? 'bg-blue-100 text-blue-600' :
                        profile.type === 'writing' ? 'bg-purple-100 text-purple-600' :
                        profile.type === 'code' ? 'bg-green-100 text-green-600' :
                        profile.type === 'planning' ? 'bg-orange-100 text-orange-600' :
                        'bg-indigo-100 text-indigo-600'
                      }`}>
                        {profile.type === 'research' && <Lightbulb className="w-5 h-5" />}
                        {profile.type === 'writing' && <Zap className="w-5 h-5" />}
                        {profile.type === 'code' && <Brain className="w-5 h-5" />}
                        {profile.type === 'planning' && <ArrowRight className="w-5 h-5" />}
                        {profile.type === 'analysis' && <Users className="w-5 h-5" />}
                      </div>
                      <div className="text-xs font-medium text-secondary-900">{profile.name}</div>
                    </button>
                  ))}
                </div>
                
                {/* Workflow Suggestions */}
                <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <h4 className="text-sm font-semibold text-blue-900 mb-2 flex items-center gap-2">
                    <Lightbulb className="w-4 h-4" />
                    Suggested Workflows
                  </h4>
                  <div className="text-xs text-blue-800 space-y-1">
                    <p><strong>Content Creation:</strong> Research → Writing → Analysis</p>
                    <p><strong>Development:</strong> Planning → Code → Analysis</p>
                    <p><strong>Strategy:</strong> Research → Planning → Analysis</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Active Agents Bar (when chat is active) */}
        {activeChat && instances.filter(a => a.id !== 'base_agent_instance').length > 0 && (
          <div className="bg-secondary-50 border-b border-secondary-200 p-3">
            <div className="flex items-center gap-3 overflow-x-auto">
              <span className="text-sm font-medium text-secondary-700 whitespace-nowrap">Active Agents:</span>
              {instances.filter(a => a.id !== 'base_agent_instance').map((agent) => (
                <button
                  key={agent.id}
                  onClick={() => setActiveChat(agent)}
                  className={`active-agent-tab flex items-center gap-2 px-3 py-2 rounded-lg text-sm whitespace-nowrap ${
                    activeChat?.id === agent.id 
                      ? 'bg-primary-600 text-white shadow-md' 
                      : 'bg-white text-secondary-700 hover:bg-secondary-100'
                  }`}
                >
                  <MessageSquare className="w-3 h-3" />
                  {agent.name}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Chat Area */}
        {activeChat && (
          <div className="flex-1 bg-white">
            <ChatInterface
              agent={activeChat}
              onClose={() => setActiveChat(null)}
              isEmbedded={true}
            />
          </div>
        )}
      </div>

      {/* Error Toast */}
      {error && (
        <div className="fixed top-4 right-4 z-50 bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3 shadow-lg">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <p className="text-red-800">{error}</p>
          <button 
            onClick={() => setError(null)}
            className="ml-auto text-red-600 hover:text-red-800"
          >
            ×
          </button>
        </div>
      )}

      {/* Custom Agent Creation Modal */}
      {showCustomAgent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg m-4">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-secondary-900 mb-4 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-primary-600" />
                Create Custom Agent
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">
                    Agent Name
                  </label>
                  <input
                    type="text"
                    value={customAgentForm.name}
                    onChange={(e) => setCustomAgentForm(prev => ({ ...prev, name: e.target.value }))}
                    className="input-field"
                    placeholder="e.g., Marketing Assistant"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">
                    Description & Purpose
                  </label>
                  <textarea
                    value={customAgentForm.description}
                    onChange={(e) => setCustomAgentForm(prev => ({ ...prev, description: e.target.value }))}
                    className="input-field"
                    rows={4}
                    placeholder="Describe what this agent should do and how it should behave..."
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">
                    Agent Type
                  </label>
                  <select
                    value={customAgentForm.agent_type}
                    onChange={(e) => setCustomAgentForm(prev => ({ ...prev, agent_type: e.target.value as AgentType }))}
                    className="input-field"
                  >
                    <option value={AgentType.CUSTOM}>Custom</option>
                    <option value={AgentType.RESEARCH}>Research</option>
                    <option value={AgentType.WRITING}>Writing</option>
                    <option value={AgentType.CODE}>Code</option>
                    <option value={AgentType.PLANNING}>Planning</option>
                    <option value={AgentType.ANALYSIS}>Analysis</option>
                  </select>
                </div>
              </div>
              
              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => setShowCustomAgent(false)}
                  className="btn-secondary flex-1"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateCustomAgent}
                  className="btn-primary flex-1"
                  disabled={!customAgentForm.name.trim() || !customAgentForm.description.trim()}
                >
                  Create Agent
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Loading Overlay */}
      {loading && (
        <div className="fixed inset-0 bg-white bg-opacity-90 flex items-center justify-center z-50">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
            <p className="text-secondary-600">Loading ABC Framework...</p>
          </div>
        </div>
      )}
    </div>
  );
}