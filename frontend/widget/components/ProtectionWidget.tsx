/**
 * Protection Widget - Embeddable Protection Status Component
 * 
 * Displays content protection status in a compact embeddable format
 * Shows protection level and recent security events
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import React, { useState, useEffect } from 'react';
import { 
  ShieldCheckIcon, 
  ExclamationTriangleIcon,
  LockClosedIcon,
  EyeIcon
} from '@heroicons/react/24/outline';

interface ProtectionWidgetProps {
  apiKey: string;
  userId: string;
  showTitle?: boolean;
  data?: any;
}

interface ProtectionData {
  protectionLevel: number;
  activeScans: number;
  threatsBlocked: number;
  lastScan: string;
  status: 'protected' | 'warning' | 'vulnerable';
}

export function ProtectionWidget({ apiKey, userId, showTitle = true, data }: ProtectionWidgetProps) {
  const [protection, setProtection] = useState<ProtectionData>({
    protectionLevel: 0,
    activeScans: 0,
    threatsBlocked: 0,
    lastScan: new Date().toISOString(),
    status: 'protected'
  });
  
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProtectionData = async () => {
      try {
        if (data) {
          setProtection(data);
          setIsLoading(false);
          return;
        }

        if (!apiKey || !userId) {
          throw new Error('API Key et User ID requis');
        }

        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Mock data
        setProtection({
          protectionLevel: 98,
          activeScans: 3,
          threatsBlocked: 127,
          lastScan: new Date().toISOString(),
          status: 'protected'
        });
        
        setIsLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erreur de chargement');
        setIsLoading(false);
      }
    };

    fetchProtectionData();
  }, [apiKey, userId, data]);

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 border-2 border-green-600 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-sm text-gray-600">Vérification...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 text-center">
        <div className="text-red-500 text-sm">
          <ExclamationTriangleIcon className="h-8 w-8 mx-auto mb-2 opacity-50" />
          {error}
        </div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'protected': return 'green';
      case 'warning': return 'yellow';
      case 'vulnerable': return 'red';
      default: return 'gray';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'protected': return 'Protégé';
      case 'warning': return 'Attention';
      case 'vulnerable': return 'Vulnérable';
      default: return 'Inconnu';
    }
  };

  const statusColor = getStatusColor(protection.status);
  const statusText = getStatusText(protection.status);

  const formatTimeAgo = (timestamp: string) => {
    const minutes = Math.floor((new Date().getTime() - new Date(timestamp).getTime()) / 60000);
    if (minutes < 1) return 'À l\'instant';
    if (minutes < 60) return `Il y a ${minutes} min`;
    const hours = Math.floor(minutes / 60);
    return `Il y a ${hours}h`;
  };

  return (
    <div className="p-4">
      {showTitle && (
        <div className="flex items-center space-x-2 mb-4">
          <ShieldCheckIcon className="h-5 w-5 text-green-600" />
          <h3 className="font-semibold text-gray-900">Protection Ainflue</h3>
        </div>
      )}

      <div className="space-y-4">
        {/* Protection Status */}
        <div className="text-center">
          <div className={`w-16 h-16 mx-auto mb-3 bg-${statusColor}-100 rounded-full flex items-center justify-center`}>
            <ShieldCheckIcon className={`h-8 w-8 text-${statusColor}-600`} />
          </div>
          <div className={`text-lg font-bold text-${statusColor}-600`}>
            {protection.protectionLevel}%
          </div>
          <div className={`text-sm text-${statusColor}-600 font-medium`}>
            {statusText}
          </div>
        </div>

        {/* Protection Metrics */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <EyeIcon className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">Scans actifs</span>
            </div>
            <span className="font-semibold text-blue-600">
              {protection.activeScans}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <LockClosedIcon className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">Menaces bloquées</span>
            </div>
            <span className="font-semibold text-red-600">
              {protection.threatsBlocked}
            </span>
          </div>
        </div>

        {/* Protection Level Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-xs text-gray-500">
            <span>Niveau de protection</span>
            <span>{protection.protectionLevel}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`bg-gradient-to-r from-${statusColor}-500 to-${statusColor}-600 h-2 rounded-full transition-all duration-500`}
              style={{ width: `${protection.protectionLevel}%` }}
            ></div>
          </div>
        </div>

        {/* Status Indicator */}
        <div className={`p-3 bg-${statusColor}-50 rounded-lg border border-${statusColor}-200`}>
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 bg-${statusColor}-500 rounded-full`}></div>
            <span className={`text-sm font-medium text-${statusColor}-700`}>
              Votre contenu est {statusText.toLowerCase()}
            </span>
          </div>
          <div className={`text-xs text-${statusColor}-600 mt-1`}>
            Dernier scan: {formatTimeAgo(protection.lastScan)}
          </div>
        </div>

        {/* Powered by Ainflue */}
        <div className="text-xs text-gray-400 text-center pt-2 border-t border-gray-100">
          <span>Powered by </span>
          <a 
            href="https://ainflue.com" 
            target="_blank" 
            rel="noopener noreferrer" 
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            Ainflue
          </a>
        </div>
      </div>
    </div>
  );
}