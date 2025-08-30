/**
 * Camera Service - Professional Camera Integration
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import { CameraPermissions, CameraConfiguration, CapturedMedia, BaseService, ServiceEventListener, ServiceEvent } from './types';

class CameraService implements BaseService {
  private initialized: boolean = false;
  private listeners: Map<string, ServiceEventListener[]> = new Map();

  async initialize(): Promise<void> {
    await this.requestPermissions();
    this.initialized = true;
    this.emit('initialized', { success: true });
  }

  async destroy(): Promise<void> {
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
      const event: ServiceEvent<T> = { type, data, timestamp: new Date(), source: 'CameraService' };
      listeners.forEach(listener => listener(event));
    }
  }

  async requestPermissions(): Promise<CameraPermissions> {
    const permissions: CameraPermissions = {
      camera: true,
      microphone: true,
      storage: true,
    };
    return permissions;
  }

  async capturePhoto(config: CameraConfiguration): Promise<CapturedMedia> {
    // Mock photo capture
    const media: CapturedMedia = {
      uri: 'file://mock/photo.jpg',
      type: 'image',
      metadata: {
        width: 4000,
        height: 3000,
        fileSize: 2 * 1024 * 1024,
        format: 'JPEG',
        orientation: 1,
        timestamp: new Date(),
        deviceInfo: {
          make: 'Apple',
          model: 'iPhone',
          os: 'iOS',
        },
      },
    };
    this.emit('photoCaptured', { media });
    return media;
  }
}

export default new CameraService();