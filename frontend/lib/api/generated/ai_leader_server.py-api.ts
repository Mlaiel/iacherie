/**
 * AI_LEADER_SERVER.PY API CLIENT
 * Auto-generated from backend endpoints
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright © 2025 Fahed Mlaiel. All rights reserved.
 */

import { apiClient } from '../client';
import type { APIResponse, PaginatedResponse } from './common-types';


// ============================================================================
// TYPES
// ============================================================================


export interface AiLeaderServerItem {
  id: string;
  created_at: string;
  updated_at: string;
  [key: string]: any;
}


export interface CreateAiLeaderServerpyDto {
  [key: string]: any;
}

export interface UpdateAiLeaderServerpyDto {
  [key: string]: any;
}

export interface AiLeaderServerpyFilters {
  search?: string;
  status?: string;
  limit?: number;
  offset?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}


/**
 * Ai_leader_server.py API Client
 */
class AiLeaderServerAPI {

  /**
   * Health check
   * 
   * @endpoint GET /
   */
  async root() {
    try {
      const response = await apiClient.get<any>('/');
      return response.data;
    } catch (error) {
      console.error(`root error:`, error);
      throw error;
    }
  }

  /**
   * Get AI Leader autonomy status
   * 
   * @endpoint GET /api/leader/status
   */
  async getStatus() {
    try {
      const response = await apiClient.get<any>('/api/leader/status');
      return response.data;
    } catch (error) {
      console.error(`get_status error:`, error);
      throw error;
    }
  }

  /**
   * Get status of a training job
   * 
   * @endpoint GET /api/leader/training/{job_id}
   */
  async getTrainingStatus(job_id: string) {
    try {
      const response = await apiClient.get<any>('/api/leader/training/{job_id}');
      return response.data;
    } catch (error) {
      console.error(`get_training_status error:`, error);
      throw error;
    }
  }

  /**
   * Get health status of external API providers
   * 
   * @endpoint GET /api/leader/providers/health
   */
  async getProviderHealth() {
    try {
      const response = await apiClient.get<any>('/api/leader/providers/health');
      return response.data;
    } catch (error) {
      console.error(`get_provider_health error:`, error);
      throw error;
    }
  }

  /**
   * List all registered capabilities
   * 
   * @endpoint GET /api/leader/capabilities
   */
  async listCapabilities() {
    try {
      const response = await apiClient.get<any>('/api/leader/capabilities');
      return response.data;
    } catch (error) {
      console.error(`list_capabilities error:`, error);
      throw error;
    }
  }

  /**
   * Execute a capability using AI Leader
    Will use internal model if available, otherwise fallback to external API
   * 
   * @endpoint POST /api/leader/execute
   */
  async executeCapability() {
    try {
      const response = await apiClient.post<any>('/api/leader/execute');
      return response.data;
    } catch (error) {
      console.error(`execute_capability error:`, error);
      throw error;
    }
  }

  /**
   * Start training a capability
    Requires sufficient training data collected from API calls
   * 
   * @endpoint POST /api/leader/train
   */
  async trainCapability() {
    try {
      const response = await apiClient.post<any>('/api/leader/train');
      return response.data;
    } catch (error) {
      console.error(`train_capability error:`, error);
      throw error;
    }
  }

  /**
   * Register a new capability for the AI to learn
   * 
   * @endpoint POST /api/leader/capabilities/register
   */
  async registerCapability(capability: any) {
    try {
      const response = await apiClient.post<any>('/api/leader/capabilities/register'), {
        capability
      });
      return response.data;
    } catch (error) {
      console.error(`register_capability error:`, error);
      throw error;
    }
  }

}

// Export singleton instance
export const ai_leader_server.pyAPI = new AiLeaderServerAPI();
