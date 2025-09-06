'use client';

import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/24/outline';
import { clsx } from 'clsx';

interface MetricCardProps {
  title: string;
  value: string;
  icon: React.ComponentType<{ className?: string }>;
  trend?: number;
  trendDirection?: 'up' | 'down';
  color?: 'blue' | 'green' | 'purple' | 'indigo' | 'red' | 'yellow';
  suffix?: string;
}

const colorClasses = {
  blue: 'bg-blue-50 text-blue-600 border-blue-200',
  green: 'bg-green-50 text-green-600 border-green-200', 
  purple: 'bg-purple-50 text-purple-600 border-purple-200',
  indigo: 'bg-indigo-50 text-indigo-600 border-indigo-200',
  red: 'bg-red-50 text-red-600 border-red-200',
  yellow: 'bg-yellow-50 text-yellow-600 border-yellow-200',
};

export function MetricCard({ 
  title, 
  value, 
  icon: Icon, 
  trend, 
  trendDirection = 'up',
  color = 'blue',
  suffix 
}: MetricCardProps) {
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">
            {value}
            {suffix && <span className="text-sm font-normal text-gray-500 ml-1">{suffix}</span>}
          </p>
          {trend !== undefined && (
            <div className="flex items-center mt-2">
              {trendDirection === 'up' ? (
                <ArrowUpIcon className="w-4 h-4 text-green-500" />
              ) : (
                <ArrowDownIcon className="w-4 h-4 text-red-500" />
              )}
              <span className={clsx(
                'text-sm font-medium ml-1',
                trendDirection === 'up' ? 'text-green-600' : 'text-red-600'
              )}>
                {trend}%
              </span>
              <span className="text-sm text-gray-500 ml-1">from last month</span>
            </div>
          )}
        </div>
        <div className={clsx(
          'p-3 rounded-lg border',
          colorClasses[color]
        )}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  );
}