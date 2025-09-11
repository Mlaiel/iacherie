/**
 * @fileoverview Collaborative Workspace Component
 * @author Fahed Mlaiel <mlaiel@live.de> - Collaboration Engineer Role
 * @copyright 2025 Fahed Mlaiel - All Rights Reserved
 */

'use client';

import React, { useState, useCallback } from 'react';

export interface Collaborator {
  id: string;
  name: string;
  avatar?: string;
  role: 'owner' | 'editor' | 'viewer' | 'commenter';
  isOnline: boolean;
  lastActive: Date;
  cursor?: {
    x: number;
    y: number;
    color: string;
  };
}

export interface CollaborativeWorkspaceProps {
  collaborators: Collaborator[];
  currentUserId: string;
  onInviteUser: (email: string, role: Collaborator['role']) => void;
  onUpdateUserRole: (userId: string, role: Collaborator['role']) => void;
  onRemoveUser: (userId: string) => void;
  onSendMessage: (message: string) => void;
  messages: Array<{
    id: string;
    userId: string;
    message: string;
    timestamp: Date;
    type: 'text' | 'system' | 'audio';
  }>;
}

const CollaborativeWorkspace: React.FC<CollaborativeWorkspaceProps> = ({
  collaborators,
  currentUserId,
  onInviteUser,
  onUpdateUserRole,
  onRemoveUser,
  onSendMessage,
  messages
}) => {
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<Collaborator['role']>('editor');
  const [chatMessage, setChatMessage] = useState('');
  const [showChat, setShowChat] = useState(false);

  const handleInvite = useCallback(() => {
    if (inviteEmail.trim()) {
      onInviteUser(inviteEmail.trim(), inviteRole);
      setInviteEmail('');
      setShowInviteModal(false);
    }
  }, [inviteEmail, inviteRole, onInviteUser]);

  const handleSendMessage = useCallback(() => {
    if (chatMessage.trim()) {
      onSendMessage(chatMessage.trim());
      setChatMessage('');
    }
  }, [chatMessage, onSendMessage]);

  const getRoleColor = (role: Collaborator['role']) => {
    switch (role) {
      case 'owner': return 'text-yellow-400';
      case 'editor': return 'text-green-400';
      case 'viewer': return 'text-blue-400';
      case 'commenter': return 'text-purple-400';
      default: return 'text-gray-400';
    }
  };

  const onlineCollaborators = collaborators.filter(c => c.isOnline);

  return (
    <div className="collaborative-workspace bg-gray-900 p-4 h-full">
      <div className="workspace-header mb-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-white text-lg font-bold flex items-center">
            <span className="mr-2">👥</span>
            Collaboration
          </h3>
          <button
            onClick={() => setShowChat(!showChat)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm"
          >
            Chat ({messages.length})
          </button>
        </div>

        {/* Online Collaborators */}
        <div className="online-collaborators mb-4">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-gray-300 text-sm">Online Now:</span>
            <span className="text-green-400 text-sm">{onlineCollaborators.length}</span>
          </div>
          
          <div className="collaborator-avatars flex -space-x-2">
            {onlineCollaborators.slice(0, 5).map((collaborator) => (
              <div
                key={collaborator.id}
                className="relative w-8 h-8 rounded-full bg-gray-700 border-2 border-gray-900 flex items-center justify-center"
                title={`${collaborator.name} (${collaborator.role})`}
              >
                {collaborator.avatar ? (
                  <img
                    src={collaborator.avatar}
                    alt={collaborator.name}
                    className="w-full h-full rounded-full"
                  />
                ) : (
                  <span className="text-white text-xs">
                    {collaborator.name.charAt(0).toUpperCase()}
                  </span>
                )}
                <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 rounded-full border border-gray-900" />
              </div>
            ))}
            {onlineCollaborators.length > 5 && (
              <div className="w-8 h-8 rounded-full bg-gray-600 border-2 border-gray-900 flex items-center justify-center">
                <span className="text-white text-xs">+{onlineCollaborators.length - 5}</span>
              </div>
            )}
          </div>
        </div>

        {/* Invite Button */}
        <button
          onClick={() => setShowInviteModal(true)}
          className="w-full bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded text-sm font-medium"
        >
          + Invite Collaborator
        </button>
      </div>

      {/* Collaborators List */}
      <div className="collaborators-list mb-4">
        <h4 className="text-gray-300 font-medium mb-2">Team Members</h4>
        <div className="space-y-2 max-h-48 overflow-y-auto">
          {collaborators.map((collaborator) => (
            <div
              key={collaborator.id}
              className="collaborator-item bg-gray-800 rounded p-3 flex items-center justify-between"
            >
              <div className="flex items-center space-x-3">
                <div className="relative">
                  <div className="w-10 h-10 rounded-full bg-gray-700 flex items-center justify-center">
                    {collaborator.avatar ? (
                      <img
                        src={collaborator.avatar}
                        alt={collaborator.name}
                        className="w-full h-full rounded-full"
                      />
                    ) : (
                      <span className="text-white">
                        {collaborator.name.charAt(0).toUpperCase()}
                      </span>
                    )}
                  </div>
                  {collaborator.isOnline && (
                    <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 rounded-full border border-gray-800" />
                  )}
                </div>
                
                <div>
                  <p className="text-white font-medium">{collaborator.name}</p>
                  <p className={`text-sm ${getRoleColor(collaborator.role)}`}>
                    {collaborator.role.charAt(0).toUpperCase() + collaborator.role.slice(1)}
                  </p>
                </div>
              </div>

              {collaborator.id !== currentUserId && (
                <div className="flex items-center space-x-2">
                  <select
                    value={collaborator.role}
                    onChange={(e) => onUpdateUserRole(collaborator.id, e.target.value as Collaborator['role'])}
                    className="bg-gray-700 text-white text-xs p-1 rounded border border-gray-600"
                  >
                    <option value="viewer">Viewer</option>
                    <option value="commenter">Commenter</option>
                    <option value="editor">Editor</option>
                    <option value="owner">Owner</option>
                  </select>
                  <button
                    onClick={() => onRemoveUser(collaborator.id)}
                    className="text-red-400 hover:text-red-300 text-sm"
                  >
                    ×
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Chat Panel */}
      {showChat && (
        <div className="chat-panel bg-gray-800 rounded-lg p-3">
          <h4 className="text-white font-medium mb-3">Team Chat</h4>
          
          <div className="messages max-h-40 overflow-y-auto mb-3 space-y-2">
            {messages.length === 0 ? (
              <p className="text-gray-500 text-sm">No messages yet</p>
            ) : (
              messages.map((message) => {
                const sender = collaborators.find(c => c.id === message.userId);
                return (
                  <div key={message.id} className="message">
                    <div className="flex items-start space-x-2">
                      <span className="text-blue-400 text-sm font-medium">
                        {sender?.name || 'Unknown'}:
                      </span>
                      <span className="text-gray-300 text-sm">{message.message}</span>
                    </div>
                    <span className="text-gray-500 text-xs">
                      {message.timestamp.toLocaleTimeString()}
                    </span>
                  </div>
                );
              })
            )}
          </div>
          
          <div className="chat-input flex space-x-2">
            <input
              type="text"
              value={chatMessage}
              onChange={(e) => setChatMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Type a message..."
              className="flex-1 bg-gray-700 text-white p-2 rounded border border-gray-600 text-sm"
            />
            <button
              onClick={handleSendMessage}
              className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded text-sm"
            >
              Send
            </button>
          </div>
        </div>
      )}

      {/* Invite Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-96">
            <h3 className="text-white font-bold mb-4">Invite Collaborator</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-gray-300 text-sm mb-1">Email Address</label>
                <input
                  type="email"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  placeholder="colleague@example.com"
                  className="w-full bg-gray-700 text-white p-2 rounded border border-gray-600"
                />
              </div>
              
              <div>
                <label className="block text-gray-300 text-sm mb-1">Role</label>
                <select
                  value={inviteRole}
                  onChange={(e) => setInviteRole(e.target.value as Collaborator['role'])}
                  className="w-full bg-gray-700 text-white p-2 rounded border border-gray-600"
                >
                  <option value="viewer">Viewer - Can view only</option>
                  <option value="commenter">Commenter - Can view and comment</option>
                  <option value="editor">Editor - Can edit and collaborate</option>
                  <option value="owner">Owner - Full access</option>
                </select>
              </div>
            </div>
            
            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => setShowInviteModal(false)}
                className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-2 px-4 rounded"
              >
                Cancel
              </button>
              <button
                onClick={handleInvite}
                className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded"
              >
                Send Invite
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CollaborativeWorkspace;