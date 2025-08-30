/**
 * Biometric Service - Secure Authentication System
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import { BiometricOptions, BiometricResult, BaseService, ServiceEventListener, ServiceEvent } from './types';

class BiometricService implements BaseService {
  private initialized: boolean = false;
  private listeners: Map<string, ServiceEventListener[]> = new Map();

  async initialize(): Promise<void> {
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
      const event: ServiceEvent<T> = { type, data, timestamp: new Date(), source: 'BiometricService' };
      listeners.forEach(listener => listener(event));
    }
  }

  async authenticate(options: BiometricOptions = {}): Promise<BiometricResult> {
    // Mock biometric authentication
    const result: BiometricResult = {
      success: true,
      biometryType: 'TouchID',
    };
    this.emit('authenticationCompleted', { result });
    return result;
  }

  async isAvailable(): Promise<boolean> {
    return true; // Mock availability
  }
}

export default new BiometricService();