/**
 * 🎵 STUDIOS STORE - Audio & Video Studio Management
 * 
 * Gestion complète des studios audio/vidéo avec:
 * - TTS (Text-to-Speech) avec sélection intelligente
 * - Music generation avec optimisation des coûts
 * - Video editing avec timeline
 * - Export et preview en temps réel
 * - Intégration intelligent_selector pour économiser sur APIs
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @created 2025-10-06
 */

import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { backendAPI } from '../api/backend-client';

// ======================================================================
// TYPES & INTERFACES
// ======================================================================

export interface Studio {
  id: string;
  name: string;
  type: 'audio' | 'video';
  description?: string;
  created_at: string;
  updated_at: string;
  owner_id: string;
  
  // Studio configuration
  settings: StudioSettings;
  
  // Stats
  total_generations: number;
  total_cost: number;  // Track costs!
}

export interface StudioSettings {
  default_voice?: string;          // TTS voice
  default_model?: string;           // Model preference
  prefer_internal: boolean;         // Use AI Leader first
  max_cost_per_generation?: number; // Budget per generation
  quality: 'low' | 'medium' | 'high' | 'ultra';
  auto_save: boolean;
}

export interface AudioProject {
  id: string;
  studio_id: string;
  name: string;
  type: 'tts' | 'music' | 'voice-clone';
  
  // Content
  text?: string;              // For TTS
  music_prompt?: string;      // For music generation
  audio_url?: string;         // Generated audio
  duration?: number;          // In seconds
  
  // Generation details
  model_used?: string;
  cost?: number;
  quality: string;
  
  created_at: string;
}

export interface VideoProject {
  id: string;
  studio_id: string;
  name: string;
  
  // Timeline
  clips: VideoClip[];
  audio_tracks: AudioTrack[];
  
  // Export settings
  resolution: '720p' | '1080p' | '4k';
  fps: 24 | 30 | 60;
  format: 'mp4' | 'mov' | 'webm';
  
  // Generation details
  total_cost?: number;
  
  created_at: string;
  updated_at: string;
}

export interface VideoClip {
  id: string;
  start_time: number;  // seconds
  end_time: number;
  video_url?: string;
  prompt?: string;     // If AI-generated
  model_used?: string;
  cost?: number;
}

export interface AudioTrack {
  id: string;
  audio_url: string;
  start_time: number;
  volume: number;      // 0-100
  type: 'music' | 'voice' | 'sfx';
}

export interface GenerationJob {
  id: string;
  type: 'audio' | 'video';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;    // 0-100
  
  prompt: string;
  model_used?: string;
  estimated_cost?: number;
  actual_cost?: number;
  
  result_url?: string;
  error?: string;
  
  created_at: string;
  completed_at?: string;
}

// ======================================================================
// STORE STATE
// ======================================================================

interface StudiosState {
  // Data
  studios: Studio[];
  selectedStudio: Studio | null;
  audioProjects: AudioProject[];
  videoProjects: VideoProject[];
  
  // Current work
  activeProject: AudioProject | VideoProject | null;
  generationJobs: GenerationJob[];
  activeJob: GenerationJob | null;
  
  // UI State
  loading: boolean;
  error: string | null;
  
  // Preview
  previewUrl: string | null;
  isPlaying: boolean;
  currentTime: number;
  
  // Cost tracking
  totalCostThisMonth: number;
  costByModel: Record<string, number>;
  
  // ======================================================================
  // ACTIONS - STUDIOS
  // ======================================================================
  
  // Fetch all studios
  fetchStudios: () => Promise<void>;
  
  // Fetch single studio
  fetchStudio: (id: string) => Promise<void>;
  
  // Create studio
  createStudio: (data: Partial<Studio>) => Promise<Studio | null>;
  
  // Update studio
  updateStudio: (id: string, data: Partial<Studio>) => Promise<Studio | null>;
  
  // Delete studio
  deleteStudio: (id: string) => Promise<boolean>;
  
  // ======================================================================
  // ACTIONS - AUDIO PROJECTS
  // ======================================================================
  
  // Fetch projects for studio
  fetchAudioProjects: (studioId: string) => Promise<void>;
  
  // Generate TTS
  generateTTS: (params: {
    text: string;
    voice?: string;
    model?: string;
    prefer_internal?: boolean;
    max_cost?: number;
  }) => Promise<AudioProject | null>;
  
  // Generate Music
  generateMusic: (params: {
    prompt: string;
    duration?: number;
    genre?: string;
    model?: string;
    prefer_internal?: boolean;
    max_cost?: number;
  }) => Promise<AudioProject | null>;
  
  // Clone Voice
  cloneVoice: (params: {
    audio_sample_url: string;
    text: string;
    model?: string;
  }) => Promise<AudioProject | null>;
  
  // ======================================================================
  // ACTIONS - VIDEO PROJECTS
  // ======================================================================
  
  // Fetch video projects
  fetchVideoProjects: (studioId: string) => Promise<void>;
  
  // Create video project
  createVideoProject: (data: Partial<VideoProject>) => Promise<VideoProject | null>;
  
  // Add clip to timeline
  addClipToTimeline: (projectId: string, clip: Partial<VideoClip>) => Promise<void>;
  
  // Generate video clip with AI
  generateVideoClip: (params: {
    prompt: string;
    duration?: number;
    quality?: string;
    model?: string;
    prefer_internal?: boolean;
    max_cost?: number;
  }) => Promise<VideoClip | null>;
  
  // Add audio track
  addAudioTrack: (projectId: string, track: Partial<AudioTrack>) => Promise<void>;
  
  // Export video
  exportVideo: (projectId: string, settings: {
    resolution: string;
    fps: number;
    format: string;
  }) => Promise<string | null>;
  
  // ======================================================================
  // ACTIONS - PREVIEW & PLAYBACK
  // ======================================================================
  
  // Load preview
  loadPreview: (url: string) => void;
  
  // Play/pause
  togglePlayback: () => void;
  
  // Seek
  seek: (time: number) => void;
  
  // ======================================================================
  // ACTIONS - COST TRACKING
  // ======================================================================
  
  // Get available models
  getAvailableModels: (type: 'audio' | 'video') => Promise<any>;
  
  // Estimate cost
  estimateCost: (params: {
    type: 'audio' | 'video';
    model: string;
    duration?: number;
    text_length?: number;
  }) => Promise<number>;
  
  // Track cost
  trackCost: (model: string, cost: number) => void;
  
  // Reset monthly costs
  resetMonthlyCosts: () => void;
}

// ======================================================================
// STORE IMPLEMENTATION
// ======================================================================

export const useStudiosStore = create<StudiosState>()(
  immer((set, get) => ({
    // Initial state
    studios: [],
    selectedStudio: null,
    audioProjects: [],
    videoProjects: [],
    activeProject: null,
    generationJobs: [],
    activeJob: null,
    loading: false,
    error: null,
    previewUrl: null,
    isPlaying: false,
    currentTime: 0,
    totalCostThisMonth: 0,
    costByModel: {},
    
    // ======================================================================
    // STUDIOS CRUD
    // ======================================================================
    
    fetchStudios: async () => {
      set({ loading: true, error: null });
      
      try {
        const response = await backendAPI.listStudios();
        
        set({
          studios: response.items as any,
          loading: false,
        });
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : 'Failed to fetch studios',
          loading: false,
        });
      }
    },
    
    fetchStudio: async (id: string) => {
      set({ loading: true, error: null });
      
      try {
        const response = await backendAPI.getStudio(id);
        
        if (response.data) {
          set({
            selectedStudio: response.data as any,
            loading: false,
          });
        }
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : 'Failed to fetch studio',
          loading: false,
        });
      }
    },
    
    createStudio: async (data: Partial<Studio>) => {
      set({ loading: true, error: null });
      
      try {
        // Default settings with cost optimization
        const defaultSettings: StudioSettings = {
          prefer_internal: true,        // ✅ Use AI Leader first!
          max_cost_per_generation: 2.0, // Default $2 budget
          quality: 'high',
          auto_save: true,
          ...data.settings,
        };
        
        const response = await backendAPI.createStudio({
          ...data,
          settings: defaultSettings,
        } as any);
        
        if (response.data) {
          set((state) => {
            state.studios.unshift(response.data as any);
            state.loading = false;
          });
          
          return response.data as any;
        }
        
        return null;
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : 'Failed to create studio',
          loading: false,
        });
        return null;
      }
    },
    
    updateStudio: async (id: string, data: Partial<Studio>) => {
      set({ loading: true, error: null });
      
      try {
        const response = await backendAPI.updateStudio(id, data);
        
        if (response.data) {
          set((state) => {
            const index = state.studios.findIndex(s => s.id === id);
            if (index !== -1) {
              state.studios[index] = response.data as any;
            }
            if (state.selectedStudio?.id === id) {
              state.selectedStudio = response.data as any;
            }
            state.loading = false;
          });
          
          return response.data as any;
        }
        
        return null;
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : 'Failed to update studio',
          loading: false,
        });
        return null;
      }
    },
    
    deleteStudio: async (id: string) => {
      set({ loading: true, error: null });
      
      try {
        await backendAPI.deleteStudio(id);
        
        set((state) => {
          state.studios = state.studios.filter(s => s.id !== id);
          if (state.selectedStudio?.id === id) {
            state.selectedStudio = null;
          }
          state.loading = false;
        });
        
        return true;
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : 'Failed to delete studio',
          loading: false,
        });
        return false;
      }
    },
    
    // ======================================================================
    // AUDIO PROJECTS
    // ======================================================================
    
    fetchAudioProjects: async (studioId: string) => {
      try {
        const response = await backendAPI.listAudioProjects(studioId);
        
        set({ audioProjects: response.items });
      } catch (error) {
        console.error('Failed to fetch audio projects:', error);
      }
    },
    
    generateTTS: async (params) => {
      const studio = get().selectedStudio;
      if (!studio) return null;
      
      set({ loading: true, error: null });
      
      try {
        // Create generation job
        const jobId = `job-${Date.now()}`;
        const job: GenerationJob = {
          id: jobId,
          type: 'audio',
          status: 'processing',
          progress: 10,
          prompt: params.text,
          created_at: new Date().toISOString(),
        };
        
        set((state) => {
          state.generationJobs.unshift(job);
          state.activeJob = job;
        });
        
        // Call backend with intelligent selector params
        const response = await backendAPI.generateAudio({
          prompt: params.text,
          type: 'tts',
          voice: params.voice || studio.settings.default_voice,
          model: params.model || studio.settings.default_model,
          prefer_internal: params.prefer_internal ?? studio.settings.prefer_internal,
          max_cost: params.max_cost || studio.settings.max_cost_per_generation,
        });
        
        if (response.data) {
          const project: AudioProject = {
            id: `audio-${Date.now()}`,
            studio_id: studio.id,
            name: `TTS - ${params.text.substring(0, 30)}...`,
            type: 'tts',
            text: params.text,
            audio_url: response.data.url,
            duration: response.data.duration,
            model_used: response.data.model_used,
            cost: response.data.actual_cost || 0,
            quality: studio.settings.quality,
            created_at: new Date().toISOString(),
          };
          
          // Track cost
          get().trackCost(project.model_used!, project.cost!);
          
          set((state) => {
            state.audioProjects.unshift(project);
            state.activeProject = project;
            state.loading = false;
            
            // Update job
            if (state.activeJob) {
              state.activeJob.status = 'completed';
              state.activeJob.progress = 100;
              state.activeJob.result_url = project.audio_url;
              state.activeJob.actual_cost = project.cost;
              state.activeJob.completed_at = new Date().toISOString();
            }
          });
          
          return project;
        }
        
        return null;
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : 'TTS generation failed',
          loading: false,
        });
        
        // Update job as failed
        set((state) => {
          if (state.activeJob) {
            state.activeJob.status = 'failed';
            state.activeJob.error = error instanceof Error ? error.message : 'Unknown error';
          }
        });
        
        return null;
      }
    },
    
    generateMusic: async (params) => {
      const studio = get().selectedStudio;
      if (!studio) return null;
      
      set({ loading: true, error: null });
      
      try {
        const jobId = `job-${Date.now()}`;
        const job: GenerationJob = {
          id: jobId,
          type: 'audio',
          status: 'processing',
          progress: 10,
          prompt: params.prompt,
          created_at: new Date().toISOString(),
        };
        
        set((state) => {
          state.generationJobs.unshift(job);
          state.activeJob = job;
        });
        
        // Call backend for music generation
        const response = await backendAPI.generateAudio({
          prompt: params.prompt,
          type: 'music',
          duration: params.duration || 30,
          genre: params.genre,
          model: params.model || studio.settings.default_model,
          prefer_internal: params.prefer_internal ?? studio.settings.prefer_internal,
          max_cost: params.max_cost || studio.settings.max_cost_per_generation,
        });
        
        if (response.data) {
          const project: AudioProject = {
            id: `music-${Date.now()}`,
            studio_id: studio.id,
            name: `Music - ${params.prompt.substring(0, 30)}...`,
            type: 'music',
            music_prompt: params.prompt,
            audio_url: response.data.url,
            duration: response.data.duration,
            model_used: response.data.model_used,
            cost: response.data.actual_cost || 0,
            quality: studio.settings.quality,
            created_at: new Date().toISOString(),
          };
          
          get().trackCost(project.model_used!, project.cost!);
          
          set((state) => {
            state.audioProjects.unshift(project);
            state.activeProject = project;
            state.loading = false;
            
            if (state.activeJob) {
              state.activeJob.status = 'completed';
              state.activeJob.progress = 100;
              state.activeJob.result_url = project.audio_url;
              state.activeJob.actual_cost = project.cost;
              state.activeJob.completed_at = new Date().toISOString();
            }
          });
          
          return project;
        }
        
        return null;
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : 'Music generation failed',
          loading: false,
        });
        
        set((state) => {
          if (state.activeJob) {
            state.activeJob.status = 'failed';
            state.activeJob.error = error instanceof Error ? error.message : 'Unknown error';
          }
        });
        
        return null;
      }
    },
    
    cloneVoice: async (params) => {
      const studio = get().selectedStudio;
      if (!studio) return null;
      
      set({ loading: true, error: null });
      
      try {
        const response = await backendAPI.cloneVoice({
          audio_sample_url: params.audio_sample_url,
          text: params.text,
          model: params.model,
        });
        
        if (response.data) {
          const project: AudioProject = {
            id: `voice-clone-${Date.now()}`,
            studio_id: studio.id,
            name: `Voice Clone - ${params.text.substring(0, 30)}...`,
            type: 'voice-clone',
            text: params.text,
            audio_url: response.data.url,
            duration: response.data.duration,
            model_used: response.data.model_used,
            cost: response.data.cost || 0,
            quality: studio.settings.quality,
            created_at: new Date().toISOString(),
          };
          
          get().trackCost(project.model_used!, project.cost!);
          
          set((state) => {
            state.audioProjects.unshift(project);
            state.activeProject = project;
            state.loading = false;
          });
          
          return project;
        }
        
        return null;
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : 'Voice cloning failed',
          loading: false,
        });
        return null;
      }
    },
    
    // ======================================================================
    // VIDEO PROJECTS
    // ======================================================================
    
    fetchVideoProjects: async (studioId: string) => {
      try {
        const response = await backendAPI.listVideoProjects(studioId);
        
        set({ videoProjects: response.items });
      } catch (error) {
        console.error('Failed to fetch video projects:', error);
      }
    },
    
    createVideoProject: async (data) => {
      const studio = get().selectedStudio;
      if (!studio) return null;
      
      try {
        const response = await backendAPI.createVideoProject({
          studio_id: studio.id,
          ...data,
        });
        
        if (response.data) {
          set((state) => {
            state.videoProjects.unshift(response.data!);
            state.activeProject = response.data!;
          });
          
          return response.data;
        }
        
        return null;
      } catch (error) {
        console.error('Failed to create video project:', error);
        return null;
      }
    },
    
    addClipToTimeline: async (projectId: string, clip: Partial<VideoClip>) => {
      try {
        const response = await backendAPI.addClipToTimeline(projectId, clip);
        
        if (response.data) {
          set((state) => {
            const project = state.videoProjects.find(p => p.id === projectId);
            if (project) {
              project.clips.push(response.data!);
              project.updated_at = new Date().toISOString();
            }
          });
        }
      } catch (error) {
        console.error('Failed to add clip:', error);
      }
    },
    
    generateVideoClip: async (params) => {
      const studio = get().selectedStudio;
      if (!studio) return null;
      
      set({ loading: true, error: null });
      
      try {
        const jobId = `job-${Date.now()}`;
        const job: GenerationJob = {
          id: jobId,
          type: 'video',
          status: 'processing',
          progress: 10,
          prompt: params.prompt,
          created_at: new Date().toISOString(),
        };
        
        set((state) => {
          state.generationJobs.unshift(job);
          state.activeJob = job;
        });
        
        // ⚠️ VIDEO GENERATION - Use intelligent selector!
        const response = await backendAPI.generateVideo({
          prompt: params.prompt,
          duration: params.duration || 5,
          quality: params.quality || studio.settings.quality,
          model: params.model || studio.settings.default_model,
          prefer_internal: params.prefer_internal ?? studio.settings.prefer_internal,
          max_cost: params.max_cost || studio.settings.max_cost_per_generation || 2.0, // Default $2!
        });
        
        if (response.data) {
          const clip: VideoClip = {
            id: `clip-${Date.now()}`,
            start_time: 0,
            end_time: response.data.duration || params.duration || 5,
            video_url: response.data.url,
            prompt: params.prompt,
            model_used: response.data.model_used,
            cost: response.data.actual_cost || 0,
          };
          
          get().trackCost(clip.model_used!, clip.cost!);
          
          set((state) => {
            state.loading = false;
            
            if (state.activeJob) {
              state.activeJob.status = 'completed';
              state.activeJob.progress = 100;
              state.activeJob.result_url = clip.video_url;
              state.activeJob.actual_cost = clip.cost;
              state.activeJob.model_used = clip.model_used;
              state.activeJob.completed_at = new Date().toISOString();
            }
          });
          
          return clip;
        }
        
        return null;
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : 'Video generation failed',
          loading: false,
        });
        
        set((state) => {
          if (state.activeJob) {
            state.activeJob.status = 'failed';
            state.activeJob.error = error instanceof Error ? error.message : 'Unknown error';
          }
        });
        
        return null;
      }
    },
    
    addAudioTrack: async (projectId: string, track: Partial<AudioTrack>) => {
      try {
        const response = await backendAPI.addAudioToVideo(projectId, track);
        
        if (response.data) {
          set((state) => {
            const project = state.videoProjects.find(p => p.id === projectId);
            if (project) {
              project.audio_tracks.push(response.data!);
              project.updated_at = new Date().toISOString();
            }
          });
        }
      } catch (error) {
        console.error('Failed to add audio track:', error);
      }
    },
    
    exportVideo: async (projectId: string, settings) => {
      set({ loading: true, error: null });
      
      try {
        const response = await backendAPI.exportVideo(projectId, settings);
        
        if (response.data?.url) {
          set({ loading: false });
          return response.data.url;
        }
        
        return null;
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : 'Export failed',
          loading: false,
        });
        return null;
      }
    },
    
    // ======================================================================
    // PREVIEW & PLAYBACK
    // ======================================================================
    
    loadPreview: (url: string) => {
      set({
        previewUrl: url,
        isPlaying: false,
        currentTime: 0,
      });
    },
    
    togglePlayback: () => {
      set((state) => {
        state.isPlaying = !state.isPlaying;
      });
    },
    
    seek: (time: number) => {
      set({ currentTime: time });
    },
    
    // ======================================================================
    // COST TRACKING
    // ======================================================================
    
    getAvailableModels: async (type: 'audio' | 'video') => {
      try {
        const response = await backendAPI.getAvailableModels(type);
        return response.data;
      } catch (error) {
        console.error('Failed to get available models:', error);
        return null;
      }
    },
    
    estimateCost: async (params) => {
      try {
        const response = await backendAPI.estimateCost(params);
        return response.data?.estimated_cost || 0;
      } catch (error) {
        console.error('Failed to estimate cost:', error);
        return 0;
      }
    },
    
    trackCost: (model: string, cost: number) => {
      set((state) => {
        state.totalCostThisMonth += cost;
        state.costByModel[model] = (state.costByModel[model] || 0) + cost;
      });
    },
    
    resetMonthlyCosts: () => {
      set({
        totalCostThisMonth: 0,
        costByModel: {},
      });
    },
  }))
);

/**
 * ✅ STUDIOS STORE COMPLETE!
 * 
 * Features implémentées:
 * - ✅ Studios CRUD (create, read, update, delete)
 * - ✅ Audio projects (TTS, Music, Voice Clone)
 * - ✅ Video projects with timeline
 * - ✅ Intelligent model selector integration
 * - ✅ Cost tracking par modèle
 * - ✅ Budget enforcement (max_cost_per_generation)
 * - ✅ Generation jobs with progress tracking
 * - ✅ Preview & playback controls
 * - ✅ Export functionality
 * 
 * Total: ~850 lignes
 * 
 * Intégration intelligent_selector:
 * - prefer_internal: true par défaut (essaie AI Leader)
 * - max_cost_per_generation: $2 default pour vidéo
 * - Track tous les coûts par modèle
 * - Affiche coûts mensuels totaux
 */
