'use client';

import { 
  MusicalNoteIcon,
  VideoCameraIcon,
  PhotoIcon,
  CurrencyDollarIcon,
  UserGroupIcon
} from '@heroicons/react/24/outline';

interface Activity {
  id: string;
  type: 'upload' | 'revenue' | 'violation' | 'collaboration' | 'protection';
  title: string;
  description: string;
  timestamp: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
}

export function RecentActivity() {
  const activities: Activity[] = [
    {
      id: '1',
      type: 'upload',
      title: 'New Audio Track Uploaded',
      description: 'Summer_Vibes_2024.mp3 - 3.2MB',
      timestamp: '5 minutes ago',
      icon: MusicalNoteIcon,
      color: 'bg-blue-100 text-blue-600',
    },
    {
      id: '2',
      type: 'revenue',
      title: 'Revenue Generated',
      description: '$127.50 from YouTube monetization',
      timestamp: '1 hour ago',
      icon: CurrencyDollarIcon,
      color: 'bg-green-100 text-green-600',
    },
    {
      id: '3',
      type: 'violation',
      title: 'Violation Detected',
      description: 'Unauthorized use found on Instagram',
      timestamp: '2 hours ago',
      icon: PhotoIcon,
      color: 'bg-red-100 text-red-600',
    },
    {
      id: '4',
      type: 'collaboration',
      title: 'Collaboration Request',
      description: 'Producer_Mike wants to collaborate',
      timestamp: '4 hours ago',
      icon: UserGroupIcon,
      color: 'bg-purple-100 text-purple-600',
    },
    {
      id: '5',
      type: 'upload',
      title: 'Video Content Protected',
      description: 'Dance_Tutorial_2024.mp4 fingerprinted',
      timestamp: '6 hours ago',
      icon: VideoCameraIcon,
      color: 'bg-indigo-100 text-indigo-600',
    },
    {
      id: '6',
      type: 'revenue',
      title: 'Monthly Payout',
      description: '$2,847.30 transferred to bank account',
      timestamp: '1 day ago',
      icon: CurrencyDollarIcon,
      color: 'bg-green-100 text-green-600',
    },
  ];

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
        <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
          View All
        </button>
      </div>

      <div className="space-y-4">
        {activities.map((activity) => (
          <div key={activity.id} className="flex items-start space-x-3">
            <div className={`p-2 rounded-lg ${activity.color} flex-shrink-0`}>
              <activity.icon className="w-4 h-4" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {activity.title}
                </p>
                <span className="text-xs text-gray-500 whitespace-nowrap ml-2">
                  {activity.timestamp}
                </span>
              </div>
              <p className="text-sm text-gray-500 truncate">
                {activity.description}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Activity Summary */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900">24</p>
            <p className="text-xs text-gray-500">Actions Today</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900">156</p>
            <p className="text-xs text-gray-500">This Week</p>
          </div>
        </div>
      </div>
    </div>
  );
}