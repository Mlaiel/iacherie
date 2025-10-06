/**
 * ROUTES API CLIENT
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


export interface RoutesItem {
  id: string;
  created_at: string;
  updated_at: string;
  [key: string]: any;
}


export interface CreateRoutesDto {
  [key: string]: any;
}

export interface UpdateRoutesDto {
  [key: string]: any;
}

export interface RoutesFilters {
  search?: string;
  status?: string;
  limit?: number;
  offset?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}


/**
 * Routes API Client
 */
class RoutesAPI {

  /**
   * Statistiques d'utilisation de l'AI Leader Agent
   * 
   * @endpoint GET /example/usage-stats
   */
  async getUsageStats() {
    try {
      const response = await apiClient.get<any>('/example/usage-stats');
      return response.data;
    } catch (error) {
      console.error(`get_usage_stats error:`, error);
      throw error;
    }
  }

  /**
   * Génération de texte avec AI Leader Agent
    
    Observe l'appel OpenAI et peut le remplacer automatiquement si l'API échoue
   * 
   * @endpoint POST /example/text-generation
   */
  async textGenerationWithAiLeader() {
    try {
      const response = await apiClient.post<any>('/example/text-generation');
      return response.data;
    } catch (error) {
      console.error(`text_generation_with_ai_leader error:`, error);
      throw error;
    }
  }

  /**
   * Génération d'images avec AI Leader Agent
    
    Observe DALL-E et peut basculer vers capacité interne
   * 
   * @endpoint POST /example/image-generation
   */
  async imageGenerationWithAiLeader() {
    try {
      const response = await apiClient.post<any>('/example/image-generation');
      return response.data;
    } catch (error) {
      console.error(`image_generation_with_ai_leader error:`, error);
      throw error;
    }
  }

  /**
   * Génération de vidéos avec AI Leader Agent
    
    Observe RunwayML et peut basculer vers capacité interne
   * 
   * @endpoint POST /example/video-generation
   */
  async videoGenerationWithAiLeader() {
    try {
      const response = await apiClient.post<any>('/example/video-generation');
      return response.data;
    } catch (error) {
      console.error(`video_generation_with_ai_leader error:`, error);
      throw error;
    }
  }

  /**
   * Exemple d'observation manuelle d'un appel API
    
    Utilisez ceci si vous voulez observer sans le fallback automatique
   * 
   * @endpoint POST /example/manual-observation
   */
  async manualApiObservation() {
    try {
      const response = await apiClient.post<any>('/example/manual-observation');
      return response.data;
    } catch (error) {
      console.error(`manual_api_observation error:`, error);
      throw error;
    }
  }

  /**
   * Lance un test automatique pour simuler des appels et voir l'agent apprendre
   * 
   * @endpoint POST /example/run-test
   */
  async runAutomatedTest() {
    try {
      const response = await apiClient.post<any>('/example/run-test');
      return response.data;
    } catch (error) {
      console.error(`run_automated_test error:`, error);
      throw error;
    }
  }

  /**
   * Récupère le statut complet de l'AI Leader Agent
   * 
   * @endpoint GET /ai-leader/status
   */
  async getAgentStatus() {
    try {
      const response = await apiClient.get<any>('/ai-leader/status');
      return response.data;
    } catch (error) {
      console.error(`get_agent_status error:`, error);
      throw error;
    }
  }

  /**
   * Liste toutes les capacités internes de l'agent
   * 
   * @endpoint GET /ai-leader/capabilities
   */
  async getCapabilities() {
    try {
      const response = await apiClient.get<any>('/ai-leader/capabilities');
      return response.data;
    } catch (error) {
      console.error(`get_capabilities error:`, error);
      throw error;
    }
  }

  /**
   * Récupère les données d'apprentissage pour toutes les APIs
   * 
   * @endpoint GET /ai-leader/learning-data
   */
  async getLearningData() {
    try {
      const response = await apiClient.get<any>('/ai-leader/learning-data');
      return response.data;
    } catch (error) {
      console.error(`get_learning_data error:`, error);
      throw error;
    }
  }

  /**
   * Métriques détaillées sur l'autonomie de l'agent
   * 
   * @endpoint GET /ai-leader/autonomy-metrics
   */
  async getAutonomyMetrics() {
    try {
      const response = await apiClient.get<any>('/ai-leader/autonomy-metrics');
      return response.data;
    } catch (error) {
      console.error(`get_autonomy_metrics error:`, error);
      throw error;
    }
  }

  /**
   * Compare les performances de la capacité interne avec l'API externe
   * 
   * @endpoint GET /ai-leader/comparison/{api_name}
   */
  async compareWithExternal(api_name: string) {
    try {
      const response = await apiClient.get<any>('/ai-leader/comparison/{api_name}');
      return response.data;
    } catch (error) {
      console.error(`compare_with_external error:`, error);
      throw error;
    }
  }

  /**
   * Timeline de l'évolution de l'agent
   * 
   * @endpoint GET /ai-leader/evolution-timeline
   */
  async getEvolutionTimeline() {
    try {
      const response = await apiClient.get<any>('/ai-leader/evolution-timeline');
      return response.data;
    } catch (error) {
      console.error(`get_evolution_timeline error:`, error);
      throw error;
    }
  }

  /**
   * Force le passage en mode autonome (pour test)
   * 
   * @endpoint POST /ai-leader/force-autonomous
   */
  async forceAutonomousMode() {
    try {
      const response = await apiClient.post<any>('/ai-leader/force-autonomous');
      return response.data;
    } catch (error) {
      console.error(`force_autonomous_mode error:`, error);
      throw error;
    }
  }

  /**
   * Déclenche l'entraînement de toutes les capacités
   * 
   * @endpoint POST /ai-leader/trigger-training
   */
  async triggerTraining() {
    try {
      const response = await apiClient.post<any>('/ai-leader/trigger-training');
      return response.data;
    } catch (error) {
      console.error(`trigger_training error:`, error);
      throw error;
    }
  }

}

// Export singleton instance
export const routesAPI = new RoutesAPI();
