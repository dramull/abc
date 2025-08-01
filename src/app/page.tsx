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
  Users
} from 'lucide-react';

export default function Home() {
  const [profiles, setProfiles] = useState<AgentProfile[]>([]);
  const [instances, setInstances] = useState<AgentInstance[]>([]);
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeChat, setActiveChat] = useState<AgentInstance | null>(null);
  const [showCustomAgent, setShowCustomAgent] = useState(false);
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

  if (loading) {
    return (
      <div className="min-h-screen bg-secondary-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-secondary-600">Loading ABC Framework...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-secondary-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-secondary-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-secondary-900">ABC Framework</h1>
                <p className="text-xs text-secondary-600">Multi-Agent Intelligence</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              {status && (
                <div className="flex items-center gap-2">
                  {status.kimi_configured ? (
                    <div className="flex items-center gap-1 text-green-600">
                      <CheckCircle className="w-4 h-4" />
                      <span className="text-sm">Kimi K2 Ready</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-1 text-red-600">
                      <AlertCircle className="w-4 h-4" />
                      <span className="text-sm">Configure API Key</span>
                    </div>
                  )}
                </div>
              )}
              
              <button className="btn-secondary">
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Error Alert */}
      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <p className="text-red-800">{error}</p>
            <button 
              onClick={() => setError(null)}
              className="ml-auto text-red-600 hover:text-red-800"
            >
              ×
            </button>
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section with Base Agent */}
        {baseAgent && (
          <section className="mb-8">
            <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl text-white p-6 mb-6">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 bg-white bg-opacity-20 rounded-xl flex items-center justify-center">
                  <Sparkles className="w-8 h-8" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold mb-2">Welcome to ABC Framework</h2>
                  <p className="text-primary-100">
                    Your intelligent base agent is ready. Describe your project or choose from pre-built agent profiles.
                  </p>
                </div>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <AgentCard 
                agent={baseAgent}
                onChat={handleChatWithAgent}
                className="border-2 border-primary-200"
              />
              
              <div className="card">
                <h3 className="font-semibold text-secondary-900 mb-3 flex items-center gap-2">
                  <Zap className="w-5 h-5 text-primary-600" />
                  Quick Start
                </h3>
                <div className="space-y-2">
                  <button 
                    onClick={() => handleChatWithAgent(baseAgent.id)}
                    className="w-full btn-primary text-left"
                  >
                    💬 Chat with Base Agent
                  </button>
                  <button 
                    onClick={() => setShowCustomAgent(true)}
                    className="w-full btn-outline text-left"
                  >
                    ✨ Create Custom Agent
                  </button>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Available Agent Profiles */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold text-secondary-900 mb-4 flex items-center gap-2">
            <Users className="w-5 h-5" />
            Ready-to-Use Agent Profiles
          </h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {predefinedProfiles.map((profile) => (
              <AgentProfileCard
                key={profile.id}
                profile={profile}
                onSelect={handleCreateFromProfile}
                disabled={!status?.kimi_configured}
              />
            ))}
          </div>
        </section>

        {/* Active Agents */}
        {otherAgents.length > 0 && (
          <section>
            <h2 className="text-xl font-semibold text-secondary-900 mb-4 flex items-center gap-2">
              <Brain className="w-5 h-5" />
              Active Agents ({otherAgents.length})
            </h2>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {otherAgents.map((agent) => (
                <AgentCard
                  key={agent.id}
                  agent={agent}
                  onDelete={handleDeleteAgent}
                  onChat={handleChatWithAgent}
                />
              ))}
            </div>
          </section>
        )}
      </div>

      {/* Custom Agent Creation Modal */}
      {showCustomAgent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg m-4">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-secondary-900 mb-4">
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

      {/* Chat Interface */}
      {activeChat && (
        <ChatInterface
          agent={activeChat}
          onClose={() => setActiveChat(null)}
        />
      )}
    </div>
  );
}