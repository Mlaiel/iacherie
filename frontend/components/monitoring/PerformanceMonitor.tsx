/**
 * 📊 Performance Monitor - Real-time Performance Tracking
 * 
 * @fileoverview Client-side performance monitoring with metrics collection
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @role DevOps Expert + Performance Engineer
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useHealthMonitor } from '../../core/api/hooks';

// === PERFORMANCE INTERFACES ===

interface PerformanceMetrics {
  webVitals: {
    fcp: number; // First Contentful Paint
    lcp: number; // Largest Contentful Paint
    fid: number; // First Input Delay
    cls: number; // Cumulative Layout Shift
  };
  api: {
    averageResponseTime: number;
    errorRate: number;
    successRate: number;
    totalRequests: number;
  };
  websocket: {
    connectionStatus: 'connected' | 'disconnected' | 'error';
    messagesSent: number;
    messagesReceived: number;
    reconnectCount: number;
  };
  memory: {
    usedJSHeapSize: number;
    totalJSHeapSize: number;
    usagePercentage: number;
  };
}

// === PERFORMANCE MONITOR HOOK ===

export function usePerformanceMonitor() {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    webVitals: { fcp: 0, lcp: 0, fid: 0, cls: 0 },
    api: { averageResponseTime: 0, errorRate: 0, successRate: 100, totalRequests: 0 },
    websocket: { connectionStatus: 'disconnected', messagesSent: 0, messagesReceived: 0, reconnectCount: 0 },
    memory: { usedJSHeapSize: 0, totalJSHeapSize: 0, usagePercentage: 0 }
  });

  const { isHealthy, lastCheck } = useHealthMonitor();

  // Monitor Memory Usage
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const monitorMemory = () => {
      if ('memory' in performance) {
        const memory = (performance as any).memory;
        const usagePercentage = (memory.usedJSHeapSize / memory.totalJSHeapSize) * 100;
        
        setMetrics(prev => ({
          ...prev,
          memory: {
            usedJSHeapSize: memory.usedJSHeapSize,
            totalJSHeapSize: memory.totalJSHeapSize,
            usagePercentage
          }
        }));
      }
    };

    const interval = setInterval(monitorMemory, 5000);
    monitorMemory(); // Initial call

    return () => clearInterval(interval);
  }, []);

  // API Performance Tracking
  const trackApiRequest = useCallback((responseTime: number, success: boolean) => {
    setMetrics(prev => {
      const newTotalRequests = prev.api.totalRequests + 1;
      const newAverageResponseTime = 
        (prev.api.averageResponseTime * prev.api.totalRequests + responseTime) / newTotalRequests;
      const newErrorRate = success 
        ? (prev.api.errorRate * prev.api.totalRequests) / newTotalRequests
        : (prev.api.errorRate * prev.api.totalRequests + 1) / newTotalRequests;

      return {
        ...prev,
        api: {
          averageResponseTime: newAverageResponseTime,
          errorRate: newErrorRate,
          successRate: 100 - newErrorRate,
          totalRequests: newTotalRequests
        }
      };
    });
  }, []);

  // WebSocket Performance Tracking
  const trackWebSocketEvent = useCallback((event: 'sent' | 'received' | 'reconnect' | 'connected' | 'disconnected' | 'error') => {
    setMetrics(prev => {
      const websocket = { ...prev.websocket };
      
      switch (event) {
        case 'sent':
          websocket.messagesSent++;
          break;
        case 'received':
          websocket.messagesReceived++;
          break;
        case 'reconnect':
          websocket.reconnectCount++;
          break;
        case 'connected':
          websocket.connectionStatus = 'connected';
          break;
        case 'disconnected':
          websocket.connectionStatus = 'disconnected';
          break;
        case 'error':
          websocket.connectionStatus = 'error';
          break;
      }

      return { ...prev, websocket };
    });
  }, []);

  return {
    metrics,
    trackApiRequest,
    trackWebSocketEvent,
    isHealthy,
    lastCheck
  };
}

// === PERFORMANCE DASHBOARD COMPONENT ===

interface PerformanceDashboardProps {
  isOpen: boolean;
  onClose: () => void;
}

export function PerformanceDashboard({ isOpen, onClose }: PerformanceDashboardProps) {
  const { metrics, isHealthy, lastCheck } = usePerformanceMonitor();

  if (!isOpen) return null;

  const formatBytes = (bytes: number) => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'text-green-500';
      case 'disconnected': return 'text-yellow-500';
      case 'error': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="border-b border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
              Monitoring Performance
            </h2>
            <div className="flex items-center space-x-4">
              <div className={`flex items-center space-x-2 ${isHealthy ? 'text-green-500' : 'text-red-500'}`}>
                <div className={`w-3 h-3 rounded-full ${isHealthy ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-sm font-medium">
                  {isHealthy ? 'Sain' : 'Problème détecté'}
                </span>
              </div>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                ✕
              </button>
            </div>
          </div>
          {lastCheck && (
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Dernière vérification: {lastCheck.toLocaleTimeString()}
            </p>
          )}
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* API Performance */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
              Performance API
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Temps moyen</div>
                <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {Math.round(metrics.api.averageResponseTime)}ms
                </div>
              </div>

              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Taux de succès</div>
                <div className="text-2xl font-bold text-green-600">
                  {metrics.api.successRate.toFixed(1)}%
                </div>
              </div>

              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Taux d'erreur</div>
                <div className="text-2xl font-bold text-red-600">
                  {metrics.api.errorRate.toFixed(1)}%
                </div>
              </div>

              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Total requêtes</div>
                <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {metrics.api.totalRequests}
                </div>
              </div>
            </div>
          </div>

          {/* WebSocket Status */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
              Statut WebSocket
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Statut</div>
                <div className={`text-lg font-bold ${getStatusColor(metrics.websocket.connectionStatus)}`}>
                  {metrics.websocket.connectionStatus}
                </div>
              </div>

              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Messages envoyés</div>
                <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {metrics.websocket.messagesSent}
                </div>
              </div>

              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Messages reçus</div>
                <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {metrics.websocket.messagesReceived}
                </div>
              </div>

              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Reconnexions</div>
                <div className="text-2xl font-bold text-yellow-600">
                  {metrics.websocket.reconnectCount}
                </div>
              </div>
            </div>
          </div>

          {/* Memory Usage */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
              Utilisation Mémoire
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Utilisée</div>
                <div className="text-xl font-bold text-gray-900 dark:text-gray-100">
                  {formatBytes(metrics.memory.usedJSHeapSize)}
                </div>
              </div>

              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Total</div>
                <div className="text-xl font-bold text-gray-900 dark:text-gray-100">
                  {formatBytes(metrics.memory.totalJSHeapSize)}
                </div>
              </div>

              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Pourcentage</div>
                <div className={`text-xl font-bold ${metrics.memory.usagePercentage > 80 ? 'text-red-600' : 'text-green-600'}`}>
                  {metrics.memory.usagePercentage.toFixed(1)}%
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PerformanceDashboard;