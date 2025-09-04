/**
 * Mobile Interface Entry Point
 * 
 * Main mobile application interface with responsive design
 * Optimized for mobile devices and touch interactions
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import React from 'react';
import { MobileNavigation } from './components/MobileNavigation';
import { MobileDashboard } from './components/MobileDashboard';
import { MobileHeader } from './components/MobileHeader';
import { useMobile } from './hooks/useMobile';

export function MobileInterface() {
  const { isOnline, deviceInfo, orientation } = useMobile();

  return (
    <div className={`mobile-interface min-h-screen bg-gray-50 ${orientation === 'landscape' ? 'landscape' : 'portrait'}`}>
      {/* Mobile Header */}
      <MobileHeader isOnline={isOnline} />
      
      {/* Main Content */}
      <main className="pb-16 pt-14"> {/* Account for fixed header and nav */}
        <MobileDashboard />
      </main>
      
      {/* Bottom Navigation */}
      <MobileNavigation />
      
      {/* PWA Install Prompt */}
      {deviceInfo.isPWACompatible && (
        <div className="fixed bottom-20 left-4 right-4 z-50">
          <div className="bg-blue-600 text-white p-3 rounded-lg shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">Installer l'application</p>
                <p className="text-xs opacity-90">Accès rapide depuis votre écran d'accueil</p>
              </div>
              <button className="bg-white text-blue-600 px-3 py-1 rounded text-sm font-medium">
                Installer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default MobileInterface;