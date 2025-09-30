/**
 * @fileoverview Timeline Editor Component for Remix Studio
 * @author Fahed Mlaiel <mlaiel@live.de> - Audio Engineer Role
 * @copyright 2025 Fahed Mlaiel - All Rights Reserved
 */

'use client';

import React, { useState, useCallback, useRef, useEffect } from 'react';

export interface TimelineTrack {
  id: string;
  name: string;
  audioBuffer?: AudioBuffer;
  startTime: number;
  duration: number;
  volume: number;
  muted: boolean;
  solo: boolean;
  color: string;
}

export interface TimelineEditorProps {
  tracks: TimelineTrack[];
  currentTime: number;
  duration: number;
  zoom: number;
  onTimeChange: (time: number) => void;
  onTrackUpdate: (trackId: string, updates: Partial<TimelineTrack>) => void;
  onTrackSelect: (trackId: string) => void;
  selectedTrackId?: string;
}

const TimelineEditor: React.FC<TimelineEditorProps> = ({
  tracks,
  currentTime,
  duration,
  zoom,
  onTimeChange,
  onTrackUpdate,
  onTrackSelect,
  selectedTrackId
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleCanvasClick = useCallback((event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const timeAtX = (x / canvas.width) * duration;
    
    onTimeChange(Math.max(0, Math.min(duration, timeAtX)));
  }, [duration, onTimeChange]);

  const renderTimeline = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw timeline background
    ctx.fillStyle = '#1a1a1a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw time ruler
    ctx.strokeStyle = '#404040';
    ctx.lineWidth = 1;
    
    const secondsPerPixel = duration / canvas.width;
    const majorInterval = Math.pow(10, Math.floor(Math.log10(secondsPerPixel * 100)));
    
    for (let time = 0; time <= duration; time += majorInterval) {
      const x = (time / duration) * canvas.width;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, 20);
      ctx.stroke();
      
      // Draw time labels
      ctx.fillStyle = '#ffffff';
      ctx.font = '12px monospace';
      ctx.fillText(`${time.toFixed(1)}s`, x + 2, 15);
    }

    // Draw tracks
    tracks.forEach((track, index) => {
      const trackY = 30 + index * 60;
      const trackHeight = 50;
      
      // Track background
      ctx.fillStyle = selectedTrackId === track.id ? '#2a2a3a' : '#252525';
      ctx.fillRect(0, trackY, canvas.width, trackHeight);
      
      // Track audio visualization
      if (track.audioBuffer) {
        const startX = (track.startTime / duration) * canvas.width;
        const endX = ((track.startTime + track.duration) / duration) * canvas.width;
        
        ctx.fillStyle = track.muted ? '#606060' : track.color;
        ctx.fillRect(startX, trackY + 5, endX - startX, trackHeight - 10);
        
        // Simple waveform visualization
        ctx.strokeStyle = track.muted ? '#808080' : '#ffffff';
        ctx.lineWidth = 1;
        ctx.beginPath();
        
        const channelData = track.audioBuffer.getChannelData(0);
        const samplesPerPixel = Math.floor(channelData.length / (endX - startX));
        
        for (let x = startX; x < endX; x++) {
          const sampleIndex = Math.floor((x - startX) * samplesPerPixel);
          const amplitude = channelData[sampleIndex] || 0;
          const y = trackY + trackHeight / 2 + amplitude * (trackHeight / 4);
          
          if (x === startX) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        }
        ctx.stroke();
      }
      
      // Track name
      ctx.fillStyle = '#ffffff';
      ctx.font = '14px Arial';
      ctx.fillText(track.name, 5, trackY + 25);
      
      // Volume indicator
      ctx.fillStyle = track.muted ? '#ff4444' : '#44ff44';
      ctx.fillRect(5, trackY + 35, track.volume * 100, 5);
    });

    // Draw playhead
    const playheadX = (currentTime / duration) * canvas.width;
    ctx.strokeStyle = '#ff6b6b';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(playheadX, 0);
    ctx.lineTo(playheadX, canvas.height);
    ctx.stroke();

  }, [tracks, currentTime, duration, selectedTrackId]);

  useEffect(() => {
    renderTimeline();
  }, [renderTimeline]);

  return (
    <div className="timeline-editor w-full h-full bg-gray-900">
      <div className="timeline-header p-2 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="text-white font-semibold">Timeline</h3>
          <div className="flex items-center space-x-2">
            <span className="text-gray-300 text-sm">
              {Math.floor(currentTime / 60)}:{(currentTime % 60).toFixed(2).padStart(5, '0')}
            </span>
            <button className="px-2 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700">
              Zoom
            </button>
          </div>
        </div>
      </div>
      
      <div className="timeline-content relative">
        <canvas
          ref={canvasRef}
          width={800}
          height={Math.max(200, 30 + tracks.length * 60)}
          className="w-full cursor-pointer"
          onClick={handleCanvasClick}
          onMouseDown={() => setIsDragging(true)}
          onMouseUp={() => setIsDragging(false)}
          onMouseLeave={() => setIsDragging(false)}
        />
        
        <div className="track-controls absolute left-0 top-0 bg-gray-800 w-48 h-full overflow-y-auto">
          {tracks.map((track, index) => (
            <div
              key={track.id}
              className={`track-control p-2 border-b border-gray-700 cursor-pointer ${
                selectedTrackId === track.id ? 'bg-gray-700' : 'hover:bg-gray-750'
              }`}
              onClick={() => onTrackSelect(track.id)}
              style={{ height: '60px' }}
            >
              <div className="flex items-center justify-between">
                <span className="text-white text-sm font-medium">{track.name}</span>
                <div className="flex space-x-1">
                  <button
                    className={`px-2 py-1 text-xs rounded ${
                      track.muted ? 'bg-red-600 text-white' : 'bg-gray-600 text-gray-300'
                    }`}
                    onClick={(e) => {
                      e.stopPropagation();
                      onTrackUpdate(track.id, { muted: !track.muted });
                    }}
                  >
                    M
                  </button>
                  <button
                    className={`px-2 py-1 text-xs rounded ${
                      track.solo ? 'bg-yellow-600 text-white' : 'bg-gray-600 text-gray-300'
                    }`}
                    onClick={(e) => {
                      e.stopPropagation();
                      onTrackUpdate(track.id, { solo: !track.solo });
                    }}
                  >
                    S
                  </button>
                </div>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={track.volume}
                className="w-full mt-1"
                onChange={(e) => onTrackUpdate(track.id, { volume: parseFloat(e.target.value) })}
                onClick={(e) => e.stopPropagation()}
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TimelineEditor;