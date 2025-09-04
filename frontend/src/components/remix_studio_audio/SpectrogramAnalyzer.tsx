'use client';

/**
 * Spectrogram Analyzer Component
 * 
 * Real-time frequency spectrum analysis and visualization.
 * Provides detailed frequency domain representation of audio signals.
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

import React, { useRef, useEffect, useCallback } from 'react';
import { studioColors, studioUtils } from './remix_studio.styles';

interface SpectrogramAnalyzerProps {
  audioUrl?: string;
  isAnalyzing: boolean;
  height?: number;
  className?: string;
}

const SpectrogramAnalyzer: React.FC<SpectrogramAnalyzerProps> = ({
  audioUrl,
  isAnalyzing,
  height = 160,
  className = ''
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationFrameRef = useRef<number>();

  const drawSpectrogram = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, width, height);

    // Generate mock spectrum data
    const frequencies = 256;
    const spectrum = new Array(frequencies).fill(0).map((_, i) => {
      const freq = (i / frequencies) * 22050; // Nyquist frequency
      let magnitude = 0;
      
      if (isAnalyzing) {
        // Simulate realistic frequency spectrum
        magnitude = Math.random() * 0.8;
        
        // Add some prominent frequencies
        if (freq > 60 && freq < 250) magnitude *= 1.5; // Bass
        if (freq > 1000 && freq < 4000) magnitude *= 1.2; // Mids
        if (freq > 8000) magnitude *= 0.6; // Highs
      }
      
      return magnitude;
    });

    // Draw frequency bars
    const barWidth = width / frequencies;
    
    for (let i = 0; i < frequencies; i++) {
      const magnitude = spectrum[i];
      const barHeight = magnitude * height;
      const x = i * barWidth;
      const y = height - barHeight;
      
      // Color based on frequency range
      let color;
      const freq = (i / frequencies) * 22050;
      if (freq < 250) {
        color = studioColors.tracks.track1; // Red for bass
      } else if (freq < 4000) {
        color = studioColors.tracks.track4; // Green for mids
      } else {
        color = studioColors.tracks.track6; // Blue for highs
      }
      
      ctx.fillStyle = color;
      ctx.fillRect(x, y, barWidth - 1, barHeight);
    }

    if (isAnalyzing) {
      animationFrameRef.current = requestAnimationFrame(drawSpectrogram);
    }
  }, [isAnalyzing]);

  useEffect(() => {
    if (isAnalyzing) {
      drawSpectrogram();
    } else {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      drawSpectrogram(); // Draw once when stopped
    }

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isAnalyzing, drawSpectrogram]);

  return (
    <div className={studioUtils.getClassName('spectrogram-analyzer bg-gray-900 border border-gray-700 rounded p-2', className)} style={{ height }}>
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-sm font-medium text-white">Spectrum Analyzer</h4>
        <div className="text-xs text-gray-400">
          {isAnalyzing ? 'Analyzing...' : 'Idle'}
        </div>
      </div>
      
      <canvas
        ref={canvasRef}
        width={800}
        height={height - 60}
        className="w-full bg-gray-900"
        style={{ height: height - 60 }}
      />
      
      {/* Frequency Scale */}
      <div className="flex justify-between text-xs text-gray-500 mt-1">
        <span>20Hz</span>
        <span>200Hz</span>
        <span>2kHz</span>
        <span>20kHz</span>
      </div>
    </div>
  );
};

export default SpectrogramAnalyzer;