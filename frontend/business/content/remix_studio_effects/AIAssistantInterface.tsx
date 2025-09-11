/**
 * @fileoverview AI Assistant Interface for Audio Studio
 * @author Fahed Mlaiel <mlaiel@live.de> - IA Engineer Role
 * @copyright 2025 Fahed Mlaiel - All Rights Reserved
 */

'use client';

import React, { useState, useCallback } from 'react';

export interface AIAssistantProps {
  onAIGenerate: (type: string, parameters: any) => void;
  onAIAnalyze: (audioData: AudioBuffer) => void;
  onAIEnhance: (enhancement: string) => void;
  isProcessing: boolean;
}

const AIAssistantInterface: React.FC<AIAssistantProps> = ({
  onAIGenerate,
  onAIAnalyze,
  onAIEnhance,
  isProcessing
}) => {
  const [selectedTab, setSelectedTab] = useState<'generate' | 'analyze' | 'enhance'>('generate');
  const [prompt, setPrompt] = useState('');

  const aiFeatures = {
    generate: [
      { id: 'melody', label: 'Generate Melody', icon: '🎵' },
      { id: 'harmony', label: 'Add Harmony', icon: '🎼' },
      { id: 'rhythm', label: 'Create Rhythm', icon: '🥁' },
      { id: 'bassline', label: 'Generate Bassline', icon: '🎸' }
    ],
    analyze: [
      { id: 'key', label: 'Detect Key', icon: '🔑' },
      { id: 'tempo', label: 'Analyze Tempo', icon: '⏱️' },
      { id: 'mood', label: 'Mood Analysis', icon: '😊' },
      { id: 'structure', label: 'Song Structure', icon: '🏗️' }
    ],
    enhance: [
      { id: 'mastering', label: 'AI Mastering', icon: '✨' },
      { id: 'mixing', label: 'Auto Mix', icon: '🎚️' },
      { id: 'noise-reduction', label: 'Noise Reduction', icon: '🔇' },
      { id: 'vocal-tuning', label: 'Vocal Tuning', icon: '🎤' }
    ]
  };

  const handleAIAction = useCallback((action: string) => {
    switch (selectedTab) {
      case 'generate':
        onAIGenerate(action, { prompt });
        break;
      case 'enhance':
        onAIEnhance(action);
        break;
      default:
        break;
    }
  }, [selectedTab, prompt, onAIGenerate, onAIEnhance]);

  return (
    <div className="ai-assistant bg-gray-900 p-4 h-full">
      <div className="assistant-header mb-4">
        <h3 className="text-white text-lg font-bold mb-3 flex items-center">
          <span className="mr-2">🤖</span>
          AI Studio Assistant
        </h3>
        
        {/* Tab Navigation */}
        <div className="tab-navigation flex space-x-2 mb-4">
          {(['generate', 'analyze', 'enhance'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setSelectedTab(tab)}
              className={`px-3 py-2 rounded text-sm capitalize ${
                selectedTab === tab
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Generate Tab */}
      {selectedTab === 'generate' && (
        <div className="generate-section">
          <div className="prompt-input mb-4">
            <label className="block text-gray-300 text-sm mb-2">AI Prompt</label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe what you want to generate... (e.g., 'Create a uplifting piano melody in C major')"
              className="w-full bg-gray-800 text-white p-3 rounded border border-gray-700 focus:border-blue-500 h-20 resize-none"
            />
          </div>
          
          <div className="ai-features grid grid-cols-2 gap-3">
            {aiFeatures.generate.map((feature) => (
              <button
                key={feature.id}
                onClick={() => handleAIAction(feature.id)}
                disabled={isProcessing}
                className="feature-button bg-gray-800 hover:bg-gray-700 disabled:opacity-50 p-3 rounded border border-gray-700 text-left transition-colors"
              >
                <div className="flex items-center space-x-2">
                  <span className="text-lg">{feature.icon}</span>
                  <span className="text-white text-sm">{feature.label}</span>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Analyze Tab */}
      {selectedTab === 'analyze' && (
        <div className="analyze-section">
          <p className="text-gray-400 text-sm mb-4">
            Analyze your audio tracks with AI-powered insights
          </p>
          
          <div className="ai-features grid grid-cols-2 gap-3">
            {aiFeatures.analyze.map((feature) => (
              <button
                key={feature.id}
                onClick={() => handleAIAction(feature.id)}
                disabled={isProcessing}
                className="feature-button bg-gray-800 hover:bg-gray-700 disabled:opacity-50 p-3 rounded border border-gray-700 text-left transition-colors"
              >
                <div className="flex items-center space-x-2">
                  <span className="text-lg">{feature.icon}</span>
                  <span className="text-white text-sm">{feature.label}</span>
                </div>
              </button>
            ))}
          </div>
          
          {/* Analysis Results */}
          <div className="analysis-results mt-6 bg-gray-800 rounded-lg p-4">
            <h4 className="text-white font-medium mb-3">Analysis Results</h4>
            <div className="results-placeholder text-gray-500 text-sm">
              Select an analysis tool to see results here
            </div>
          </div>
        </div>
      )}

      {/* Enhance Tab */}
      {selectedTab === 'enhance' && (
        <div className="enhance-section">
          <p className="text-gray-400 text-sm mb-4">
            Enhance your audio with AI-powered processing
          </p>
          
          <div className="ai-features grid grid-cols-2 gap-3">
            {aiFeatures.enhance.map((feature) => (
              <button
                key={feature.id}
                onClick={() => handleAIAction(feature.id)}
                disabled={isProcessing}
                className="feature-button bg-gray-800 hover:bg-gray-700 disabled:opacity-50 p-3 rounded border border-gray-700 text-left transition-colors"
              >
                <div className="flex items-center space-x-2">
                  <span className="text-lg">{feature.icon}</span>
                  <span className="text-white text-sm">{feature.label}</span>
                </div>
              </button>
            ))}
          </div>
          
          {/* Enhancement Settings */}
          <div className="enhancement-settings mt-6 bg-gray-800 rounded-lg p-4">
            <h4 className="text-white font-medium mb-3">Enhancement Settings</h4>
            
            <div className="setting-item mb-3">
              <label className="block text-gray-300 text-sm mb-1">Enhancement Intensity</label>
              <input type="range" min="0" max="100" defaultValue="50" className="w-full" />
            </div>
            
            <div className="setting-item mb-3">
              <label className="block text-gray-300 text-sm mb-1">Preserve Original</label>
              <input type="checkbox" className="mr-2" />
              <span className="text-gray-400 text-sm">Keep original for comparison</span>
            </div>
          </div>
        </div>
      )}

      {/* Processing Indicator */}
      {isProcessing && (
        <div className="processing-indicator mt-4 bg-blue-900 border border-blue-700 rounded-lg p-3">
          <div className="flex items-center space-x-2">
            <div className="animate-spin w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full"></div>
            <span className="text-blue-300 text-sm">AI is processing...</span>
          </div>
        </div>
      )}

      {/* AI Tips */}
      <div className="ai-tips mt-6 bg-gray-800 rounded-lg p-4">
        <h4 className="text-white font-medium mb-2">💡 AI Tips</h4>
        <ul className="text-gray-400 text-sm space-y-1">
          <li>• Be specific in your prompts for better results</li>
          <li>• Use reference tracks for style matching</li>
          <li>• Experiment with different AI parameters</li>
          <li>• Combine multiple AI features for best results</li>
        </ul>
      </div>
    </div>
  );
};

export default AIAssistantInterface;