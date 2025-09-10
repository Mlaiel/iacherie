/**
 * Ainflue Desktop - Studio Timeline Component
 * 
 * Professional timeline editing interface for multi-track content creation
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This software is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

const { EventEmitter } = require('events');
const log = require('electron-log');

class StudioTimeline extends EventEmitter {
  constructor() {
    super();
    this.tracks = new Map();
    this.clips = new Map();
    this.playhead = 0;
    this.zoom = 1.0;
    this.selection = { start: 0, end: 0 };
    this.isPlaying = false;
    this.duration = 0;
    this.fps = 30;
    this.sampleRate = 48000;
    this.undoStack = [];
    this.redoStack = [];
    this.maxUndoSize = 50;
    
    // Timeline settings
    this.settings = {
      snapEnabled: true,
      snapGrid: 'beats',
      magnetEnabled: true,
      autoScroll: true,
      showWaveforms: true,
      showThumbnails: true,
      trackHeight: 80,
      minTrackHeight: 40,
      maxTrackHeight: 200
    };
    
    // Track types
    this.trackTypes = {
      audio: 'Audio Track',
      video: 'Video Track',
      subtitle: 'Subtitle Track',
      marker: 'Marker Track',
      automation: 'Automation Track'
    };
  }

  async initialize() {
    try {
      log.info('Initializing Studio Timeline...');
      
      // Setup default tracks
      await this.createDefaultTracks();
      
      // Setup keyboard shortcuts
      this.setupKeyboardShortcuts();
      
      // Setup UI elements
      this.setupTimelineUI();
      
      log.info('Studio Timeline initialized successfully');
      this.emit('timeline:ready');
      
    } catch (error) {
      log.error('Failed to initialize Studio Timeline:', error);
      throw error;
    }
  }

  async createDefaultTracks() {
    // Create master audio track
    await this.addTrack({
      name: 'Master Audio',
      type: 'audio',
      isMaster: true,
      muted: false,
      solo: false,
      volume: 1.0,
      pan: 0
    });
    
    // Create default video track
    await this.addTrack({
      name: 'Video 1',
      type: 'video',
      muted: false,
      solo: false,
      opacity: 1.0,
      blendMode: 'normal'
    });
  }

  async addTrack(trackData) {
    const trackId = `track_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const track = {
      id: trackId,
      name: trackData.name || `Track ${this.tracks.size + 1}`,
      type: trackData.type || 'audio',
      clips: [],
      muted: trackData.muted || false,
      solo: trackData.solo || false,
      locked: trackData.locked || false,
      height: trackData.height || this.settings.trackHeight,
      color: trackData.color || this.generateTrackColor(),
      effects: [],
      automation: new Map(),
      created: new Date().toISOString(),
      ...trackData
    };

    // Type-specific properties
    if (track.type === 'audio') {
      track.volume = trackData.volume !== undefined ? trackData.volume : 1.0;
      track.pan = trackData.pan !== undefined ? trackData.pan : 0;
      track.inputGain = trackData.inputGain !== undefined ? trackData.inputGain : 1.0;
    }
    
    if (track.type === 'video') {
      track.opacity = trackData.opacity !== undefined ? trackData.opacity : 1.0;
      track.blendMode = trackData.blendMode || 'normal';
      track.transform = {
        x: 0, y: 0, scaleX: 1, scaleY: 1, rotation: 0
      };
    }

    this.tracks.set(trackId, track);
    
    this.pushUndo('add_track', { trackId, track: { ...track } });
    
    log.info(`Added track: ${track.name} (${trackId})`);
    this.emit('track:added', { track });
    
    return track;
  }

  async removeTrack(trackId) {
    const track = this.tracks.get(trackId);
    if (!track) {
      throw new Error(`Track not found: ${trackId}`);
    }
    
    if (track.isMaster) {
      throw new Error('Cannot remove master track');
    }
    
    // Remove all clips from track
    for (const clipId of track.clips) {
      this.clips.delete(clipId);
    }
    
    this.tracks.delete(trackId);
    
    this.pushUndo('remove_track', { trackId, track: { ...track } });
    
    log.info(`Removed track: ${track.name} (${trackId})`);
    this.emit('track:removed', { trackId, track });
  }

  async addClip(trackId, clipData) {
    const track = this.tracks.get(trackId);
    if (!track) {
      throw new Error(`Track not found: ${trackId}`);
    }
    
    const clipId = `clip_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const clip = {
      id: clipId,
      trackId,
      name: clipData.name || 'Untitled Clip',
      startTime: clipData.startTime || 0,
      duration: clipData.duration || 5,
      offset: clipData.offset || 0,
      source: clipData.source,
      muted: clipData.muted || false,
      locked: clipData.locked || false,
      color: clipData.color || track.color,
      effects: [],
      created: new Date().toISOString(),
      ...clipData
    };

    // Validate clip placement
    if (!this.canPlaceClip(clip)) {
      throw new Error('Clip overlaps with existing content');
    }

    this.clips.set(clipId, clip);
    track.clips.push(clipId);
    
    // Update timeline duration if needed
    const clipEnd = clip.startTime + clip.duration;
    if (clipEnd > this.duration) {
      this.duration = clipEnd;
    }
    
    this.pushUndo('add_clip', { clipId, clip: { ...clip } });
    
    log.info(`Added clip: ${clip.name} to track ${track.name}`);
    this.emit('clip:added', { clip, track });
    
    return clip;
  }

  async removeClip(clipId) {
    const clip = this.clips.get(clipId);
    if (!clip) {
      throw new Error(`Clip not found: ${clipId}`);
    }
    
    const track = this.tracks.get(clip.trackId);
    if (track) {
      const clipIndex = track.clips.indexOf(clipId);
      if (clipIndex > -1) {
        track.clips.splice(clipIndex, 1);
      }
    }
    
    this.clips.delete(clipId);
    
    this.pushUndo('remove_clip', { clipId, clip: { ...clip } });
    
    log.info(`Removed clip: ${clip.name} (${clipId})`);
    this.emit('clip:removed', { clipId, clip });
  }

  canPlaceClip(clip) {
    const track = this.tracks.get(clip.trackId);
    if (!track) return false;
    
    // Check for overlaps with existing clips
    for (const existingClipId of track.clips) {
      const existingClip = this.clips.get(existingClipId);
      if (!existingClip || existingClip.id === clip.id) continue;
      
      const clipEnd = clip.startTime + clip.duration;
      const existingEnd = existingClip.startTime + existingClip.duration;
      
      // Check for overlap
      if (clip.startTime < existingEnd && clipEnd > existingClip.startTime) {
        return false;
      }
    }
    
    return true;
  }

  moveClip(clipId, newStartTime, newTrackId = null) {
    const clip = this.clips.get(clipId);
    if (!clip) {
      throw new Error(`Clip not found: ${clipId}`);
    }
    
    const oldStartTime = clip.startTime;
    const oldTrackId = clip.trackId;
    
    // Create temporary clip for validation
    const tempClip = {
      ...clip,
      startTime: newStartTime,
      trackId: newTrackId || clip.trackId
    };
    
    if (!this.canPlaceClip(tempClip)) {
      throw new Error('Cannot place clip at the specified position');
    }
    
    // Move clip between tracks if needed
    if (newTrackId && newTrackId !== clip.trackId) {
      const oldTrack = this.tracks.get(clip.trackId);
      const newTrack = this.tracks.get(newTrackId);
      
      if (!newTrack) {
        throw new Error(`Target track not found: ${newTrackId}`);
      }
      
      // Remove from old track
      if (oldTrack) {
        const clipIndex = oldTrack.clips.indexOf(clipId);
        if (clipIndex > -1) {
          oldTrack.clips.splice(clipIndex, 1);
        }
      }
      
      // Add to new track
      newTrack.clips.push(clipId);
      clip.trackId = newTrackId;
    }
    
    clip.startTime = newStartTime;
    
    this.pushUndo('move_clip', {
      clipId,
      oldStartTime,
      oldTrackId,
      newStartTime,
      newTrackId: clip.trackId
    });
    
    this.emit('clip:moved', { clipId, clip, oldStartTime, oldTrackId });
  }

  trimClip(clipId, newStartTime, newDuration) {
    const clip = this.clips.get(clipId);
    if (!clip) {
      throw new Error(`Clip not found: ${clipId}`);
    }
    
    const oldStartTime = clip.startTime;
    const oldDuration = clip.duration;
    
    // Validate new dimensions
    if (newDuration <= 0) {
      throw new Error('Clip duration must be positive');
    }
    
    clip.startTime = newStartTime;
    clip.duration = newDuration;
    
    this.pushUndo('trim_clip', {
      clipId,
      oldStartTime,
      oldDuration,
      newStartTime,
      newDuration
    });
    
    this.emit('clip:trimmed', { clipId, clip, oldStartTime, oldDuration });
  }

  setPlayhead(time) {
    if (time < 0) time = 0;
    if (time > this.duration) time = this.duration;
    
    this.playhead = time;
    this.emit('playhead:changed', { time });
  }

  play() {
    if (this.isPlaying) return;
    
    this.isPlaying = true;
    this.emit('playback:started', { time: this.playhead });
    
    // Start playback timer
    this.playbackTimer = setInterval(() => {
      this.playhead += 1 / this.fps;
      
      if (this.playhead >= this.duration) {
        this.stop();
        return;
      }
      
      this.emit('playhead:changed', { time: this.playhead });
    }, 1000 / this.fps);
  }

  pause() {
    if (!this.isPlaying) return;
    
    this.isPlaying = false;
    
    if (this.playbackTimer) {
      clearInterval(this.playbackTimer);
      this.playbackTimer = null;
    }
    
    this.emit('playback:paused', { time: this.playhead });
  }

  stop() {
    this.pause();
    this.setPlayhead(0);
    this.emit('playback:stopped');
  }

  setZoom(zoomLevel) {
    if (zoomLevel < 0.1) zoomLevel = 0.1;
    if (zoomLevel > 10) zoomLevel = 10;
    
    this.zoom = zoomLevel;
    this.emit('zoom:changed', { zoom: zoomLevel });
  }

  setSelection(start, end) {
    if (start < 0) start = 0;
    if (end > this.duration) end = this.duration;
    if (start > end) [start, end] = [end, start];
    
    this.selection = { start, end };
    this.emit('selection:changed', { selection: this.selection });
  }

  clearSelection() {
    this.selection = { start: 0, end: 0 };
    this.emit('selection:cleared');
  }

  // Snap to grid functionality
  snapTime(time) {
    if (!this.settings.snapEnabled) return time;
    
    const snapInterval = this.getSnapInterval();
    return Math.round(time / snapInterval) * snapInterval;
  }

  getSnapInterval() {
    switch (this.settings.snapGrid) {
      case 'frames': return 1 / this.fps;
      case 'seconds': return 1;
      case 'beats': return 60 / 120; // Assuming 120 BPM
      case 'bars': return (60 / 120) * 4;
      default: return 1 / this.fps;
    }
  }

  // Undo/Redo functionality
  pushUndo(action, data) {
    this.undoStack.push({ action, data, timestamp: Date.now() });
    
    if (this.undoStack.length > this.maxUndoSize) {
      this.undoStack.shift();
    }
    
    // Clear redo stack when new action is performed
    this.redoStack.length = 0;
    
    this.emit('history:changed', {
      canUndo: this.canUndo(),
      canRedo: this.canRedo()
    });
  }

  undo() {
    if (!this.canUndo()) return false;
    
    const operation = this.undoStack.pop();
    this.redoStack.push(operation);
    
    this.executeUndoRedo(operation, true);
    
    this.emit('history:changed', {
      canUndo: this.canUndo(),
      canRedo: this.canRedo()
    });
    
    return true;
  }

  redo() {
    if (!this.canRedo()) return false;
    
    const operation = this.redoStack.pop();
    this.undoStack.push(operation);
    
    this.executeUndoRedo(operation, false);
    
    this.emit('history:changed', {
      canUndo: this.canUndo(),
      canRedo: this.canRedo()
    });
    
    return true;
  }

  canUndo() {
    return this.undoStack.length > 0;
  }

  canRedo() {
    return this.redoStack.length > 0;
  }

  executeUndoRedo(operation, isUndo) {
    const { action, data } = operation;
    
    switch (action) {
      case 'add_track':
        if (isUndo) {
          this.tracks.delete(data.trackId);
        } else {
          this.tracks.set(data.trackId, data.track);
        }
        break;
        
      case 'remove_track':
        if (isUndo) {
          this.tracks.set(data.trackId, data.track);
        } else {
          this.tracks.delete(data.trackId);
        }
        break;
        
      case 'add_clip':
        if (isUndo) {
          this.clips.delete(data.clipId);
          const track = this.tracks.get(data.clip.trackId);
          if (track) {
            const index = track.clips.indexOf(data.clipId);
            if (index > -1) track.clips.splice(index, 1);
          }
        } else {
          this.clips.set(data.clipId, data.clip);
          const track = this.tracks.get(data.clip.trackId);
          if (track) {
            track.clips.push(data.clipId);
          }
        }
        break;
        
      case 'move_clip':
        const clip = this.clips.get(data.clipId);
        if (clip) {
          if (isUndo) {
            clip.startTime = data.oldStartTime;
            if (data.oldTrackId !== data.newTrackId) {
              // Move back to old track
              const newTrack = this.tracks.get(data.newTrackId);
              const oldTrack = this.tracks.get(data.oldTrackId);
              if (newTrack && oldTrack) {
                const index = newTrack.clips.indexOf(data.clipId);
                if (index > -1) newTrack.clips.splice(index, 1);
                oldTrack.clips.push(data.clipId);
                clip.trackId = data.oldTrackId;
              }
            }
          } else {
            clip.startTime = data.newStartTime;
            if (data.oldTrackId !== data.newTrackId) {
              // Move to new track
              const oldTrack = this.tracks.get(data.oldTrackId);
              const newTrack = this.tracks.get(data.newTrackId);
              if (oldTrack && newTrack) {
                const index = oldTrack.clips.indexOf(data.clipId);
                if (index > -1) oldTrack.clips.splice(index, 1);
                newTrack.clips.push(data.clipId);
                clip.trackId = data.newTrackId;
              }
            }
          }
        }
        break;
    }
    
    this.emit('timeline:updated');
  }

  // Utility methods
  generateTrackColor() {
    const colors = [
      '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
      '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
    ];
    return colors[this.tracks.size % colors.length];
  }

  getTrackAtPosition(y) {
    let currentY = 0;
    for (const [trackId, track] of this.tracks) {
      if (y >= currentY && y < currentY + track.height) {
        return track;
      }
      currentY += track.height;
    }
    return null;
  }

  getTimeAtPosition(x) {
    // Convert pixel position to time based on zoom
    return x / (this.zoom * 100); // Assuming 100 pixels per second at zoom 1.0
  }

  getPositionAtTime(time) {
    // Convert time to pixel position based on zoom
    return time * this.zoom * 100;
  }

  setupKeyboardShortcuts() {
    // Placeholder for keyboard shortcut setup
    // Would be implemented with actual UI framework
  }

  setupTimelineUI() {
    // Placeholder for UI setup
    // Would be implemented with actual UI framework
  }

  // Export/Import
  exportTimeline() {
    return {
      version: '1.0.0',
      duration: this.duration,
      fps: this.fps,
      sampleRate: this.sampleRate,
      tracks: Array.from(this.tracks.values()),
      clips: Array.from(this.clips.values()),
      settings: { ...this.settings },
      exported: new Date().toISOString()
    };
  }

  importTimeline(timelineData) {
    this.tracks.clear();
    this.clips.clear();
    
    this.duration = timelineData.duration || 0;
    this.fps = timelineData.fps || 30;
    this.sampleRate = timelineData.sampleRate || 48000;
    
    // Import tracks
    for (const track of timelineData.tracks || []) {
      this.tracks.set(track.id, track);
    }
    
    // Import clips
    for (const clip of timelineData.clips || []) {
      this.clips.set(clip.id, clip);
    }
    
    // Import settings
    if (timelineData.settings) {
      Object.assign(this.settings, timelineData.settings);
    }
    
    this.emit('timeline:imported', { timelineData });
  }

  // Getters
  getTracks() {
    return Array.from(this.tracks.values());
  }

  getClips() {
    return Array.from(this.clips.values());
  }

  getTrackClips(trackId) {
    const track = this.tracks.get(trackId);
    if (!track) return [];
    
    return track.clips.map(clipId => this.clips.get(clipId)).filter(Boolean);
  }

  // Cleanup
  cleanup() {
    if (this.playbackTimer) {
      clearInterval(this.playbackTimer);
      this.playbackTimer = null;
    }
    
    this.tracks.clear();
    this.clips.clear();
    this.undoStack.length = 0;
    this.redoStack.length = 0;
    
    log.info('Studio Timeline cleaned up');
  }
}

module.exports = StudioTimeline;