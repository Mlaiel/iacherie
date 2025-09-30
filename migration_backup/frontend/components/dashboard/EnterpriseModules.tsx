// Enterprise Dashboard Components - Multi-Expert Implementation
import React from 'react';
import {
  CpuChipIcon,
  MusicalNoteIcon, 
  ChartBarIcon,
  ShieldCheckIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  BoltIcon
} from '@heroicons/react/24/outline';

// AI Services Dashboard Component - Lead IA + ML Engineer Implementation
export function AIServicesDashboard({ aiServices }: any) {
  if (aiServices.loading) {
    return (
      <div className="animate-pulse">
        <div className="h-8 bg-gray-200 rounded mb-4"></div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
          <CpuChipIcon className="h-8 w-8 text-purple-600" />
          AI Services Dashboard
        </h2>
        <div className="flex gap-2">
          <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
            53 AI Agents Active
          </span>
          <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
            18 Services Running
          </span>
        </div>
      </div>

      {/* AI Metrics Overview */}
      {aiServices.metrics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Inferences</p>
                <p className="text-2xl font-bold text-gray-900">
                  {aiServices.metrics.totalInferences.toLocaleString()}
                </p>
              </div>
              <BoltIcon className="h-12 w-12 text-yellow-500" />
            </div>
            <div className="mt-4">
              <div className="flex items-center text-sm text-green-600">
                <span>Success Rate: {(aiServices.metrics.successRate * 100).toFixed(1)}%</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Agents</p>
                <p className="text-2xl font-bold text-gray-900">
                  {aiServices.metrics.activeAgents}/{aiServices.metrics.totalAgents}
                </p>
              </div>
              <CpuChipIcon className="h-12 w-12 text-purple-500" />
            </div>
            <div className="mt-4">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-purple-500 h-2 rounded-full" 
                  style={{ width: `${(aiServices.metrics.activeAgents / aiServices.metrics.totalAgents) * 100}%` }}
                ></div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg Response Time</p>
                <p className="text-2xl font-bold text-gray-900">
                  {aiServices.metrics.avgResponseTime}ms
                </p>
              </div>
              <ClockIcon className="h-12 w-12 text-blue-500" />
            </div>
            <div className="mt-4">
              <span className="text-sm text-gray-600">Target: &lt; 100ms</span>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Training Jobs</p>
                <p className="text-2xl font-bold text-gray-900">
                  {aiServices.metrics.trainingJobs}
                </p>
              </div>
              <div className="h-12 w-12 rounded-full bg-gradient-to-r from-green-400 to-blue-500 flex items-center justify-center">
                <span className="text-white font-bold">ML</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* AI Agents Status */}
      <div className="bg-white rounded-xl border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">AI Agents Status</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {aiServices.aiAgents.map((agent: any) => (
              <div key={agent.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900">{agent.name}</h4>
                  <div className={`w-3 h-3 rounded-full ${
                    agent.status === 'active' ? 'bg-green-500' :
                    agent.status === 'training' ? 'bg-yellow-500' :
                    agent.status === 'idle' ? 'bg-gray-400' : 'bg-red-500'
                  }`}></div>
                </div>
                <p className="text-sm text-gray-600 mb-2">{agent.type}</p>
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Performance: {(agent.performance * 100).toFixed(0)}%</span>
                  <span className="capitalize">{agent.status}</span>
                </div>
                <div className="mt-2">
                  <div className="w-full bg-gray-200 rounded-full h-1">
                    <div 
                      className="bg-blue-500 h-1 rounded-full" 
                      style={{ width: `${agent.performance * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* AI Services Health */}
      <div className="bg-white rounded-xl border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">AI Services Health</h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {aiServices.aiServices.map((service: any) => (
              <div key={service.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">{service.name}</h4>
                  <p className="text-sm text-gray-600">{service.description}</p>
                </div>
                <div className="text-right">
                  <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    service.status === 'healthy' ? 'bg-green-100 text-green-800' :
                    service.status === 'degraded' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {service.status}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {service.responseTime}ms • {service.throughput}/min
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// Audio Processing Dashboard Component - Audio Specialist Implementation
export function AudioProcessingDashboard({ audioProcessing }: any) {
  if (audioProcessing.loading) {
    return <div className="animate-pulse"><div className="h-64 bg-gray-200 rounded"></div></div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
          <MusicalNoteIcon className="h-8 w-8 text-green-600" />
          Audio Processing Studio
        </h2>
      </div>

      {/* Audio Metrics */}
      {audioProcessing.metrics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Projects</p>
                <p className="text-2xl font-bold text-gray-900">{audioProcessing.metrics.totalProjects}</p>
              </div>
              <MusicalNoteIcon className="h-12 w-12 text-green-500" />
            </div>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Processing</p>
                <p className="text-2xl font-bold text-gray-900">{audioProcessing.metrics.activeProcessing}</p>
              </div>
              <div className="h-12 w-12 rounded-full bg-gradient-to-r from-green-400 to-blue-500 flex items-center justify-center">
                <BoltIcon className="h-6 w-6 text-white" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Success Rate</p>
                <p className="text-2xl font-bold text-gray-900">
                  {(audioProcessing.metrics.successRate * 100).toFixed(1)}%
                </p>
              </div>
              <CheckCircleIcon className="h-12 w-12 text-green-500" />
            </div>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Audio Generated</p>
                <p className="text-2xl font-bold text-gray-900">
                  {audioProcessing.metrics.totalAudioGenerated}min
                </p>
              </div>
              <ClockIcon className="h-12 w-12 text-blue-500" />
            </div>
          </div>
        </div>
      )}

      {/* Processing Queue */}
      <div className="bg-white rounded-xl border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Processing Queue</h3>
        </div>
        <div className="p-6">
          {audioProcessing.processingQueue.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No items in processing queue</p>
          ) : (
            <div className="space-y-4">
              {audioProcessing.processingQueue.map((project: any) => (
                <div key={project.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div>
                    <h4 className="font-medium text-gray-900">{project.name}</h4>
                    <p className="text-sm text-gray-600">
                      {project.type} • {project.duration}s • {project.quality}
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`px-2 py-1 rounded text-xs ${
                        project.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                        project.status === 'queued' ? 'bg-yellow-100 text-yellow-800' :
                        project.status === 'completed' ? 'bg-green-100 text-green-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {project.status}
                      </span>
                    </div>
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full transition-all duration-300" 
                        style={{ width: `${project.progress * 100}%` }}
                      ></div>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {(project.progress * 100).toFixed(0)}% complete
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Audio Engines Status */}
      <div className="bg-white rounded-xl border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Audio Engines</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {audioProcessing.engines.map((engine: any) => (
              <div key={engine.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900">{engine.name}</h4>
                  <div className={`w-3 h-3 rounded-full ${
                    engine.status === 'available' ? 'bg-green-500' :
                    engine.status === 'busy' ? 'bg-yellow-500' : 'bg-red-500'
                  }`}></div>
                </div>
                <p className="text-sm text-gray-600 mb-2">{engine.type}</p>
                <div className="text-xs text-gray-500">
                  Performance: {(engine.performance * 100).toFixed(0)}% • Queue: {engine.queueLength}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}