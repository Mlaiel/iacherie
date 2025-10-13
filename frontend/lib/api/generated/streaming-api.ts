/**
 * STREAMING API CLIENT
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


export interface StreamingItem {
  id: string;
  created_at: string;
  updated_at: string;
  [key: string]: any;
}


export interface CreateStreamingDto {
  [key: string]: any;
}

export interface UpdateStreamingDto {
  [key: string]: any;
}

export interface StreamingFilters {
  search?: string;
  status?: string;
  limit?: number;
  offset?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}


/**
 * Streaming API Client
 */
class StreamingAPI {

  /**
   * get_streaming_stats
   * 
   * @endpoint GET /stats
   */
  async getStreamingStats() {
    try {
      const response = await apiClient.get<any>('/stats');
      return response.data;
    } catch (error) {
      console.error(`get_streaming_stats error:`, error);
      throw error;
    }
  }

}

// Export singleton instance
export const streamingAPI = new StreamingAPI();
