/**
 * PWA Manager Component
 * 
 * Handles Progressive Web App features including service worker registration,
 * install prompts, and offline functionality.
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import { useEffect, useState } from 'react';
import { toast } from 'react-hot-toast';

interface BeforeInstallPromptEvent extends Event {
  prompt(): Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

export default function PWAManager() {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [isInstallable, setIsInstallable] = useState(false);
  const [isOnline, setIsOnline] = useState(true);
  const [swRegistration, setSwRegistration] = useState<ServiceWorkerRegistration | null>(null);

  useEffect(() => {
    // Register service worker
    if ('serviceWorker' in navigator) {
      registerServiceWorker();
    }

    // Handle install prompt
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      const event = e as BeforeInstallPromptEvent;
      setDeferredPrompt(event);
      setIsInstallable(true);
      
      toast.success('📱 Ainflue can be installed as an app!', {
        duration: 5000,
        position: 'bottom-right',
      });
    };

    // Handle online/offline status
    const handleOnlineStatus = () => {
      setIsOnline(navigator.onLine);
      if (navigator.onLine) {
        toast.success('🌐 Connection restored', { duration: 3000 });
        syncOfflineData();
      } else {
        toast.error('📱 Working offline', { duration: 3000 });
      }
    };

    // Event listeners
    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('online', handleOnlineStatus);
    window.addEventListener('offline', handleOnlineStatus);

    // Check initial online status
    setIsOnline(navigator.onLine);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('online', handleOnlineStatus);
      window.removeEventListener('offline', handleOnlineStatus);
    };
  }, []);

  const registerServiceWorker = async () => {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js', {
        scope: '/',
      });
      
      setSwRegistration(registration);
      console.log('✅ PWA Service Worker registered:', registration);

      // Handle service worker updates
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;
        if (newWorker) {
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              toast.success('🔄 App updated! Refresh to use the latest version.', {
                duration: 8000,
                position: 'top-center',
              });
            }
          });
        }
      });

      // Handle service worker messages
      navigator.serviceWorker.addEventListener('message', (event) => {
        handleServiceWorkerMessage(event.data);
      });

    } catch (error) {
      console.error('❌ PWA Service Worker registration failed:', error);
    }
  };

  const handleServiceWorkerMessage = (data: any) => {
    switch (data.type) {
      case 'CACHE_UPDATED':
        toast.success('📦 Content cached for offline use');
        break;
      case 'BACKGROUND_SYNC':
        toast.success('🔄 Content synced in background');
        break;
      case 'PUSH_NOTIFICATION':
        // Handle push notification data
        break;
      default:
        console.log('SW Message:', data);
    }
  };

  const installPWA = async () => {
    if (!deferredPrompt) return;

    try {
      await deferredPrompt.prompt();
      const choiceResult = await deferredPrompt.userChoice;
      
      if (choiceResult.outcome === 'accepted') {
        toast.success('🎉 Ainflue installed successfully!');
        console.log('✅ PWA installation accepted');
      } else {
        toast.info('📱 You can install Ainflue later from the browser menu');
        console.log('❌ PWA installation dismissed');
      }
      
      setDeferredPrompt(null);
      setIsInstallable(false);
    } catch (error) {
      console.error('❌ PWA installation failed:', error);
      toast.error('Installation failed. Please try again.');
    }
  };

  const syncOfflineData = async () => {
    if (swRegistration && 'sync' in swRegistration) {
      try {
        // Trigger background sync for pending uploads
        await swRegistration.sync.register('content-upload');
        await swRegistration.sync.register('analytics-sync');
        console.log('🔄 Background sync registered');
      } catch (error) {
        console.error('❌ Background sync registration failed:', error);
      }
    }
  };

  const requestNotificationPermission = async () => {
    if (!('Notification' in window)) {
      toast.error('Notifications not supported');
      return false;
    }

    const permission = await Notification.requestPermission();
    
    if (permission === 'granted') {
      toast.success('🔔 Notifications enabled');
      
      // Subscribe to push notifications if supported
      if (swRegistration && 'pushManager' in swRegistration) {
        try {
          const subscription = await swRegistration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY,
          });
          
          // Send subscription to server
          await fetch('/api/notifications/subscribe', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(subscription),
          });
          
          console.log('✅ Push subscription created');
        } catch (error) {
          console.error('❌ Push subscription failed:', error);
        }
      }
      
      return true;
    } else {
      toast.error('Notifications permission denied');
      return false;
    }
  };

  // Show install button if installable
  if (isInstallable && deferredPrompt) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <div className="bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-3">
          <span className="text-sm">Install Ainflue as an app</span>
          <button
            onClick={installPWA}
            className="bg-white text-blue-600 px-3 py-1 rounded text-sm font-medium hover:bg-gray-100 transition-colors"
          >
            Install
          </button>
          <button
            onClick={() => {
              setIsInstallable(false);
              setDeferredPrompt(null);
            }}
            className="text-white hover:text-gray-200 text-lg leading-none"
          >
            ×
          </button>
        </div>
      </div>
    );
  }

  // Show offline indicator
  if (!isOnline) {
    return (
      <div className="fixed top-0 left-0 right-0 bg-yellow-500 text-black text-center py-2 z-50">
        <span className="text-sm font-medium">
          📱 Working offline - Content will sync when connection is restored
        </span>
      </div>
    );
  }

  return null;
}