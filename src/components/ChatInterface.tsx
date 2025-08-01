import React, { useState, useRef, useEffect } from 'react';
import { AgentInstance, TaskRequest, TaskResponse, AgentStatus } from '@/types';
import { Send, Loader2, X, Minimize2 } from 'lucide-react';
import { agentAPI } from '@/lib/api';

interface ChatInterfaceProps {
  agent: AgentInstance;
  onClose: () => void;
  onMinimize?: () => void;
  isMinimized?: boolean;
  isEmbedded?: boolean;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'agent';
  content: string;
  timestamp: Date;
  status?: AgentStatus;
  taskId?: string;
}

export default function ChatInterface({ 
  agent, 
  onClose, 
  onMinimize,
  isMinimized = false,
  isEmbedded = false 
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      role: 'agent',
      content: `Hello! I'm ${agent.name}. How can I help you today?`,
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const taskRequest: TaskRequest = {
        agent_id: agent.id,
        instruction: inputValue
      };

      const response: TaskResponse = await agentAPI.executeTask(taskRequest);

      const agentMessage: ChatMessage = {
        id: response.task_id,
        role: 'agent',
        content: response.result || response.error || 'No response received',
        timestamp: new Date(),
        status: response.status,
        taskId: response.task_id
      };

      setMessages(prev => [...prev, agentMessage]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'agent',
        content: `Error: ${error instanceof Error ? error.message : 'Unknown error occurred'}`,
        timestamp: new Date(),
        status: AgentStatus.ERROR
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (isMinimized) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <button
          onClick={onMinimize}
          className="bg-primary-600 text-white px-4 py-2 rounded-lg shadow-lg hover:bg-primary-700 transition-colors"
        >
          Chat with {agent.name}
        </button>
      </div>
    );
  }

  if (isEmbedded) {
    return (
      <div className="h-full flex flex-col">
        {/* Embedded Header */}
        <div className="flex items-center justify-between p-4 border-b border-secondary-200 bg-secondary-50">
          <div>
            <h3 className="font-semibold text-secondary-900">{agent.name}</h3>
            <p className="text-sm text-secondary-600">
              Status: <span className={`status-${agent.status} px-2 py-1 rounded-full text-xs`}>
                {agent.status}
              </span>
            </p>
          </div>
          
          <button
            onClick={onClose}
            className="p-2 text-secondary-500 hover:text-secondary-700 hover:bg-secondary-100 rounded-lg transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  message.role === 'user'
                    ? 'bg-primary-600 text-white'
                    : message.status === AgentStatus.ERROR
                    ? 'bg-red-50 text-red-800 border border-red-200'
                    : 'bg-secondary-100 text-secondary-800'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
                <p className={`text-xs mt-1 ${
                  message.role === 'user' ? 'text-primary-100' : 'text-secondary-500'
                }`}>
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-secondary-100 text-secondary-800 rounded-lg px-4 py-2 flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Thinking...</span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-secondary-200 p-4 bg-white">
          <div className="flex gap-2">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              className="flex-1 input-field resize-none"
              rows={2}
              disabled={isLoading}
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isLoading}
              className="btn-primary px-3 py-2 self-end"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl h-[600px] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-secondary-200">
          <div>
            <h3 className="font-semibold text-secondary-900">{agent.name}</h3>
            <p className="text-sm text-secondary-600">
              Status: <span className={`status-${agent.status} px-2 py-1 rounded-full text-xs`}>
                {agent.status}
              </span>
            </p>
          </div>
          
          <div className="flex items-center gap-2">
            {onMinimize && (
              <button
                onClick={onMinimize}
                className="p-2 text-secondary-500 hover:text-secondary-700 hover:bg-secondary-100 rounded-lg transition-colors"
              >
                <Minimize2 className="w-4 h-4" />
              </button>
            )}
            <button
              onClick={onClose}
              className="p-2 text-secondary-500 hover:text-secondary-700 hover:bg-secondary-100 rounded-lg transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  message.role === 'user'
                    ? 'bg-primary-600 text-white'
                    : message.status === AgentStatus.ERROR
                    ? 'bg-red-50 text-red-800 border border-red-200'
                    : 'bg-secondary-100 text-secondary-800'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
                <p className={`text-xs mt-1 ${
                  message.role === 'user' ? 'text-primary-100' : 'text-secondary-500'
                }`}>
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-secondary-100 text-secondary-800 rounded-lg px-4 py-2 flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Thinking...</span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-secondary-200 p-4">
          <div className="flex gap-2">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              className="flex-1 input-field resize-none"
              rows={2}
              disabled={isLoading}
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isLoading}
              className="btn-primary px-3 py-2 self-end"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}