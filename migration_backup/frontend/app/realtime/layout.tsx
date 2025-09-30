/**
 * Real-Time Dashboard Layout
 * 
 * Layout component for the real-time analytics dashboard
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import React from 'react';

interface RealTimeLayoutProps {
  children: React.ReactNode;
}

export default function RealTimeLayout({ children }: RealTimeLayoutProps) {
  return (
    <div className="realtime-dashboard">
      {children}
    </div>
  );
}