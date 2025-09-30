'use client';

import { ShieldCheckIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

interface ProtectionStatusProps {
  totalViolations: number;
  resolvedViolations: number;
}

export function ProtectionStatus({ totalViolations, resolvedViolations }: ProtectionStatusProps) {
  const activeViolations = totalViolations - resolvedViolations;
  const resolutionRate = totalViolations > 0 ? (resolvedViolations / totalViolations) * 100 : 0;

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Protection Status</h3>
        <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
          activeViolations === 0 
            ? 'bg-green-100 text-green-800' 
            : 'bg-yellow-100 text-yellow-800'
        }`}>
          {activeViolations === 0 ? 'All Clear' : `${activeViolations} Active Issues`}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Resolution Rate */}
        <div className="text-center">
          <div className="relative inline-flex items-center justify-center w-32 h-32 mb-4">
            <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 36 36">
              <path
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke="#e5e7eb"
                strokeWidth="3"
              />
              <path
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke="#10b981"
                strokeWidth="3"
                strokeDasharray={`${resolutionRate}, 100`}
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-2xl font-bold text-gray-900">{resolutionRate.toFixed(0)}%</span>
            </div>
          </div>
          <p className="text-sm font-medium text-gray-900">Resolution Rate</p>
          <p className="text-xs text-gray-500">Cases resolved automatically</p>
        </div>

        {/* Violations Breakdown */}
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
            <div className="flex items-center">
              <ShieldCheckIcon className="w-5 h-5 text-green-600 mr-2" />
              <span className="text-sm font-medium text-green-900">Resolved</span>
            </div>
            <span className="text-lg font-bold text-green-900">{resolvedViolations}</span>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
            <div className="flex items-center">
              <ExclamationTriangleIcon className="w-5 h-5 text-yellow-600 mr-2" />
              <span className="text-sm font-medium text-yellow-900">Active</span>
            </div>
            <span className="text-lg font-bold text-yellow-900">{activeViolations}</span>
          </div>

          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center">
              <span className="w-5 h-5 bg-gray-400 rounded-full mr-2"></span>
              <span className="text-sm font-medium text-gray-900">Total</span>
            </div>
            <span className="text-lg font-bold text-gray-900">{totalViolations}</span>
          </div>
        </div>
      </div>

      {/* Recent Protection Actions */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <h4 className="text-sm font-medium text-gray-900 mb-4">Recent Protection Actions</h4>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
              <div>
                <p className="text-sm font-medium text-gray-900">DMCA Takedown Sent</p>
                <p className="text-xs text-gray-500">YouTube violation detected and processed</p>
              </div>
            </div>
            <span className="text-xs text-gray-500">2 min ago</span>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
              <div>
                <p className="text-sm font-medium text-gray-900">Content Fingerprinted</p>
                <p className="text-xs text-gray-500">New audio track protected</p>
              </div>
            </div>
            <span className="text-xs text-gray-500">15 min ago</span>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-2 h-2 bg-yellow-500 rounded-full mr-3"></div>
              <div>
                <p className="text-sm font-medium text-gray-900">Monitoring Alert</p>
                <p className="text-xs text-gray-500">Potential violation on TikTok</p>
              </div>
            </div>
            <span className="text-xs text-gray-500">1 hour ago</span>
          </div>
        </div>
      </div>
    </div>
  );
}