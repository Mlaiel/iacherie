/**
 * 🔌 BACKEND API CLIENT - SOLID FOUNDATION
 * ==========================================
 * Client TypeScript pour tous les endpoints CRUD backend
 * 
 * @author Fahed Mlaiel
 * @date 2025-10-05
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ============================================================================
// TYPES
// ============================================================================

export interface Crawler {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'inactive' | 'pending' | 'error';
  type: string;
  config: Record<string, any>;
  created_at: string;
  updated_at: string;
  stats: {
    requests: number;
    success: number;
    errors: number;
    last_run: string | null;
  };
}

export interface Generator {
  id: string;
  name: string;
  type: 'text' | 'image' | 'audio' | 'video' | 'code' | '3d';
  description: string;
  status: 'active' | 'inactive';
  config: Record<string, any>;
  created_at: string;
  updated_at: string;
  stats: {
    generations: number;
    success_rate: number;
    avg_duration: number;
  };
}

export interface Agent {
  id: string;
  name: string;
  category: 'business' | 'technical' | 'creative' | 'protection' | 'specialized';
  description: string;
  status: 'active' | 'inactive';
  capabilities: string[];
  config: Record<string, any>;
  created_at: string;
  updated_at: string;
  stats: {
    tasks_completed: number;
    success_rate: number;
    avg_response_time: number;
  };
}

export interface Chatroom {
  id: string;
  name: string;
  type: 'text' | 'audio' | 'video' | 'collaboration';
  description: string;
  status: 'active' | 'inactive';
  participants: string[];
  created_at: string;
  updated_at: string;
  stats: {
    messages: number;
    active_users: number;
    total_participants: number;
  };
}

export interface Automation {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'inactive' | 'paused';
  trigger: Record<string, any>;
  actions: any[];
  schedule: string | null;
  created_at: string;
  updated_at: string;
  stats: {
    executions: number;
    success_rate: number;
    last_execution: string | null;
  };
}

export interface Studio {
  id: string;
  name: string;
  type: 'audio' | 'video' | 'image' | 'text' | 'remix' | 'podcast' | 'ai';
  description: string;
  status: 'active' | 'inactive';
  features: string[];
  created_at: string;
  updated_at: string;
  stats: {
    projects: number;
    active_sessions: number;
    total_outputs: number;
  };
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export interface APIResponse<T> {
  message?: string;
  data?: T;
  error?: string;
}

export interface ListFilters {
  limit?: number;
  offset?: number;
  status?: string;
  type?: string;
  category?: string;
  search?: string;
}

// ============================================================================
// API CLIENT CLASS
// ============================================================================

class BackendAPIClient {
  private baseURL: string;

  constructor(baseURL = API_BASE) {
    this.baseURL = baseURL;
  }

  /**
   * Generic fetch wrapper with error handling
   */
  private async fetch<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.error || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }

  // ========================================================================
  // CRAWLERS
  // ========================================================================

  async listCrawlers(filters?: ListFilters): Promise<PaginatedResponse<Crawler>> {
    const params = new URLSearchParams();
    if (filters?.limit) params.append('limit', filters.limit.toString());
    if (filters?.offset) params.append('offset', filters.offset.toString());
    if (filters?.status) params.append('status', filters.status);
    if (filters?.search) params.append('search', filters.search);

    const query = params.toString();
    return this.fetch<PaginatedResponse<Crawler>>(
      `/api/crawlers${query ? `?${query}` : ''}`
    );
  }

  async getCrawler(id: string): Promise<APIResponse<Crawler>> {
    return this.fetch<APIResponse<Crawler>>(`/api/crawlers/${id}`);
  }

  async createCrawler(data: Partial<Crawler>): Promise<APIResponse<Crawler>> {
    return this.fetch<APIResponse<Crawler>>('/api/crawlers', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateCrawler(id: string, data: Partial<Crawler>): Promise<APIResponse<Crawler>> {
    return this.fetch<APIResponse<Crawler>>(`/api/crawlers/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteCrawler(id: string): Promise<APIResponse<{ id: string }>> {
    return this.fetch<APIResponse<{ id: string }>>(`/api/crawlers/${id}`, {
      method: 'DELETE',
    });
  }

  // ========================================================================
  // GENERATORS
  // ========================================================================

  async listGenerators(filters?: ListFilters): Promise<PaginatedResponse<Generator>> {
    const params = new URLSearchParams();
    if (filters?.limit) params.append('limit', filters.limit.toString());
    if (filters?.offset) params.append('offset', filters.offset.toString());
    if (filters?.type) params.append('type', filters.type);
    if (filters?.status) params.append('status', filters.status);

    const query = params.toString();
    return this.fetch<PaginatedResponse<Generator>>(
      `/api/generators${query ? `?${query}` : ''}`
    );
  }

  async getGenerator(id: string): Promise<APIResponse<Generator>> {
    return this.fetch<APIResponse<Generator>>(`/api/generators/${id}`);
  }

  async createGenerator(data: Partial<Generator>): Promise<APIResponse<Generator>> {
    return this.fetch<APIResponse<Generator>>('/api/generators', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateGenerator(id: string, data: Partial<Generator>): Promise<APIResponse<Generator>> {
    return this.fetch<APIResponse<Generator>>(`/api/generators/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteGenerator(id: string): Promise<APIResponse<{ id: string }>> {
    return this.fetch<APIResponse<{ id: string }>>(`/api/generators/${id}`, {
      method: 'DELETE',
    });
  }

  // ========================================================================
  // AGENTS
  // ========================================================================

  async listAgents(filters?: ListFilters): Promise<PaginatedResponse<Agent>> {
    const params = new URLSearchParams();
    if (filters?.limit) params.append('limit', filters.limit.toString());
    if (filters?.offset) params.append('offset', filters.offset.toString());
    if (filters?.category) params.append('category', filters.category);

    const query = params.toString();
    return this.fetch<PaginatedResponse<Agent>>(
      `/api/agents${query ? `?${query}` : ''}`
    );
  }

  async getAgent(id: string): Promise<APIResponse<Agent>> {
    return this.fetch<APIResponse<Agent>>(`/api/agents/${id}`);
  }

  async createAgent(data: Partial<Agent>): Promise<APIResponse<Agent>> {
    return this.fetch<APIResponse<Agent>>('/api/agents', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateAgent(id: string, data: Partial<Agent>): Promise<APIResponse<Agent>> {
    return this.fetch<APIResponse<Agent>>(`/api/agents/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteAgent(id: string): Promise<APIResponse<{ id: string }>> {
    return this.fetch<APIResponse<{ id: string }>>(`/api/agents/${id}`, {
      method: 'DELETE',
    });
  }

  // ========================================================================
  // AUTOMATION
  // ========================================================================

  async listAutomation(filters?: ListFilters): Promise<PaginatedResponse<Automation>> {
    const params = new URLSearchParams();
    if (filters?.limit) params.append('limit', filters.limit.toString());
    if (filters?.offset) params.append('offset', filters.offset.toString());
    if (filters?.status) params.append('status', filters.status);

    const query = params.toString();
    return this.fetch<PaginatedResponse<Automation>>(
      `/api/automation${query ? `?${query}` : ''}`
    );
  }

  async getAutomation(id: string): Promise<APIResponse<Automation>> {
    return this.fetch<APIResponse<Automation>>(`/api/automation/${id}`);
  }

  async createAutomation(data: Partial<Automation>): Promise<APIResponse<Automation>> {
    return this.fetch<APIResponse<Automation>>('/api/automation', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateAutomation(id: string, data: Partial<Automation>): Promise<APIResponse<Automation>> {
    return this.fetch<APIResponse<Automation>>(`/api/automation/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteAutomation(id: string): Promise<APIResponse<{ id: string }>> {
    return this.fetch<APIResponse<{ id: string }>>(`/api/automation/${id}`, {
      method: 'DELETE',
    });
  }

  // ========================================================================
  // STUDIOS
  // ========================================================================

  async listStudios(filters?: ListFilters): Promise<PaginatedResponse<Studio>> {
    const params = new URLSearchParams();
    if (filters?.limit) params.append('limit', filters.limit.toString());
    if (filters?.offset) params.append('offset', filters.offset.toString());
    if (filters?.type) params.append('type', filters.type);

    const query = params.toString();
    return this.fetch<PaginatedResponse<Studio>>(
      `/api/studios${query ? `?${query}` : ''}`
    );
  }

  async getStudio(id: string): Promise<APIResponse<Studio>> {
    return this.fetch<APIResponse<Studio>>(`/api/studios/${id}`);
  }

  async createStudio(data: Partial<Studio>): Promise<APIResponse<Studio>> {
    return this.fetch<APIResponse<Studio>>('/api/studios', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateStudio(id: string, data: Partial<Studio>): Promise<APIResponse<Studio>> {
    return this.fetch<APIResponse<Studio>>(`/api/studios/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteStudio(id: string): Promise<APIResponse<{ id: string }>> {
    return this.fetch<APIResponse<{ id: string }>>(`/api/studios/${id}`, {
      method: 'DELETE',
    });
  }

  // ============================================================================
  // 🎨 GENERATION APIs - REAL AI POWER! ✨
  // ============================================================================

  /**
   * Get available models for a generation type
   */
  async getAvailableModels(type: string): Promise<APIResponse<any>> {
    return this.fetch<APIResponse<any>>(`/api/generate/models/${type}`, {
      method: 'GET',
    });
  }

  /**
   * Generate image with DALL-E
   */
  async generateImage(params: {
    prompt: string;
    model?: string;
    size?: string;
    quality?: string;
    n?: number;
    prefer_internal?: boolean;
    max_cost?: number;
  }): Promise<APIResponse<any>> {
    return this.fetch<APIResponse<any>>('/api/generate/image', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  /**
   * Generate text with GPT-4
   */
  async generateText(params: {
    prompt: string;
    model?: string;
    max_tokens?: number;
    temperature?: number;
    prefer_internal?: boolean;
    max_cost?: number;
  }): Promise<APIResponse<any>> {
    return this.fetch<APIResponse<any>>('/api/generate/text', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  /**
   * Generate audio with TTS/Music generation
   */
  async generateAudio(params: {
    prompt: string;
    model?: string;
    type?: string;
    voice?: string;
    speed?: number;
    duration?: number;
    genre?: string;
    prefer_internal?: boolean;
    max_cost?: number;
  }): Promise<APIResponse<any>> {
    return this.fetch<APIResponse<any>>('/api/generate/audio', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  /**
   * Generate video
   */
  async generateVideo(params: {
    prompt: string;
    model?: string;
    duration?: number;
    quality?: string;
    prefer_internal?: boolean;
    max_cost?: number;
  }): Promise<APIResponse<any>> {
    return this.fetch<APIResponse<any>>('/api/generate/video', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  /**
   * Generate code
   */
  async generateCode(params: {
    prompt: string;
    model?: string;
    language?: string;
    framework?: string;
    prefer_internal?: boolean;
    max_cost?: number;
  }): Promise<APIResponse<any>> {
    return this.fetch<APIResponse<any>>('/api/generate/code', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  /**
   * Generate 3D models
   */
  async generate3D(params: {
    prompt: string;
    model?: string;
    format?: string;
    quality?: string;
    prefer_internal?: boolean;
    max_cost?: number;
  }): Promise<APIResponse<any>> {
    return this.fetch<APIResponse<any>>('/api/generate/3d', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  // ============================================================================
  // 💬 CHATROOMS APIs - REAL-TIME CHAT! 🚀
  // ============================================================================

  /**
   * List chatrooms
   */
  async listChatrooms(filters?: any): Promise<{ items: Chatroom[], total: number }> {
    const response = await this.fetch<APIResponse<{ items: Chatroom[], total: number }>>('/api/chatrooms', {
      method: 'GET',
    });
    return response.data;
  }

  /**
   * Get chatroom by ID
   */
  async getChatroom(id: string): Promise<APIResponse<Chatroom>> {
    return this.fetch<APIResponse<Chatroom>>(`/api/chatrooms/${id}`, {
      method: 'GET',
    });
  }

  /**
   * Create chatroom
   */
  async createChatroom(data: Partial<Chatroom>): Promise<APIResponse<Chatroom>> {
    return this.fetch<APIResponse<Chatroom>>('/api/chatrooms', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * Update chatroom
   */
  async updateChatroom(id: string, data: Partial<Chatroom>): Promise<APIResponse<Chatroom>> {
    return this.fetch<APIResponse<Chatroom>>(`/api/chatrooms/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  /**
   * Delete chatroom
   */
  async deleteChatroom(id: string): Promise<APIResponse<{ id: string }>> {
    return this.fetch<APIResponse<{ id: string }>>(`/api/chatrooms/${id}`, {
      method: 'DELETE',
    });
  }

  /**
   * Get chatroom messages
   */
  async getChatroomMessages(roomId: string, limit: number = 50): Promise<APIResponse<{ messages: any[], has_more: boolean }>> {
    return this.fetch<APIResponse<{ messages: any[], has_more: boolean }>>(
      `/api/chatrooms/${roomId}/messages?limit=${limit}`,
      { method: 'GET' }
    );
  }

  /**
   * Get chatroom participants
   */
  async getChatroomParticipants(roomId: string): Promise<APIResponse<{ participants: any[], count: number }>> {
    return this.fetch<APIResponse<{ participants: any[], count: number }>>(
      `/api/chatrooms/${roomId}/participants`,
      { method: 'GET' }
    );
  }

  /**
   * Send typing indicator
   */
  async sendTypingIndicator(roomId: string, userId?: string, username?: string): Promise<APIResponse<any>> {
    return this.fetch<APIResponse<any>>(`/api/chatrooms/${roomId}/typing`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId || 'guest', username: username || 'Guest' }),
    });
  }

  // ============================================================================
  // 🎬 STUDIOS GENERATION APIs - AUDIO & VIDEO! 🚀
  // ============================================================================

  /**
   * List audio projects for a studio
   */
  async listAudioProjects(studioId: string): Promise<{ items: any[], total: number }> {
    const response = await this.fetch<APIResponse<{ items: any[], total: number }>>(
      `/api/studios/${studioId}/audio-projects`,
      { method: 'GET' }
    );
    return response.data;
  }

  /**
   * Generate TTS
   */
  async generateTTS(data: any): Promise<APIResponse<any>> {
    return this.fetch<APIResponse<any>>('/api/studios/generate-tts', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * Generate music
   */
  async generateMusic(data: any): Promise<APIResponse<any>> {
    return this.fetch<APIResponse<any>>('/api/studios/generate-music', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * Clone voice
   */
  async cloneVoice(data: any): Promise<APIResponse<any>> {
    return this.fetch<APIResponse<any>>('/api/studios/voice-clone', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * List video projects for a studio
   */
  async listVideoProjects(studioId: string): Promise<{ items: any[], total: number }> {
    const response = await this.fetch<APIResponse<{ items: any[], total: number }>>(
      `/api/studios/${studioId}/video-projects`,
      { method: 'GET' }
    );
    return response.data;
  }

  /**
   * Create video project
   */
  async createVideoProject(data: any): Promise<APIResponse<any>> {
    return this.fetch<APIResponse<any>>('/api/studios/video-projects', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * Add clip to video project timeline
   */
  async addClipToTimeline(projectId: string, data: any): Promise<APIResponse<any>> {
    return this.fetch<APIResponse<any>>(
      `/api/studios/video-projects/${projectId}/clips`,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
  }

  /**
   * Add audio track to video project
   */
  async addAudioToVideo(projectId: string, data: any): Promise<APIResponse<any>> {
    return this.fetch<APIResponse<any>>(
      `/api/studios/video-projects/${projectId}/audio-tracks`,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
  }

  /**
   * Export video project
   */
  async exportVideo(projectId: string, settings: any): Promise<APIResponse<any>> {
    return this.fetch<APIResponse<any>>(
      `/api/studios/video-projects/${projectId}/export`,
      {
        method: 'POST',
        body: JSON.stringify(settings),
      }
    );
  }

  /**
   * Estimate generation cost
   */
  async estimateCost(params: any): Promise<APIResponse<{ estimated_cost: number, model: any }>> {
    return this.fetch<APIResponse<{ estimated_cost: number, model: any }>>(
      '/api/studios/estimate-cost',
      {
        method: 'POST',
        body: JSON.stringify(params),
      }
    );
  }
}

// Export singleton instance
export const backendAPI = new BackendAPIClient();
export default BackendAPIClient;
