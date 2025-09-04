'use client';

/**
 * Remix Studio Showcase Page
 * 
 * Demonstration page showcasing the Creative Studio Interface.
 * Provides a live preview of all remix studio components.
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Project: IA-Influencer Agent + Content Protection Platform
 * Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps
 * 
 * WARNING: This code is the intellectual property of Fahed Mlaiel.
 * Any unauthorized use, reproduction, or distribution without explicit written permission
 * is strictly prohibited and will be prosecuted to the full extent of the law.
 * 
 * Contact: mlaiel@live.de for licensing inquiries.
 */

import React from 'react';
import RemixStudioMain from '@/components/remix_studio_core/RemixStudioMain';

export default function RemixStudioPage() {
  const handleSave = async (projectData: any) => {
    console.log('Saving project:', projectData);
    // In real implementation, would save to backend
  };

  const handleExport = async (exportData: any) => {
    console.log('Exporting audio:', exportData);
    // In real implementation, would handle export
  };

  return (
    <div className="min-h-screen bg-gray-950">
      <RemixStudioMain
        projectId="demo-project-2024"
        onSave={handleSave}
        onExport={handleExport}
      />
    </div>
  );
}