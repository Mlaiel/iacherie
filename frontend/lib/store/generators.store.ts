/**
 * 🎨 GENERATORS STORE - REAL AI GENERATION
 * ==========================================
 * Store for AI generators with REAL backend API calls
 * Supports: Text, Image, Audio, Video, Code, 3D
 * 
 * @author Fahed Mlaiel
 * @date 2025-10-05
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import { backendAPI, type Generator, type ListFilters } from '../api/backend-client';

// ============================================================================
// ADDITIONAL TYPES FOR GENERATION
// ============================================================================

export interface GenerationJob {
  id: string;
  generator_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  prompt: string;
  result?: {
    url?: string;
    text?: string;
    data?: any;
  };
  error?: string;
  created_at: string;
  completed_at?: string;
}

interface GeneratorsState {
  // Data
  items: Generator[];
  selectedItem: Generator | null;
  
  // Generation jobs
  jobs: GenerationJob[];
  activeJob: GenerationJob | null;
  
  // UI State
  loading: boolean;
  generating: boolean;
  error: string | null;
  
  // Filters & Pagination
  filters: ListFilters;
  total: number;
  hasNext: boolean;
  hasPrev: boolean;
  
  // Actions - CRUD
  fetchItems: () => Promise<void>;
  fetchItem: (id: string) => Promise<void>;
  createItem: (data: Partial<Generator>) => Promise<Generator | null>;
  updateItem: (id: string, data: Partial<Generator>) => Promise<Generator | null>;
  deleteItem: (id: string) => Promise<void>;
  
  // Actions - Generation
  generate: (generatorId: string, prompt: string, options?: any) => Promise<GenerationJob | null>;
  getJob: (jobId: string) => GenerationJob | null;
  clearJobs: () => void;
  
  // Filters
  setFilters: (filters: Partial<ListFilters>) => void;
  clearFilters: () => void;
  selectItem: (item: Generator | null) => void;
  clearError: () => void;
  reset: () => void;
}

const initialState = {
  items: [],
  selectedItem: null,
  jobs: [],
  activeJob: null,
  loading: false,
  generating: false,
  error: null,
  filters: {
    limit: 50,
    offset: 0,
  },
  total: 0,
  hasNext: false,
  hasPrev: false,
};

export const useGeneratorsStore = create<GeneratorsState>()(
  devtools(
    immer((set, get) => ({
      ...initialState,
      
      // ======================================================================
      // FETCH ITEMS
      // ======================================================================
      fetchItems: async () => {
        set({ loading: true, error: null });
        
        try {
          const response = await backendAPI.listGenerators(get().filters);
          
          set({
            items: response.items,
            total: response.total,
            hasNext: response.hasNext,
            hasPrev: response.hasPrev,
            loading: false,
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch generators',
            loading: false,
          });
        }
      },
      
      fetchItem: async (id: string) => {
        set({ loading: true, error: null });
        
        try {
          const response = await backendAPI.getGenerator(id);
          
          if (response.data) {
            set({
              selectedItem: response.data,
              loading: false,
            });
          }
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch generator',
            loading: false,
          });
        }
      },
      
      // ======================================================================
      // CREATE/UPDATE/DELETE
      // ======================================================================
      createItem: async (data: Partial<Generator>) => {
        set({ loading: true, error: null });
        
        try {
          const response = await backendAPI.createGenerator(data);
          
          if (response.data) {
            set((state) => {
              state.items.unshift(response.data!);
              state.total += 1;
              state.loading = false;
            });
            
            return response.data;
          }
          
          return null;
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to create generator',
            loading: false,
          });
          return null;
        }
      },
      
      updateItem: async (id: string, data: Partial<Generator>) => {
        set({ loading: true, error: null });
        
        try {
          const response = await backendAPI.updateGenerator(id, data);
          
          if (response.data) {
            set((state) => {
              const index = state.items.findIndex(i => i.id === id);
              if (index !== -1) {
                state.items[index] = response.data!;
              }
              if (state.selectedItem?.id === id) {
                state.selectedItem = response.data!;
              }
              state.loading = false;
            });
            
            return response.data;
          }
          
          return null;
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to update generator',
            loading: false,
          });
          return null;
        }
      },
      
      deleteItem: async (id: string) => {
        set({ loading: true, error: null });
        
        try {
          await backendAPI.deleteGenerator(id);
          
          set((state) => {
            state.items = state.items.filter(i => i.id !== id);
            state.total -= 1;
            if (state.selectedItem?.id === id) {
              state.selectedItem = null;
            }
            state.loading = false;
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to delete generator',
            loading: false,
          });
        }
      },
      
      // ======================================================================
      // GENERATE - LA VRAIE MAGIE AVEC VRAIES APIs! 🎨✨
      // ======================================================================
      
      // 💡 Récupérer les modèles disponibles pour un type
      getAvailableModels: async (type: string) => {
        try {
          const models = await backendAPI.getAvailableModels(type);
          return models;
        } catch (error) {
          console.error(`Erreur lors de la récupération des modèles ${type}:`, error);
          throw error;
        }
      },
      
      // 🎨 Fonction PRINCIPALE: Générer du contenu
      generate: async (generatorId: string, prompt: string, options?: any) => {
        set({ generating: true, error: null });
        
        try {
          // Récupérer le generator pour connaître le type
          const generator = get().items.find(g => g.id === generatorId);
          if (!generator) {
            throw new Error('Generator not found');
          }
          
          // Créer un job de génération
          const jobId = `job-${Date.now()}`;
          const job: GenerationJob = {
            id: jobId,
            generator_id: generatorId,
            status: 'processing',
            progress: 10,
            prompt,
            created_at: new Date().toISOString(),
          };
          
          set((state) => {
            state.jobs.unshift(job);
            state.activeJob = job;
          });
          
          // Update progress
          set((state) => {
            if (state.activeJob) state.activeJob.progress = 30;
          });
          
          let result: any;
          
          // ✨ APPEL RÉEL selon le type de generator
          switch (generator.type) {
            case 'image':
              // Appel DALL-E via backend avec sélection intelligente
              result = await backendAPI.generateImage({
                prompt,
                model: options?.model,
                size: options?.size || '1024x1024',
                quality: options?.quality || 'standard',
                n: options?.n || 1,
                prefer_internal: options?.prefer_internal !== false,  // Default: true
                max_cost: options?.max_cost,
              });
              break;
              
            case 'text':
              // Appel GPT-4 via backend avec sélection intelligente
              result = await backendAPI.generateText({
                prompt,
                model: options?.model,
                max_tokens: options?.max_tokens || 1000,
                temperature: options?.temperature || 0.7,
                prefer_internal: options?.prefer_internal !== false,
                max_cost: options?.max_cost,
              });
              break;
              
            case 'audio':
              // Appel TTS/Music generation via backend
              result = await backendAPI.generateAudio({
                prompt,
                model: options?.model,
                type: options?.type || 'tts',
                voice: options?.voice || 'alloy',
                speed: options?.speed || 1.0,
                prefer_internal: options?.prefer_internal !== false,
                max_cost: options?.max_cost,
              });
              break;
              
            case 'video':
              // ⚠️ VIDEO: TOUJOURS essayer AI Leader d'abord (Runway TROP CHER!)
              result = await backendAPI.generateVideo({
                prompt,
                model: options?.model,
                duration: options?.duration || 5,
                quality: options?.quality || 'hd',
                prefer_internal: options?.prefer_internal !== false,  // IMPORTANT!
                max_cost: options?.max_cost || 2.0,  // Default: $2 max pour éviter Runway!
              });
              break;
              
            case 'code':
              // Appel Code generation via backend
              result = await backendAPI.generateCode({
                prompt,
                model: options?.model,
                language: options?.language || 'typescript',
                framework: options?.framework,
                prefer_internal: options?.prefer_internal !== false,
                max_cost: options?.max_cost,
              });
              break;
              
            case '3d':
              // Appel 3D generation via backend
              result = await backendAPI.generate3D({
                prompt,
                model: options?.model,
                format: options?.format || 'glb',
                quality: options?.quality || 'medium',
                prefer_internal: options?.prefer_internal !== false,
                max_cost: options?.max_cost,
              });
              break;
              
            default:
              throw new Error(`Unknown generator type: ${generator.type}`);
          }
          
          // Update progress
          set((state) => {
            if (state.activeJob) state.activeJob.progress = 90;
          });
          
          // Créer le job complété avec le résultat
          const completedJob: GenerationJob = {
            ...job,
            status: 'completed',
            progress: 100,
            result: result.data || result,
            completed_at: new Date().toISOString(),
          };
          
          set((state) => {
            const index = state.jobs.findIndex(j => j.id === jobId);
            if (index !== -1) {
              state.jobs[index] = completedJob;
            }
            state.activeJob = completedJob;
            state.generating = false;
          });
          
          // Update generator stats
          if (generator) {
            await get().updateItem(generatorId, {
              stats: {
                ...generator.stats,
                generations: (generator.stats.generations || 0) + 1,
              },
            });
          }
          
          return completedJob;
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Generation failed';
          
          set((state) => {
            if (state.activeJob) {
              state.activeJob.status = 'failed';
              state.activeJob.error = errorMessage;
            }
            state.generating = false;
            state.error = errorMessage;
          });
          
          console.error('Generation error:', error);
          return null;
        }
      },
      
      getJob: (jobId: string) => {
        return get().jobs.find(j => j.id === jobId) || null;
      },
      
      clearJobs: () => {
        set({ jobs: [], activeJob: null });
      },
      
      // ======================================================================
      // FILTERS & UTILITIES
      // ======================================================================
      setFilters: (filters: Partial<ListFilters>) => {
        set((state) => {
          state.filters = { ...state.filters, ...filters };
        });
        get().fetchItems();
      },
      
      clearFilters: () => {
        set((state) => {
          state.filters = initialState.filters;
        });
        get().fetchItems();
      },
      
      selectItem: (item: Generator | null) => {
        set({ selectedItem: item });
      },
      
      clearError: () => {
        set({ error: null });
      },
      
      reset: () => {
        set(initialState);
      },
    })),
    { name: 'GeneratorsStore' }
  )
);

// ============================================================================
// HOOKS
// ============================================================================

export const useGeneratorsItems = () => {
  const items = useGeneratorsStore((state) => state.items);
  const loading = useGeneratorsStore((state) => state.loading);
  const error = useGeneratorsStore((state) => state.error);
  const fetchItems = useGeneratorsStore((state) => state.fetchItems);
  
  return { items, loading, error, fetchItems };
};

export const useGeneration = () => {
  const generate = useGeneratorsStore((state) => state.generate);
  const generating = useGeneratorsStore((state) => state.generating);
  const activeJob = useGeneratorsStore((state) => state.activeJob);
  const jobs = useGeneratorsStore((state) => state.jobs);
  
  return { generate, generating, activeJob, jobs };
};
