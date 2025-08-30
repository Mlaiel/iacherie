/**
 * Audio Service - Professional Audio Processing
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import { AudioConfiguration, AudioRecording, AudioLevel, BaseService, ServiceEventListener, ServiceEvent } from './types';

class AudioService implements BaseService {
  private initialized: boolean = false;
  private listeners: Map<string, ServiceEventListener[]> = new Map();
  private isRecording: boolean = false;

  async initialize(): Promise<void> {
    this.initialized = true;
    this.emit('initialized', { success: true });
  }

  async destroy(): Promise<void> {
    if (this.isRecording) await this.stopRecording();
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
      const event: ServiceEvent<T> = { type, data, timestamp: new Date(), source: 'AudioService' };
      listeners.forEach(listener => listener(event));
    }
  }

  async startRecording(config: AudioConfiguration): Promise<void> {
    this.isRecording = true;
    this.emit('recordingStarted', { config });
  }

  async stopRecording(): Promise<AudioRecording> {
    this.isRecording = false;
    const recording: AudioRecording = {
      uri: 'file://mock/recording.wav',
      duration: 60,
      fileSize: 1024 * 1024,
      format: 'WAV',
      metadata: {
        sampleRate: 44100,
        bitRate: 1411,
        channels: 2,
        peakLevel: 0.8,
        averageLevel: 0.6,
        timestamp: new Date(),
      },
    };
    this.emit('recordingStopped', { recording });
    return recording;
  }
}

export default new AudioService();