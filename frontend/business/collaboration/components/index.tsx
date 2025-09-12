/**
 * CollaborationHub - Advanced collaboration management interface
 * 
 * Hub for managing collaborations, team matching, project coordination,
 * and real-time communication
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import React, { useState, useEffect } from 'react';
import {
  UsersIcon,
  UserPlusIcon,
  ChatBubbleLeftRightIcon,
  VideoCameraIcon,
  CalendarIcon,
  FolderIcon,
  StarIcon,
  EyeIcon,
  HeartIcon,
  ShareIcon,
  ClockIcon,
  MapPinIcon,
  TagIcon,
  CheckCircleIcon,
  XMarkIcon,
  MagnifyingGlassIcon,
  AdjustmentsHorizontalIcon,
  BoltIcon,
  TrophyIcon,
  FireIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';

export interface Collaborator {
  id: string;
  name: string;
  avatar: string;
  role: string;
  specialties: string[];
  location: string;
  rating: number;
  followers: number;
  completedProjects: number;
  responseTime: string;
  languages: string[];
  availability: 'available' | 'busy' | 'offline';
  verified: boolean;
  matchScore?: number;
}

export interface Project {
  id: string;
  title: string;
  description: string;
  type: 'music' | 'video' | 'photography' | 'content' | 'marketing';
  status: 'draft' | 'open' | 'in_progress' | 'review' | 'completed' | 'cancelled';
  budget: {
    min: number;
    max: number;
    currency: string;
  };
  deadline: Date;
  skills: string[];
  collaborators: Collaborator[];
  applicants: number;
  createdAt: Date;
  owner: Collaborator;
}

export interface Message {
  id: string;
  senderId: string;
  content: string;
  timestamp: Date;
  type: 'text' | 'file' | 'image' | 'video';
  read: boolean;
}

export interface CollaborationHubProps {
  currentUser?: Collaborator;
  projects?: Project[];
  collaborators?: Collaborator[];
  messages?: Message[];
  onCreateProject?: (project: Partial<Project>) => void;
  onJoinProject?: (projectId: string) => void;
  onInviteCollaborator?: (collaboratorId: string, projectId: string) => void;
  onSendMessage?: (message: Partial<Message>) => void;
  onScheduleMeeting?: (projectId: string, datetime: Date) => void;
  className?: string;
}

const projectTypes = {
  music: { name: 'Music Production', icon: '🎵', color: 'purple' },
  video: { name: 'Video Content', icon: '🎬', color: 'red' },
  photography: { name: 'Photography', icon: '📸', color: 'blue' },
  content: { name: 'Content Creation', icon: '✍️', color: 'green' },
  marketing: { name: 'Marketing', icon: '📊', color: 'orange' }
};

const skillTags = [
  'Music Production', 'Video Editing', 'Photography', 'Graphic Design',
  'Social Media', 'Content Writing', 'Voice Acting', 'Animation',
  'SEO', 'Marketing', 'Branding', 'Web Development'
];

const formatBudget = (budget: { min: number; max: number; currency: string }) => {
  if (budget.min === budget.max) {
    return `${budget.currency}${budget.min.toLocaleString()}`;
  }
  return `${budget.currency}${budget.min.toLocaleString()} - ${budget.currency}${budget.max.toLocaleString()}`;
};

const formatTimeAgo = (date: Date): string => {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return `${diffDays}d ago`;
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'open': return 'bg-green-100 text-green-800';
    case 'in_progress': return 'bg-blue-100 text-blue-800';
    case 'review': return 'bg-yellow-100 text-yellow-800';
    case 'completed': return 'bg-purple-100 text-purple-800';
    case 'cancelled': return 'bg-red-100 text-red-800';
    default: return 'bg-gray-100 text-gray-800';
  }
};

const getAvailabilityStatus = (availability: string) => {
  switch (availability) {
    case 'available': return { color: 'bg-green-400', text: 'Available' };
    case 'busy': return { color: 'bg-yellow-400', text: 'Busy' };
    case 'offline': return { color: 'bg-gray-400', text: 'Offline' };
    default: return { color: 'bg-gray-400', text: 'Unknown' };
  }
};

export const CollaborationHub: React.FC<CollaborationHubProps> = ({
  currentUser,
  projects = [],
  collaborators = [],
  messages = [],
  onCreateProject,
  onJoinProject,
  onInviteCollaborator,
  onSendMessage,
  onScheduleMeeting,
  className = ''
}) => {
  const [activeTab, setActiveTab] = useState<'discover' | 'my_projects' | 'collaborators' | 'messages'>('discover');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [selectedProjectType, setSelectedProjectType] = useState<string>('');
  const [showCreateProject, setShowCreateProject] = useState(false);
  const [aiRecommendations, setAiRecommendations] = useState<Collaborator[]>([]);

  // Mock AI-powered recommendations
  useEffect(() => {
    const recommendations = collaborators
      .filter(c => c.matchScore && c.matchScore > 80)
      .sort((a, b) => (b.matchScore || 0) - (a.matchScore || 0))
      .slice(0, 3);
    setAiRecommendations(recommendations);
  }, [collaborators]);

  const filteredProjects = projects.filter(project => {
    const matchesSearch = !searchTerm || 
      project.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      project.description.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesType = !selectedProjectType || project.type === selectedProjectType;
    
    const matchesSkills = selectedSkills.length === 0 ||
      selectedSkills.some(skill => project.skills.includes(skill));

    return matchesSearch && matchesType && matchesSkills;
  });

  const myProjects = projects.filter(project => 
    currentUser && (project.owner.id === currentUser.id || 
    project.collaborators.some(c => c.id === currentUser.id))
  );

  const stats = {
    totalProjects: projects.length,
    activeProjects: projects.filter(p => p.status === 'in_progress').length,
    completedProjects: projects.filter(p => p.status === 'completed').length,
    totalCollaborators: collaborators.length
  };

  const toggleSkillFilter = (skill: string) => {
    setSelectedSkills(prev => 
      prev.includes(skill) 
        ? prev.filter(s => s !== skill)
        : [...prev, skill]
    );
  };

  return (
    <div className={`w-full ${className}`}>
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md border p-6 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-purple-100 rounded-lg">
              <UsersIcon className="w-8 h-8 text-purple-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Collaboration Hub</h1>
              <p className="text-gray-600">Connect, collaborate, and create together</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setShowCreateProject(true)}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center space-x-2"
            >
              <UserPlusIcon className="w-4 h-4" />
              <span>Create Project</span>
            </button>
            <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 flex items-center space-x-2">
              <VideoCameraIcon className="w-4 h-4" />
              <span>Start Meeting</span>
            </button>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow-md border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Projects</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalProjects}</p>
            </div>
            <FolderIcon className="w-8 h-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Projects</p>
              <p className="text-2xl font-bold text-blue-900">{stats.activeProjects}</p>
            </div>
            <FireIcon className="w-8 h-8 text-orange-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Completed</p>
              <p className="text-2xl font-bold text-green-900">{stats.completedProjects}</p>
            </div>
            <TrophyIcon className="w-8 h-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Collaborators</p>
              <p className="text-2xl font-bold text-purple-900">{stats.totalCollaborators}</p>
            </div>
            <UsersIcon className="w-8 h-8 text-purple-500" />
          </div>
        </div>
      </div>

      {/* AI Recommendations */}
      {aiRecommendations.length > 0 && (
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200 p-6 mb-6">
          <div className="flex items-center space-x-2 mb-4">
            <SparklesIcon className="w-5 h-5 text-purple-600" />
            <h3 className="text-lg font-semibold text-purple-900">AI-Powered Recommendations</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {aiRecommendations.map((collaborator) => (
              <div key={collaborator.id} className="bg-white rounded-lg p-4 border border-purple-200">
                <div className="flex items-center space-x-3 mb-3">
                  <img
                    src={collaborator.avatar}
                    alt={collaborator.name}
                    className="w-10 h-10 rounded-full"
                  />
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <p className="font-medium text-gray-900">{collaborator.name}</p>
                      {collaborator.verified && (
                        <CheckCircleIcon className="w-4 h-4 text-blue-500" />
                      )}
                    </div>
                    <p className="text-sm text-gray-600">{collaborator.role}</p>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center space-x-1">
                      <BoltIcon className="w-4 h-4 text-purple-500" />
                      <span className="text-sm font-medium text-purple-600">{collaborator.matchScore}%</span>
                    </div>
                  </div>
                </div>
                <div className="flex flex-wrap gap-1 mb-3">
                  {collaborator.specialties.slice(0, 2).map((specialty) => (
                    <span key={specialty} className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">
                      {specialty}
                    </span>
                  ))}
                </div>
                <button
                  onClick={() => onInviteCollaborator?.(collaborator.id, '')}
                  className="w-full px-3 py-2 bg-purple-600 text-white text-sm rounded-md hover:bg-purple-700"
                >
                  Connect
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="bg-white rounded-lg shadow-md border">
        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'discover', name: 'Discover Projects', icon: MagnifyingGlassIcon },
              { id: 'my_projects', name: 'My Projects', icon: FolderIcon },
              { id: 'collaborators', name: 'Collaborators', icon: UsersIcon },
              { id: 'messages', name: 'Messages', icon: ChatBubbleLeftRightIcon }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`
                  flex items-center space-x-2 py-4 px-2 border-b-2 font-medium text-sm
                  ${activeTab === tab.id
                    ? 'border-purple-500 text-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <tab.icon className="w-5 h-5" />
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {/* Discover Projects Tab */}
          {activeTab === 'discover' && (
            <div className="space-y-6">
              {/* Filters */}
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
                <div className="flex items-center space-x-4">
                  <div className="relative">
                    <MagnifyingGlassIcon className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Search projects..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>
                  
                  <select
                    value={selectedProjectType}
                    onChange={(e) => setSelectedProjectType(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    <option value="">All Types</option>
                    {Object.entries(projectTypes).map(([key, type]) => (
                      <option key={key} value={key}>{type.name}</option>
                    ))}
                  </select>
                </div>

                <div className="flex items-center space-x-2">
                  <AdjustmentsHorizontalIcon className="w-5 h-5 text-gray-400" />
                  <span className="text-sm text-gray-600">Skills:</span>
                  <div className="flex flex-wrap gap-2">
                    {skillTags.slice(0, 4).map((skill) => (
                      <button
                        key={skill}
                        onClick={() => toggleSkillFilter(skill)}
                        className={`px-3 py-1 text-xs rounded-full border transition-colors ${
                          selectedSkills.includes(skill)
                            ? 'bg-purple-100 text-purple-800 border-purple-300'
                            : 'bg-gray-100 text-gray-600 border-gray-300 hover:bg-gray-200'
                        }`}
                      >
                        {skill}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Projects Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {filteredProjects.map((project) => (
                  <div key={project.id} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h3 className="text-lg font-semibold text-gray-900">{project.title}</h3>
                          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(project.status)}`}>
                            {project.status.replace('_', ' ').toUpperCase()}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">{project.description}</p>
                        
                        <div className="flex items-center space-x-4 text-sm text-gray-500 mb-3">
                          <span className="flex items-center space-x-1">
                            <CalendarIcon className="w-4 h-4" />
                            <span>Due: {project.deadline.toLocaleDateString()}</span>
                          </span>
                          <span className="flex items-center space-x-1">
                            <TagIcon className="w-4 h-4" />
                            <span>{formatBudget(project.budget)}</span>
                          </span>
                        </div>

                        <div className="flex flex-wrap gap-1 mb-4">
                          {project.skills.slice(0, 3).map((skill) => (
                            <span key={skill} className="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded-full">
                              {skill}
                            </span>
                          ))}
                          {project.skills.length > 3 && (
                            <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                              +{project.skills.length - 3} more
                            </span>
                          )}
                        </div>

                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <img
                              src={project.owner.avatar}
                              alt={project.owner.name}
                              className="w-6 h-6 rounded-full"
                            />
                            <span className="text-sm text-gray-600">{project.owner.name}</span>
                          </div>
                          <span className="text-sm text-gray-500">{project.applicants} applicants</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                      <div className="flex items-center space-x-2 text-sm text-gray-500">
                        <ClockIcon className="w-4 h-4" />
                        <span>Posted {formatTimeAgo(project.createdAt)}</span>
                      </div>
                      <button
                        onClick={() => onJoinProject?.(project.id)}
                        className="px-4 py-2 bg-purple-600 text-white text-sm rounded-md hover:bg-purple-700"
                      >
                        Apply
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* My Projects Tab */}
          {activeTab === 'my_projects' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">My Projects</h3>
                <button
                  onClick={() => setShowCreateProject(true)}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center space-x-2"
                >
                  <UserPlusIcon className="w-4 h-4" />
                  <span>New Project</span>
                </button>
              </div>

              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Project
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Collaborators
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Deadline
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {myProjects.map((project) => (
                      <tr key={project.id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900">{project.title}</div>
                            <div className="text-sm text-gray-500">{projectTypes[project.type]?.name}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(project.status)}`}>
                            {project.status.replace('_', ' ').toUpperCase()}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex -space-x-1">
                            {project.collaborators.slice(0, 3).map((collaborator) => (
                              <img
                                key={collaborator.id}
                                src={collaborator.avatar}
                                alt={collaborator.name}
                                className="w-6 h-6 rounded-full border-2 border-white"
                              />
                            ))}
                            {project.collaborators.length > 3 && (
                              <div className="w-6 h-6 rounded-full bg-gray-300 border-2 border-white flex items-center justify-center">
                                <span className="text-xs text-gray-600">+{project.collaborators.length - 3}</span>
                              </div>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {project.deadline.toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <button className="text-purple-600 hover:text-purple-900 mr-3">
                            Edit
                          </button>
                          <button
                            onClick={() => onScheduleMeeting?.(project.id, new Date())}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            Meeting
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Collaborators Tab */}
          {activeTab === 'collaborators' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">Find Collaborators</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {collaborators.map((collaborator) => {
                  const availabilityStatus = getAvailabilityStatus(collaborator.availability);
                  return (
                    <div key={collaborator.id} className="border border-gray-200 rounded-lg p-6">
                      <div className="flex items-center space-x-3 mb-4">
                        <div className="relative">
                          <img
                            src={collaborator.avatar}
                            alt={collaborator.name}
                            className="w-12 h-12 rounded-full"
                          />
                          <div className={`absolute -bottom-1 -right-1 w-4 h-4 ${availabilityStatus.color} rounded-full border-2 border-white`} />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <h4 className="font-medium text-gray-900">{collaborator.name}</h4>
                            {collaborator.verified && (
                              <CheckCircleIcon className="w-4 h-4 text-blue-500" />
                            )}
                          </div>
                          <p className="text-sm text-gray-600">{collaborator.role}</p>
                          <div className="flex items-center space-x-1 text-xs text-gray-500">
                            <MapPinIcon className="w-3 h-3" />
                            <span>{collaborator.location}</span>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-1">
                          <StarIcon className="w-4 h-4 text-yellow-400 fill-current" />
                          <span className="text-sm font-medium">{collaborator.rating}</span>
                        </div>
                        <div className="text-sm text-gray-500">
                          {collaborator.completedProjects} projects
                        </div>
                      </div>

                      <div className="flex flex-wrap gap-1 mb-4">
                        {collaborator.specialties.slice(0, 3).map((specialty) => (
                          <span key={specialty} className="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded-full">
                            {specialty}
                          </span>
                        ))}
                      </div>

                      <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                        <span>{collaborator.followers.toLocaleString()} followers</span>
                        <span>Responds in {collaborator.responseTime}</span>
                      </div>

                      <div className="flex space-x-2">
                        <button
                          onClick={() => onInviteCollaborator?.(collaborator.id, '')}
                          className="flex-1 px-3 py-2 bg-purple-600 text-white text-sm rounded-md hover:bg-purple-700"
                        >
                          Invite
                        </button>
                        <button className="px-3 py-2 border border-gray-300 text-gray-700 text-sm rounded-md hover:bg-gray-50">
                          <ChatBubbleLeftRightIcon className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Messages Tab */}
          {activeTab === 'messages' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">Messages</h3>
              
              <div className="border border-gray-200 rounded-lg">
                <div className="p-4 border-b border-gray-200">
                  <div className="flex items-center space-x-3">
                    <div className="relative">
                      <img
                        src="/api/avatar/default-chat.svg"
                        alt="Chat"
                        className="w-10 h-10 rounded-full"
                      />
                      <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-400 rounded-full border-2 border-white" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">Project Team Chat</h4>
                      <p className="text-sm text-gray-500">3 members online</p>
                    </div>
                  </div>
                </div>

                <div className="p-4 space-y-4 max-h-96 overflow-y-auto">
                  {messages.slice(0, 5).map((message) => (
                    <div key={message.id} className="flex items-start space-x-3">
                      <img
                        src="/api/avatar/default-user.svg"
                        alt="User"
                        className="w-8 h-8 rounded-full"
                      />
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <span className="text-sm font-medium text-gray-900">User Name</span>
                          <span className="text-xs text-gray-500">
                            {formatTimeAgo(message.timestamp)}
                          </span>
                        </div>
                        <p className="text-sm text-gray-700">{message.content}</p>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="p-4 border-t border-gray-200">
                  <div className="flex items-center space-x-3">
                    <input
                      type="text"
                      placeholder="Type a message..."
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                    <button
                      onClick={() => onSendMessage?.({ content: '', senderId: currentUser?.id || '' })}
                      className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                    >
                      Send
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CollaborationHub;