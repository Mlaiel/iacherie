/**
 * Mobile Hook - Device Detection and Mobile Features
 * 
 * Custom hook for mobile device detection and mobile-specific functionality
 * Provides device info, orientation, and PWA capabilities
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import { useState, useEffect } from 'react';

interface DeviceInfo {
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  isPWACompatible: boolean;
  hasTouch: boolean;
  userAgent: string;
}

interface MobileHookReturn {
  isOnline: boolean;
  deviceInfo: DeviceInfo;
  orientation: 'portrait' | 'landscape';
  installPWA: () => void;
  canInstallPWA: boolean;
}

export function useMobile(): MobileHookReturn {
  const [isOnline, setIsOnline] = useState(true);
  const [deviceInfo, setDeviceInfo] = useState<DeviceInfo>({
    isMobile: false,
    isTablet: false,
    isDesktop: true,
    isPWACompatible: false,
    hasTouch: false,
    userAgent: ''
  });
  const [orientation, setOrientation] = useState<'portrait' | 'landscape'>('portrait');
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [canInstallPWA, setCanInstallPWA] = useState(false);

  useEffect(() => {
    // Device detection
    const detectDevice = () => {
      const userAgent = navigator.userAgent || '';
      const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);
      const isTablet = /iPad|Android(?=.*Tablet)|(?=.*Android.*(?=.*Mobile))(?!.*Tablet)/i.test(userAgent);
      const hasTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
      const isPWACompatible = 'serviceWorker' in navigator && 'PushManager' in window;

      setDeviceInfo({
        isMobile: isMobile && !isTablet,
        isTablet,
        isDesktop: !isMobile,
        isPWACompatible,
        hasTouch,
        userAgent
      });
    };

    // Orientation detection
    const updateOrientation = () => {
      if (screen && screen.orientation) {
        setOrientation(screen.orientation.angle === 0 || screen.orientation.angle === 180 ? 'portrait' : 'landscape');
      } else {
        setOrientation(window.innerHeight > window.innerWidth ? 'portrait' : 'landscape');
      }
    };

    // Online/Offline status
    const updateOnlineStatus = () => {
      setIsOnline(navigator.onLine);
    };

    // PWA install prompt
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setCanInstallPWA(true);
    };

    // Initial setup
    detectDevice();
    updateOrientation();
    updateOnlineStatus();

    // Event listeners
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    window.addEventListener('orientationchange', updateOrientation);
    window.addEventListener('resize', updateOrientation);
    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    // Cleanup
    return () => {
      window.removeEventListener('online', updateOnlineStatus);
      window.removeEventListener('offline', updateOnlineStatus);
      window.removeEventListener('orientationchange', updateOrientation);
      window.removeEventListener('resize', updateOrientation);
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);

  const installPWA = async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      
      if (outcome === 'accepted') {
        setCanInstallPWA(false);
        setDeferredPrompt(null);
      }
    }
  };

  return {
    isOnline,
    deviceInfo,
    orientation,
    installPWA,
    canInstallPWA
  };
}