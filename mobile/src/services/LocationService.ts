/**
 * Location Service - Intelligent Location Management
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import { LocationOptions, LocationData, GeofenceRegion, BaseService, ServiceEventListener, ServiceEvent } from './types';

class LocationService implements BaseService {
  private initialized: boolean = false;
  private listeners: Map<string, ServiceEventListener[]> = new Map();
  private watching: boolean = false;

  async initialize(): Promise<void> {
    await this.requestPermissions();
    this.initialized = true;
    this.emit('initialized', { success: true });
  }

  async destroy(): Promise<void> {
    if (this.watching) await this.stopWatching();
    this.listeners.clear();
    this.initialized = false;
  }

  isInitialized(): boolean { return this.initialized; }
  addEventListener<T>(type: string, listener: ServiceEventListener<T>): void {
    if (!this.listeners.has(type)) this.listeners.set(type, []);
    this.listeners.get(type)!.push(listener as ServiceEventListener);
  }
  removeEventListener<T>(type: string, listener: ServiceEventListener<T>): void {
    const listeners = this.listeners.get(type);
    if (listeners) {
      const index = listeners.indexOf(listener as ServiceEventListener);
      if (index > -1) listeners.splice(index, 1);
    }
  }
  emit<T>(type: string, data: T): void {
    const listeners = this.listeners.get(type);
    if (listeners) {
      const event: ServiceEvent<T> = { type, data, timestamp: new Date(), source: 'LocationService' };
      listeners.forEach(listener => listener(event));
    }
  }

  async requestPermissions(): Promise<boolean> {
    // Mock permission request
    this.emit('permissionGranted', { granted: true });
    return true;
  }

  async getCurrentLocation(options: LocationOptions = { accuracy: 'balanced', timeout: 10000, maximumAge: 60000, enableHighAccuracy: false, distanceFilter: 10 }): Promise<LocationData> {
    const location: LocationData = {
      latitude: 48.8566,
      longitude: 2.3522,
      altitude: 35,
      accuracy: 5,
      timestamp: new Date(),
      address: {
        city: 'Paris',
        country: 'France',
      },
    };
    this.emit('locationUpdate', { location });
    return location;
  }

  async startWatching(options: LocationOptions): Promise<void> {
    this.watching = true;
    this.emit('watchingStarted', { options });
  }

  async stopWatching(): Promise<void> {
    this.watching = false;
    this.emit('watchingStopped', {});
  }
}

export default new LocationService();