import React from 'react';

interface MonitoringDashboardProps {
  userId?: string;
}

export default function MonitoringDashboard(_props: MonitoringDashboardProps) {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="mb-4">
          <h2 className="text-lg font-semibold">
            Monitoring Dashboard
          </h2>
          <p className="text-sm text-gray-600 mt-2">
            Monitor content violations and protection status
          </p>
        </div>
        
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
          <p className="text-gray-500">
            Monitoring dashboard - Under development
          </p>
          <p className="text-sm text-gray-400 mt-2">
            This component will show real-time monitoring data
          </p>
        </div>
      </div>
    </div>
  );
}