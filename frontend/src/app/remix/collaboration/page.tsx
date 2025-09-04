/**
 * Remix Collaboration Page - Ultra-Advanced Enterprise Collaboration System
 * 
 * This page provides real-time collaborative workspace for global creators
 * with advanced sharing, communication, and project management capabilities.
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️  CRITICAL LEGAL NOTICE:
 * This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
 * Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
 * Contact: mlaiel@live.de for licensing inquiries.
 * 
 * 🏆 Expert Development Team Specialties:
 * - Lead AI Developer: Advanced machine learning and AI systems
 * - Backend Senior Engineer: Enterprise Python/FastAPI architecture
 * - ML Engineer: TensorFlow/PyTorch and neural networks
 * - Database Administrator: PostgreSQL and vector databases
 * - Security Specialist: Enterprise security protocols
 * - Microservices Architect: Scalable distributed systems
 * - Audio Engineer: Professional audio processing
 * - DevOps Engineer: CI/CD and cloud infrastructure
 * - AI Prompt Engineer: Advanced prompt engineering
 */

'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { 
  CollaborativeWorkspace
} from '@/components/remix_studio';
import studioStyles from '@/components/remix_studio/remix_studio.styles';
import { 
  UsersIcon,
  PlusIcon,
  ShareIcon,
  ChatBubbleLeftRightIcon,
  VideoCameraIcon,
  MicrophoneIcon,
  PhoneIcon,
  EllipsisVerticalIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  ClockIcon,
  MusicalNoteIcon,
  PlayIcon,
  PauseIcon,
  StarIcon,
  EyeIcon,
  ArrowLeftIcon,
  GlobeAltIcon,
  ShieldCheckIcon,
  CogIcon,
  BellIcon,
  UserPlusIcon
} from '@heroicons/react/24/outline';
import clsx from 'clsx';

interface CollaborationPageProps {
  params?: { [key: string]: string };
}

interface CollaborationProject {
  id: string;
  name: string;
  description: string;
  thumbnail: string;
  owner: CollaborationUser;
  collaborators: CollaborationUser[];
  status: 'active' | 'completed' | 'paused' | 'archived';
  lastActivity: Date;
  totalTracks: number;
  duration: number;
  genre: string;
  visibility: 'public' | 'private' | 'invite-only';
  permissions: ProjectPermissions;
}

interface CollaborationUser {
  id: string;
  name: string;
  username: string;
  avatar: string;
  role: 'owner' | 'collaborator' | 'viewer' | 'producer' | 'vocalist' | 'mixer';
  isOnline: boolean;
  lastSeen?: Date;
  skills: string[];
  rating: number;
  location: string;
  timezone: string;
}

interface ProjectPermissions {
  canEdit: boolean;
  canInvite: boolean;
  canExport: boolean;
  canDelete: boolean;
  canModifyPermissions: boolean;
}

interface CollaborationRoom {
  id: string;
  projectId: string;
  activeUsers: CollaborationUser[];
  audioEnabled: boolean;
  videoEnabled: boolean;
  screenShare: boolean;
  messages: ChatMessage[];
}

interface ChatMessage {
  id: string;
  userId: string;
  content: string;
  timestamp: Date;
  type: 'text' | 'audio' | 'file' | 'system';
  replyTo?: string;
}

const CollaborationPage: React.FC<CollaborationPageProps> = ({ params }) => {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('projects');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [selectedProject, setSelectedProject] = useState<string | null>(null);
  
  const [collaborationProjects, setCollaborationProjects] = useState<CollaborationProject[]>([]);
  const [activeRoom, setActiveRoom] = useState<CollaborationRoom | null>(null);
  const [currentUser] = useState<CollaborationUser>({
    id: 'current-user',
    name: 'Fahed Mlaiel',
    username: 'fmlaiel',
    avatar: '/avatars/fahed.jpg',
    role: 'owner',
    isOnline: true,
    skills: ['Producer', 'Audio Engineer', 'Mixer'],
    rating: 4.9,
    location: 'Berlin, Germany',
    timezone: 'CET'
  });

  const tabs = [
    { id: 'projects', label: 'My Projects', description: 'Active and completed collaboration projects' },
    { id: 'discover', label: 'Discover', description: 'Find new collaboration opportunities' },
    { id: 'invitations', label: 'Invitations', description: 'Pending invitations and requests' },
    { id: 'network', label: 'Network', description: 'Your collaborator network and connections' }
  ];

  const statusFilters = [
    { value: 'all', label: 'All Projects' },
    { value: 'active', label: 'Active' },
    { value: 'completed', label: 'Completed' },
    { value: 'paused', label: 'Paused' }
  ];

  useEffect(() => {
    loadCollaborationProjects();
  }, []);

  const loadCollaborationProjects = async () => {
    // Simulate API call to load collaboration projects
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockProjects: CollaborationProject[] = [
        {
          id: 'project-1',
          name: 'Summer Vibes Remix',
          description: 'Electronic remix of popular summer hits with tropical house influences',
          thumbnail: '/projects/summer-vibes.jpg',
          owner: {
            id: 'user-1',
            name: 'Alex Producer',
            username: 'alexbeats',
            avatar: '/avatars/alex.jpg',
            role: 'owner',
            isOnline: true,
            skills: ['Producer', 'DJ'],
            rating: 4.8,
            location: 'Los Angeles, USA',
            timezone: 'PST'
          },
          collaborators: [
            currentUser,
            {
              id: 'user-2',
              name: 'Maria Vocalist',
              username: 'maria_voice',
              avatar: '/avatars/maria.jpg',
              role: 'vocalist',
              isOnline: false,
              lastSeen: new Date(Date.now() - 3600000),
              skills: ['Vocalist', 'Songwriter'],
              rating: 4.9,
              location: 'Nashville, USA',
              timezone: 'CST'
            }
          ],
          status: 'active',
          lastActivity: new Date(Date.now() - 1800000),
          totalTracks: 8,
          duration: 245,
          genre: 'Tropical House',
          visibility: 'private',
          permissions: {
            canEdit: true,
            canInvite: true,
            canExport: true,
            canDelete: false,
            canModifyPermissions: false
          }
        },
        {
          id: 'project-2',
          name: 'Urban Fusion',
          description: 'Hip-hop and jazz fusion collaboration with live instruments',
          thumbnail: '/projects/urban-fusion.jpg',
          owner: currentUser,
          collaborators: [
            {
              id: 'user-3',
              name: 'Jazz Drummer',
              username: 'jazz_beats',
              avatar: '/avatars/drummer.jpg',
              role: 'producer',
              isOnline: true,
              skills: ['Drummer', 'Producer'],
              rating: 4.7,
              location: 'New York, USA',
              timezone: 'EST'
            },
            {
              id: 'user-4',
              name: 'MC Flow',
              username: 'mc_flow',
              avatar: '/avatars/mc.jpg',
              role: 'vocalist',
              isOnline: true,
              skills: ['Rapper', 'Lyricist'],
              rating: 4.6,
              location: 'Atlanta, USA',
              timezone: 'EST'
            }
          ],
          status: 'active',
          lastActivity: new Date(Date.now() - 900000),
          totalTracks: 12,
          duration: 198,
          genre: 'Hip-Hop Jazz',
          visibility: 'invite-only',
          permissions: {
            canEdit: true,
            canInvite: true,
            canExport: true,
            canDelete: true,
            canModifyPermissions: true
          }
        },
        {
          id: 'project-3',
          name: 'Ambient Soundscape',
          description: 'Meditative ambient music for wellness and relaxation',
          thumbnail: '/projects/ambient.jpg',
          owner: {
            id: 'user-5',
            name: 'Zen Producer',
            username: 'zen_sounds',
            avatar: '/avatars/zen.jpg',
            role: 'owner',
            isOnline: false,
            lastSeen: new Date(Date.now() - 7200000),
            skills: ['Ambient Producer', 'Sound Designer'],
            rating: 4.9,
            location: 'Tokyo, Japan',
            timezone: 'JST'
          },
          collaborators: [
            currentUser,
            {
              id: 'user-6',
              name: 'Nature Sounds',
              username: 'nature_fx',
              avatar: '/avatars/nature.jpg',
              role: 'producer',
              isOnline: false,
              lastSeen: new Date(Date.now() - 10800000),
              skills: ['Field Recording', 'Sound Design'],
              rating: 4.8,
              location: 'Iceland',
              timezone: 'GMT'
            }
          ],
          status: 'completed',
          lastActivity: new Date(Date.now() - 86400000),
          totalTracks: 6,
          duration: 3420,
          genre: 'Ambient',
          visibility: 'public',
          permissions: {
            canEdit: false,
            canInvite: false,
            canExport: true,
            canDelete: false,
            canModifyPermissions: false
          }
        }
      ];

      setCollaborationProjects(mockProjects);
    } catch (error) {
      console.error('Failed to load collaboration projects:', error);
    }
  };

  const handleProjectSelect = (projectId: string) => {
    setSelectedProject(projectId);
    router.push(`/remix/studio?project=${projectId}&collaboration=true`);
  };

  const handleInviteCollaborator = async (email: string, role: string) => {
    try {
      // Simulate API call to invite collaborator
      await new Promise(resolve => setTimeout(resolve, 500));
      console.log(`Invited ${email} as ${role}`);
      setShowInviteModal(false);
    } catch (error) {
      console.error('Failed to invite collaborator:', error);
    }
  };

  const filteredProjects = collaborationProjects.filter(project => {
    const matchesSearch = project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         project.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         project.genre.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesStatus = filterStatus === 'all' || project.status === filterStatus;
    
    return matchesSearch && matchesStatus;
  });

  const renderProjectCard = (project: CollaborationProject) => (
    <div
      key={project.id}
      onClick={() => handleProjectSelect(project.id)}
      className={clsx(
        studioStyles.container.card,
        "p-6 cursor-pointer transition-all duration-200 hover:scale-105 hover:shadow-lg group"
      )}
    >
      {/* Project Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white group-hover:text-purple-600 transition-colors">
              {project.name}
            </h3>
            <span className={clsx(
              "px-2 py-1 text-xs font-medium rounded-full",
              project.status === 'active' && "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300",
              project.status === 'completed' && "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300",
              project.status === 'paused' && "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300"
            )}>
              {project.status}
            </span>
          </div>
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-3 line-clamp-2">
            {project.description}
          </p>
        </div>
        <div className="flex items-center space-x-1">
          {project.visibility === 'public' && <GlobeAltIcon className="h-4 w-4 text-slate-400" />}
          {project.visibility === 'private' && <ShieldCheckIcon className="h-4 w-4 text-slate-400" />}
          <button className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300">
            <EllipsisVerticalIcon className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Project Metadata */}
      <div className="flex items-center justify-between text-sm text-slate-500 dark:text-slate-400 mb-4">
        <div className="flex items-center space-x-4">
          <span className="flex items-center space-x-1">
            <MusicalNoteIcon className="h-4 w-4" />
            <span>{project.totalTracks} tracks</span>
          </span>
          <span className="flex items-center space-x-1">
            <ClockIcon className="h-4 w-4" />
            <span>{Math.floor(project.duration / 60)}:{String(project.duration % 60).padStart(2, '0')}</span>
          </span>
          <span className="px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded text-xs">
            {project.genre}
          </span>
        </div>
        <span className="text-xs">
          {new Intl.RelativeTimeFormat('en', { numeric: 'auto' }).format(
            Math.floor((project.lastActivity.getTime() - Date.now()) / (1000 * 60)),
            'minute'
          )}
        </span>
      </div>

      {/* Collaborators */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="text-sm text-slate-600 dark:text-slate-400">Contributors:</span>
          <div className="flex -space-x-2">
            <div
              className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-xs font-medium text-white border-2 border-white dark:border-slate-900"
              title={project.owner.name}
            >
              {project.owner.name.split(' ').map(n => n[0]).join('')}
            </div>
            {project.collaborators.slice(0, 3).map((collaborator) => (
              <div
                key={collaborator.id}
                className="w-8 h-8 rounded-full bg-gradient-to-br from-green-500 to-teal-500 flex items-center justify-center text-xs font-medium text-white border-2 border-white dark:border-slate-900"
                title={collaborator.name}
              >
                {collaborator.name.split(' ').map(n => n[0]).join('')}
              </div>
            ))}
            {project.collaborators.length > 3 && (
              <div className="w-8 h-8 rounded-full bg-slate-400 flex items-center justify-center text-xs font-medium text-white border-2 border-white dark:border-slate-900">
                +{project.collaborators.length - 3}
              </div>
            )}
          </div>
        </div>

        {/* Online Indicator */}
        <div className="flex items-center space-x-2">
          {project.collaborators.some(c => c.isOnline) && (
            <div className="flex items-center space-x-1 text-green-600">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-xs">Live</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const renderProjectsTab = () => (
    <div className="space-y-6">
      {/* Search and Filters */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search projects..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 pr-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            />
          </div>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
          >
            {statusFilters.map((filter) => (
              <option key={filter.value} value={filter.value}>
                {filter.label}
              </option>
            ))}
          </select>
        </div>
        <button
          onClick={() => setShowInviteModal(true)}
          className={clsx(studioStyles.buttons.primary, "px-4 py-2")}
        >
          <PlusIcon className="h-4 w-4 mr-2" />
          New Project
        </button>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredProjects.map(renderProjectCard)}
      </div>

      {filteredProjects.length === 0 && (
        <div className="text-center py-12">
          <MusicalNoteIcon className="h-12 w-12 text-slate-400 mx-auto mb-4" />
          <p className="text-lg text-slate-600 dark:text-slate-400">No projects found</p>
          <p className="text-sm text-slate-500 dark:text-slate-500 mt-2">
            Try adjusting your search or filters
          </p>
        </div>
      )}
    </div>
  );

  const renderDiscoverTab = () => (
    <div className="space-y-6">
      <div className={clsx(studioStyles.container.card, "p-6 text-center")}>
        <UsersIcon className="h-12 w-12 text-purple-500 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
          Discover New Collaborations
        </h3>
        <p className="text-slate-600 dark:text-slate-400 mb-4">
          Find talented creators worldwide and start your next musical journey
        </p>
        <button className={clsx(studioStyles.buttons.primary, "px-6 py-3")}>
          Browse Creators
        </button>
      </div>
    </div>
  );

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'projects':
        return renderProjectsTab();
      case 'discover':
        return renderDiscoverTab();
      case 'invitations':
        return (
          <div className={clsx(studioStyles.container.card, "p-6 text-center")}>
            <BellIcon className="h-12 w-12 text-orange-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
              No Pending Invitations
            </h3>
            <p className="text-slate-600 dark:text-slate-400">
              You're all caught up with collaboration invitations
            </p>
          </div>
        );
      case 'network':
        return (
          <div className={clsx(studioStyles.container.card, "p-6 text-center")}>
            <UserPlusIcon className="h-12 w-12 text-blue-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
              Your Network
            </h3>
            <p className="text-slate-600 dark:text-slate-400">
              Connect with other creators and build your collaboration network
            </p>
          </div>
        );
      default:
        return renderProjectsTab();
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      {/* Header */}
      <div className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
        <div className="px-6 py-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/remix')}
                className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
              >
                <ArrowLeftIcon className="h-5 w-5" />
              </button>
              <div>
                <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
                  Collaboration Hub
                </h1>
                <p className="text-slate-600 dark:text-slate-400 mt-2">
                  Connect, create, and collaborate with creators worldwide
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowInviteModal(true)}
                className={clsx(studioStyles.buttons.secondary, "px-4 py-2")}
              >
                <UserPlusIcon className="h-5 w-5 mr-2" />
                Invite Creator
              </button>
              <button
                onClick={() => router.push('/remix/studio')}
                className={clsx(studioStyles.buttons.primary, "px-6 py-3")}
              >
                <MusicalNoteIcon className="h-5 w-5 mr-2" />
                New Project
              </button>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="px-6">
          <div className="flex space-x-8 border-b border-slate-200 dark:border-slate-700">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={clsx(
                  "pb-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200",
                  activeTab === tab.id
                    ? "border-purple-500 text-purple-600 dark:text-purple-400"
                    : "border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300"
                )}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Description */}
        <div className="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
          <div className="px-6 py-3">
            <p className="text-sm text-slate-600 dark:text-slate-400">
              {tabs.find(tab => tab.id === activeTab)?.description}
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="px-6 py-8">
        {renderActiveTab()}
      </div>

      {/* Invite Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className={clsx(studioStyles.container.card, "max-w-md w-full p-6")}>
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
              Invite Collaborator
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Email Address
                </label>
                <input
                  type="email"
                  placeholder="creator@example.com"
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Role
                </label>
                <select className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500">
                  <option value="collaborator">Collaborator</option>
                  <option value="producer">Producer</option>
                  <option value="vocalist">Vocalist</option>
                  <option value="mixer">Mixer</option>
                  <option value="viewer">Viewer</option>
                </select>
              </div>
              <div className="flex space-x-3 pt-4">
                <button
                  onClick={() => setShowInviteModal(false)}
                  className={clsx(studioStyles.buttons.ghost, "flex-1")}
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleInviteCollaborator('creator@example.com', 'collaborator')}
                  className={clsx(studioStyles.buttons.primary, "flex-1")}
                >
                  Send Invite
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CollaborationPage;