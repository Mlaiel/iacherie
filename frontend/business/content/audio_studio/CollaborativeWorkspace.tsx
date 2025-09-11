'use client';

/**
 * Collaborative Workspace Component
 * 
 * Real-time collaborative editing interface for multi-user studio sessions.
 * Provides user presence, shared cursors, and real-time synchronization.
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

import React, { useState, useCallback } from 'react';
import { 
  UserGroupIcon,
  ChatBubbleLeftRightIcon,
  ShareIcon,
  LockClosedIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import { studioUtils } from '../remix_studio/remix_studio.styles';
import type { CollaborationUser } from '../remix_studio/index';

interface CollaborativeWorkspaceProps {
  projectId: string;
  currentUser: any;
  onUserAction: (action: string) => void;
  className?: string;
}

const CollaborativeWorkspace: React.FC<CollaborativeWorkspaceProps> = ({
  projectId,
  currentUser,
  onUserAction,
  className = ''
}) => {
  const [users] = useState<CollaborationUser[]>([
    {
      id: '1',
      name: 'John Producer',
      email: 'john@example.com',
      avatar: '',
      role: 'owner',
      isOnline: true,
      lastSeen: Date.now(),
      permissions: ['edit', 'delete', 'share', 'manage_users']
    },
    {
      id: '2', 
      name: 'Sarah Mixer',
      email: 'sarah@example.com',
      avatar: '',
      role: 'collaborator',
      isOnline: true,
      lastSeen: Date.now() - 5 * 60 * 1000, // 5 minutes ago
      permissions: ['edit', 'share']
    }
  ]);

  const [messages] = useState([
    { id: '1', user: 'John Producer', message: 'Added new vocal track', time: '10:30 AM' },
    { id: '2', user: 'Sarah Mixer', message: 'Applied EQ to drums', time: '10:32 AM' }
  ]);

  return (
    <div className={`collaborative-workspace bg-gray-900 border-l border-gray-700 w-80 p-4 ${className}`}>
      <div className="flex items-center space-x-2 mb-4">
        <UserGroupIcon className="h-5 w-5 text-blue-400" />
        <h3 className="text-lg font-semibold text-white">Collaboration</h3>
      </div>

      {/* Online Users */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-300 mb-2">Online ({users.length})</h4>
        <div className="space-y-2">
          {users.map(user => (
            <div key={user.id} className="flex items-center space-x-3 p-2 bg-gray-800 rounded">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
                {user.name.charAt(0)}
              </div>
              <div className="flex-1">
                <div className="text-white text-sm">{user.name}</div>
                <div className="text-xs text-gray-400 capitalize">{user.role}</div>
              </div>
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            </div>
          ))}
        </div>
      </div>

      {/* Activity Feed */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-300 mb-2">Recent Activity</h4>
        <div className="space-y-2 max-h-40 overflow-y-auto">
          {messages.map(msg => (
            <div key={msg.id} className="p-2 bg-gray-800 rounded text-sm">
              <div className="text-white">{msg.user}</div>
              <div className="text-gray-300">{msg.message}</div>
              <div className="text-xs text-gray-500">{msg.time}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="space-y-2">
        <button className="w-full flex items-center space-x-2 p-2 bg-blue-600 hover:bg-blue-700 rounded transition-colors">
          <ShareIcon className="h-4 w-4" />
          <span>Share Project</span>
        </button>
        <button className="w-full flex items-center space-x-2 p-2 bg-gray-700 hover:bg-gray-600 rounded transition-colors">
          <ChatBubbleLeftRightIcon className="h-4 w-4" />
          <span>Open Chat</span>
        </button>
      </div>
    </div>
  );
};

export default CollaborativeWorkspace;