/**
 * Location Service - Professional Location and Geo-tagging Management
 * 
 * Enterprise-grade location service with high-accuracy positioning,
 * geofencing, privacy controls, and content geo-tagging capabilities.
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * Team Specialties:
 * - Lead AI Developer + Backend Senior + ML Engineer
 * - Database Administrator + Security Expert
 * - Microservices Architect + Audio Processing Specialist
 * - DevOps Engineer + IA Prompt Engineer
 * 
 * ⚠️ STRICT COPYRIGHT NOTICE ⚠️
 * This code is proprietary and confidential to Fahed Mlaiel.
 * Any unauthorized use, copying, modification, or distribution
 * without explicit written permission is strictly prohibited.
 * Violations will result in legal action.
 * Contact: mlaiel@live.de for licensing inquiries.
 */

import {
  LocationConfig,
  LocationData,
  AddressData,
  LocationMetadata,
  ServiceResponse,
  ServiceError
} from './types';
import {
  handleServiceError,
  formatServiceResponse,
  generateCorrelationId,
  createLocationConfig
} from './utils';
import { STORAGE_KEYS, SERVICE_ENDPOINTS } from './constants';
import MobileAPIService from './MobileAPIService';
import OfflineStorageService from './OfflineStorageService';

interface Geofence {
  id: string;
  name: string;
  center: { latitude: number; longitude: number };
  radius: number; // in meters
  isActive: boolean;
  triggerEvents: ('enter' | 'exit' | 'dwell')[];
  dwellTime?: number; // minimum time to trigger dwell event
  metadata: Record<string, any>;
  createdAt: number;
}

interface LocationTracking {
  id: string;
  startTime: number;
  endTime?: number;
  locations: LocationData[];
  isActive: boolean;
  purpose: 'content_creation' | 'collaboration' | 'analytics' | 'security';
  privacy: 'private' | 'public' | 'collaborative';
}

interface GeolocationHistory {
  timestamp: number;
  location: LocationData;
  accuracy: number;
  activity?: 'stationary' | 'walking' | 'driving' | 'unknown';
  source: 'gps' | 'network' | 'passive';
}

interface PrivacySettings {
  enableLocationTracking: boolean;
  enableGeofencing: boolean;
  enableBackgroundTracking: boolean;
  shareLocationWithCollaborators: boolean;
  anonymizeLocation: boolean;
  precisionLevel: 'exact' | 'approximate' | 'city' | 'region';
  retentionDays: number;
}

/**
 * Professional location service for content creators
 */
class LocationService {
  private static instance: LocationService;
  private config: LocationConfig;
  private apiService: MobileAPIService;
  private storageService: OfflineStorageService;
  private isInitialized = false;
  private currentLocation: LocationData | null = null;
  private watchId: number | null = null;
  private geofences: Map<string, Geofence> = new Map();
  private activeTracking: LocationTracking | null = null;
  private locationHistory: GeolocationHistory[] = [];
  private privacySettings: PrivacySettings = {
    enableLocationTracking: true,
    enableGeofencing: false,
    enableBackgroundTracking: false,
    shareLocationWithCollaborators: false,
    anonymizeLocation: false,
    precisionLevel: 'approximate',
    retentionDays: 30
  };
  private lastKnownLocation: LocationData | null = null;
  private locationCache: Map<string, LocationData> = new Map();

  private constructor(config: LocationConfig) {
    this.config = config;
    this.apiService = MobileAPIService.getInstance();
    this.storageService = OfflineStorageService.getInstance();
    this.initialize();
  }

  public static getInstance(config?: LocationConfig): LocationService {
    if (!LocationService.instance) {
      const defaultConfig = createLocationConfig(config);
      LocationService.instance = new LocationService(defaultConfig);
    }
    return LocationService.instance;
  }

  /**
   * Initialize the location service
   */
  private async initialize(): Promise<void> {
    try {
      // Load persisted data
      await this.loadLocationHistory();
      await this.loadGeofences();
      await this.loadPrivacySettings();
      await this.loadLastKnownLocation();

      // Request location permissions
      await this.requestPermissions();

      // Setup location tracking if enabled
      if (this.privacySettings.enableLocationTracking) {
        await this.startLocationTracking();
      }

      // Setup geofencing if enabled
      if (this.privacySettings.enableGeofencing) {
        await this.setupGeofencing();
      }

      // Start cleanup timer
      this.startCleanupTimer();

      this.isInitialized = true;

    } catch (error) {
      const serviceError = handleServiceError(error, 'LocationService', 'initialize');
      console.error('Failed to initialize location service:', serviceError);
    }
  }

  /**
   * Get current position
   */
  public async getCurrentPosition(
    options: {
      useCache?: boolean;
      timeout?: number;
      maxAge?: number;
    } = {}
  ): Promise<ServiceResponse<LocationData>> {
    try {
      if (!this.isInitialized) {
        await this.initialize();
      }

      if (!this.privacySettings.enableLocationTracking) {
        return {
          success: false,
          error: 'Location tracking is disabled',
          timestamp: Date.now()
        };
      }

      // Use cached location if requested and available
      if (options.useCache && this.currentLocation) {
        const age = Date.now() - this.currentLocation.timestamp;
        const maxAge = options.maxAge || this.config.maximumAge;
        
        if (age < maxAge) {
          return formatServiceResponse(this.currentLocation, true);
        }
      }

      // Get fresh location
      const position = await this.getDevicePosition({
        enableHighAccuracy: this.config.enableHighAccuracy,
        timeout: options.timeout || this.config.timeout,
        maximumAge: options.maxAge || this.config.maximumAge
      });

      const locationData = await this.processLocationData(position);

      // Apply privacy settings
      const processedLocation = this.applyPrivacySettings(locationData);

      // Cache location
      this.currentLocation = processedLocation;
      this.lastKnownLocation = processedLocation;

      // Save to history
      await this.addToLocationHistory(processedLocation, 'gps');

      // Store last known location
      await this.saveLastKnownLocation();

      return formatServiceResponse(processedLocation, false, {
        accuracy: processedLocation.accuracy,
        source: 'gps',
        cached: false
      });

    } catch (error) {
      // Fallback to last known location
      if (this.lastKnownLocation) {
        return formatServiceResponse(this.lastKnownLocation, true, {
          fallback: true,
          source: 'cache'
        });
      }

      const serviceError = handleServiceError(error, 'LocationService', 'getCurrentPosition');
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Start location tracking session
   */
  public async startLocationTracking(
    purpose: 'content_creation' | 'collaboration' | 'analytics' | 'security' = 'content_creation',
    privacy: 'private' | 'public' | 'collaborative' = 'private'
  ): Promise<ServiceResponse<string>> {
    try {
      if (!this.privacySettings.enableLocationTracking) {
        return {
          success: false,
          error: 'Location tracking is disabled',
          timestamp: Date.now()
        };
      }

      // End any active tracking
      if (this.activeTracking) {
        await this.stopLocationTracking();
      }

      const trackingId = generateCorrelationId();

      this.activeTracking = {
        id: trackingId,
        startTime: Date.now(),
        locations: [],
        isActive: true,
        purpose,
        privacy
      };

      // Start continuous location watching
      this.watchId = navigator.geolocation.watchPosition(
        (position) => this.handleLocationUpdate(position),
        (error) => this.handleLocationError(error),
        {
          enableHighAccuracy: this.config.enableHighAccuracy,
          timeout: this.config.timeout,
          maximumAge: this.config.maximumAge
        }
      );

      return formatServiceResponse(trackingId, false, {
        purpose,
        privacy,
        highAccuracy: this.config.enableHighAccuracy
      });

    } catch (error) {
      const serviceError = handleServiceError(error, 'LocationService', 'startLocationTracking');
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Stop location tracking
   */
  public async stopLocationTracking(): Promise<ServiceResponse<{
    trackingId: string;
    duration: number;
    locationCount: number;
    totalDistance: number;
  }>> {
    try {
      if (!this.activeTracking) {
        return {
          success: false,
          error: 'No active location tracking',
          timestamp: Date.now()
        };
      }

      // Stop watching location
      if (this.watchId !== null) {
        navigator.geolocation.clearWatch(this.watchId);
        this.watchId = null;
      }

      const tracking = this.activeTracking;
      tracking.endTime = Date.now();
      tracking.isActive = false;

      // Calculate statistics
      const duration = tracking.endTime - tracking.startTime;
      const locationCount = tracking.locations.length;
      const totalDistance = this.calculateTotalDistance(tracking.locations);

      // Save tracking session
      await this.storageService.store(
        `location_tracking_${tracking.id}`,
        tracking,
        { priority: 6, encrypted: true }
      );

      // Sync with server if not private
      if (tracking.privacy !== 'private') {
        await this.syncLocationTracking(tracking);
      }

      this.activeTracking = null;

      return formatServiceResponse({
        trackingId: tracking.id,
        duration,
        locationCount,
        totalDistance
      });

    } catch (error) {
      const serviceError = handleServiceError(error, 'LocationService', 'stopLocationTracking');
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Create geofence
   */
  public async createGeofence(
    name: string,
    center: { latitude: number; longitude: number },
    radius: number,
    options: {
      triggerEvents?: ('enter' | 'exit' | 'dwell')[];
      dwellTime?: number;
      metadata?: Record<string, any>;
    } = {}
  ): Promise<ServiceResponse<string>> {
    try {
      if (!this.privacySettings.enableGeofencing) {
        return {
          success: false,
          error: 'Geofencing is disabled',
          timestamp: Date.now()
        };
      }

      const geofenceId = generateCorrelationId();

      const geofence: Geofence = {
        id: geofenceId,
        name,
        center,
        radius,
        isActive: true,
        triggerEvents: options.triggerEvents || ['enter', 'exit'],
        dwellTime: options.dwellTime,
        metadata: options.metadata || {},
        createdAt: Date.now()
      };

      this.geofences.set(geofenceId, geofence);
      await this.saveGeofences();

      return formatServiceResponse(geofenceId, false, {
        name,
        radius,
        triggerEvents: geofence.triggerEvents
      });

    } catch (error) {
      const serviceError = handleServiceError(error, 'LocationService', 'createGeofence', { name });
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Remove geofence
   */
  public async removeGeofence(geofenceId: string): Promise<ServiceResponse<boolean>> {
    try {
      if (!this.geofences.has(geofenceId)) {
        return {
          success: false,
          error: 'Geofence not found',
          timestamp: Date.now()
        };
      }

      this.geofences.delete(geofenceId);
      await this.saveGeofences();

      return formatServiceResponse(true);

    } catch (error) {
      const serviceError = handleServiceError(error, 'LocationService', 'removeGeofence', { geofenceId });
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Get address from coordinates
   */
  public async reverseGeocode(
    latitude: number,
    longitude: number
  ): Promise<ServiceResponse<AddressData>> {
    try {
      const cacheKey = `${latitude.toFixed(4)},${longitude.toFixed(4)}`;
      
      // Check cache first
      if (this.config.enableCaching) {
        const cached = await this.storageService.retrieve(`geocode_${cacheKey}`);
        if (cached.success) {
          return formatServiceResponse(cached.data, true);
        }
      }

      // Reverse geocode via API
      const geocodeResult = await this.apiService.request({
        method: 'GET',
        endpoint: '/location/reverse-geocode',
        data: { latitude, longitude },
        requiresAuth: false,
        cacheKey: `geocode_${cacheKey}`,
        cacheTTL: 86400000 // 24 hours
      });

      if (!geocodeResult.success) {
        // Fallback to basic location data
        return formatServiceResponse({
          formatted: `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`,
          city: 'Unknown',
          country: 'Unknown'
        });
      }

      const addressData: AddressData = geocodeResult.data;

      // Cache result
      if (this.config.enableCaching) {
        await this.storageService.store(`geocode_${cacheKey}`, addressData, {
          ttl: 86400000, // 24 hours
          priority: 3
        });
      }

      return formatServiceResponse(addressData);

    } catch (error) {
      const serviceError = handleServiceError(error, 'LocationService', 'reverseGeocode', { latitude, longitude });
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Get location history
   */
  public async getLocationHistory(
    filter: {
      startDate?: number;
      endDate?: number;
      source?: 'gps' | 'network' | 'passive';
      limit?: number;
    } = {}
  ): Promise<ServiceResponse<{
    history: GeolocationHistory[];
    totalCount: number;
    averageAccuracy: number;
  }>> {
    try {
      let filteredHistory = [...this.locationHistory];

      // Apply filters
      if (filter.startDate) {
        filteredHistory = filteredHistory.filter(h => h.timestamp >= filter.startDate!);
      }

      if (filter.endDate) {
        filteredHistory = filteredHistory.filter(h => h.timestamp <= filter.endDate!);
      }

      if (filter.source) {
        filteredHistory = filteredHistory.filter(h => h.source === filter.source);
      }

      // Sort by timestamp (newest first)
      filteredHistory.sort((a, b) => b.timestamp - a.timestamp);

      // Apply limit
      if (filter.limit) {
        filteredHistory = filteredHistory.slice(0, filter.limit);
      }

      // Calculate average accuracy
      const averageAccuracy = filteredHistory.length > 0 
        ? filteredHistory.reduce((sum, h) => sum + h.accuracy, 0) / filteredHistory.length
        : 0;

      return formatServiceResponse({
        history: filteredHistory,
        totalCount: filteredHistory.length,
        averageAccuracy
      });

    } catch (error) {
      const serviceError = handleServiceError(error, 'LocationService', 'getLocationHistory');
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Update privacy settings
   */
  public async updatePrivacySettings(
    settings: Partial<PrivacySettings>
  ): Promise<ServiceResponse<boolean>> {
    try {
      const oldSettings = { ...this.privacySettings };
      this.privacySettings = { ...this.privacySettings, ...settings };

      // Save settings
      await this.savePrivacySettings();

      // Apply changes
      if (oldSettings.enableLocationTracking !== this.privacySettings.enableLocationTracking) {
        if (this.privacySettings.enableLocationTracking) {
          await this.startLocationTracking();
        } else {
          await this.stopLocationTracking();
        }
      }

      if (oldSettings.enableGeofencing !== this.privacySettings.enableGeofencing) {
        if (this.privacySettings.enableGeofencing) {
          await this.setupGeofencing();
        } else {
          await this.clearGeofences();
        }
      }

      return formatServiceResponse(true);

    } catch (error) {
      const serviceError = handleServiceError(error, 'LocationService', 'updatePrivacySettings');
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Get location statistics
   */
  public async getLocationStatistics(): Promise<ServiceResponse<{
    totalLocations: number;
    trackingSessions: number;
    averageAccuracy: number;
    mostVisitedArea: string;
    geofenceCount: number;
    privacyLevel: string;
  }>> {
    try {
      const totalLocations = this.locationHistory.length;
      
      // Count tracking sessions
      const sessionKeys = await this.storageService.getKeys();
      const trackingSessions = sessionKeys.filter(key => key.startsWith('location_tracking_')).length;

      // Calculate average accuracy
      const averageAccuracy = totalLocations > 0 
        ? this.locationHistory.reduce((sum, h) => sum + h.accuracy, 0) / totalLocations
        : 0;

      // Find most visited area (simplified)
      const mostVisitedArea = 'Unknown'; // Would implement proper clustering

      const geofenceCount = this.geofences.size;
      const privacyLevel = this.privacySettings.precisionLevel;

      return formatServiceResponse({
        totalLocations,
        trackingSessions,
        averageAccuracy,
        mostVisitedArea,
        geofenceCount,
        privacyLevel
      });

    } catch (error) {
      const serviceError = handleServiceError(error, 'LocationService', 'getLocationStatistics');
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  // Private helper methods

  private async requestPermissions(): Promise<boolean> {
    try {
      if (!navigator.geolocation) {
        return false;
      }

      // Test location access
      return new Promise((resolve) => {
        navigator.geolocation.getCurrentPosition(
          () => resolve(true),
          () => resolve(false),
          { timeout: 10000 }
        );
      });
    } catch (error) {
      console.error('Failed to request location permissions:', error);
      return false;
    }
  }

  private async getDevicePosition(options: PositionOptions): Promise<GeolocationPosition> {
    return new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject, options);
    });
  }

  private async processLocationData(position: GeolocationPosition): Promise<LocationData> {
    const coords = position.coords;
    
    const locationData: LocationData = {
      latitude: coords.latitude,
      longitude: coords.longitude,
      altitude: coords.altitude || undefined,
      accuracy: coords.accuracy,
      timestamp: position.timestamp,
      metadata: {
        provider: 'gps',
        speed: coords.speed || undefined,
        heading: coords.heading || undefined,
        cached: false,
        batteryOptimized: false
      }
    };

    // Get address if not anonymized
    if (!this.privacySettings.anonymizeLocation) {
      try {
        const addressResult = await this.reverseGeocode(coords.latitude, coords.longitude);
        if (addressResult.success) {
          locationData.address = addressResult.data;
        }
      } catch (error) {
        console.warn('Failed to get address:', error);
      }
    }

    return locationData;
  }

  private applyPrivacySettings(location: LocationData): LocationData {
    const processed = { ...location };

    switch (this.privacySettings.precisionLevel) {
      case 'city':
        // Round to city level precision (~1km)
        processed.latitude = Math.round(processed.latitude * 100) / 100;
        processed.longitude = Math.round(processed.longitude * 100) / 100;
        processed.accuracy = Math.max(processed.accuracy, 1000);
        break;

      case 'region':
        // Round to region level precision (~10km)
        processed.latitude = Math.round(processed.latitude * 10) / 10;
        processed.longitude = Math.round(processed.longitude * 10) / 10;
        processed.accuracy = Math.max(processed.accuracy, 10000);
        break;

      case 'approximate':
        // Round to approximate precision (~100m)
        processed.latitude = Math.round(processed.latitude * 1000) / 1000;
        processed.longitude = Math.round(processed.longitude * 1000) / 1000;
        processed.accuracy = Math.max(processed.accuracy, 100);
        break;

      case 'exact':
      default:
        // Keep exact location
        break;
    }

    if (this.privacySettings.anonymizeLocation) {
      delete processed.address;
    }

    return processed;
  }

  private async handleLocationUpdate(position: GeolocationPosition): Promise<void> {
    try {
      const locationData = await this.processLocationData(position);
      const processedLocation = this.applyPrivacySettings(locationData);

      this.currentLocation = processedLocation;

      // Add to tracking session if active
      if (this.activeTracking && this.activeTracking.isActive) {
        this.activeTracking.locations.push(processedLocation);
      }

      // Add to history
      await this.addToLocationHistory(processedLocation, 'gps');

      // Check geofences
      await this.checkGeofences(processedLocation);

    } catch (error) {
      console.error('Failed to handle location update:', error);
    }
  }

  private handleLocationError(error: GeolocationPositionError): void {
    console.error('Location error:', error.message);
  }

  private async checkGeofences(location: LocationData): Promise<void> {
    if (!this.privacySettings.enableGeofencing) return;

    for (const geofence of this.geofences.values()) {
      if (!geofence.isActive) continue;

      const distance = this.calculateDistance(
        location.latitude,
        location.longitude,
        geofence.center.latitude,
        geofence.center.longitude
      );

      const isInside = distance <= geofence.radius;

      // Trigger events based on geofence state
      if (isInside && geofence.triggerEvents.includes('enter')) {
        await this.triggerGeofenceEvent(geofence, 'enter', location);
      } else if (!isInside && geofence.triggerEvents.includes('exit')) {
        await this.triggerGeofenceEvent(geofence, 'exit', location);
      }
    }
  }

  private async triggerGeofenceEvent(
    geofence: Geofence,
    event: 'enter' | 'exit' | 'dwell',
    location: LocationData
  ): Promise<void> {
    try {
      // Log geofence event
      console.log(`Geofence ${event}: ${geofence.name}`);

      // Notify via API
      await this.apiService.request({
        method: 'POST',
        endpoint: '/location/geofence-event',
        data: {
          geofenceId: geofence.id,
          event,
          location,
          timestamp: Date.now()
        },
        requiresAuth: true,
        priority: 'normal'
      });

    } catch (error) {
      console.error('Failed to trigger geofence event:', error);
    }
  }

  private calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
    const R = 6371e3; // Earth's radius in meters
    const φ1 = lat1 * Math.PI / 180;
    const φ2 = lat2 * Math.PI / 180;
    const Δφ = (lat2 - lat1) * Math.PI / 180;
    const Δλ = (lon2 - lon1) * Math.PI / 180;

    const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
              Math.cos(φ1) * Math.cos(φ2) *
              Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return R * c;
  }

  private calculateTotalDistance(locations: LocationData[]): number {
    if (locations.length < 2) return 0;

    let totalDistance = 0;
    for (let i = 1; i < locations.length; i++) {
      totalDistance += this.calculateDistance(
        locations[i - 1].latitude,
        locations[i - 1].longitude,
        locations[i].latitude,
        locations[i].longitude
      );
    }

    return totalDistance;
  }

  private async addToLocationHistory(
    location: LocationData,
    source: 'gps' | 'network' | 'passive'
  ): Promise<void> {
    const historyEntry: GeolocationHistory = {
      timestamp: location.timestamp,
      location,
      accuracy: location.accuracy,
      source
    };

    this.locationHistory.push(historyEntry);

    // Keep only recent history
    const retentionTime = this.privacySettings.retentionDays * 24 * 60 * 60 * 1000;
    const cutoffTime = Date.now() - retentionTime;
    this.locationHistory = this.locationHistory.filter(h => h.timestamp > cutoffTime);

    await this.saveLocationHistory();
  }

  private async setupGeofencing(): Promise<void> {
    // Setup geofencing monitoring
    console.log('Setting up geofencing with', this.geofences.size, 'geofences');
  }

  private async clearGeofences(): Promise<void> {
    this.geofences.clear();
    await this.saveGeofences();
  }

  private async syncLocationTracking(tracking: LocationTracking): Promise<void> {
    try {
      await this.apiService.request({
        method: 'POST',
        endpoint: SERVICE_ENDPOINTS.ANALYTICS.EVENTS,
        data: {
          type: 'location_tracking',
          trackingId: tracking.id,
          purpose: tracking.purpose,
          privacy: tracking.privacy,
          locationCount: tracking.locations.length,
          duration: tracking.endTime! - tracking.startTime,
          locations: tracking.privacy === 'public' ? tracking.locations : []
        },
        requiresAuth: true
      });
    } catch (error) {
      console.error('Failed to sync location tracking:', error);
    }
  }

  private startCleanupTimer(): void {
    // Cleanup old data every hour
    setInterval(async () => {
      try {
        const retentionTime = this.privacySettings.retentionDays * 24 * 60 * 60 * 1000;
        const cutoffTime = Date.now() - retentionTime;
        
        this.locationHistory = this.locationHistory.filter(h => h.timestamp > cutoffTime);
        await this.saveLocationHistory();
      } catch (error) {
        console.error('Failed to cleanup location data:', error);
      }
    }, 60 * 60 * 1000);
  }

  // Storage methods

  private async loadLocationHistory(): Promise<void> {
    try {
      const result = await this.storageService.retrieve(STORAGE_KEYS.LOCATION_HISTORY);
      if (result.success) {
        this.locationHistory = result.data || [];
      }
    } catch (error) {
      console.warn('Failed to load location history:', error);
      this.locationHistory = [];
    }
  }

  private async saveLocationHistory(): Promise<void> {
    try {
      await this.storageService.store(STORAGE_KEYS.LOCATION_HISTORY, this.locationHistory, {
        priority: 4,
        encrypted: true
      });
    } catch (error) {
      console.error('Failed to save location history:', error);
    }
  }

  private async loadGeofences(): Promise<void> {
    try {
      const result = await this.storageService.retrieve(STORAGE_KEYS.GEOFENCES);
      if (result.success) {
        const geofences = result.data || {};
        this.geofences = new Map(Object.entries(geofences));
      }
    } catch (error) {
      console.warn('Failed to load geofences:', error);
      this.geofences = new Map();
    }
  }

  private async saveGeofences(): Promise<void> {
    try {
      const geofences = Object.fromEntries(this.geofences);
      await this.storageService.store(STORAGE_KEYS.GEOFENCES, geofences, {
        priority: 5,
        encrypted: true
      });
    } catch (error) {
      console.error('Failed to save geofences:', error);
    }
  }

  private async loadPrivacySettings(): Promise<void> {
    try {
      const result = await this.storageService.retrieve('location_privacy_settings');
      if (result.success) {
        this.privacySettings = { ...this.privacySettings, ...result.data };
      }
    } catch (error) {
      console.warn('Failed to load privacy settings:', error);
    }
  }

  private async savePrivacySettings(): Promise<void> {
    try {
      await this.storageService.store('location_privacy_settings', this.privacySettings, {
        priority: 6,
        encrypted: true
      });
    } catch (error) {
      console.error('Failed to save privacy settings:', error);
    }
  }

  private async loadLastKnownLocation(): Promise<void> {
    try {
      const result = await this.storageService.retrieve(STORAGE_KEYS.LOCATION_CACHE);
      if (result.success) {
        this.lastKnownLocation = result.data;
      }
    } catch (error) {
      console.warn('Failed to load last known location:', error);
    }
  }

  private async saveLastKnownLocation(): Promise<void> {
    try {
      if (this.lastKnownLocation) {
        await this.storageService.store(STORAGE_KEYS.LOCATION_CACHE, this.lastKnownLocation, {
          priority: 7
        });
      }
    } catch (error) {
      console.error('Failed to save last known location:', error);
    }
  }

  /**
   * Cleanup resources
   */
  public destroy(): void {
    if (this.watchId !== null) {
      navigator.geolocation.clearWatch(this.watchId);
      this.watchId = null;
    }

    if (this.activeTracking) {
      this.stopLocationTracking();
    }

    this.geofences.clear();
    this.locationHistory = [];
    this.locationCache.clear();
  }
}

export default LocationService;