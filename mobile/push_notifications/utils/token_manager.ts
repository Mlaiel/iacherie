/**
 * Token Manager - Device token management and storage
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import { DeviceToken, UserPreferences } from '../types/notification_types';

export class TokenManager {
  private tokens: Map<string, DeviceToken[]> = new Map(); // userId -> tokens
  private userPreferences: Map<string, UserPreferences> = new Map(); // userId -> preferences
  private debugMode: boolean = false;

  /**
   * Initialize token manager
   */
  public async initialize(): Promise<void> {
    try {
      // Load existing tokens from storage (database, file, etc.)
      await this.loadTokensFromStorage();
      await this.loadUserPreferencesFromStorage();
      
      // Set up cleanup interval
      this.setupCleanupInterval();
      
      this.log('Token manager initialized successfully');
    } catch (error) {
      this.log('Failed to initialize token manager:', error);
      throw error;
    }
  }

  /**
   * Register a new device token
   */
  public async registerToken(platform: 'firebase' | 'apns' | 'web', token: string, userId?: string): Promise<boolean> {
    try {
      if (!userId) {
        // Get userId from current session or context
        userId = await this.getCurrentUserId();
      }

      if (!userId) {
        this.log('Cannot register token without user ID');
        return false;
      }

      const deviceToken: DeviceToken = {
        token,
        platform,
        userId,
        deviceId: await this.generateDeviceId(),
        lastUsed: new Date(),
        isActive: true,
        appVersion: await this.getAppVersion(),
        osVersion: await this.getOSVersion(),
        deviceModel: await this.getDeviceModel()
      };

      // Get existing tokens for user
      const userTokens = this.tokens.get(userId) || [];
      
      // Check if token already exists
      const existingTokenIndex = userTokens.findIndex(t => t.token === token && t.platform === platform);
      
      if (existingTokenIndex >= 0) {
        // Update existing token
        userTokens[existingTokenIndex] = deviceToken;
      } else {
        // Add new token
        userTokens.push(deviceToken);
      }

      // Update tokens map
      this.tokens.set(userId, userTokens);
      
      // Save to persistent storage
      await this.saveTokensToStorage();
      
      this.log(`Registered ${platform} token for user ${userId}`);
      return true;
    } catch (error) {
      this.log('Failed to register token:', error);
      return false;
    }
  }

  /**
   * Get all tokens for a user
   */
  public async getUserTokens(userId: string): Promise<{
    firebase: string[];
    apns: string[];
    web: string[];
  }> {
    try {
      const userTokens = this.tokens.get(userId) || [];
      const activeTokens = userTokens.filter(token => token.isActive);

      return {
        firebase: activeTokens.filter(t => t.platform === 'firebase').map(t => t.token),
        apns: activeTokens.filter(t => t.platform === 'apns').map(t => t.token),
        web: activeTokens.filter(t => t.platform === 'web').map(t => t.token)
      };
    } catch (error) {
      this.log('Failed to get user tokens:', error);
      return { firebase: [], apns: [], web: [] };
    }
  }

  /**
   * Remove a specific token
   */
  public async removeToken(token: string, platform: 'firebase' | 'apns' | 'web'): Promise<boolean> {
    try {
      let removed = false;

      for (const [userId, userTokens] of this.tokens.entries()) {
        const tokenIndex = userTokens.findIndex(t => t.token === token && t.platform === platform);
        
        if (tokenIndex >= 0) {
          userTokens.splice(tokenIndex, 1);
          this.tokens.set(userId, userTokens);
          removed = true;
          break;
        }
      }

      if (removed) {
        await this.saveTokensToStorage();
        this.log(`Removed ${platform} token`);
      }

      return removed;
    } catch (error) {
      this.log('Failed to remove token:', error);
      return false;
    }
  }

  /**
   * Mark token as inactive
   */
  public async deactivateToken(token: string, platform: 'firebase' | 'apns' | 'web'): Promise<boolean> {
    try {
      let deactivated = false;

      for (const [userId, userTokens] of this.tokens.entries()) {
        const tokenObj = userTokens.find(t => t.token === token && t.platform === platform);
        
        if (tokenObj) {
          tokenObj.isActive = false;
          deactivated = true;
          break;
        }
      }

      if (deactivated) {
        await this.saveTokensToStorage();
        this.log(`Deactivated ${platform} token`);
      }

      return deactivated;
    } catch (error) {
      this.log('Failed to deactivate token:', error);
      return false;
    }
  }

  /**
   * Update user notification preferences
   */
  public async updateUserPreferences(userId: string, preferences: UserPreferences): Promise<boolean> {
    try {
      this.userPreferences.set(userId, preferences);
      await this.saveUserPreferencesToStorage();
      
      this.log(`Updated preferences for user ${userId}`);
      return true;
    } catch (error) {
      this.log('Failed to update user preferences:', error);
      return false;
    }
  }

  /**
   * Get user notification preferences
   */
  public async getUserPreferences(userId: string): Promise<UserPreferences | null> {
    try {
      return this.userPreferences.get(userId) || null;
    } catch (error) {
      this.log('Failed to get user preferences:', error);
      return null;
    }
  }

  /**
   * Clean up expired and inactive tokens
   */
  public async cleanupTokens(): Promise<number> {
    try {
      let removedCount = 0;
      const now = new Date();
      const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);

      for (const [userId, userTokens] of this.tokens.entries()) {
        const activeTokens = userTokens.filter(token => {
          const isRecentlyUsed = token.lastUsed > thirtyDaysAgo;
          const isActive = token.isActive;
          
          if (!isRecentlyUsed || !isActive) {
            removedCount++;
            return false;
          }
          
          return true;
        });

        this.tokens.set(userId, activeTokens);
      }

      if (removedCount > 0) {
        await this.saveTokensToStorage();
        this.log(`Cleaned up ${removedCount} expired tokens`);
      }

      return removedCount;
    } catch (error) {
      this.log('Failed to cleanup tokens:', error);
      return 0;
    }
  }

  /**
   * Get statistics about registered tokens
   */
  public getTokenStatistics(): {
    totalUsers: number;
    totalTokens: number;
    tokensByPlatform: { firebase: number; apns: number; web: number };
    activeTokens: number;
  } {
    let totalTokens = 0;
    let activeTokens = 0;
    const tokensByPlatform = { firebase: 0, apns: 0, web: 0 };

    for (const userTokens of this.tokens.values()) {
      for (const token of userTokens) {
        totalTokens++;
        
        if (token.isActive) {
          activeTokens++;
        }

        tokensByPlatform[token.platform]++;
      }
    }

    return {
      totalUsers: this.tokens.size,
      totalTokens,
      tokensByPlatform,
      activeTokens
    };
  }

  /**
   * Set debug mode
   */
  public setDebugMode(enabled: boolean): void {
    this.debugMode = enabled;
  }

  /**
   * Load tokens from persistent storage
   */
  private async loadTokensFromStorage(): Promise<void> {
    // In a real implementation, this would load from database
    // For now, we'll use mock data
    this.tokens.clear();
  }

  /**
   * Save tokens to persistent storage
   */
  private async saveTokensToStorage(): Promise<void> {
    // In a real implementation, this would save to database
    // For simulation, we'll just log
    this.log('Tokens saved to storage');
  }

  /**
   * Load user preferences from persistent storage
   */
  private async loadUserPreferencesFromStorage(): Promise<void> {
    // In a real implementation, this would load from database
    this.userPreferences.clear();
  }

  /**
   * Save user preferences to persistent storage
   */
  private async saveUserPreferencesToStorage(): Promise<void> {
    // In a real implementation, this would save to database
    this.log('User preferences saved to storage');
  }

  /**
   * Set up cleanup interval
   */
  private setupCleanupInterval(): void {
    // Run cleanup every 6 hours
    setInterval(async () => {
      await this.cleanupTokens();
    }, 6 * 60 * 60 * 1000);
  }

  /**
   * Get current user ID from session/context
   */
  private async getCurrentUserId(): Promise<string | null> {
    // In a real implementation, this would get from current session
    // For simulation, return a mock user ID
    return 'mock_user_123';
  }

  /**
   * Generate unique device ID
   */
  private async generateDeviceId(): Promise<string> {
    // In a real implementation, this would use device-specific identifiers
    return `device_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Get application version
   */
  private async getAppVersion(): Promise<string> {
    // In a real implementation, this would get from app metadata
    return '1.0.0';
  }

  /**
   * Get OS version
   */
  private async getOSVersion(): Promise<string> {
    // In a real implementation, this would get from device info
    return 'iOS 17.0';
  }

  /**
   * Get device model
   */
  private async getDeviceModel(): Promise<string> {
    // In a real implementation, this would get from device info
    return 'iPhone 15 Pro';
  }

  /**
   * Log debug messages
   */
  private log(...args: any[]): void {
    if (this.debugMode) {
      console.log('[TokenManager]', ...args);
    }
  }
}