/**
 * @fileoverview Track Mixer Component for Audio Studio
 * @author Fahed Mlaiel <mlaiel@live.de> - Audio Engineer Role
 * @copyright 2025 Fahed Mlaiel - All Rights Reserved
 */

'use client';

import React, { useState, useCallback } from 'react';

export interface MixerChannel {
  id: string;
  name: string;
  volume: number;
  gain: number;
  pan: number;
  muted: boolean;
  solo: boolean;
  color: string;
}

export interface TrackMixerProps {
  channels: MixerChannel[];
  onChannelUpdate: (channelId: string, updates: Partial<MixerChannel>) => void;
  masterVolume: number;
  onMasterVolumeChange: (volume: number) => void;
}

const TrackMixer: React.FC<TrackMixerProps> = ({
  channels,
  onChannelUpdate,
  masterVolume,
  onMasterVolumeChange
}) => {
  const updateChannelProperty = useCallback((channelId: string, property: string, value: any) => {
    onChannelUpdate(channelId, { [property]: value });
  }, [onChannelUpdate]);

  return (
    <div className="track-mixer bg-gray-900 p-4 h-full overflow-y-auto">
      <div className="mixer-header mb-4">
        <h3 className="text-white text-lg font-bold mb-2">Audio Mixer</h3>
        
        {/* Master Section */}
        <div className="master-section bg-gray-800 p-3 rounded-lg mb-4">
          <h4 className="text-white font-semibold mb-2">Master</h4>
          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <label className="block text-gray-300 text-sm mb-1">Volume</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={masterVolume}
                onChange={(e) => onMasterVolumeChange(parseFloat(e.target.value))}
                className="w-full"
              />
              <span className="text-gray-400 text-xs">{Math.round(masterVolume * 100)}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Channel Strips */}
      <div className="channels-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {channels.map((channel) => (
          <div key={channel.id} className="channel-strip bg-gray-800 rounded-lg p-3">
            <div className="channel-header mb-3">
              <div className="flex items-center justify-between mb-2">
                <h5 className="text-white font-medium truncate" style={{ color: channel.color }}>
                  {channel.name}
                </h5>
              </div>
              
              {/* Mute/Solo buttons */}
              <div className="flex space-x-2 mb-3">
                <button
                  className={`px-2 py-1 text-xs rounded font-medium ${
                    channel.muted ? 'bg-red-600 text-white' : 'bg-gray-600 text-gray-300 hover:bg-gray-500'
                  }`}
                  onClick={() => updateChannelProperty(channel.id, 'muted', !channel.muted)}
                >
                  MUTE
                </button>
                <button
                  className={`px-2 py-1 text-xs rounded font-medium ${
                    channel.solo ? 'bg-yellow-600 text-white' : 'bg-gray-600 text-gray-300 hover:bg-gray-500'
                  }`}
                  onClick={() => updateChannelProperty(channel.id, 'solo', !channel.solo)}
                >
                  SOLO
                </button>
              </div>
            </div>

            {/* Main Controls */}
            <div className="main-controls">
              {/* Pan */}
              <div className="mb-3">
                <label className="block text-gray-400 text-xs mb-1">Pan</label>
                <input
                  type="range"
                  min="-1"
                  max="1"
                  step="0.01"
                  value={channel.pan}
                  onChange={(e) => updateChannelProperty(channel.id, 'pan', parseFloat(e.target.value))}
                  className="w-full"
                />
                <span className="text-gray-500 text-xs">
                  {channel.pan === 0 ? 'C' : channel.pan < 0 ? `L${Math.round(Math.abs(channel.pan) * 100)}` : `R${Math.round(channel.pan * 100)}`}
                </span>
              </div>

              {/* Volume Fader */}
              <div className="volume-fader">
                <label className="block text-gray-400 text-xs mb-1">Volume</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={channel.volume}
                  onChange={(e) => updateChannelProperty(channel.id, 'volume', parseFloat(e.target.value))}
                  className="w-full"
                />
                <span className="text-gray-400 text-xs">{Math.round(channel.volume * 100)}%</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TrackMixer;