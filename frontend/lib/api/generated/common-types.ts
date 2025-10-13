/**
 * COMMON TYPES
 * Shared types across all API clients
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright © 2025 Fahed Mlaiel. All rights reserved.
 */

/**
 * Standard API Response
 */
export interface APIResponse<T = any> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
}

/**
 * Paginated Response
 */
export interface PaginatedResponse<T = any> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
  has_next: boolean;
  has_prev: boolean;
}

/**
 * Filter Options
 */
export interface FilterOptions {
  search?: string;
  limit?: number;
  offset?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

/**
 * API Error
 */
export interface APIError {
  message: string;
  code: string;
  details?: any;
}

/**
 * Status Response
 */
export interface StatusResponse {
  status: 'active' | 'inactive' | 'pending' | 'error';
  message?: string;
}

/**
 * Batch Operation Response
 */
export interface BatchOperationResponse {
  success: number;
  failed: number;
  errors: Array<{
    id: string;
    error: string;
  }>;
}
