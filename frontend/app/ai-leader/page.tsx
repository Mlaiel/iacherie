'use client';

import React, { useState, useEffect } from 'react';
import {
  Brain,
  Zap,
  TrendingUp,
  Database,
  Activity,
  Shield,
  RefreshCw,
  CheckCircle,
  AlertTriangle,
  Clock
} from 'lucide-react';

interface Capability {
  type: string;
  name: string;
  description: string;
  is_trained: boolean;
  can_replace_api: boolean;
  training_samples: number;
  accuracy: number;
  original_api: string;
}

interface AutonomyStatus {
  autonomy_level: number;
  total_capabilities: number;
  trained_capabilities: number;
  replaceable_capabilities: number;
  training_samples: number;
  cost_saved_usd: number;
  capabilities: Capability[];
}

export default function AILeaderPage() {
  const [status, setStatus] = useState<AutonomyStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedCapability, setSelectedCapability] = useState<string | null>(null);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000); // Refresh every 5s
    return () => clearInterval(interval);
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/leader/status');
      const data = await response.json();
      if (data.success) {
        setStatus(data.data);
      }
    } catch (error) {
      console.error('Error fetching status:', error);
    } finally {
      setLoading(false);
    }
  };

  const startTraining = async (capabilityType: string) => {
    try {
      const response = await fetch('http://localhost:8001/api/leader/train', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ capability_type: capabilityType })
      });
      
      const data = await response.json();
      
      if (data.success) {
        alert(`Training started! Job ID: ${data.data.job_id}`);
        fetchStatus();
      } else {
        alert(`Training failed: ${data.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error starting training:', error);
      alert('Failed to start training');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <RefreshCw className="w-12 h-12 text-purple-400 animate-spin" />
          <p className="text-white text-xl">Loading AI Leader Status...</p>
        </div>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900 flex items-center justify-center">
        <div className="text-white text-xl">Failed to load AI Leader status</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900 p-8">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex items-center gap-4 mb-4">
          <Brain className="w-12 h-12 text-purple-400" />
          <div>
            <h1 className="text-4xl font-bold text-white">AI Leader Agent</h1>
            <p className="text-purple-300">Autonomous Learning System</p>
          </div>
        </div>

        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-white">Autonomy Progress</h2>
            <span className="text-3xl font-bold text-purple-400">
              {status.autonomy_level.toFixed(1)}%
            </span>
          </div>
          
          <div className="w-full bg-gray-700 rounded-full h-6 mb-4">
            <div
              className="bg-gradient-to-r from-purple-500 to-pink-500 h-6 rounded-full transition-all duration-500 flex items-center justify-center"
              style={{ width: `${status.autonomy_level}%` }}
            >
              <span className="text-white text-sm font-bold">
                {status.replaceable_capabilities}/{status.total_capabilities} APIs Replaced
              </span>
            </div>
          </div>

          <p className="text-purple-200 text-center">
            Learning from external APIs to become fully autonomous
          </p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/20 backdrop-blur-lg rounded-xl p-6 border border-blue-400/30">
          <Database className="w-8 h-8 text-blue-400 mb-3" />
          <div className="text-3xl font-bold text-white mb-1">
            {status.training_samples.toLocaleString()}
          </div>
          <div className="text-blue-300 text-sm">Training Samples</div>
        </div>

        <div className="bg-gradient-to-br from-green-500/20 to-green-600/20 backdrop-blur-lg rounded-xl p-6 border border-green-400/30">
          <CheckCircle className="w-8 h-8 text-green-400 mb-3" />
          <div className="text-3xl font-bold text-white mb-1">
            {status.trained_capabilities}
          </div>
          <div className="text-green-300 text-sm">Trained Capabilities</div>
        </div>

        <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/20 backdrop-blur-lg rounded-xl p-6 border border-purple-400/30">
          <Shield className="w-8 h-8 text-purple-400 mb-3" />
          <div className="text-3xl font-bold text-white mb-1">
            {status.replaceable_capabilities}
          </div>
          <div className="text-purple-300 text-sm">Ready to Replace</div>
        </div>

        <div className="bg-gradient-to-br from-yellow-500/20 to-yellow-600/20 backdrop-blur-lg rounded-xl p-6 border border-yellow-400/30">
          <TrendingUp className="w-8 h-8 text-yellow-400 mb-3" />
          <div className="text-3xl font-bold text-white mb-1">
            ${status.cost_saved_usd.toFixed(2)}
          </div>
          <div className="text-yellow-300 text-sm">Cost Saved</div>
        </div>
      </div>

      {/* Capabilities List */}
      <div className="max-w-7xl mx-auto">
        <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
          <Activity className="w-8 h-8 text-purple-400" />
          Learned Capabilities
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {status.capabilities.map((capability) => (
            <div
              key={capability.type}
              className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 hover:border-purple-400/50 transition-all cursor-pointer"
              onClick={() => setSelectedCapability(
                selectedCapability === capability.type ? null : capability.type
              )}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-white mb-2">
                    {capability.name}
                  </h3>
                  <p className="text-purple-200 text-sm mb-3">
                    {capability.description}
                  </p>
                  <div className="flex items-center gap-2 text-sm text-gray-300">
                    <Clock className="w-4 h-4" />
                    Original API: {capability.original_api}
                  </div>
                </div>

                <div className="flex flex-col items-end gap-2">
                  {capability.can_replace_api ? (
                    <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm font-semibold flex items-center gap-1">
                      <CheckCircle className="w-4 h-4" />
                      Ready
                    </span>
                  ) : capability.is_trained ? (
                    <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-sm font-semibold">
                      Trained
                    </span>
                  ) : (
                    <span className="px-3 py-1 bg-yellow-500/20 text-yellow-400 rounded-full text-sm font-semibold flex items-center gap-1">
                      <AlertTriangle className="w-4 h-4" />
                      Learning
                    </span>
                  )}
                </div>
              </div>

              {/* Progress Bar */}
              <div className="mb-4">
                <div className="flex justify-between text-sm text-purple-300 mb-2">
                  <span>Accuracy</span>
                  <span>{(capability.accuracy * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${
                      capability.accuracy >= 0.85
                        ? 'bg-green-500'
                        : capability.accuracy >= 0.7
                        ? 'bg-blue-500'
                        : 'bg-yellow-500'
                    }`}
                    style={{ width: `${capability.accuracy * 100}%` }}
                  />
                </div>
              </div>

              {/* Details when expanded */}
              {selectedCapability === capability.type && (
                <div className="mt-4 pt-4 border-t border-white/10">
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <div className="text-sm text-purple-300 mb-1">Training Samples</div>
                      <div className="text-xl font-bold text-white">
                        {capability.training_samples.toLocaleString()}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-purple-300 mb-1">Status</div>
                      <div className="text-xl font-bold text-white">
                        {capability.can_replace_api ? 'Production' : 'Training'}
                      </div>
                    </div>
                  </div>

                  {!capability.is_trained && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        startTraining(capability.type);
                      }}
                      className="w-full px-4 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg font-semibold hover:from-purple-600 hover:to-pink-600 transition-all flex items-center justify-center gap-2"
                    >
                      <Zap className="w-5 h-5" />
                      Start Training
                    </button>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Info Panel */}
      <div className="max-w-7xl mx-auto mt-8">
        <div className="bg-gradient-to-r from-purple-500/10 to-pink-500/10 backdrop-blur-lg rounded-xl p-6 border border-purple-400/30">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Brain className="w-6 h-6 text-purple-400" />
            How It Works
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-purple-200">
            <div>
              <div className="text-lg font-semibold text-white mb-2">1. Learn</div>
              <p className="text-sm">
                AI observes and records every external API call, building training datasets
              </p>
            </div>
            <div>
              <div className="text-lg font-semibold text-white mb-2">2. Train</div>
              <p className="text-sm">
                Internal models train on collected data to replicate API capabilities
              </p>
            </div>
            <div>
              <div className="text-lg font-semibold text-white mb-2">3. Replace</div>
              <p className="text-sm">
                Once accuracy is high enough, AI automatically replaces external APIs
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
