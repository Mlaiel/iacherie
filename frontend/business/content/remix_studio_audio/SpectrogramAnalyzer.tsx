/**
 * @fileoverview Spectrogram Analyzer Component for Audio Studio
 * @author Fahed Mlaiel <mlaiel@live.de> - Audio Engineer Role
 * @copyright 2025 Fahed Mlaiel - All Rights Reserved
 */

'use client';

import React, { useRef, useEffect, useCallback } from 'react';

export interface SpectrogramAnalyzerProps {
  audioContext?: AudioContext;
  analyser?: AnalyserNode;
  isPlaying: boolean;
  width?: number;
  height?: number;
}

const SpectrogramAnalyzer: React.FC<SpectrogramAnalyzerProps> = ({
  audioContext,
  analyser,
  isPlaying,
  width = 800,
  height = 200
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationFrameRef = useRef<number>();

  const drawSpectrogram = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || !analyser) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    analyser.getByteFrequencyData(dataArray);

    // Clear canvas
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, width, height);

    // Draw frequency bars
    const barWidth = width / bufferLength;
    
    for (let i = 0; i < bufferLength; i++) {
      const barHeight = (dataArray[i] / 255) * height;
      
      // Create color gradient based on frequency
      const hue = (i / bufferLength) * 360;
      const saturation = 100;
      const lightness = 50 + (dataArray[i] / 255) * 30;
      
      ctx.fillStyle = `hsl(${hue}, ${saturation}%, ${lightness}%)`;
      ctx.fillRect(i * barWidth, height - barHeight, barWidth, barHeight);
    }

    if (isPlaying) {
      animationFrameRef.current = requestAnimationFrame(drawSpectrogram);
    }
  }, [analyser, isPlaying, width, height]);

  useEffect(() => {
    if (isPlaying) {
      drawSpectrogram();
    } else if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isPlaying, drawSpectrogram]);

  return (
    <div className="spectrogram-analyzer">
      <h4 className="text-white text-sm font-medium mb-2">Frequency Spectrum</h4>
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        className="w-full border border-gray-700 rounded bg-black"
      />
      <div className="frequency-labels flex justify-between text-xs text-gray-400 mt-1">
        <span>20Hz</span>
        <span>1kHz</span>
        <span>5kHz</span>
        <span>20kHz</span>
      </div>
    </div>
  );
};

export default SpectrogramAnalyzer;