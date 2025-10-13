/**
 * API Client for IA2Good Backend
 * Handles all API communications with the backend services
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseUrl}${endpoint}`;
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return { data };
    } catch (error) {
      console.error('API request failed:', error);
      return {
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }

  // Guardian Module - Case Reporting
  async createCase(caseData: any): Promise<ApiResponse> {
    return this.request('/api/guardian/cases', {
      method: 'POST',
      body: JSON.stringify(caseData),
    });
  }

  async reportCase(caseData: any): Promise<ApiResponse> {
    return this.createCase(caseData);
  }

  async getCases(filters?: any): Promise<ApiResponse> {
    const queryParams = filters ? `?${new URLSearchParams(filters)}` : '';
    return this.request(`/api/guardian/cases${queryParams}`);
  }

  async getCase(caseId: string): Promise<ApiResponse> {
    return this.request(`/api/guardian/cases/${caseId}`);
  }

  async updateCase(caseId: string, caseData: any): Promise<ApiResponse> {
    return this.request(`/api/guardian/cases/${caseId}`, {
      method: 'PUT',
      body: JSON.stringify(caseData),
    });
  }

  async updateCaseStatus(caseId: string, status: string): Promise<ApiResponse> {
    return this.request(`/api/guardian/cases/${caseId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
  }

  // MedCare Module APIs
  async getMedicalResources(location?: { lat: number; lng: number }): Promise<ApiResponse> {
    const params = location ? `?lat=${location.lat}&lng=${location.lng}` : '';
    return this.request(`/api/medcare/resources${params}`);
  }

  async requestMedicalHelp(requestData: any): Promise<ApiResponse> {
    return this.request('/api/medcare/help', {
      method: 'POST',
      body: JSON.stringify(requestData),
    });
  }

  // EduVerify Module APIs
  async verifyEducationalInstitution(data: any): Promise<ApiResponse> {
    return this.request('/api/eduverify/institutions', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getEducationalInstitutions(filters?: any): Promise<ApiResponse> {
    const queryParams = filters ? `?${new URLSearchParams(filters)}` : '';
    return this.request(`/api/eduverify/institutions${queryParams}`);
  }

  // Volunteer APIs
  async registerVolunteer(volunteerData: any): Promise<ApiResponse> {
    return this.request('/api/volunteers/register', {
      method: 'POST',
      body: JSON.stringify(volunteerData),
    });
  }

  async getVolunteers(filters?: any): Promise<ApiResponse> {
    const queryParams = filters ? `?${new URLSearchParams(filters)}` : '';
    return this.request(`/api/volunteers${queryParams}`);
  }

  async updateVolunteerProfile(id: string, profileData: any): Promise<ApiResponse> {
    return this.request(`/api/volunteers/${id}`, {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
  }

  // Statistics APIs
  async getStatistics(module?: string): Promise<ApiResponse> {
    const params = module ? `?module=${module}` : '';
    return this.request(`/api/statistics${params}`);
  }

  // Notifications APIs
  async getNotifications(userId: string): Promise<ApiResponse> {
    return this.request(`/api/notifications/${userId}`);
  }

  async markNotificationRead(notificationId: string): Promise<ApiResponse> {
    return this.request(`/api/notifications/${notificationId}/read`, {
      method: 'PATCH',
    });
  }

  // Health check
  async healthCheck(): Promise<ApiResponse> {
    return this.request('/health');
  }
}

// Export singleton instance
export const api = new ApiClient();

// Export class for testing or custom instances
export { ApiClient };
export type { ApiResponse };
