'use client';

/**
 * Waveform Visualizer Component
 * 
 * Real-time waveform visualization with interactive playback control.
 * Provides professional audio visualization for precise editing.
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Project: IA-Influencer Agent + Content Protection Platform
 * Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps
 * 
 * WARNING: This code is the intellectual property of Fahed Mlaiel.
 * Any unauthorized use, reproduction, or distribution without explicit written permission
 * is strictly prohibited and will be prosecuted to the full extent of the law.
 * 
 * Contact: mlaiel@live.de for licensing inquiries.
 */

import React, { useRef, useEffect, useState, useCallback, useMemo } from 'react';
import { studioColors, studioComponents, studioUtils } from './remix_studio.styles';

interface WaveformVisualizerProps {
  audioUrl?: string;
  currentTime: number;
  isPlaying: boolean;
  onSeek: (time: number) => void;
  height?: number;
  className?: string;
  showGrid?: boolean;
  showTimecode?: boolean;
  zoomLevel?: number;
}

interface WaveformData {
  peaks: number[];
  duration: number;
  sampleRate: number;
}

const WaveformVisualizer: React.FC<WaveformVisualizerProps> = ({
  audioUrl,
  currentTime,
  isPlaying,
  onSeek,
  height = 120,
  className = '',
  showGrid = true,
  showTimecode = true,
  zoomLevel = 1
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const animationFrameRef = useRef<number>();
  
  // Waveform state
  const [waveformData, setWaveformData] = useState<WaveformData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  // Generate mock waveform data for demonstration
  const generateMockWaveform = useCallback((duration: number = 180): WaveformData => {
    const sampleRate = 44100;
    const samplesPerPixel = Math.floor(sampleRate * duration / (window.innerWidth * zoomLevel));
    const peaks: number[] = [];
    
    for (let i = 0; i < window.innerWidth * zoomLevel; i++) {
      // Generate realistic waveform with varying amplitude
      const progress = i / (window.innerWidth * zoomLevel);
      let amplitude = 0;
      
      // Add multiple frequency components for realistic look
      amplitude += Math.sin(progress * Math.PI * 40) * 0.3;
      amplitude += Math.sin(progress * Math.PI * 120) * 0.2;
      amplitude += Math.sin(progress * Math.PI * 300) * 0.1;
      amplitude += (Math.random() - 0.5) * 0.1; // Add some noise
      
      // Apply envelope for more natural look
      const envelope = Math.exp(-Math.abs(progress - 0.5) * 3) * 2;
      amplitude *= envelope;
      
      // Normalize and add some variation
      amplitude = Math.max(-1, Math.min(1, amplitude * (0.5 + Math.random() * 0.5)));
      peaks.push(amplitude);
    }
    
    return {
      peaks,
      duration: duration * 1000, // Convert to milliseconds
      sampleRate
    };
  }, [zoomLevel]);

  // Load waveform data
  useEffect(() => {
    if (audioUrl) {
      setIsLoading(true);
      setError(null);
      
      // Simulate loading delay
      const timeout = setTimeout(() => {
        try {
          const mockData = generateMockWaveform();
          setWaveformData(mockData);
        } catch (err) {
          setError('Failed to load waveform data');
        } finally {
          setIsLoading(false);
        }
      }, 500);
      
      return () => clearTimeout(timeout);
    } else {
      // Use default waveform if no audio URL
      setWaveformData(generateMockWaveform());
    }
  }, [audioUrl, generateMockWaveform]);

  // Drawing functions
  const drawWaveform = useCallback((ctx: CanvasRenderingContext2D, width: number, height: number) => {
    if (!waveformData) return;
    
    const { peaks } = waveformData;
    const centerY = height / 2;
    const amplitudeScale = centerY * 0.8;
    
    // Clear canvas
    ctx.fillStyle = studioComponents.waveform.backgroundColor;
    ctx.fillRect(0, 0, width, height);
    
    // Draw grid if enabled
    if (showGrid) {
      drawGrid(ctx, width, height);
    }
    
    // Draw waveform
    ctx.strokeStyle = studioComponents.waveform.waveColor;
    ctx.lineWidth = 1;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    
    ctx.beginPath();
    
    for (let x = 0; x < width && x < peaks.length; x++) {
      const peak = peaks[x] || 0;
      const y = centerY - (peak * amplitudeScale);
      
      if (x === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    }
    
    ctx.stroke();
    
    // Draw fill under waveform
    ctx.fillStyle = studioComponents.waveform.waveColor + '40'; // Add transparency
    ctx.beginPath();
    ctx.moveTo(0, centerY);
    
    for (let x = 0; x < width && x < peaks.length; x++) {
      const peak = peaks[x] || 0;
      const y = centerY - (peak * amplitudeScale);
      ctx.lineTo(x, y);
    }
    
    ctx.lineTo(width, centerY);
    ctx.closePath();
    ctx.fill();
    
    // Draw center line
    ctx.strokeStyle = '#666';
    ctx.lineWidth = 1;
    ctx.setLineDash([2, 2]);
    ctx.beginPath();
    ctx.moveTo(0, centerY);
    ctx.lineTo(width, centerY);
    ctx.stroke();
    ctx.setLineDash([]);
  }, [waveformData, showGrid]);

  const drawGrid = useCallback((ctx: CanvasRenderingContext2D, width: number, height: number) => {
    const gridInterval = 50; // 50px intervals
    const timeInterval = 5000; // 5 second intervals
    
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 1;
    ctx.setLineDash([1, 3]);
    
    // Vertical grid lines (time markers)
    for (let x = 0; x < width; x += gridInterval) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    
    // Horizontal grid lines (amplitude markers)
    const quarters = [height * 0.25, height * 0.5, height * 0.75];
    quarters.forEach(y => {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    });
    
    ctx.setLineDash([]);
  }, []);

  const drawPlayhead = useCallback((ctx: CanvasRenderingContext2D, width: number, height: number) => {
    if (!waveformData) return;
    
    const progress = currentTime / waveformData.duration;
    const x = progress * width;
    
    // Draw playhead line
    ctx.strokeStyle = studioComponents.waveform.cursorColor;
    ctx.lineWidth = 2;
    ctx.setLineDash([]);
    
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, height);
    ctx.stroke();
    
    // Draw playhead handle
    ctx.fillStyle = studioComponents.waveform.cursorColor;
    ctx.beginPath();
    ctx.arc(x, 10, 6, 0, Math.PI * 2);
    ctx.fill();
    
    // Draw progress fill
    if (progress > 0) {
      const gradient = ctx.createLinearGradient(0, 0, x, 0);
      gradient.addColorStop(0, studioComponents.waveform.progressColor + '40');
      gradient.addColorStop(1, studioComponents.waveform.progressColor + '20');
      
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, x, height);
    }
  }, [currentTime, waveformData]);

  const drawTimecode = useCallback((ctx: CanvasRenderingContext2D, width: number, height: number) => {
    if (!waveformData || !showTimecode) return;
    
    const interval = 100; // Every 100px
    const timePerPixel = waveformData.duration / width;
    
    ctx.fillStyle = '#ccc';
    ctx.font = '10px monospace';
    ctx.textAlign = 'center';
    
    for (let x = 0; x < width; x += interval) {
      const time = x * timePerPixel;
      const timeStr = studioUtils.msToTime(time);
      ctx.fillText(timeStr, x, height - 5);
    }
  }, [waveformData, showTimecode]);

  // Render waveform
  const render = useCallback(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    const rect = container.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;
    
    // Set canvas size
    canvas.width = width * window.devicePixelRatio;
    canvas.height = height * window.devicePixelRatio;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    
    // Scale for high DPI displays
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    
    // Draw components
    drawWaveform(ctx, width, height);
    drawPlayhead(ctx, width, height);
    drawTimecode(ctx, width, height);
  }, [drawWaveform, drawPlayhead, drawTimecode]);

  // Handle canvas interactions
  const handleCanvasClick = useCallback((event: React.MouseEvent) => {
    if (!waveformData || isDragging) return;
    
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const progress = x / rect.width;
    const newTime = progress * waveformData.duration;
    
    onSeek(newTime);
  }, [waveformData, isDragging, onSeek]);

  const handleMouseDown = useCallback((event: React.MouseEvent) => {
    setIsDragging(true);
    handleCanvasClick(event);
  }, [handleCanvasClick]);

  const handleMouseMove = useCallback((event: React.MouseEvent) => {
    if (!isDragging) return;
    handleCanvasClick(event);
  }, [isDragging, handleCanvasClick]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  // Animation loop for playhead movement
  const animate = useCallback(() => {
    render();
    if (isPlaying) {
      animationFrameRef.current = requestAnimationFrame(animate);
    }
  }, [render, isPlaying]);

  // Start/stop animation
  useEffect(() => {
    if (isPlaying) {
      animate();
    } else {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      render(); // Render once when stopped
    }
    
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isPlaying, animate, render]);

  // Render on resize
  useEffect(() => {
    const handleResize = () => {
      setTimeout(render, 100); // Debounce resize
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [render]);

  // Initial render
  useEffect(() => {
    render();
  }, [waveformData, render]);

  const waveformClasses = studioUtils.getClassName(
    'waveform-visualizer relative bg-gray-900 border border-gray-700 rounded overflow-hidden',
    className
  );

  return (
    <div className={waveformClasses} style={{ height }}>
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 bg-gray-800 bg-opacity-90 p-2 z-10">
        <div className="flex items-center justify-between">
          <div className="text-sm font-medium text-white">
            Waveform
          </div>
          <div className="flex items-center space-x-2 text-xs text-gray-300">
            {waveformData && (
              <span>{studioUtils.msToTime(waveformData.duration)}</span>
            )}
            <span>{Math.round(zoomLevel * 100)}%</span>
          </div>
        </div>
      </div>

      {/* Canvas Container */}
      <div 
        ref={containerRef}
        className="absolute inset-0 pt-12 cursor-pointer"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <canvas
          ref={canvasRef}
          className="w-full h-full"
        />
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="absolute inset-0 bg-gray-900 bg-opacity-75 flex items-center justify-center">
          <div className="text-white text-sm">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
            Loading waveform...
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="absolute inset-0 bg-gray-900 bg-opacity-75 flex items-center justify-center">
          <div className="text-red-400 text-sm text-center">
            <div className="mb-2">⚠️</div>
            <div>{error}</div>
          </div>
        </div>
      )}

      {/* Current Time Indicator */}
      {showTimecode && waveformData && (
        <div className="absolute bottom-2 left-2 bg-black bg-opacity-50 rounded px-2 py-1 text-xs text-white font-mono">
          {studioUtils.msToTime(currentTime)} / {studioUtils.msToTime(waveformData.duration)}
        </div>
      )}
    </div>
  );
};

export default WaveformVisualizer;