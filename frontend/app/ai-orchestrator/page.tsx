'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Bot, Play, Pause, Settings, TrendingUp, Zap, Target, Activity, Loader2, CheckCircle, XCircle } from 'lucide-react';

interface AIAgent {
  agent_id: string;
  name: string;
  category: string;
  description: string;
  status: 'active' | 'idle' | 'error' | 'busy';
  capabilities: string[];
  performance_score?: number;
  tasks_completed?: number;
  success_rate?: number;
}

interface AgentTask {
  task_id: string;
  agent_id: string;
  task_type: string;
  parameters: any;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result?: any;
  created_at: string;
  completed_at?: string;
}

interface AgentConfig {
  temperature?: number;
  max_tokens?: number;
  model?: string;
  priority?: 'low' | 'medium' | 'high' | 'critical';
  timeout?: number;
}

export default function AIOrchestrator() {
  const [agents, setAgents] = useState<AIAgent[]>([]);
  const [tasks, setTasks] = useState<AgentTask[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<AIAgent | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [taskInput, setTaskInput] = useState('');
  const [agentConfig, setAgentConfig] = useState<AgentConfig>({
    temperature: 0.7,
    max_tokens: 2000,
    model: 'gpt-4',
    priority: 'medium',
    timeout: 30,
  });
  const [stats, setStats] = useState({
    total_agents: 0,
    active_agents: 0,
    total_tasks: 0,
    success_rate: 0,
  });

  useEffect(() => {
    fetchAgents();
    fetchTasks();
    fetchStats();
    
    const agentsInterval = setInterval(fetchAgents, 5000);
    const tasksInterval = setInterval(fetchTasks, 3000);
    const statsInterval = setInterval(fetchStats, 10000);
    
    return () => {
      clearInterval(agentsInterval);
      clearInterval(tasksInterval);
      clearInterval(statsInterval);
    };
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await fetch('http://localhost:8000/ai-agents', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setAgents(data.agents || []);
      }
    } catch (error) {
      console.error('Error fetching agents:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTasks = async () => {
    try {
      const response = await fetch('http://localhost:8000/ai-agents/tasks', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setTasks(data.tasks || []);
      }
    } catch (error) {
      console.error('Error fetching tasks:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/ai-agents/stats', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data.stats || stats);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const runAgent = async (agentId: string, taskDescription: string) => {
    try {
      const response = await fetch(`http://localhost:8000/ai-agents/${agentId}/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          task: taskDescription,
          config: agentConfig,
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        await fetchTasks();
        setTaskInput('');
        return data;
      }
    } catch (error) {
      console.error('Error running agent:', error);
    }
  };

  const stopAgent = async (agentId: string) => {
    try {
      await fetch(`http://localhost:8000/ai-agents/${agentId}/stop`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      await fetchAgents();
    } catch (error) {
      console.error('Error stopping agent:', error);
    }
  };

  const categories = ['all', 'content', 'automation', 'analytics', 'social', 'optimization', 'monitoring'];

  const filteredAgents = selectedCategory === 'all' 
    ? agents 
    : agents.filter(a => a.category === selectedCategory);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-700';
      case 'idle': return 'bg-gray-100 text-gray-700';
      case 'busy': return 'bg-yellow-100 text-yellow-700';
      case 'error': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const getTaskStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'failed': return <XCircle className="h-5 w-5 text-red-600" />;
      case 'running': return <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />;
      default: return <Activity className="h-5 w-5 text-gray-600" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center">
        <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <div className="bg-white shadow-md border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/" className="text-gray-600 hover:text-blue-600 transition">
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <Bot className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">AI Orchestrator</h1>
                <p className="text-sm text-gray-500">53 AI Agents • Multi-task Automation • Real-time Intelligence</p>
              </div>
            </div>
            <button
              onClick={() => setShowConfigModal(true)}
              className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:shadow-lg transition"
            >
              <Settings className="h-5 w-5" />
              <span>Configure</span>
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-2">
              <Bot className="h-8 w-8 text-blue-600" />
              <span className="text-xs text-gray-500">Total</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{stats.total_agents}</div>
            <div className="text-sm text-gray-600">AI Agents</div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-2">
              <Activity className="h-8 w-8 text-green-600" />
              <span className="text-xs text-gray-500">Running</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{stats.active_agents}</div>
            <div className="text-sm text-gray-600">Active Agents</div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-2">
              <Target className="h-8 w-8 text-purple-600" />
              <span className="text-xs text-gray-500">Completed</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{stats.total_tasks}</div>
            <div className="text-sm text-gray-600">Tasks</div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-2">
              <TrendingUp className="h-8 w-8 text-amber-600" />
              <span className="text-xs text-gray-500">Performance</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{stats.success_rate}%</div>
            <div className="text-sm text-gray-600">Success Rate</div>
          </div>
        </div>

        {/* Category Filter */}
        <div className="flex space-x-2 mb-6 overflow-x-auto">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-4 py-2 rounded-lg font-semibold whitespace-nowrap transition ${
                selectedCategory === cat
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-50'
              }`}
            >
              {cat.charAt(0).toUpperCase() + cat.slice(1)}
            </button>
          ))}
        </div>

        {/* Agents Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {filteredAgents.map((agent) => (
                <div key={agent.agent_id} className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h3 className="text-lg font-bold text-gray-900">{agent.name}</h3>
                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(agent.status)}`}>
                          {agent.status}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-3">{agent.description}</p>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-semibold">
                          {agent.category}
                        </span>
                        {agent.performance_score && (
                          <span className="flex items-center">
                            <TrendingUp className="h-4 w-4 mr-1" />
                            {agent.performance_score}%
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Capabilities */}
                  <div className="mb-4">
                    <div className="text-xs font-semibold text-gray-500 mb-2">Capabilities:</div>
                    <div className="flex flex-wrap gap-1">
                      {agent.capabilities.slice(0, 3).map((cap, idx) => (
                        <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                          {cap}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="flex space-x-2 pt-4 border-t">
                    <button
                      onClick={() => setSelectedAgent(agent)}
                      className="flex-1 px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:shadow-lg transition"
                    >
                      <Play className="h-4 w-4 inline-block mr-2" />
                      Run Task
                    </button>
                    {agent.status === 'active' && (
                      <button
                        onClick={() => stopAgent(agent.agent_id)}
                        className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-500 transition"
                      >
                        <Pause className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Task Queue Sidebar */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
              <Activity className="h-5 w-5 mr-2 text-blue-600" />
              Active Tasks
            </h3>
            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              {tasks.slice(0, 10).map((task) => (
                <div key={task.task_id} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="text-sm font-semibold text-gray-900 mb-1">{task.task_type}</div>
                      <div className="text-xs text-gray-500">
                        Agent: {agents.find(a => a.agent_id === task.agent_id)?.name || 'Unknown'}
                      </div>
                    </div>
                    {getTaskStatusIcon(task.status)}
                  </div>
                  <div className="text-xs text-gray-600">
                    {new Date(task.created_at).toLocaleString()}
                  </div>
                  {task.result && (
                    <div className="mt-2 p-2 bg-white rounded text-xs text-gray-700">
                      {JSON.stringify(task.result).substring(0, 100)}...
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Run Task Modal */}
      {selectedAgent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-2xl p-8 max-w-2xl w-full mx-4">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Run {selectedAgent.name}</h2>
            
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Task Description</label>
                <textarea
                  value={taskInput}
                  onChange={(e) => setTaskInput(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={4}
                  placeholder={`Describe the task for ${selectedAgent.name}...`}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Model</label>
                  <select
                    value={agentConfig.model}
                    onChange={(e) => setAgentConfig({...agentConfig, model: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="gpt-4">GPT-4</option>
                    <option value="gpt-4-turbo">GPT-4 Turbo</option>
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                    <option value="claude-3">Claude 3</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Priority</label>
                  <select
                    value={agentConfig.priority}
                    onChange={(e) => setAgentConfig({...agentConfig, priority: e.target.value as any})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Temperature</label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="2"
                    value={agentConfig.temperature}
                    onChange={(e) => setAgentConfig({...agentConfig, temperature: parseFloat(e.target.value)})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Max Tokens</label>
                  <input
                    type="number"
                    value={agentConfig.max_tokens}
                    onChange={(e) => setAgentConfig({...agentConfig, max_tokens: parseInt(e.target.value)})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>
            
            <div className="flex space-x-4">
              <button
                onClick={() => setSelectedAgent(null)}
                className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  runAgent(selectedAgent.agent_id, taskInput);
                  setSelectedAgent(null);
                }}
                disabled={!taskInput.trim()}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:shadow-lg transition disabled:opacity-50"
              >
                <Play className="h-5 w-5 inline-block mr-2" />
                Run Agent
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
