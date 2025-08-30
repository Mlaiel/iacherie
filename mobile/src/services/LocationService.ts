/**
 * Location Service - Advanced GPS and location services
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * WARNING: This software is proprietary and confidential. 
 * Unauthorized copying, distribution, or use is strictly prohibited.
 * All rights reserved by Fahed Mlaiel.
 */

import { offlineStorageService } from './OfflineStorageService';
import { mobileAPIService } from './MobileAPIService';

export interface LocationCapabilities {
  isSupported: boolean;
  highAccuracy: boolean;
  backgroundTracking: boolean;
  geofencing: boolean;
  compass: boolean;
  altimeter: boolean;
}

export interface LocationData {
  latitude: number;
  longitude: number;
  accuracy: number; // meters
  altitude?: number; // meters
  altitudeAccuracy?: number; // meters
  heading?: number; // degrees
  speed?: number; // m/s
  timestamp: number;
}

export interface LocationOptions {
  enableHighAccuracy?: boolean;
  timeout?: number; // milliseconds
  maximumAge?: number; // milliseconds
  distanceFilter?: number; // meters
  desiredAccuracy?: number; // meters
  interval?: number; // milliseconds for continuous tracking
  backgroundTracking?: boolean;
}

export interface GeofenceRegion {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  radius: number; // meters
  type: 'enter' | 'exit' | 'both';
  active: boolean;
  metadata?: Record<string, any>;
}

export interface GeofenceEvent {
  regionId: string;
  type: 'enter' | 'exit';
  location: LocationData;
  timestamp: number;
  dwellTime?: number; // for exit events
}

export interface LocationHistory {
  locations: LocationData[];
  startTime: number;
  endTime: number;
  totalDistance: number; // meters
  averageSpeed: number; // m/s
  maxSpeed: number; // m/s
  boundingBox: {
    north: number;
    south: number;
    east: number;
    west: number;
  };
}

export interface PlaceInfo {
  name: string;
  address: string;
  category: string;
  rating?: number;
  phone?: string;
  website?: string;
  location: LocationData;
  distance?: number; // meters from current location
}

export interface RouteInfo {
  origin: LocationData;
  destination: LocationData;
  waypoints?: LocationData[];
  distance: number; // meters
  duration: number; // seconds
  coordinates: LocationData[];
  instructions: {
    instruction: string;
    distance: number;
    duration: number;
    location: LocationData;
  }[];
}

export interface LocationPrivacySettings {
  enabled: boolean;
  shareLocation: boolean;
  trackHistory: boolean;
  backgroundTracking: boolean;
  shareWithCollaborators: boolean;
  shareWithPlatforms: boolean;
  anonymizeData: boolean;
  dataRetentionDays: number;
  geofenceAlerts: boolean;
}

export interface ContentLocationData {
  contentId: string;
  location: LocationData;
  venue?: string;
  city: string;
  country: string;
  region: string;
  timezone: string;
  weather?: {
    temperature: number;
    condition: string;
    humidity: number;
  };
  nearbyPlaces: PlaceInfo[];
  tags: string[];
}

export class LocationService {
  private isInitialized: boolean = false;
  private capabilities: LocationCapabilities;
  private privacySettings: LocationPrivacySettings;
  private currentLocation: LocationData | null = null;
  private watchId: number | null = null;
  private isTracking: boolean = false;
  private geofences: Map<string, GeofenceRegion> = new Map();
  private locationHistory: LocationData[] = [];
  private trackingStartTime: number = 0;
  private backgroundTrackingEnabled: boolean = false;

  constructor() {
    this.capabilities = {
      isSupported: false,
      highAccuracy: false,
      backgroundTracking: false,
      geofencing: false,
      compass: false,
      altimeter: false,
    };

    this.privacySettings = {
      enabled: true,
      shareLocation: false,
      trackHistory: false,
      backgroundTracking: false,
      shareWithCollaborators: false,
      shareWithPlatforms: false,
      anonymizeData: true,
      dataRetentionDays: 30,
      geofenceAlerts: true,
    };

    this.initializeService();
  }

  private async initializeService(): Promise<void> {
    try {
      // Check for geolocation support
      if (!navigator.geolocation) {
        console.warn('Geolocation API not supported');
        return;
      }

      // Detect location capabilities
      await this.detectCapabilities();
      
      // Load settings
      await this.loadSettings();
      
      // Load geofences
      await this.loadGeofences();
      
      // Load location history
      await this.loadLocationHistory();
      
      // Setup background tracking if enabled
      if (this.privacySettings.backgroundTracking) {
        await this.enableBackgroundTracking();
      }
      
      this.isInitialized = true;
      console.log('Location Service initialized successfully');
    } catch (error) {
      console.error('Failed to initialize Location Service:', error);
    }
  }

  // Public API Methods
  async requestPermissions(): Promise<'granted' | 'denied' | 'prompt'> {
    try {
      // Try to get current position to trigger permission request
      await this.getCurrentPosition();
      return 'granted';
    } catch (error) {
      if (error.code === 1) { // PERMISSION_DENIED
        return 'denied';
      }
      return 'prompt';
    }
  }

  getCapabilities(): LocationCapabilities {
    return { ...this.capabilities };
  }

  async getCurrentPosition(options?: LocationOptions): Promise<LocationData> {
    return new Promise((resolve, reject) => {
      const positionOptions: PositionOptions = {
        enableHighAccuracy: options?.enableHighAccuracy ?? true,
        timeout: options?.timeout ?? 15000,
        maximumAge: options?.maximumAge ?? 60000,
      };

      navigator.geolocation.getCurrentPosition(
        (position) => {
          const locationData = this.createLocationData(position);
          this.currentLocation = locationData;
          
          if (this.privacySettings.trackHistory) {
            this.addToLocationHistory(locationData);
          }
          
          resolve(locationData);
        },
        (error) => {
          reject(this.handleLocationError(error));
        },
        positionOptions
      );
    });
  }

  async startTracking(options?: LocationOptions): Promise<boolean> {
    try {
      if (!this.capabilities.isSupported) {
        throw new Error('Location services not supported');
      }

      if (this.isTracking) {
        console.warn('Location tracking already active');
        return true;
      }

      const trackingOptions: PositionOptions = {
        enableHighAccuracy: options?.enableHighAccuracy ?? true,
        timeout: options?.timeout ?? 30000,
        maximumAge: options?.maximumAge ?? 5000,
      };

      this.watchId = navigator.geolocation.watchPosition(
        (position) => {
          const locationData = this.createLocationData(position);
          this.handleLocationUpdate(locationData, options);
        },
        (error) => {
          this.handleLocationError(error);
        },
        trackingOptions
      );

      this.isTracking = true;
      this.trackingStartTime = Date.now();
      
      this.emitLocationEvent('tracking-started', { options });
      
      return true;
    } catch (error) {
      console.error('Failed to start location tracking:', error);
      return false;
    }
  }

  async stopTracking(): Promise<boolean> {
    try {
      if (!this.isTracking || !this.watchId) {
        return false;
      }

      navigator.geolocation.clearWatch(this.watchId);
      this.watchId = null;
      this.isTracking = false;
      
      // Save location history
      await this.saveLocationHistory();
      
      this.emitLocationEvent('tracking-stopped', {
        duration: Date.now() - this.trackingStartTime,
        pointsRecorded: this.locationHistory.length,
      });
      
      return true;
    } catch (error) {
      console.error('Failed to stop location tracking:', error);
      return false;
    }
  }

  getCurrentLocation(): LocationData | null {
    return this.currentLocation ? { ...this.currentLocation } : null;
  }

  isLocationTracking(): boolean {
    return this.isTracking;
  }

  // Geofencing
  async addGeofence(region: Omit<GeofenceRegion, 'id'>): Promise<string> {
    const geofence: GeofenceRegion = {
      ...region,
      id: `geofence_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    };

    this.geofences.set(geofence.id, geofence);
    await this.saveGeofences();
    
    this.emitLocationEvent('geofence-added', { geofence });
    
    return geofence.id;
  }

  async removeGeofence(geofenceId: string): Promise<boolean> {
    const removed = this.geofences.delete(geofenceId);
    
    if (removed) {
      await this.saveGeofences();
      this.emitLocationEvent('geofence-removed', { geofenceId });
    }
    
    return removed;
  }

  getGeofences(): GeofenceRegion[] {
    return Array.from(this.geofences.values());
  }

  async updateGeofence(geofenceId: string, updates: Partial<GeofenceRegion>): Promise<boolean> {
    const geofence = this.geofences.get(geofenceId);
    if (!geofence) return false;

    Object.assign(geofence, updates);
    this.geofences.set(geofenceId, geofence);
    await this.saveGeofences();
    
    this.emitLocationEvent('geofence-updated', { geofence });
    
    return true;
  }

  // Location History
  getLocationHistory(startTime?: number, endTime?: number): LocationHistory {
    let filteredLocations = this.locationHistory;
    
    if (startTime || endTime) {
      filteredLocations = this.locationHistory.filter(location => {
        return (!startTime || location.timestamp >= startTime) &&
               (!endTime || location.timestamp <= endTime);
      });
    }

    return this.analyzeLocationHistory(filteredLocations);
  }

  async clearLocationHistory(): Promise<void> {
    this.locationHistory = [];
    await offlineStorageService.remove('location_history');
    this.emitLocationEvent('history-cleared');
  }

  async exportLocationHistory(format: 'json' | 'gpx' | 'kml' = 'json'): Promise<string> {
    const history = this.getLocationHistory();
    
    switch (format) {
      case 'gpx':
        return this.exportToGPX(history);
      case 'kml':
        return this.exportToKML(history);
      default:
        return JSON.stringify(history, null, 2);
    }
  }

  // Places and Points of Interest
  async searchNearbyPlaces(
    category?: string,
    radius: number = 1000,
    limit: number = 20
  ): Promise<PlaceInfo[]> {
    try {
      if (!this.currentLocation) {
        await this.getCurrentPosition();
      }

      if (!this.currentLocation) {
        throw new Error('Current location not available');
      }

      // In a real implementation, this would call a places API
      const response = await mobileAPIService.makeRequest('/location/places/search', {
        method: 'POST',
        body: JSON.stringify({
          location: this.currentLocation,
          category,
          radius,
          limit,
        }),
      });

      return response.data.places || [];
    } catch (error) {
      console.error('Failed to search nearby places:', error);
      return [];
    }
  }

  async getPlaceInfo(placeId: string): Promise<PlaceInfo | null> {
    try {
      const response = await mobileAPIService.makeRequest(`/location/places/${placeId}`);
      return response.data || null;
    } catch (error) {
      console.error('Failed to get place info:', error);
      return null;
    }
  }

  // Route Planning
  async calculateRoute(
    destination: LocationData,
    waypoints?: LocationData[],
    mode: 'driving' | 'walking' | 'cycling' | 'transit' = 'driving'
  ): Promise<RouteInfo | null> {
    try {
      if (!this.currentLocation) {
        await this.getCurrentPosition();
      }

      if (!this.currentLocation) {
        throw new Error('Current location not available');
      }

      const response = await mobileAPIService.makeRequest('/location/routes/calculate', {
        method: 'POST',
        body: JSON.stringify({
          origin: this.currentLocation,
          destination,
          waypoints: waypoints || [],
          mode,
        }),
      });

      return response.data || null;
    } catch (error) {
      console.error('Failed to calculate route:', error);
      return null;
    }
  }

  // Content Integration
  async tagContentWithLocation(contentId: string): Promise<ContentLocationData | null> {
    try {
      if (!this.currentLocation) {
        await this.getCurrentPosition();
      }

      if (!this.currentLocation) {
        throw new Error('Current location not available');
      }

      // Get location details
      const [places, geocoding] = await Promise.all([
        this.searchNearbyPlaces(undefined, 500, 10),
        this.reverseGeocode(this.currentLocation),
      ]);

      const contentLocationData: ContentLocationData = {
        contentId,
        location: this.currentLocation,
        city: geocoding.city,
        country: geocoding.country,
        region: geocoding.region,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        nearbyPlaces: places,
        tags: this.generateLocationTags(geocoding, places),
      };

      // Add venue if at a specific place
      const nearestPlace = places.find(place => place.distance && place.distance < 50);
      if (nearestPlace) {
        contentLocationData.venue = nearestPlace.name;
      }

      // Save location data
      await offlineStorageService.store(`content_location_${contentId}`, contentLocationData);
      
      // Sync with server if privacy settings allow
      if (this.privacySettings.shareWithPlatforms) {
        await this.syncContentLocation(contentLocationData);
      }

      return contentLocationData;
    } catch (error) {
      console.error('Failed to tag content with location:', error);
      return null;
    }
  }

  async getContentLocation(contentId: string): Promise<ContentLocationData | null> {
    return await offlineStorageService.retrieve(`content_location_${contentId}`);
  }

  // Collaboration Features
  async shareLocationWithCollaborator(
    collaboratorId: string,
    duration: number = 3600 // 1 hour
  ): Promise<boolean> {
    try {
      if (!this.privacySettings.shareWithCollaborators) {
        throw new Error('Location sharing with collaborators is disabled');
      }

      if (!this.currentLocation) {
        await this.getCurrentPosition();
      }

      const response = await mobileAPIService.makeRequest('/collaboration/share-location', {
        method: 'POST',
        body: JSON.stringify({
          collaboratorId,
          location: this.currentLocation,
          duration,
          timestamp: Date.now(),
        }),
      });

      return response.status === 200;
    } catch (error) {
      console.error('Failed to share location:', error);
      return false;
    }
  }

  async getCollaboratorLocations(): Promise<Array<{
    collaboratorId: string;
    location: LocationData;
    sharedAt: number;
    expiresAt: number;
  }>> {
    try {
      const response = await mobileAPIService.makeRequest('/collaboration/locations');
      return response.data || [];
    } catch (error) {
      console.error('Failed to get collaborator locations:', error);
      return [];
    }
  }

  // Privacy and Settings
  async updatePrivacySettings(settings: Partial<LocationPrivacySettings>): Promise<void> {
    this.privacySettings = { ...this.privacySettings, ...settings };
    await offlineStorageService.store('location_privacy_settings', this.privacySettings);
    
    // Apply changes
    if (!settings.trackHistory && this.isTracking) {
      await this.stopTracking();
    }
    
    if (settings.backgroundTracking !== undefined) {
      if (settings.backgroundTracking) {
        await this.enableBackgroundTracking();
      } else {
        await this.disableBackgroundTracking();
      }
    }
    
    this.emitLocationEvent('privacy-settings-updated', { settings: this.privacySettings });
  }

  getPrivacySettings(): LocationPrivacySettings {
    return { ...this.privacySettings };
  }

  // Utility Methods
  calculateDistance(location1: LocationData, location2: LocationData): number {
    const R = 6371000; // Earth's radius in meters
    const lat1Rad = location1.latitude * Math.PI / 180;
    const lat2Rad = location2.latitude * Math.PI / 180;
    const deltaLatRad = (location2.latitude - location1.latitude) * Math.PI / 180;
    const deltaLonRad = (location2.longitude - location1.longitude) * Math.PI / 180;

    const a = Math.sin(deltaLatRad / 2) * Math.sin(deltaLatRad / 2) +
              Math.cos(lat1Rad) * Math.cos(lat2Rad) *
              Math.sin(deltaLonRad / 2) * Math.sin(deltaLonRad / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return R * c;
  }

  calculateBearing(from: LocationData, to: LocationData): number {
    const lat1Rad = from.latitude * Math.PI / 180;
    const lat2Rad = to.latitude * Math.PI / 180;
    const deltaLonRad = (to.longitude - from.longitude) * Math.PI / 180;

    const y = Math.sin(deltaLonRad) * Math.cos(lat2Rad);
    const x = Math.cos(lat1Rad) * Math.sin(lat2Rad) - 
              Math.sin(lat1Rad) * Math.cos(lat2Rad) * Math.cos(deltaLonRad);

    const bearing = Math.atan2(y, x) * 180 / Math.PI;
    return (bearing + 360) % 360;
  }

  isLocationWithinRadius(
    center: LocationData,
    location: LocationData,
    radius: number
  ): boolean {
    const distance = this.calculateDistance(center, location);
    return distance <= radius;
  }

  // Private Methods
  private async detectCapabilities(): Promise<void> {
    this.capabilities.isSupported = 'geolocation' in navigator;
    
    if (this.capabilities.isSupported) {
      // Check for high accuracy support
      this.capabilities.highAccuracy = true; // Most modern devices support this
      
      // Check for background tracking support (requires service worker)
      this.capabilities.backgroundTracking = 'serviceWorker' in navigator;
      
      // Check for compass support
      this.capabilities.compass = 'DeviceOrientationEvent' in window;
      
      // Geofencing is software-implemented
      this.capabilities.geofencing = true;
    }
  }

  private createLocationData(position: GeolocationPosition): LocationData {
    return {
      latitude: position.coords.latitude,
      longitude: position.coords.longitude,
      accuracy: position.coords.accuracy,
      altitude: position.coords.altitude || undefined,
      altitudeAccuracy: position.coords.altitudeAccuracy || undefined,
      heading: position.coords.heading || undefined,
      speed: position.coords.speed || undefined,
      timestamp: position.timestamp,
    };
  }

  private handleLocationUpdate(location: LocationData, options?: LocationOptions): void {
    // Apply distance filter
    if (options?.distanceFilter && this.currentLocation) {
      const distance = this.calculateDistance(this.currentLocation, location);
      if (distance < options.distanceFilter) {
        return; // Skip this update
      }
    }

    this.currentLocation = location;
    
    // Add to history if tracking is enabled
    if (this.privacySettings.trackHistory) {
      this.addToLocationHistory(location);
    }
    
    // Check geofences
    this.checkGeofences(location);
    
    // Emit location update event
    this.emitLocationEvent('location-updated', { location });
  }

  private addToLocationHistory(location: LocationData): void {
    this.locationHistory.push(location);
    
    // Apply data retention policy
    const retentionTime = this.privacySettings.dataRetentionDays * 24 * 60 * 60 * 1000;
    const cutoffTime = Date.now() - retentionTime;
    
    this.locationHistory = this.locationHistory.filter(
      loc => loc.timestamp > cutoffTime
    );
  }

  private checkGeofences(location: LocationData): void {
    for (const geofence of this.geofences.values()) {
      if (!geofence.active) continue;

      const isInside = this.isLocationWithinRadius(
        { latitude: geofence.latitude, longitude: geofence.longitude, accuracy: 0, timestamp: 0 },
        location,
        geofence.radius
      );

      // Check for geofence events
      // This would need state tracking in a real implementation
      this.handleGeofenceEvent(geofence, location, isInside ? 'enter' : 'exit');
    }
  }

  private handleGeofenceEvent(
    geofence: GeofenceRegion,
    location: LocationData,
    eventType: 'enter' | 'exit'
  ): void {
    if (geofence.type !== 'both' && geofence.type !== eventType) {
      return;
    }

    const event: GeofenceEvent = {
      regionId: geofence.id,
      type: eventType,
      location,
      timestamp: Date.now(),
    };

    this.emitLocationEvent('geofence-event', { event, geofence });
    
    if (this.privacySettings.geofenceAlerts) {
      this.showGeofenceNotification(geofence, eventType);
    }
  }

  private showGeofenceNotification(geofence: GeofenceRegion, eventType: 'enter' | 'exit'): void {
    // This would integrate with the push notification service
    const message = `${eventType === 'enter' ? 'Entered' : 'Exited'} ${geofence.name}`;
    
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('Location Alert', {
        body: message,
        icon: '/icons/location-icon.png',
        tag: `geofence-${geofence.id}`,
      });
    }
  }

  private analyzeLocationHistory(locations: LocationData[]): LocationHistory {
    if (locations.length === 0) {
      return {
        locations: [],
        startTime: 0,
        endTime: 0,
        totalDistance: 0,
        averageSpeed: 0,
        maxSpeed: 0,
        boundingBox: { north: 0, south: 0, east: 0, west: 0 },
      };
    }

    let totalDistance = 0;
    let maxSpeed = 0;
    let minLat = locations[0].latitude;
    let maxLat = locations[0].latitude;
    let minLon = locations[0].longitude;
    let maxLon = locations[0].longitude;

    for (let i = 1; i < locations.length; i++) {
      const current = locations[i];
      const previous = locations[i - 1];
      
      // Calculate distance
      totalDistance += this.calculateDistance(previous, current);
      
      // Track max speed
      if (current.speed && current.speed > maxSpeed) {
        maxSpeed = current.speed;
      }
      
      // Update bounding box
      minLat = Math.min(minLat, current.latitude);
      maxLat = Math.max(maxLat, current.latitude);
      minLon = Math.min(minLon, current.longitude);
      maxLon = Math.max(maxLon, current.longitude);
    }

    const startTime = locations[0].timestamp;
    const endTime = locations[locations.length - 1].timestamp;
    const duration = (endTime - startTime) / 1000; // seconds
    const averageSpeed = duration > 0 ? totalDistance / duration : 0;

    return {
      locations,
      startTime,
      endTime,
      totalDistance,
      averageSpeed,
      maxSpeed,
      boundingBox: {
        north: maxLat,
        south: minLat,
        east: maxLon,
        west: minLon,
      },
    };
  }

  private async reverseGeocode(location: LocationData): Promise<{
    city: string;
    country: string;
    region: string;
    address?: string;
  }> {
    try {
      const response = await mobileAPIService.makeRequest('/location/reverse-geocode', {
        method: 'POST',
        body: JSON.stringify({ location }),
      });

      return response.data || {
        city: 'Unknown',
        country: 'Unknown',
        region: 'Unknown',
      };
    } catch (error) {
      console.error('Reverse geocoding failed:', error);
      return {
        city: 'Unknown',
        country: 'Unknown',
        region: 'Unknown',
      };
    }
  }

  private generateLocationTags(
    geocoding: { city: string; country: string; region: string },
    places: PlaceInfo[]
  ): string[] {
    const tags: string[] = [
      geocoding.city,
      geocoding.region,
      geocoding.country,
    ];

    // Add place categories
    places.forEach(place => {
      if (place.category && !tags.includes(place.category)) {
        tags.push(place.category);
      }
    });

    return tags.filter(tag => tag !== 'Unknown');
  }

  private async syncContentLocation(contentLocationData: ContentLocationData): Promise<void> {
    try {
      await mobileAPIService.makeRequest('/content/location', {
        method: 'POST',
        body: JSON.stringify(contentLocationData),
      });
    } catch (error) {
      console.error('Failed to sync content location:', error);
    }
  }

  private async enableBackgroundTracking(): Promise<void> {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.register('/location-worker.js');
        this.backgroundTrackingEnabled = true;
        console.log('Background location tracking enabled');
      } catch (error) {
        console.error('Failed to enable background tracking:', error);
      }
    }
  }

  private async disableBackgroundTracking(): Promise<void> {
    if ('serviceWorker' in navigator) {
      const registrations = await navigator.serviceWorker.getRegistrations();
      for (const registration of registrations) {
        if (registration.scope.includes('location-worker')) {
          await registration.unregister();
        }
      }
      this.backgroundTrackingEnabled = false;
      console.log('Background location tracking disabled');
    }
  }

  private exportToGPX(history: LocationHistory): string {
    const gpx = `<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Ainflue">
  <trk>
    <name>Location History</name>
    <trkseg>
${history.locations.map(loc => `      <trkpt lat="${loc.latitude}" lon="${loc.longitude}">
        <time>${new Date(loc.timestamp).toISOString()}</time>
        ${loc.altitude ? `<ele>${loc.altitude}</ele>` : ''}
      </trkpt>`).join('\n')}
    </trkseg>
  </trk>
</gpx>`;
    return gpx;
  }

  private exportToKML(history: LocationHistory): string {
    const kml = `<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Location History</name>
    <Placemark>
      <name>Track</name>
      <LineString>
        <coordinates>
${history.locations.map(loc => `          ${loc.longitude},${loc.latitude}${loc.altitude ? `,${loc.altitude}` : ''}`).join('\n')}
        </coordinates>
      </LineString>
    </Placemark>
  </Document>
</kml>`;
    return kml;
  }

  private handleLocationError(error: GeolocationPositionError): Error {
    let message: string;
    
    switch (error.code) {
      case error.PERMISSION_DENIED:
        message = 'Location access denied by user';
        break;
      case error.POSITION_UNAVAILABLE:
        message = 'Location information unavailable';
        break;
      case error.TIMEOUT:
        message = 'Location request timed out';
        break;
      default:
        message = 'Unknown location error';
        break;
    }
    
    return new Error(message);
  }

  private emitLocationEvent(type: string, data?: any): void {
    const event = new CustomEvent(`location-${type}`, { detail: data });
    window.dispatchEvent(event);
  }

  // Storage Methods
  private async loadSettings(): Promise<void> {
    const stored = await offlineStorageService.retrieve('location_privacy_settings');
    if (stored) {
      this.privacySettings = { ...this.privacySettings, ...stored };
    }
  }

  private async loadGeofences(): Promise<void> {
    const stored = await offlineStorageService.retrieve('location_geofences');
    if (stored && Array.isArray(stored)) {
      this.geofences.clear();
      stored.forEach((geofence: GeofenceRegion) => {
        this.geofences.set(geofence.id, geofence);
      });
    }
  }

  private async saveGeofences(): Promise<void> {
    const geofencesArray = Array.from(this.geofences.values());
    await offlineStorageService.store('location_geofences', geofencesArray);
  }

  private async loadLocationHistory(): Promise<void> {
    const stored = await offlineStorageService.retrieve('location_history');
    if (stored && Array.isArray(stored)) {
      this.locationHistory = stored;
    }
  }

  private async saveLocationHistory(): Promise<void> {
    await offlineStorageService.store('location_history', this.locationHistory);
  }
}

// Export singleton instance
export const locationService = new LocationService();