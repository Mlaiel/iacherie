/**
 * 🎯 DASHBOARD PRINCIPAL CONSOLIDÉ - 57 MODULES
 * Page principale intégrant tous les modules enterprise
 * 
 * @author Fahed Mlaiel - Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + DevOps
 * @date 25 Septembre 2025
 */

'use client';

import React from 'react';
import ConsolidatedEnterpriseDashboard from '@/components/dashboard/ConsolidatedDashboard';

export default function EnterpriseDashboardPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <ConsolidatedEnterpriseDashboard />
    </div>
  );
}