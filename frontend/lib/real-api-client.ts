/**
 * 🚀 IA CHÉRIE ENTERPRISE API CLIENT - REAL BACKEND ONLY
 * 
 * Client API complet pour toutes les fonctionnalités enterprise
 * Connexion directe au backend avec 53+ agents IA et 680+ microservices
 * 
 * AUCUNE SIMULATION - TOUT EST RÉEL
 * 
 * @author Fahed Mlaiel - IA Chérie Enterprise
 * @version 3.0.0-enterprise
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ============================================================================
// TYPES RÉELS DU BACKEND
// ============================================================================

export interface BackendResponse<T = any> {
  success?: boolean;
  data?: T;
  result?: T;
  error?: string;
  message?: string;
  [key: string]: any;
}

export interface AIGenerationRequest {
  prompt: string;
  type: string;
  options?: Record<string, any>;
}

export interface ContentCreationRequest {
  type: 'audio' | 'video';
  prompt?: string;
  style?: string;
  duration?: number;
  format?: string;
  quality?: string;
  [key: string]: any;
}

export interface UploadRequest {
  title: string;
  description: string;
  tags: string[];
  category: string;
  privacy: 'public' | 'private' | 'unlisted';
  [key: string]: any;
}

// ============================================================================
// CLIENT API ENTERPRISE COMPLET
// ============================================================================

class RealAPIClient {
  private baseUrl: string;
  
  constructor(baseUrl = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<BackendResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;
    
    try {
      console.log(`🔗 REAL API CALL: ${options.method || 'GET'} ${endpoint}`);
      
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${data.error || data.message || 'Unknown error'}`);
      }

      console.log(`✅ REAL API RESPONSE: ${endpoint}`, data);
      return data;
      
    } catch (error) {
      console.error(`❌ REAL API ERROR: ${endpoint}`, error);
      throw error;
    }
  }

  // ============================================================================
  // SYSTÈME & SANTÉ
  // ============================================================================

  async getHealth() {
    return this.makeRequest('/health');
  }

  async getSystemStatus() {
    return this.makeRequest('/system/status');
  }

  // ============================================================================
  // AGENTS IA (53+ AGENTS RÉELS)
  // ============================================================================

  async getAIAgents() {
    return this.makeRequest('/ai-agents');
  }

  async createAITask(taskData: any) {
    return this.makeRequest('/ai-agents', {
      method: 'POST',
      body: JSON.stringify(taskData),
    });
  }

  async generateAIContent(request: AIGenerationRequest) {
    return this.makeRequest('/api/ai/generate', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async generateMusic(prompt: string, options: any = {}) {
    return this.makeRequest('/generate/music', {
      method: 'POST',
      body: JSON.stringify({ prompt, ...options }),
    });
  }

  async generateVideo(prompt: string, options: any = {}) {
    return this.makeRequest('/generate/video', {
      method: 'POST',
      body: JSON.stringify({ prompt, ...options }),
    });
  }

  // ============================================================================
  // REMIX STUDIO (CRÉATION DE CONTENU RÉEL)
  // ============================================================================

  async getRemixStudio() {
    return this.makeRequest('/remix-studio');
  }

  async createAudio(audioData: ContentCreationRequest) {
    return this.makeRequest('/api/content/create-audio', {
      method: 'POST',
      body: JSON.stringify(audioData),
    });
  }

  async createVideo(videoData: ContentCreationRequest) {
    return this.makeRequest('/api/content/create-video', {
      method: 'POST',
      body: JSON.stringify(videoData),
    });
  }

  async uploadToYoutube(uploadData: UploadRequest) {
    return this.makeRequest('/api/content/upload-youtube', {
      method: 'POST',
      body: JSON.stringify(uploadData),
    });
  }

  async downloadContent(filePath: string) {
    const url = `${this.baseUrl}/api/content/download/${filePath}`;
    return fetch(url);
  }

  // ============================================================================
  // COLLABORATION & MATCHING
  // ============================================================================

  async getCollaboration() {
    return this.makeRequest('/collaboration');
  }

  async getChatRooms() {
    return this.makeRequest('/chat/rooms');
  }

  // ============================================================================
  // MARKETPLACE & MONÉTISATION
  // ============================================================================

  async getMarketplace() {
    return this.makeRequest('/marketplace');
  }

  // ============================================================================
  // ANALYTICS & BUSINESS INTELLIGENCE
  // ============================================================================

  async getAnalytics() {
    return this.makeRequest('/analytics');
  }

  // ============================================================================
  // MICROSERVICES (680+ SERVICES RÉELS)
  // ============================================================================

  async getMicroservices() {
    return this.makeRequest('/microservices');
  }

  // ============================================================================
  // SÉCURITÉ & PROTECTION
  // ============================================================================

  async getSecurity() {
    return this.makeRequest('/security');
  }

  // ============================================================================
  // TESTS & VALIDATION
  // ============================================================================

  async testAudioEngine() {
    return this.makeRequest('/test/audio-engine', {
      method: 'POST',
    });
  }

  // ============================================================================
  // CONTENT CREATOR
  // ============================================================================

  async getContentCreator() {
    return this.makeRequest('/content-creator');
  }
}

// ============================================================================
// HOOKS RÉELS POUR REACT
// ============================================================================

import { useState, useEffect } from 'react';

export function useRealBackendStatus() {
  const [status, setStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const client = new RealAPIClient();
        const response = await client.getHealth();
        setData(response);
        setStatus('online');
      } catch (error) {
        console.error('Backend status check failed:', error);
        setStatus('offline');
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  return { status, data };
}

export function useRealAIAgents() {
  const [agents, setAgents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        setLoading(true);
        const client = new RealAPIClient();
        const response = await client.getAIAgents();
        setAgents(response.data || response.agents || []);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch agents');
      } finally {
        setLoading(false);
      }
    };

    fetchAgents();
  }, []);

  return { agents, loading, error };
}

export function useRealMicroservices() {
  const [services, setServices] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchServices = async () => {
      try {
        setLoading(true);
        const client = new RealAPIClient();
        const response = await client.getMicroservices();
        setServices(response.data || response.services || []);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch services');
      } finally {
        setLoading(false);
      }
    };

    fetchServices();
  }, []);

  return { services, loading, error };
}

// Export du client singleton
export const realAPIClient = new RealAPIClient();
export default RealAPIClient;