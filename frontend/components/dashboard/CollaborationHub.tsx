/**
 * Collaboration Hub - Team collaboration management
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import React from 'react';
import { 
  UsersIcon, 
  PlusIcon,
  EnvelopeIcon,
  CogIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon
} from '@heroicons/react/24/outline';

interface TeamMember {
  id: string;
  name: string;
  email: string;
  role: 'owner' | 'admin' | 'editor' | 'viewer';
  avatar?: string;
  lastActive: string;
  status: 'active' | 'pending' | 'inactive';
}

interface Collaboration {
  id: string;
  title: string;
  members: number;
  contentCount: number;
  lastActivity: string;
  status: 'active' | 'paused' | 'completed';
}

const CollaborationHub: React.FC = () => {
  const [members, setMembers] = React.useState<TeamMember[]>([]);
  const [collaborations, setCollaborations] = React.useState<Collaboration[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [showInviteModal, setShowInviteModal] = React.useState(false);

  React.useEffect(() => {
    // Simulate API calls
    setTimeout(() => {
      setMembers([
        {
          id: '1',
          name: 'John Doe',
          email: 'john@example.com',
          role: 'admin',
          lastActive: '2024-01-15T10:30:00Z',
          status: 'active'
        },
        {
          id: '2',
          name: 'Jane Smith',
          email: 'jane@example.com',
          role: 'editor',
          lastActive: '2024-01-14T15:45:00Z',
          status: 'active'
        },
        {
          id: '3',
          name: 'Mike Johnson',
          email: 'mike@example.com',
          role: 'viewer',
          lastActive: '2024-01-13T09:20:00Z',
          status: 'pending'
        }
      ]);

      setCollaborations([
        {
          id: '1',
          title: 'Album Production 2024',
          members: 5,
          contentCount: 12,
          lastActivity: '2024-01-15T10:30:00Z',
          status: 'active'
        },
        {
          id: '2',
          title: 'Music Video Project',
          members: 3,
          contentCount: 8,
          lastActivity: '2024-01-14T15:45:00Z',
          status: 'active'
        }
      ]);

      setLoading(false);
    }, 1000);
  }, []);

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'owner': return 'bg-purple-100 text-purple-800';
      case 'admin': return 'bg-red-100 text-red-800';
      case 'editor': return 'bg-blue-100 text-blue-800';
      case 'viewer': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'inactive': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Collaboration Hub</h1>
            <p className="text-gray-600">Manage your team and collaborative projects</p>
          </div>
          <button 
            onClick={() => setShowInviteModal(true)}
            className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 transition-colors flex items-center"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Invite Member
          </button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Team Members</p>
              <p className="text-2xl font-bold text-gray-900">{members.length}</p>
            </div>
            <UsersIcon className="h-10 w-10 text-purple-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Projects</p>
              <p className="text-2xl font-bold text-gray-900">{collaborations.length}</p>
            </div>
            <CogIcon className="h-10 w-10 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Shared Content</p>
              <p className="text-2xl font-bold text-gray-900">
                {collaborations.reduce((sum, collab) => sum + collab.contentCount, 0)}
              </p>
            </div>
            <EyeIcon className="h-10 w-10 text-green-500" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Team Members */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Team Members</h3>
            <button className="text-purple-600 hover:text-purple-700 text-sm font-medium">
              Manage Roles
            </button>
          </div>

          <div className="space-y-4">
            {members.map((member) => (
              <div key={member.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full flex items-center justify-center text-white font-medium">
                    {member.name.split(' ').map(n => n[0]).join('')}
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">{member.name}</div>
                    <div className="text-sm text-gray-500">{member.email}</div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRoleColor(member.role)}`}>
                    {member.role.toUpperCase()}
                  </span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(member.status)}`}>
                    {member.status.toUpperCase()}
                  </span>
                  <div className="flex space-x-1">
                    <button className="text-gray-400 hover:text-gray-600">
                      <PencilIcon className="h-4 w-4" />
                    </button>
                    <button className="text-gray-400 hover:text-red-600">
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Active Collaborations */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Active Collaborations</h3>
            <button className="text-purple-600 hover:text-purple-700 text-sm font-medium">
              Create Project
            </button>
          </div>

          <div className="space-y-4">
            {collaborations.map((collaboration) => (
              <div key={collaboration.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900">{collaboration.title}</h4>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(collaboration.status)}`}>
                    {collaboration.status.toUpperCase()}
                  </span>
                </div>
                
                <div className="grid grid-cols-3 gap-4 text-sm text-gray-600 mb-3">
                  <div>
                    <span className="font-medium">{collaboration.members}</span> members
                  </div>
                  <div>
                    <span className="font-medium">{collaboration.contentCount}</span> files
                  </div>
                  <div>
                    Active <span className="font-medium">
                      {new Date(collaboration.lastActivity).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                <div className="flex space-x-2">
                  <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                    View Project
                  </button>
                  <button className="text-gray-600 hover:text-gray-700 text-sm font-medium">
                    Settings
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Invite Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-96">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Invite Team Member</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                <input 
                  type="email" 
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="member@example.com"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
                <select className="w-full border border-gray-300 rounded-md px-3 py-2">
                  <option value="viewer">Viewer</option>
                  <option value="editor">Editor</option>
                  <option value="admin">Admin</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Message (Optional)</label>
                <textarea 
                  className="w-full border border-gray-300 rounded-md px-3 py-2" 
                  rows={3}
                  placeholder="Welcome to the team!"
                />
              </div>
            </div>

            <div className="flex space-x-3 mt-6">
              <button 
                onClick={() => setShowInviteModal(false)}
                className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 transition-colors"
              >
                Cancel
              </button>
              <button 
                onClick={() => setShowInviteModal(false)}
                className="flex-1 bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 transition-colors flex items-center justify-center"
              >
                <EnvelopeIcon className="h-5 w-5 mr-2" />
                Send Invite
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CollaborationHub;