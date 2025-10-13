/**
 * AUTOMATION BUILDER
 * Visual workflow editor with drag-drop for 3,305 automation workflows
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright © 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import { useState, useEffect } from 'react';
import { useAutomationStore } from '@/lib/store/generated';
import { useAutomationWebSocket, useWebSocketStatus } from '@/lib/websocket';
import { 
  Zap, Play, Pause, Plus, Trash2, Copy, Settings, 
  Clock, CheckCircle2, AlertCircle, Activity, Grid, List 
} from 'lucide-react';

const NODE_TYPES = [
  { id: 'trigger', name: 'Triggers', icon: Zap, color: 'bg-yellow-500', items: [
    'Webhook', 'Schedule', 'File Upload', 'Email Received', 'Form Submitted'
  ]},
  { id: 'action', name: 'Actions', icon: Activity, color: 'bg-blue-500', items: [
    'Send Email', 'Create File', 'API Call', 'Database Query', 'Notification'
  ]},
  { id: 'condition', name: 'Conditions', icon: Grid, color: 'bg-purple-500', items: [
    'If/Else', 'Switch', 'Filter', 'Loop', 'Wait'
  ]},
];

const WORKFLOW_STATUS = {
  active: { label: 'Active', color: 'bg-green-500', textColor: 'text-green-700', bgColor: 'bg-green-100' },
  paused: { label: 'Paused', color: 'bg-yellow-500', textColor: 'text-yellow-700', bgColor: 'bg-yellow-100' },
  error: { label: 'Error', color: 'bg-red-500', textColor: 'text-red-700', bgColor: 'bg-red-100' },
  inactive: { label: 'Inactive', color: 'bg-gray-500', textColor: 'text-gray-700', bgColor: 'bg-gray-100' },
};

export default function AutomationPage() {
  const { items, loading, fetchItems } = useAutomationStore();
  const { workflows, getWorkflow } = useAutomationWebSocket();
  const { connected } = useWebSocketStatus();
  
  const [selectedWorkflow, setSelectedWorkflow] = useState<string | null>(null);
  const [view, setView] = useState<'grid' | 'list'>('grid');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  useEffect(() => {
    fetchItems();
  }, []);

  // Calculate stats
  const activeWorkflows = items.filter(w => w.status === 'active').length;
  const runningWorkflows = Array.from(workflows.values()).filter(w => w.status === 'running').length;
  const totalExecutions = items.reduce((sum, w) => sum + (w.executions || 0), 0);

  const filteredWorkflows = items.filter(w => 
    filterStatus === 'all' || w.status === filterStatus
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Top Bar */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Automation Builder</h1>
                <p className="text-sm text-gray-600">3,305 workflows ready to automate your tasks</p>
              </div>
            </div>
            
            <button className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg font-medium hover:shadow-lg transition flex items-center gap-2">
              <Plus className="w-5 h-5" />
              New Workflow
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-500">Total Workflows</span>
              <Zap className="w-5 h-5 text-purple-500" />
            </div>
            <p className="text-3xl font-bold text-gray-900">{items.length.toLocaleString()}</p>
            <p className="text-xs text-gray-500 mt-1">of 3,305 available</p>
          </div>
          
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-500">Active</span>
              <CheckCircle2 className="w-5 h-5 text-green-500" />
            </div>
            <p className="text-3xl font-bold text-green-600">{activeWorkflows}</p>
            <p className="text-xs text-gray-500 mt-1">workflows running</p>
          </div>
          
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-500">Executing Now</span>
              <Activity className="w-5 h-5 text-blue-500" />
            </div>
            <p className="text-3xl font-bold text-blue-600">{runningWorkflows}</p>
            <p className="text-xs text-gray-500 mt-1">in progress</p>
          </div>
          
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-500">Total Executions</span>
              <Clock className="w-5 h-5 text-orange-500" />
            </div>
            <p className="text-3xl font-bold text-orange-600">{totalExecutions.toLocaleString()}</p>
            <p className="text-xs text-gray-500 mt-1">all time</p>
          </div>
        </div>

        {/* Connection Status */}
        <div className="bg-white rounded-xl shadow-sm p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`w-3 h-3 rounded-full ${connected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
              <span className="text-sm font-medium text-gray-700">
                {connected ? 'Real-time monitoring active' : 'Reconnecting...'}
              </span>
              {runningWorkflows > 0 && (
                <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
                  {runningWorkflows} workflows executing
                </span>
              )}
            </div>
            
            <div className="flex items-center gap-2">
              <button
                onClick={() => setView('grid')}
                className={`p-2 rounded-lg transition ${view === 'grid' ? 'bg-gray-200' : 'hover:bg-gray-100'}`}
              >
                <Grid className="w-5 h-5 text-gray-600" />
              </button>
              <button
                onClick={() => setView('list')}
                className={`p-2 rounded-lg transition ${view === 'list' ? 'bg-gray-200' : 'hover:bg-gray-100'}`}
              >
                <List className="w-5 h-5 text-gray-600" />
              </button>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-sm p-4 mb-6">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-700">Status:</span>
            {['all', 'active', 'paused', 'inactive', 'error'].map((status) => (
              <button
                key={status}
                onClick={() => setFilterStatus(status)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                  filterStatus === status
                    ? 'bg-purple-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {status === 'all' ? 'All' : WORKFLOW_STATUS[status as keyof typeof WORKFLOW_STATUS]?.label}
              </button>
            ))}
          </div>
        </div>

        {/* Workflows Grid/List */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
          </div>
        ) : filteredWorkflows.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <Zap className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-gray-900 mb-2">No workflows found</h3>
            <p className="text-gray-600 mb-6">Create your first workflow to automate tasks</p>
            <button className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg font-medium">
              Create Workflow
            </button>
          </div>
        ) : view === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredWorkflows.slice(0, 12).map((workflow) => {
              const statusInfo = WORKFLOW_STATUS[workflow.status as keyof typeof WORKFLOW_STATUS] || WORKFLOW_STATUS.inactive;
              const workflowState = getWorkflow(workflow.id);
              
              return (
                <div
                  key={workflow.id}
                  className="bg-white rounded-xl shadow-sm hover:shadow-xl transition-all duration-300 overflow-hidden group cursor-pointer"
                  onClick={() => setSelectedWorkflow(workflow.id)}
                >
                  <div className="p-6">
                    {/* Header */}
                    <div className="flex items-center justify-between mb-4">
                      <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                        <Zap className="w-6 h-6 text-white" />
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusInfo.bgColor} ${statusInfo.textColor}`}>
                        {statusInfo.label}
                      </span>
                    </div>

                    {/* Content */}
                    <h3 className="text-lg font-bold text-gray-900 mb-2 group-hover:text-purple-600 transition">
                      {workflow.name || 'Untitled Workflow'}
                    </h3>
                    <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                      {workflow.description || 'No description available'}
                    </p>

                    {/* Stats */}
                    <div className="flex items-center justify-between text-xs text-gray-500 mb-4">
                      <div className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        <span>{workflow.executions || 0} runs</span>
                      </div>
                      <span>ID: {workflow.id.slice(0, 8)}</span>
                    </div>

                    {/* Progress (if running) */}
                    {workflowState?.status === 'running' && (
                      <div className="mb-4">
                        <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                          <span>Executing...</span>
                          <span>{workflowState.progress || 0}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-1.5">
                          <div
                            className="bg-gradient-to-r from-purple-500 to-pink-500 h-1.5 rounded-full transition-all duration-500"
                            style={{ width: `${workflowState.progress || 0}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Actions Footer */}
                  <div className="bg-gray-50 px-6 py-3 flex items-center justify-between border-t border-gray-100">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={(e) => { e.stopPropagation(); }}
                        className="p-2 hover:bg-white rounded-lg transition"
                        title={workflow.status === 'active' ? 'Pause' : 'Play'}
                      >
                        {workflow.status === 'active' ? (
                          <Pause className="w-4 h-4 text-gray-600" />
                        ) : (
                          <Play className="w-4 h-4 text-gray-600" />
                        )}
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); }}
                        className="p-2 hover:bg-white rounded-lg transition"
                        title="Duplicate"
                      >
                        <Copy className="w-4 h-4 text-gray-600" />
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); }}
                        className="p-2 hover:bg-white rounded-lg transition"
                        title="Settings"
                      >
                        <Settings className="w-4 h-4 text-gray-600" />
                      </button>
                    </div>
                    <button
                      onClick={(e) => { e.stopPropagation(); }}
                      className="p-2 hover:bg-red-50 rounded-lg transition"
                      title="Delete"
                    >
                      <Trash2 className="w-4 h-4 text-red-600" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Executions</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Run</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredWorkflows.slice(0, 20).map((workflow) => {
                  const statusInfo = WORKFLOW_STATUS[workflow.status as keyof typeof WORKFLOW_STATUS] || WORKFLOW_STATUS.inactive;
                  
                  return (
                    <tr key={workflow.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                            <Zap className="w-4 h-4 text-white" />
                          </div>
                          <div>
                            <p className="font-medium text-gray-900">{workflow.name || 'Untitled'}</p>
                            <p className="text-xs text-gray-500">ID: {workflow.id.slice(0, 8)}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusInfo.bgColor} ${statusInfo.textColor}`}>
                          {statusInfo.label}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">{workflow.executions || 0}</td>
                      <td className="px-6 py-4 text-sm text-gray-600">{workflow.last_run || 'Never'}</td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button className="p-2 hover:bg-gray-100 rounded-lg transition">
                            {workflow.status === 'active' ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                          </button>
                          <button className="p-2 hover:bg-gray-100 rounded-lg transition">
                            <Settings className="w-4 h-4" />
                          </button>
                          <button className="p-2 hover:bg-red-50 rounded-lg transition">
                            <Trash2 className="w-4 h-4 text-red-600" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
