/**
 * @fileoverview Waveform Visualizer Component
 * @author Fahed Mlaiel <mlaiel@live.de> - Audio Engineer Role
 * @copyright 2025 Fahed Mlaiel - All Rights Reserved
 */

'use client';

import React, { useRef, useEffect, useState, useCallback } from 'react';

export interface WaveformVisualizerProps {
  audioBuffer?: AudioBuffer;
  currentTime: number;
  duration: number;
  isPlaying: boolean;
  onTimeSeek: (time: number) => void;
  height?: number;
  color?: string;
  backgroundColor?: string;
}

const WaveformVisualizer: React.FC<WaveformVisualizerProps> = ({
  audioBuffer,
  currentTime,
  duration,
  isPlaying,
  onTimeSeek,
  height = 100,
  color = '#4ade80',
  backgroundColor = '#1f2937'
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const drawWaveform = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const { width, height: canvasHeight } = canvas;
    
    // Clear canvas
    ctx.fillStyle = backgroundColor;
    ctx.fillRect(0, 0, width, canvasHeight);

    if (!audioBuffer) {
      // Draw placeholder waveform
      ctx.strokeStyle = color;
      ctx.lineWidth = 1;
      ctx.beginPath();
      
      for (let x = 0; x < width; x += 2) {
        const y = canvasHeight / 2 + Math.sin(x * 0.1) * (canvasHeight / 4);
        if (x === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      }
      ctx.stroke();
      return;
    }

    // Draw actual waveform
    const channelData = audioBuffer.getChannelData(0);
    const samplesPerPixel = Math.floor(channelData.length / width);
    
    ctx.strokeStyle = color;
    ctx.lineWidth = 1;
    ctx.beginPath();

    for (let x = 0; x < width; x++) {
      const sampleIndex = Math.floor(x * samplesPerPixel);
      const amplitude = channelData[sampleIndex] || 0;
      const y = (canvasHeight / 2) + (amplitude * canvasHeight / 2);
      
      if (x === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    }
    ctx.stroke();

    // Draw playhead
    if (duration > 0) {
      const playheadX = (currentTime / duration) * width;
      ctx.strokeStyle = '#ef4444';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(playheadX, 0);
      ctx.lineTo(playheadX, canvasHeight);
      ctx.stroke();
    }
  }, [audioBuffer, currentTime, duration, color, backgroundColor]);

  useEffect(() => {
    drawWaveform();
  }, [drawWaveform]);

  const handleMouseDown = useCallback((event: React.MouseEvent<HTMLCanvasElement>) => {
    setIsDragging(true);
    handleTimeSeek(event);
  }, []);

  const handleMouseMove = useCallback((event: React.MouseEvent<HTMLCanvasElement>) => {
    if (isDragging) {
      handleTimeSeek(event);
    }
  }, [isDragging]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleTimeSeek = useCallback((event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas || duration <= 0) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const seekTime = (x / canvas.width) * duration;
    
    onTimeSeek(Math.max(0, Math.min(duration, seekTime)));
  }, [duration, onTimeSeek]);

  return (
    <div className="waveform-visualizer">
      <canvas
        ref={canvasRef}
        width={800}
        height={height}
        className="w-full cursor-pointer border border-gray-700 rounded"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      />
      <div className="waveform-info mt-2 flex justify-between text-sm text-gray-400">
        <span>
          {Math.floor(currentTime / 60)}:{(currentTime % 60).toFixed(1).padStart(4, '0')}
        </span>
        <span>
          {Math.floor(duration / 60)}:{(duration % 60).toFixed(1).padStart(4, '0')}
        </span>
      </div>
    </div>
  );
};

export default WaveformVisualizer;