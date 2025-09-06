/**
 * Collaboration Slice - Redux state management for collaborations
 * 
 * Manages collaboration projects, team members, messages, and workflow
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';

export interface Collaborator {
  id: string;
  name: string;
  email: string;
  avatar: string;
  role: string;
  specialties: string[];
  location: string;
  timezone: string;
  rating: number;
  followers: number;
  completedProjects: number;
  responseTime: string;
  languages: string[];
  availability: 'available' | 'busy' | 'offline';
  verified: boolean;
  joinedAt: Date;
  lastActive: Date;
  portfolio: {
    samples: string[];
    testimonials: string[];
    achievements: string[];
  };
  pricing: {
    hourlyRate?: number;
    projectRate?: number;
    currency: string;
  };
  matchScore?: number;
  connectionStatus: 'none' | 'pending' | 'connected' | 'blocked';
}

export interface Project {
  id: string;
  title: string;
  description: string;
  type: 'music' | 'video' | 'photography' | 'content' | 'marketing' | 'design' | 'other';
  status: 'draft' | 'open' | 'in_progress' | 'review' | 'completed' | 'cancelled' | 'on_hold';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  budget: {
    min: number;
    max: number;
    currency: string;
    type: 'fixed' | 'hourly' | 'milestone';
  };
  timeline: {
    startDate: Date;
    endDate: Date;
    milestones: Milestone[];
  };
  skills: string[];
  requirements: string[];
  deliverables: string[];
  collaborators: {
    owner: Collaborator;
    team: ProjectMember[];
    applicants: ProjectApplication[];
  };
  files: {
    id: string;
    name: string;
    url: string;
    type: string;
    uploadedBy: string;
    uploadedAt: Date;
  }[];
  messages: Message[];
  activity: ProjectActivity[];
  settings: {
    visibility: 'public' | 'private' | 'team_only';
    allowApplications: boolean;
    requireApproval: boolean;
    autoAccept: boolean;
  };
  createdAt: Date;
  updatedAt: Date;
}

export interface ProjectMember {
  collaborator: Collaborator;
  role: 'owner' | 'admin' | 'member' | 'contributor' | 'viewer';
  permissions: {
    canEdit: boolean;
    canInvite: boolean;
    canManageFiles: boolean;
    canManageSettings: boolean;
  };
  joinedAt: Date;
  contribution: number; // percentage
  status: 'active' | 'inactive' | 'pending';
}

export interface ProjectApplication {
  id: string;
  applicant: Collaborator;
  message: string;
  proposedRate?: number;
  proposedTimeline?: {
    startDate: Date;
    estimatedDuration: number; // in days
  };
  portfolio: string[];
  status: 'pending' | 'accepted' | 'rejected' | 'withdrawn';
  appliedAt: Date;
  reviewedAt?: Date;
  reviewedBy?: string;
}

export interface Milestone {
  id: string;
  title: string;
  description: string;
  dueDate: Date;
  status: 'pending' | 'in_progress' | 'completed' | 'overdue';
  assignee?: string;
  deliverables: string[];
  payment?: {
    amount: number;
    status: 'pending' | 'released' | 'disputed';
  };
}

export interface Message {
  id: string;
  senderId: string;
  content: string;
  type: 'text' | 'file' | 'image' | 'video' | 'audio' | 'system';
  timestamp: Date;
  edited?: boolean;
  editedAt?: Date;
  readBy: { userId: string; readAt: Date }[];
  reactions: { emoji: string; userId: string }[];
  replyTo?: string;
  attachments?: {
    id: string;
    name: string;
    url: string;
    type: string;
    size: number;
  }[];
  mentions: string[];
}

export interface ProjectActivity {
  id: string;
  type: 'created' | 'updated' | 'member_added' | 'member_removed' | 'file_uploaded' | 'milestone_completed' | 'status_changed';
  actor: string;
  description: string;
  metadata?: any;
  timestamp: Date;
}

export interface VideoCall {
  id: string;
  title: string;
  projectId?: string;
  participants: string[];
  status: 'scheduled' | 'active' | 'ended' | 'cancelled';
  scheduledAt: Date;
  startedAt?: Date;
  endedAt?: Date;
  duration?: number;
  recordingUrl?: string;
  meetingUrl: string;
}

export interface AIMatch {
  collaboratorId: string;
  projectId: string;
  score: number;
  reasoning: string[];
  compatibility: {
    skills: number;
    availability: number;
    budget: number;
    location: number;
    experience: number;
  };
  recommendedRole: string;
}

export interface CollaborationState {
  // Projects
  projects: Project[];
  currentProject: Project | null;
  userProjects: string[];
  
  // Collaborators
  collaborators: Collaborator[];
  connectedCollaborators: string[];
  blockedCollaborators: string[];
  
  // Messages and Communication
  messages: Message[];
  unreadCount: number;
  activeChat: string | null;
  typing: { userId: string; timestamp: Date }[];
  
  // Video Calls
  videoCalls: VideoCall[];
  activeCall: VideoCall | null;
  
  // AI Recommendations
  aiMatches: AIMatch[];
  suggestedCollaborators: string[];
  
  // UI State
  loading: boolean;
  error: string | null;
  filters: {
    projectType?: string;
    status?: string;
    budget?: { min: number; max: number };
    location?: string;
    skills?: string[];
    search?: string;
  };
  view: 'grid' | 'list' | 'kanban';
  selectedProjects: string[];
  
  // Real-time state
  onlineUsers: string[];
  notifications: ProjectNotification[];
}

export interface ProjectNotification {
  id: string;
  type: 'application' | 'message' | 'milestone' | 'payment' | 'system';
  title: string;
  description: string;
  projectId?: string;
  senderId?: string;
  read: boolean;
  timestamp: Date;
  action?: {
    label: string;
    url: string;
  };
}

const initialState: CollaborationState = {
  projects: [],
  currentProject: null,
  userProjects: [],
  collaborators: [],
  connectedCollaborators: [],
  blockedCollaborators: [],
  messages: [],
  unreadCount: 0,
  activeChat: null,
  typing: [],
  videoCalls: [],
  activeCall: null,
  aiMatches: [],
  suggestedCollaborators: [],
  loading: false,
  error: null,
  filters: {},
  view: 'grid',
  selectedProjects: [],
  onlineUsers: [],
  notifications: []
};

// Async thunks for API calls
export const fetchProjects = createAsyncThunk(
  'collaboration/fetchProjects',
  async (filters?: any) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Mock data - in real app, this would come from API
    const mockProjects: Project[] = [
      {
        id: '1',
        title: 'Music Video Production',
        description: 'Looking for a video editor and motion graphics artist for an indie music video',
        type: 'video',
        status: 'open',
        priority: 'high',
        budget: { min: 2000, max: 5000, currency: 'USD', type: 'fixed' },
        timeline: {
          startDate: new Date(Date.now() + 86400000),
          endDate: new Date(Date.now() + 86400000 * 30),
          milestones: []
        },
        skills: ['Video Editing', 'Motion Graphics', 'Color Grading'],
        requirements: ['5+ years experience', 'Portfolio required', 'Available weekends'],
        deliverables: ['Edited video', 'Color graded footage', 'Motion graphics package'],
        collaborators: {
          owner: {
            id: 'owner1',
            name: 'John Doe',
            email: 'john@example.com',
            avatar: 'https://via.placeholder.com/40',
            role: 'Music Producer',
            specialties: ['Music Production', 'Audio Engineering'],
            location: 'Los Angeles, CA',
            timezone: 'PST',
            rating: 4.8,
            followers: 1250,
            completedProjects: 15,
            responseTime: '< 2 hours',
            languages: ['English'],
            availability: 'available',
            verified: true,
            joinedAt: new Date(Date.now() - 86400000 * 365),
            lastActive: new Date(),
            portfolio: { samples: [], testimonials: [], achievements: [] },
            pricing: { hourlyRate: 75, currency: 'USD' },
            connectionStatus: 'none'
          },
          team: [],
          applicants: []
        },
        files: [],
        messages: [],
        activity: [],
        settings: {
          visibility: 'public',
          allowApplications: true,
          requireApproval: true,
          autoAccept: false
        },
        createdAt: new Date(Date.now() - 86400000 * 3),
        updatedAt: new Date(Date.now() - 86400000)
      }
    ];
    
    return mockProjects;
  }
);

export const createProject = createAsyncThunk(
  'collaboration/createProject',
  async (projectData: Partial<Project>) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    const newProject: Project = {
      id: Date.now().toString(),
      title: projectData.title || '',
      description: projectData.description || '',
      type: projectData.type || 'other',
      status: 'draft',
      priority: 'medium',
      budget: projectData.budget || { min: 0, max: 1000, currency: 'USD', type: 'fixed' },
      timeline: projectData.timeline || {
        startDate: new Date(),
        endDate: new Date(Date.now() + 86400000 * 30),
        milestones: []
      },
      skills: projectData.skills || [],
      requirements: projectData.requirements || [],
      deliverables: projectData.deliverables || [],
      collaborators: {
        owner: projectData.collaborators?.owner || {} as Collaborator,
        team: [],
        applicants: []
      },
      files: [],
      messages: [],
      activity: [{
        id: '1',
        type: 'created',
        actor: projectData.collaborators?.owner?.id || 'current-user',
        description: 'Project created',
        timestamp: new Date()
      }],
      settings: {
        visibility: 'public',
        allowApplications: true,
        requireApproval: true,
        autoAccept: false
      },
      createdAt: new Date(),
      updatedAt: new Date()
    };
    
    return newProject;
  }
);

export const applyToProject = createAsyncThunk(
  'collaboration/applyToProject',
  async ({ projectId, application }: { projectId: string; application: Partial<ProjectApplication> }) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const newApplication: ProjectApplication = {
      id: Date.now().toString(),
      applicant: application.applicant || {} as Collaborator,
      message: application.message || '',
      proposedRate: application.proposedRate,
      proposedTimeline: application.proposedTimeline,
      portfolio: application.portfolio || [],
      status: 'pending',
      appliedAt: new Date()
    };
    
    return { projectId, application: newApplication };
  }
);

export const sendMessage = createAsyncThunk(
  'collaboration/sendMessage',
  async ({ projectId, message }: { projectId?: string; message: Partial<Message> }) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 200));
    
    const newMessage: Message = {
      id: Date.now().toString(),
      senderId: message.senderId || 'current-user',
      content: message.content || '',
      type: message.type || 'text',
      timestamp: new Date(),
      readBy: [],
      reactions: [],
      mentions: message.mentions || [],
      attachments: message.attachments
    };
    
    return { projectId, message: newMessage };
  }
);

export const fetchAIMatches = createAsyncThunk(
  'collaboration/fetchAIMatches',
  async (projectId: string) => {
    // Simulate AI matching API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const mockMatches: AIMatch[] = [
      {
        collaboratorId: 'collab1',
        projectId,
        score: 92,
        reasoning: [
          'Perfect skill match for video editing',
          'Available in required timeframe',
          'Budget compatibility',
          'Excellent ratings and reviews'
        ],
        compatibility: {
          skills: 95,
          availability: 90,
          budget: 85,
          location: 75,
          experience: 98
        },
        recommendedRole: 'Lead Video Editor'
      },
      {
        collaboratorId: 'collab2',
        projectId,
        score: 87,
        reasoning: [
          'Strong motion graphics background',
          'Previous music video experience',
          'Quick response time'
        ],
        compatibility: {
          skills: 88,
          availability: 95,
          budget: 80,
          location: 60,
          experience: 85
        },
        recommendedRole: 'Motion Graphics Artist'
      }
    ];
    
    return mockMatches;
  }
);

export const startVideoCall = createAsyncThunk(
  'collaboration/startVideoCall',
  async ({ projectId, participants }: { projectId?: string; participants: string[] }) => {
    // Simulate video call API setup
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const videoCall: VideoCall = {
      id: Date.now().toString(),
      title: projectId ? 'Project Meeting' : 'Collaboration Call',
      projectId,
      participants,
      status: 'active',
      scheduledAt: new Date(),
      startedAt: new Date(),
      meetingUrl: `https://meet.ainflue.com/call/${Date.now()}`
    };
    
    return videoCall;
  }
);

const collaborationSlice = createSlice({
  name: 'collaboration',
  initialState,
  reducers: {
    // Project management
    setCurrentProject: (state, action: PayloadAction<Project | null>) => {
      state.currentProject = action.payload;
    },
    updateProject: (state, action: PayloadAction<{ id: string; updates: Partial<Project> }>) => {
      const project = state.projects.find(p => p.id === action.payload.id);
      if (project) {
        Object.assign(project, action.payload.updates);
        project.updatedAt = new Date();
      }
      if (state.currentProject?.id === action.payload.id) {
        Object.assign(state.currentProject, action.payload.updates);
        state.currentProject.updatedAt = new Date();
      }
    },
    addProjectMember: (state, action: PayloadAction<{ projectId: string; member: ProjectMember }>) => {
      const project = state.projects.find(p => p.id === action.payload.projectId);
      if (project) {
        project.collaborators.team.push(action.payload.member);
        project.activity.unshift({
          id: Date.now().toString(),
          type: 'member_added',
          actor: 'current-user',
          description: `${action.payload.member.collaborator.name} joined the project`,
          timestamp: new Date()
        });
      }
    },
    removeProjectMember: (state, action: PayloadAction<{ projectId: string; memberId: string }>) => {
      const project = state.projects.find(p => p.id === action.payload.projectId);
      if (project) {
        const member = project.collaborators.team.find(m => m.collaborator.id === action.payload.memberId);
        project.collaborators.team = project.collaborators.team.filter(m => m.collaborator.id !== action.payload.memberId);
        if (member) {
          project.activity.unshift({
            id: Date.now().toString(),
            type: 'member_removed',
            actor: 'current-user',
            description: `${member.collaborator.name} left the project`,
            timestamp: new Date()
          });
        }
      }
    },

    // Application management
    updateApplicationStatus: (state, action: PayloadAction<{ 
      projectId: string; 
      applicationId: string; 
      status: 'accepted' | 'rejected' 
    }>) => {
      const project = state.projects.find(p => p.id === action.payload.projectId);
      if (project) {
        const application = project.collaborators.applicants.find(a => a.id === action.payload.applicationId);
        if (application) {
          application.status = action.payload.status;
          application.reviewedAt = new Date();
          application.reviewedBy = 'current-user';
          
          if (action.payload.status === 'accepted') {
            // Add to team
            const newMember: ProjectMember = {
              collaborator: application.applicant,
              role: 'member',
              permissions: {
                canEdit: false,
                canInvite: false,
                canManageFiles: true,
                canManageSettings: false
              },
              joinedAt: new Date(),
              contribution: 0,
              status: 'active'
            };
            project.collaborators.team.push(newMember);
          }
        }
      }
    },

    // Message management
    addMessage: (state, action: PayloadAction<{ projectId?: string; message: Message }>) => {
      state.messages.unshift(action.payload.message);
      if (action.payload.projectId) {
        const project = state.projects.find(p => p.id === action.payload.projectId);
        if (project) {
          project.messages.unshift(action.payload.message);
        }
      }
      if (action.payload.message.senderId !== 'current-user') {
        state.unreadCount++;
      }
    },
    markMessageAsRead: (state, action: PayloadAction<{ messageId: string; userId: string }>) => {
      const message = state.messages.find(m => m.id === action.payload.messageId);
      if (message) {
        const readEntry = message.readBy.find(r => r.userId === action.payload.userId);
        if (!readEntry) {
          message.readBy.push({
            userId: action.payload.userId,
            readAt: new Date()
          });
        }
      }
    },
    setActiveChat: (state, action: PayloadAction<string | null>) => {
      state.activeChat = action.payload;
    },
    updateTypingStatus: (state, action: PayloadAction<{ userId: string; isTyping: boolean }>) => {
      if (action.payload.isTyping) {
        const existing = state.typing.find(t => t.userId === action.payload.userId);
        if (!existing) {
          state.typing.push({
            userId: action.payload.userId,
            timestamp: new Date()
          });
        }
      } else {
        state.typing = state.typing.filter(t => t.userId !== action.payload.userId);
      }
    },

    // Collaborator management
    connectCollaborator: (state, action: PayloadAction<string>) => {
      if (!state.connectedCollaborators.includes(action.payload)) {
        state.connectedCollaborators.push(action.payload);
      }
      // Update collaborator status
      const collaborator = state.collaborators.find(c => c.id === action.payload);
      if (collaborator) {
        collaborator.connectionStatus = 'connected';
      }
    },
    blockCollaborator: (state, action: PayloadAction<string>) => {
      if (!state.blockedCollaborators.includes(action.payload)) {
        state.blockedCollaborators.push(action.payload);
      }
      state.connectedCollaborators = state.connectedCollaborators.filter(id => id !== action.payload);
      // Update collaborator status
      const collaborator = state.collaborators.find(c => c.id === action.payload);
      if (collaborator) {
        collaborator.connectionStatus = 'blocked';
      }
    },
    updateCollaboratorAvailability: (state, action: PayloadAction<{ id: string; availability: 'available' | 'busy' | 'offline' }>) => {
      const collaborator = state.collaborators.find(c => c.id === action.payload.id);
      if (collaborator) {
        collaborator.availability = action.payload.availability;
        collaborator.lastActive = new Date();
      }
    },

    // Video calls
    endVideoCall: (state, action: PayloadAction<string>) => {
      const call = state.videoCalls.find(c => c.id === action.payload);
      if (call) {
        call.status = 'ended';
        call.endedAt = new Date();
        if (call.startedAt) {
          call.duration = call.endedAt.getTime() - call.startedAt.getTime();
        }
      }
      if (state.activeCall?.id === action.payload) {
        state.activeCall = null;
      }
    },

    // Filters and UI
    updateFilters: (state, action: PayloadAction<Partial<CollaborationState['filters']>>) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearFilters: (state) => {
      state.filters = {};
    },
    setView: (state, action: PayloadAction<'grid' | 'list' | 'kanban'>) => {
      state.view = action.payload;
    },
    selectProject: (state, action: PayloadAction<string>) => {
      if (!state.selectedProjects.includes(action.payload)) {
        state.selectedProjects.push(action.payload);
      }
    },
    deselectProject: (state, action: PayloadAction<string>) => {
      state.selectedProjects = state.selectedProjects.filter(id => id !== action.payload);
    },
    clearSelection: (state) => {
      state.selectedProjects = [];
    },

    // Online status
    updateOnlineUsers: (state, action: PayloadAction<string[]>) => {
      state.onlineUsers = action.payload;
    },

    // Notifications
    addNotification: (state, action: PayloadAction<ProjectNotification>) => {
      state.notifications.unshift(action.payload);
    },
    markNotificationAsRead: (state, action: PayloadAction<string>) => {
      const notification = state.notifications.find(n => n.id === action.payload);
      if (notification) {
        notification.read = true;
      }
    },
    clearNotifications: (state) => {
      state.notifications = [];
    },

    // Error handling
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Fetch projects
      .addCase(fetchProjects.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchProjects.fulfilled, (state, action) => {
        state.loading = false;
        state.projects = action.payload;
      })
      .addCase(fetchProjects.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch projects';
      })

      // Create project
      .addCase(createProject.pending, (state) => {
        state.loading = true;
      })
      .addCase(createProject.fulfilled, (state, action) => {
        state.loading = false;
        state.projects.unshift(action.payload);
        state.userProjects.push(action.payload.id);
        state.currentProject = action.payload;
      })
      .addCase(createProject.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to create project';
      })

      // Apply to project
      .addCase(applyToProject.fulfilled, (state, action) => {
        const project = state.projects.find(p => p.id === action.payload.projectId);
        if (project) {
          project.collaborators.applicants.push(action.payload.application);
        }
      })

      // Send message
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.messages.unshift(action.payload.message);
        if (action.payload.projectId) {
          const project = state.projects.find(p => p.id === action.payload.projectId);
          if (project) {
            project.messages.unshift(action.payload.message);
          }
        }
      })

      // AI matches
      .addCase(fetchAIMatches.fulfilled, (state, action) => {
        state.aiMatches = action.payload;
        state.suggestedCollaborators = action.payload.map(match => match.collaboratorId);
      })

      // Video calls
      .addCase(startVideoCall.fulfilled, (state, action) => {
        state.videoCalls.push(action.payload);
        state.activeCall = action.payload;
      });
  }
});

export const {
  setCurrentProject,
  updateProject,
  addProjectMember,
  removeProjectMember,
  updateApplicationStatus,
  addMessage,
  markMessageAsRead,
  setActiveChat,
  updateTypingStatus,
  connectCollaborator,
  blockCollaborator,
  updateCollaboratorAvailability,
  endVideoCall,
  updateFilters,
  clearFilters,
  setView,
  selectProject,
  deselectProject,
  clearSelection,
  updateOnlineUsers,
  addNotification,
  markNotificationAsRead,
  clearNotifications,
  setError,
  clearError
} = collaborationSlice.actions;

// Selectors
export const selectAllProjects = (state: { collaboration: CollaborationState }) => state.collaboration.projects;
export const selectCurrentProject = (state: { collaboration: CollaborationState }) => state.collaboration.currentProject;
export const selectUserProjects = (state: { collaboration: CollaborationState }) => 
  state.collaboration.projects.filter(p => state.collaboration.userProjects.includes(p.id));
export const selectCollaborators = (state: { collaboration: CollaborationState }) => state.collaboration.collaborators;
export const selectMessages = (state: { collaboration: CollaborationState }) => state.collaboration.messages;
export const selectUnreadCount = (state: { collaboration: CollaborationState }) => state.collaboration.unreadCount;
export const selectAIMatches = (state: { collaboration: CollaborationState }) => state.collaboration.aiMatches;
export const selectActiveCall = (state: { collaboration: CollaborationState }) => state.collaboration.activeCall;
export const selectNotifications = (state: { collaboration: CollaborationState }) => state.collaboration.notifications;
export const selectIsLoading = (state: { collaboration: CollaborationState }) => state.collaboration.loading;
export const selectError = (state: { collaboration: CollaborationState }) => state.collaboration.error;

// Filtered projects selector
export const selectFilteredProjects = (state: { collaboration: CollaborationState }) => {
  const { projects, filters } = state.collaboration;
  let filtered = [...projects];

  if (filters.projectType) {
    filtered = filtered.filter(project => project.type === filters.projectType);
  }

  if (filters.status) {
    filtered = filtered.filter(project => project.status === filters.status);
  }

  if (filters.budget) {
    filtered = filtered.filter(project => 
      project.budget.max >= filters.budget!.min &&
      project.budget.min <= filters.budget!.max
    );
  }

  if (filters.skills?.length) {
    filtered = filtered.filter(project =>
      filters.skills!.some(skill => project.skills.includes(skill))
    );
  }

  if (filters.search) {
    const searchLower = filters.search.toLowerCase();
    filtered = filtered.filter(project =>
      project.title.toLowerCase().includes(searchLower) ||
      project.description.toLowerCase().includes(searchLower) ||
      project.skills.some(skill => skill.toLowerCase().includes(searchLower))
    );
  }

  return filtered;
};

export default collaborationSlice.reducer;