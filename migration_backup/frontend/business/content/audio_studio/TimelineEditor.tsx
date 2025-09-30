'use client';

/**
 * Timeline Editor Component
 * 
 * Professional multi-track timeline editor with drag-drop functionality.
 * Supports precise audio editing with snap-to-grid and advanced selection.
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

import React, { useState, useRef, useCallback, useEffect, useMemo } from 'react';
import { 
  PlusIcon, 
  ScissorsIcon, 
  DocumentDuplicateIcon,
  TrashIcon,
  AdjustmentsHorizontalIcon,
  MagnifyingGlassPlusIcon,
  MagnifyingGlassMinusIcon
} from '@heroicons/react/24/outline';
import { studioColors, studioComponents, studioUtils } from '../remix_studio/remix_studio.styles';
import type { AudioTrack } from '../remix_studio/index';

interface TimelineEditorProps {
  tracks: AudioTrack[];
  currentTime: number;
  zoomLevel: number;
  isPlaying: boolean;
  selectedTracks: string[];
  onTimeChange: (time: number) => void;
  onTrackUpdate: (trackId: string, updates: Partial<AudioTrack>) => void;
  onTrackSelect: (trackId: string, multiSelect?: boolean) => void;
  onAddTrack: (track: Omit<AudioTrack, 'id'>) => void;
  onRemoveTrack: (trackId: string) => void;
  className?: string;
}

interface TimelineSelection {
  startTime: number;
  endTime: number;
  tracks: string[];
}

interface DragState {
  isDragging: boolean;
  dragType: 'move' | 'resize-left' | 'resize-right' | 'select' | null;
  startX: number;
  startY: number;
  initialTime: number;
  targetTrackId?: string;
}

const TimelineEditor: React.FC<TimelineEditorProps> = ({
  tracks,
  currentTime,
  zoomLevel,
  isPlaying,
  selectedTracks,
  onTimeChange,
  onTrackUpdate,
  onTrackSelect,
  onAddTrack,
  onRemoveTrack,
  className = ''
}) => {
  const timelineRef = useRef<HTMLDivElement>(null);
  const playheadRef = useRef<HTMLDivElement>(null);
  
  // Timeline State
  const [selection, setSelection] = useState<TimelineSelection | null>(null);
  const [dragState, setDragState] = useState<DragState>({
    isDragging: false,
    dragType: null,
    startX: 0,
    startY: 0,
    initialTime: 0
  });
  const [snapToGrid, setSnapToGrid] = useState(true);
  const [gridSize, setGridSize] = useState(0.25); // Quarter note grid
  const [showWaveforms, setShowWaveforms] = useState(true);

  // Timeline Calculations
  const pixelsPerSecond = 100 * zoomLevel;
  const totalDuration = Math.max(...tracks.map(t => t.startTime + t.duration), 300000); // Min 5 minutes
  const timelineWidth = (totalDuration / 1000) * pixelsPerSecond;
  
  // Grid calculations
  const gridInterval = gridSize * 1000; // Convert to milliseconds
  const gridPixelInterval = (gridInterval / 1000) * pixelsPerSecond;
  
  // Time conversion utilities
  const timeToPixels = useCallback((time: number) => {
    return (time / 1000) * pixelsPerSecond;
  }, [pixelsPerSecond]);
  
  const pixelsToTime = useCallback((pixels: number) => {
    return (pixels / pixelsPerSecond) * 1000;
  }, [pixelsPerSecond]);
  
  const snapTime = useCallback((time: number) => {
    if (!snapToGrid) return time;
    return Math.round(time / gridInterval) * gridInterval;
  }, [snapToGrid, gridInterval]);

  // Mouse Event Handlers
  const handleMouseDown = useCallback((event: React.MouseEvent, trackId?: string, dragType: DragState['dragType'] = 'select') => {
    const rect = timelineRef.current?.getBoundingClientRect();
    if (!rect) return;

    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    const time = pixelsToTime(x);

    setDragState({
      isDragging: true,
      dragType,
      startX: x,
      startY: y,
      initialTime: time,
      targetTrackId: trackId
    });

    if (dragType === 'select') {
      setSelection({
        startTime: time,
        endTime: time,
        tracks: trackId ? [trackId] : []
      });
    }

    event.preventDefault();
  }, [pixelsToTime]);

  const handleMouseMove = useCallback((event: React.MouseEvent) => {
    if (!dragState.isDragging || !timelineRef.current) return;

    const rect = timelineRef.current.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    const currentTime = pixelsToTime(x);

    switch (dragState.dragType) {
      case 'select':
        if (selection) {
          setSelection({
            ...selection,
            endTime: currentTime
          });
        }
        break;
        
      case 'move':
        if (dragState.targetTrackId && dragState.initialTime !== undefined) {
          const timeDelta = currentTime - dragState.initialTime;
          const track = tracks.find(t => t.id === dragState.targetTrackId);
          if (track) {
            const newStartTime = Math.max(0, snapTime(track.startTime + timeDelta));
            onTrackUpdate(dragState.targetTrackId, { startTime: newStartTime });
          }
        }
        break;
        
      case 'resize-left':
        if (dragState.targetTrackId) {
          const track = tracks.find(t => t.id === dragState.targetTrackId);
          if (track) {
            const newStartTime = snapTime(currentTime);
            const newDuration = track.duration + (track.startTime - newStartTime);
            if (newDuration > 1000) { // Minimum 1 second
              onTrackUpdate(dragState.targetTrackId, {
                startTime: newStartTime,
                duration: newDuration
              });
            }
          }
        }
        break;
        
      case 'resize-right':
        if (dragState.targetTrackId) {
          const track = tracks.find(t => t.id === dragState.targetTrackId);
          if (track) {
            const newDuration = Math.max(1000, snapTime(currentTime - track.startTime));
            onTrackUpdate(dragState.targetTrackId, { duration: newDuration });
          }
        }
        break;
    }
  }, [dragState, pixelsToTime, snapTime, selection, tracks, onTrackUpdate]);

  const handleMouseUp = useCallback(() => {
    setDragState({
      isDragging: false,
      dragType: null,
      startX: 0,
      startY: 0,
      initialTime: 0
    });
  }, []);

  // Timeline Click Handler
  const handleTimelineClick = useCallback((event: React.MouseEvent) => {
    if (dragState.isDragging) return;
    
    const rect = timelineRef.current?.getBoundingClientRect();
    if (!rect) return;

    const x = event.clientX - rect.left;
    const time = snapTime(pixelsToTime(x));
    onTimeChange(time);
  }, [dragState.isDragging, pixelsToTime, snapTime, onTimeChange]);

  // Track Actions
  const handleAddTrack = useCallback(() => {
    const newTrack = {
      name: `Track ${tracks.length + 1}`,
      type: 'audio' as const,
      color: studioUtils.getTrackColor(tracks.length.toString()),
      volume: 0.8,
      pan: 0,
      muted: false,
      solo: false,
      armed: false,
      startTime: 0,
      duration: 120000,
      length: 120000,
      effects: []
    };
    onAddTrack(newTrack);
  }, [tracks.length, onAddTrack]);

  const handleSplitTrack = useCallback(() => {
    if (selectedTracks.length !== 1) return;
    
    const trackId = selectedTracks[0];
    const track = tracks.find(t => t.id === trackId);
    if (!track) return;

    const splitTime = currentTime - track.startTime;
    if (splitTime > 0 && splitTime < track.duration) {
      // Update original track
      onTrackUpdate(trackId, { duration: splitTime });
      
      // Create new track for the second part
      const newTrack = {
        ...track,
        name: `${track.name} (Split)`,
        startTime: currentTime,
        duration: track.duration - splitTime
      };
      onAddTrack(newTrack);
    }
  }, [selectedTracks, tracks, currentTime, onTrackUpdate, onAddTrack]);

  const handleDuplicateTrack = useCallback(() => {
    selectedTracks.forEach(trackId => {
      const track = tracks.find(t => t.id === trackId);
      if (track) {
        const duplicatedTrack = {
          ...track,
          name: `${track.name} (Copy)`,
          startTime: track.startTime + track.duration
        };
        onAddTrack(duplicatedTrack);
      }
    });
  }, [selectedTracks, tracks, onAddTrack]);

  // Zoom Controls
  const handleZoomIn = useCallback(() => {
    const newZoom = Math.min(zoomLevel * 1.5, 10);
    // Would call parent zoom handler if available
  }, [zoomLevel]);

  const handleZoomOut = useCallback(() => {
    const newZoom = Math.max(zoomLevel / 1.5, 0.1);
    // Would call parent zoom handler if available
  }, [zoomLevel]);

  // Keyboard Shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.target instanceof HTMLInputElement) return;

      switch (event.code) {
        case 'Delete':
        case 'Backspace':
          if (selectedTracks.length > 0) {
            selectedTracks.forEach(trackId => onRemoveTrack(trackId));
          }
          break;
        case 'KeyD':
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault();
            handleDuplicateTrack();
          }
          break;
        case 'KeyS':
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault();
            handleSplitTrack();
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedTracks, handleDuplicateTrack, handleSplitTrack, onRemoveTrack]);

  // Render Grid
  const renderGrid = useMemo(() => {
    const gridLines = [];
    for (let x = 0; x < timelineWidth; x += gridPixelInterval) {
      gridLines.push(
        <line
          key={x}
          x1={x}
          y1={0}
          x2={x}
          y2="100%"
          stroke={studioComponents.timeline.gridColor}
          strokeWidth={0.5}
          opacity={0.3}
        />
      );
    }
    return gridLines;
  }, [timelineWidth, gridPixelInterval]);

  // Render Time Ruler
  const renderTimeRuler = useMemo(() => {
    const markers = [];
    const majorInterval = 10000; // 10 seconds
    const majorPixelInterval = (majorInterval / 1000) * pixelsPerSecond;
    
    for (let x = 0; x < timelineWidth; x += majorPixelInterval) {
      const time = pixelsToTime(x);
      markers.push(
        <div
          key={x}
          className="absolute text-xs text-gray-400"
          style={{ left: x - 20, top: 5, width: 40, textAlign: 'center' }}
        >
          {studioUtils.msToTime(time)}
        </div>
      );
    }
    return markers;
  }, [timelineWidth, pixelsPerSecond, pixelsToTime]);

  // Render Track
  const renderTrack = useCallback((track: AudioTrack, index: number) => {
    const trackY = index * studioComponents.timeline.trackHeight;
    const trackWidth = timeToPixels(track.duration);
    const trackX = timeToPixels(track.startTime);
    const isSelected = selectedTracks.includes(track.id);

    return (
      <div
        key={track.id}
        className="absolute border border-gray-600 rounded cursor-move select-none"
        style={{
          left: trackX,
          top: trackY + 5,
          width: trackWidth,
          height: studioComponents.timeline.trackHeight - 10,
          backgroundColor: track.color,
          opacity: track.muted ? 0.5 : isSelected ? 0.9 : 0.7,
          borderColor: isSelected ? studioColors.studio.highlight : 'transparent',
          borderWidth: isSelected ? 2 : 1
        }}
        onMouseDown={(e) => {
          handleMouseDown(e, track.id, 'move');
          onTrackSelect(track.id, e.ctrlKey || e.metaKey);
        }}
      >
        {/* Track Name */}
        <div className="p-2 text-xs font-medium text-white truncate">
          {track.name}
        </div>
        
        {/* Waveform Placeholder */}
        {showWaveforms && (
          <div className="absolute bottom-1 left-1 right-1 h-6 bg-black bg-opacity-30 rounded">
            <div className="h-full bg-gradient-to-r from-transparent via-white to-transparent opacity-30"></div>
          </div>
        )}
        
        {/* Resize Handles */}
        <div
          className="absolute left-0 top-0 w-2 h-full cursor-w-resize bg-white bg-opacity-20 hover:bg-opacity-40"
          onMouseDown={(e) => {
            e.stopPropagation();
            handleMouseDown(e, track.id, 'resize-left');
          }}
        />
        <div
          className="absolute right-0 top-0 w-2 h-full cursor-e-resize bg-white bg-opacity-20 hover:bg-opacity-40"
          onMouseDown={(e) => {
            e.stopPropagation();
            handleMouseDown(e, track.id, 'resize-right');
          }}
        />
        
        {/* Track Status Indicators */}
        <div className="absolute top-1 right-1 flex space-x-1">
          {track.muted && (
            <div className="w-2 h-2 bg-red-500 rounded-full" title="Muted" />
          )}
          {track.solo && (
            <div className="w-2 h-2 bg-yellow-500 rounded-full" title="Solo" />
          )}
          {track.armed && (
            <div className="w-2 h-2 bg-red-600 rounded-full animate-pulse" title="Armed for Recording" />
          )}
        </div>
      </div>
    );
  }, [timeToPixels, selectedTracks, showWaveforms, handleMouseDown, onTrackSelect]);

  return (
    <div className={studioUtils.getClassName('timeline-editor bg-gray-900 flex flex-col', className)}>
      {/* Toolbar */}
      <div className="flex items-center justify-between p-3 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center space-x-2">
          <button
            onClick={handleAddTrack}
            className="flex items-center space-x-1 px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm transition-colors"
          >
            <PlusIcon className="h-4 w-4" />
            <span>Add Track</span>
          </button>
          
          <button
            onClick={handleSplitTrack}
            disabled={selectedTracks.length !== 1}
            className="flex items-center space-x-1 px-3 py-1 bg-gray-600 hover:bg-gray-500 disabled:opacity-50 disabled:cursor-not-allowed rounded text-sm transition-colors"
          >
            <ScissorsIcon className="h-4 w-4" />
            <span>Split</span>
          </button>
          
          <button
            onClick={handleDuplicateTrack}
            disabled={selectedTracks.length === 0}
            className="flex items-center space-x-1 px-3 py-1 bg-gray-600 hover:bg-gray-500 disabled:opacity-50 disabled:cursor-not-allowed rounded text-sm transition-colors"
          >
            <DocumentDuplicateIcon className="h-4 w-4" />
            <span>Duplicate</span>
          </button>
          
          <button
            onClick={() => selectedTracks.forEach(onRemoveTrack)}
            disabled={selectedTracks.length === 0}
            className="flex items-center space-x-1 px-3 py-1 bg-red-600 hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed rounded text-sm transition-colors"
          >
            <TrashIcon className="h-4 w-4" />
            <span>Delete</span>
          </button>
        </div>

        <div className="flex items-center space-x-2">
          <label className="flex items-center space-x-2 text-sm">
            <input
              type="checkbox"
              checked={snapToGrid}
              onChange={(e) => setSnapToGrid(e.target.checked)}
              className="rounded"
            />
            <span>Snap to Grid</span>
          </label>
          
          <select
            value={gridSize}
            onChange={(e) => setGridSize(parseFloat(e.target.value))}
            className="px-2 py-1 bg-gray-700 rounded text-sm"
          >
            <option value={0.125}>1/8</option>
            <option value={0.25}>1/4</option>
            <option value={0.5}>1/2</option>
            <option value={1}>1</option>
          </select>
          
          <button
            onClick={handleZoomOut}
            className="p-1 hover:bg-gray-700 rounded"
          >
            <MagnifyingGlassMinusIcon className="h-4 w-4" />
          </button>
          
          <span className="text-sm">{Math.round(zoomLevel * 100)}%</span>
          
          <button
            onClick={handleZoomIn}
            className="p-1 hover:bg-gray-700 rounded"
          >
            <MagnifyingGlassPlusIcon className="h-4 w-4" />
          </button>
          
          <button
            onClick={() => setShowWaveforms(!showWaveforms)}
            className={studioUtils.getClassName(
              'p-1 rounded transition-colors',
              showWaveforms ? 'bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'
            )}
          >
            <AdjustmentsHorizontalIcon className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Timeline Area */}
      <div className="flex-1 relative overflow-auto">
        {/* Time Ruler */}
        <div
          className="relative bg-gray-800 border-b border-gray-700"
          style={{ height: studioComponents.timeline.rulerHeight, width: timelineWidth }}
        >
          {renderTimeRuler}
        </div>
        
        {/* Track Area */}
        <div
          ref={timelineRef}
          className="relative bg-gray-900 cursor-crosshair"
          style={{ 
            height: tracks.length * studioComponents.timeline.trackHeight,
            width: timelineWidth,
            minHeight: 400
          }}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onClick={handleTimelineClick}
        >
          {/* Grid */}
          <svg className="absolute inset-0 pointer-events-none" style={{ width: timelineWidth, height: '100%' }}>
            {renderGrid}
          </svg>
          
          {/* Track Lane Backgrounds */}
          {tracks.map((_, index) => (
            <div
              key={index}
              className="absolute border-b border-gray-700"
              style={{
                top: index * studioComponents.timeline.trackHeight,
                left: 0,
                right: 0,
                height: studioComponents.timeline.trackHeight,
                backgroundColor: index % 2 === 0 ? 'rgba(0,0,0,0.1)' : 'transparent'
              }}
            />
          ))}
          
          {/* Tracks */}
          {tracks.map((track, index) => renderTrack(track, index))}
          
          {/* Selection */}
          {selection && (
            <div
              className="absolute border-2 border-blue-400 bg-blue-400 bg-opacity-20 pointer-events-none"
              style={{
                left: timeToPixels(Math.min(selection.startTime, selection.endTime)),
                top: 0,
                width: timeToPixels(Math.abs(selection.endTime - selection.startTime)),
                height: '100%'
              }}
            />
          )}
          
          {/* Playhead */}
          <div
            ref={playheadRef}
            className="absolute top-0 w-0.5 bg-red-500 pointer-events-none z-10"
            style={{
              left: timeToPixels(currentTime),
              height: '100%',
              boxShadow: '0 0 4px rgba(239, 68, 68, 0.5)'
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default TimelineEditor;