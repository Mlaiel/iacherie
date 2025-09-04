/**
 * Remix Studio Styling System
 * 
 * Professional styling system for the Creative Studio Interface.
 * Provides cohesive design language for audio production workflows.
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

// Studio Color Palette
export const studioColors = {
  // Primary Studio Colors
  studio: {
    primary: '#1a1a2e',
    secondary: '#16213e', 
    accent: '#0f3460',
    highlight: '#e94560',
    success: '#4ade80',
    warning: '#fbbf24',
    error: '#ef4444',
  },
  
  // Audio Visualization Colors
  audio: {
    waveform: '#3b82f6',
    spectrum: '#8b5cf6',
    peak: '#ef4444',
    rms: '#10b981',
    silence: '#6b7280',
  },
  
  // Track Colors for Multi-Track Interface
  tracks: {
    track1: '#ef4444',
    track2: '#f97316', 
    track3: '#eab308',
    track4: '#22c55e',
    track5: '#06b6d4',
    track6: '#3b82f6',
    track7: '#8b5cf6',
    track8: '#ec4899',
  },
  
  // Control Panel Colors
  controls: {
    knob: '#374151',
    knobActive: '#4f46e5',
    slider: '#6b7280',
    sliderActive: '#3b82f6',
    button: '#1f2937',
    buttonActive: '#4f46e5',
    buttonDanger: '#dc2626',
  },
  
  // Status Colors
  status: {
    recording: '#dc2626',
    playing: '#22c55e',
    paused: '#f59e0b',
    stopped: '#6b7280',
    processing: '#3b82f6',
    offline: '#9ca3af',
  }
} as const;

// Typography System
export const studioTypography = {
  // Font Families
  fonts: {
    primary: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    mono: "'JetBrains Mono', 'Fira Code', 'Consolas', monospace",
    display: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
  },
  
  // Font Sizes
  sizes: {
    xs: '0.75rem',    // 12px
    sm: '0.875rem',   // 14px
    base: '1rem',     // 16px
    lg: '1.125rem',   // 18px
    xl: '1.25rem',    // 20px
    '2xl': '1.5rem',  // 24px
    '3xl': '1.875rem', // 30px
    '4xl': '2.25rem',  // 36px
  },
  
  // Font Weights
  weights: {
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
  }
} as const;

// Component-Specific Styles
export const studioComponents = {
  // Timeline Editor Styles
  timeline: {
    height: '400px',
    trackHeight: '60px',
    rulerHeight: '30px',
    scrollbarWidth: '12px',
    gridColor: '#374151',
    playheadColor: '#ef4444',
    selectionColor: 'rgba(59, 130, 246, 0.3)',
  },
  
  // Mixer Styles
  mixer: {
    channelWidth: '80px',
    faderHeight: '300px',
    knobSize: '40px',
    meterWidth: '20px',
    meterHeight: '200px',
  },
  
  // Waveform Visualizer Styles  
  waveform: {
    height: '120px',
    backgroundColor: studioColors.studio.primary,
    waveColor: studioColors.audio.waveform,
    progressColor: studioColors.studio.highlight,
    cursorColor: studioColors.studio.highlight,
  },
  
  // Effects Panel Styles
  effects: {
    knobSize: '50px',
    sliderHeight: '100px',
    buttonHeight: '36px',
    panelPadding: '16px',
  },
  
  // Container Styles
  container: {
    card: 'bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 shadow-sm',
    panel: 'bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700',
    section: 'bg-white dark:bg-slate-800 rounded-md border border-slate-200 dark:border-slate-700',
  },
  
  // Button Styles
  buttons: {
    primary: 'bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg transition-colors',
    secondary: 'bg-slate-200 hover:bg-slate-300 dark:bg-slate-700 dark:hover:bg-slate-600 text-slate-900 dark:text-white font-medium rounded-lg transition-colors',
    danger: 'bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-colors',
    ghost: 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white font-medium transition-colors',
  },

  // Control Styles
  controls: {
    playButton: {
      size: '48px',
      color: studioColors.status.playing,
      hoverColor: '#16a34a',
    },
    stopButton: {
      size: '40px', 
      color: studioColors.status.stopped,
      hoverColor: '#4b5563',
    },
    recordButton: {
      size: '40px',
      color: studioColors.status.recording,
      hoverColor: '#b91c1c',
    },
  }
} as const;

// Utility Functions
export const studioUtils = {
  // Get track color by index
  getTrackColor: (index: number): string => {
    const trackColors = Object.values(studioColors.tracks);
    return trackColors[index % trackColors.length];
  },
  
  // Get component class name
  getClassName: (...classes: (string | undefined | null | false)[]): string => {
    return classes.filter(Boolean).join(' ');
  },
  
  // Convert milliseconds to time format
  msToTime: (ms: number): string => {
    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  },
  
  // Convert frequency to note
  frequencyToNote: (frequency: number): string => {
    const noteNames = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    const a4 = 440;
    const a4Index = 57;
    
    const noteIndex = Math.round(12 * Math.log2(frequency / a4) + a4Index);
    const octave = Math.floor(noteIndex / 12);
    const note = noteNames[noteIndex % 12];
    
    return `${note}${octave}`;
  },
  
  // DB to linear conversion
  dbToLinear: (db: number): number => {
    return Math.pow(10, db / 20);
  },
  
  // Linear to DB conversion
  linearToDb: (linear: number): number => {
    return 20 * Math.log10(linear);
  }
} as const;

// Export all styles as default
export default {
  colors: studioColors,
  typography: studioTypography,
  components: studioComponents,
  container: studioComponents.container,
  buttons: studioComponents.buttons,
  utils: studioUtils,
} as const;