/**
 * PODCAST STUDIO
 * Professional podcast recording, editing, and distribution
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright © 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import { useState, useRef } from 'react';
import Link from 'next/link';
import { ArrowLeft, Mic, Radio, Users, Upload, Download, Settings, Play, Pause, SkipBack, SkipForward } from 'lucide-react';

export default function PodcastStudioPage() {
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [guests, setGuests] = useState([
    { id: '1', name: 'Host', muted: false, volume: 100 },
    { id: '2', name: 'Guest 1', muted: false, volume: 100 },
  ]);

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Top Bar */}
      <div className="bg-gradient-to-r from-yellow-500 to-orange-500 p-4">
        <div className="flex items-center justify-between text-white">
          <div className="flex items-center gap-4">
            <Link href="/studio" className="p-2 hover:bg-white/20 rounded-lg transition">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div>
              <h1 className="text-2xl font-bold">Podcast Studio</h1>
              <p className="text-sm opacity-90">Professional podcast production</p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition">
              <Settings className="w-4 h-4" />
            </button>
            <button className="px-4 py-2 bg-white text-gray-900 hover:bg-gray-100 rounded-lg flex items-center gap-2 font-medium transition">
              <Download className="w-4 h-4" />
              Export
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-80px)]">
        {/* Left Panel: Guests */}
        <div className="w-80 bg-gray-800 border-r border-gray-700 p-6 overflow-y-auto">
          <div className="mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-white">Participants</h2>
              <button className="p-2 bg-blue-500 hover:bg-blue-600 rounded-lg transition">
                <Users className="w-4 h-4 text-white" />
              </button>
            </div>
            
            {/* Guest List */}
            <div className="space-y-3">
              {guests.map((guest) => (
                <div key={guest.id} className="bg-gray-700 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-white">{guest.name}</span>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => {
                          setGuests(guests.map(g => 
                            g.id === guest.id ? { ...g, muted: !g.muted } : g
                          ));
                        }}
                        className={`p-1 rounded ${guest.muted ? 'bg-red-500' : 'bg-gray-600'}`}
                      >
                        <Mic className="w-3 h-3 text-white" />
                      </button>
                    </div>
                  </div>
                  
                  {/* Volume */}
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={guest.volume}
                    onChange={(e) => {
                      setGuests(guests.map(g => 
                        g.id === guest.id ? { ...g, volume: Number(e.target.value) } : g
                      ));
                    }}
                    className="w-full h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer"
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Recording Settings */}
          <div>
            <h3 className="text-sm font-semibold text-white mb-3">Settings</h3>
            <div className="space-y-3">
              <div className="bg-gray-700 rounded-lg p-3">
                <label className="text-xs text-gray-400 block mb-2">Format</label>
                <select className="w-full bg-gray-600 text-white rounded px-3 py-2 text-sm">
                  <option>MP3 (320kbps)</option>
                  <option>WAV (Lossless)</option>
                  <option>AAC (256kbps)</option>
                </select>
              </div>
              
              <div className="bg-gray-700 rounded-lg p-3">
                <label className="text-xs text-gray-400 block mb-2">Sample Rate</label>
                <select className="w-full bg-gray-600 text-white rounded px-3 py-2 text-sm">
                  <option>48 kHz</option>
                  <option>44.1 kHz</option>
                  <option>96 kHz</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Center: Waveform & Controls */}
        <div className="flex-1 flex flex-col">
          {/* Waveform Display */}
          <div className="flex-1 bg-black flex items-center justify-center p-8">
            <div className="w-full max-w-4xl">
              {/* Audio Waveform */}
              <div className="h-48 bg-gray-900 rounded-lg flex items-center px-4">
                <div className="flex items-center gap-1 h-full w-full">
                  {Array.from({ length: 200 }).map((_, i) => (
                    <div
                      key={i}
                      className="flex-1 bg-gradient-to-t from-yellow-500 to-orange-500 rounded-sm"
                      style={{ height: `${Math.random() * 100}%` }}
                    />
                  ))}
                </div>
              </div>

              {/* Recording Status */}
              {isRecording && (
                <div className="mt-4 flex items-center justify-center gap-3">
                  <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                  <span className="text-white font-medium">RECORDING</span>
                  <span className="text-gray-400 font-mono">00:05:23</span>
                </div>
              )}
            </div>
          </div>

          {/* Transport Controls */}
          <div className="bg-gray-800 border-t border-gray-700 p-6">
            <div className="flex items-center justify-center gap-4">
              <button className="p-3 hover:bg-gray-700 rounded-lg transition">
                <SkipBack className="w-6 h-6 text-white" />
              </button>
              
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="p-4 bg-white hover:bg-gray-100 rounded-lg transition"
              >
                {isPlaying ? (
                  <Pause className="w-6 h-6 text-gray-900" />
                ) : (
                  <Play className="w-6 h-6 text-gray-900" />
                )}
              </button>
              
              <button className="p-3 hover:bg-gray-700 rounded-lg transition">
                <SkipForward className="w-6 h-6 text-white" />
              </button>
              
              {/* Record Button */}
              <button
                onClick={() => setIsRecording(!isRecording)}
                className={`ml-8 px-6 py-3 rounded-lg font-medium flex items-center gap-2 transition ${
                  isRecording 
                    ? 'bg-red-500 hover:bg-red-600 text-white' 
                    : 'bg-gray-700 hover:bg-gray-600 text-white'
                }`}
              >
                <Radio className="w-5 h-5" />
                {isRecording ? 'Stop Recording' : 'Start Recording'}
              </button>
            </div>
            
            {/* Timeline */}
            <div className="mt-6">
              <input
                type="range"
                min="0"
                max="100"
                defaultValue="0"
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between mt-2 text-xs text-gray-400 font-mono">
                <span>00:00</span>
                <span>10:00</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
