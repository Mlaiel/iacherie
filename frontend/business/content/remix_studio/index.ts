/**
 * 🎵 Remix Studio Index - Central Export Hub
 * 
 * @fileoverview Central export point for remix studio functionality
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

// Re-export all from the unified engine
export * from '../../remix_studio_engine';
export { default } from '../../remix_studio_engine';

// Re-export specific commonly used types for backwards compatibility
export type {
  StudioState,
  AudioTrack,
  AudioEffect,
  AIAssistantSuggestion,
  CollaborationUser,
  ExportSettings,
  VirtualInstrument,
  StudioEffect
} from '../../remix_studio_engine';

// Re-export styles and utilities
export { studioColors, studioUtils } from '../../remix_studio_engine';