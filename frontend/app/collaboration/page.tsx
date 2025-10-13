'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { 
  ArrowLeft, Users, MessageSquare, Video, FileText, Folder, 
  Share2, Clock, CheckCircle, Loader2, UserPlus, Edit3, Eye, 
  Download, Upload, Star, TrendingUp
} from 'lucide-react';

interface CollaborationProject {
  project_id: string;
  name: string;
  description: string;
  project_type: string;
  status: 'active' | 'completed' | 'paused';
  created_by: string;
  creators: string[];
  created_at: string;
  deadline?: string;
  progress: number;
}

interface ProjectMember {
  user_id: string;
  username: string;
  role: string;
  is_online: boolean;
  last_seen: string;
  contributions: number;
}

interface ChatMessage {
  message_id: string;
  sender_id: string;
  sender_name: string;
  message: string;
  timestamp: string;
  attachments?: string[];
}

interface SharedFile {
  file_id: string;
  name: string;
  type: string;
  size: number;
  uploaded_by: string;
  uploaded_at: string;
  url: string;
}

interface UserPresence {
  user_id: string;
  username: string;
  cursor_x?: number;
  cursor_y?: number;
  current_file?: string;
  last_activity: string;
}

export default function CollaborationPage() {
  const [projects, setProjects] = useState<CollaborationProject[]>([]);
  const [activeProject, setActiveProject] = useState<CollaborationProject | null>(null);
  const [members, setMembers] = useState<ProjectMember[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [files, setFiles] = useState<SharedFile[]>([]);
  const [presences, setPresences] = useState<UserPresence[]>([]);
  const [loading, setLoading] = useState(true);
  const [newMessage, setNewMessage] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [projectName, setProjectName] = useState('');
  const [projectDescription, setProjectDescription] = useState('');
  const [projectType, setProjectType] = useState('video');
  const [selectedTab, setSelectedTab] = useState<'chat' | 'files' | 'members'>('chat');

  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchProjects();
    const interval = setInterval(fetchProjects, 10000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (activeProject) {
      fetchProjectDetails(activeProject.project_id);
      
      const membersInterval = setInterval(() => fetchMembers(activeProject.project_id), 5000);
      const messagesInterval = setInterval(() => fetchMessages(activeProject.project_id), 3000);
      const filesInterval = setInterval(() => fetchFiles(activeProject.project_id), 10000);
      const presenceInterval = setInterval(() => fetchPresence(activeProject.project_id), 2000);
      
      return () => {
        clearInterval(membersInterval);
        clearInterval(messagesInterval);
        clearInterval(filesInterval);
        clearInterval(presenceInterval);
      };
    }
  }, [activeProject]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchProjects = async () => {
    try {
      // ✅ CONNEXION BACKEND RÉEL - http://localhost:8000/collaboration
      const response = await fetch('http://localhost:8000/collaboration', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        console.log('✅ BACKEND RÉEL CONNECTÉ:', data);
        
        // Extraire les collaborations actives du backend
        const activeCollabs = data.active_collaborations || [];
        setProjects(activeCollabs);
        
        // Si pas de projets, créer des exemples pour démonstration
        if (activeCollabs.length === 0) {
          setProjects([
            {
              project_id: 'demo-1',
              name: 'Backend Connected - ' + data.status,
              description: 'Features: ' + Object.keys(data.features || {}).join(', '),
              project_type: 'ai_matching',
              status: 'active' as const,
              created_by: 'system',
              creators: ['Backend', 'Active'],
              created_at: new Date().toISOString(),
              progress: 100,
            }
          ]);
        }
      }
    } catch (error) {
      console.error('Error fetching projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchProjectDetails = async (projectId: string) => {
    await Promise.all([
      fetchMembers(projectId),
      fetchMessages(projectId),
      fetchFiles(projectId),
      fetchPresence(projectId),
    ]);
  };

  const fetchMembers = async (projectId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/collaboration/projects/${projectId}/members`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setMembers(data.members || []);
      }
    } catch (error) {
      console.error('Error fetching members:', error);
    }
  };

  const fetchMessages = async (projectId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/collaboration/projects/${projectId}/messages`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setMessages(data.messages || []);
      }
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  const fetchFiles = async (projectId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/collaboration/projects/${projectId}/files`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setFiles(data.files || []);
      }
    } catch (error) {
      console.error('Error fetching files:', error);
    }
  };

  const fetchPresence = async (projectId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/collaboration/projects/${projectId}/presence`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setPresences(data.presences || []);
      }
    } catch (error) {
      console.error('Error fetching presence:', error);
    }
  };

  const createProject = async () => {
    try {
      const response = await fetch('http://localhost:8000/collaboration/projects/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          name: projectName,
          description: projectDescription,
          project_type: projectType,
        }),
      });
      
      if (response.ok) {
        setShowCreateModal(false);
        setProjectName('');
        setProjectDescription('');
        await fetchProjects();
      }
    } catch (error) {
      console.error('Error creating project:', error);
    }
  };

  const sendMessage = async () => {
    if (!activeProject || !newMessage.trim()) return;

    try {
      const response = await fetch(`http://localhost:8000/collaboration/projects/${activeProject.project_id}/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ message: newMessage }),
      });
      
      if (response.ok) {
        setNewMessage('');
        await fetchMessages(activeProject.project_id);
      }
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const uploadFile = async (file: File) => {
    if (!activeProject) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`http://localhost:8000/collaboration/projects/${activeProject.project_id}/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: formData,
      });
      
      if (response.ok) {
        await fetchFiles(activeProject.project_id);
      }
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  const projectTypes = ['video', 'music', 'podcast', 'design', 'marketing', 'research'];

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-teal-50 flex items-center justify-center">
        <Loader2 className="h-12 w-12 animate-spin text-green-600" />
      </div>
    );
  }

  if (activeProject) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-teal-50">
        {/* Header */}
        <div className="bg-white shadow-md border-b sticky top-0 z-10">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <button 
                  onClick={() => setActiveProject(null)}
                  className="text-gray-600 hover:text-green-600 transition"
                >
                  <ArrowLeft className="h-5 w-5" />
                </button>
                <Folder className="h-8 w-8 text-green-600" />
                <div>
                  <h2 className="text-xl font-bold text-gray-900">{activeProject.name}</h2>
                  <p className="text-sm text-gray-500">{members.length} members • {presences.filter(p => p.last_activity).length} online</p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                {/* Online Indicators */}
                <div className="flex -space-x-2">
                  {presences.slice(0, 5).map((presence) => (
                    <div
                      key={presence.user_id}
                      className="w-8 h-8 bg-gradient-to-br from-green-400 to-teal-500 rounded-full flex items-center justify-center text-white font-bold text-sm border-2 border-white relative"
                      title={presence.username}
                    >
                      {presence.username.charAt(0).toUpperCase()}
                      <div className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-green-500 rounded-full border-2 border-white"></div>
                    </div>
                  ))}
                </div>
                <button className="px-4 py-2 bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-lg hover:shadow-lg transition">
                  <UserPlus className="h-4 w-4 inline-block mr-2" />
                  Invite
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Content */}
            <div className="lg:col-span-2 space-y-6">
              {/* Progress Card */}
              <div className="bg-gradient-to-r from-green-500 to-teal-500 rounded-xl shadow-lg p-6 text-white">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <div className="text-sm opacity-90">Project Progress</div>
                    <div className="text-3xl font-bold">{activeProject.progress}%</div>
                  </div>
                  <CheckCircle className="h-12 w-12 opacity-80" />
                </div>
                <div className="w-full bg-white bg-opacity-30 rounded-full h-3">
                  <div
                    className="bg-white h-3 rounded-full transition-all"
                    style={{ width: `${activeProject.progress}%` }}
                  />
                </div>
              </div>

              {/* Tabs */}
              <div className="bg-white rounded-xl shadow-lg overflow-hidden">
                <div className="flex border-b">
                  <button
                    onClick={() => setSelectedTab('chat')}
                    className={`flex-1 py-4 px-6 font-semibold transition ${
                      selectedTab === 'chat'
                        ? 'bg-green-50 text-green-600 border-b-2 border-green-600'
                        : 'text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    <MessageSquare className="h-5 w-5 inline-block mr-2" />
                    Chat
                  </button>
                  <button
                    onClick={() => setSelectedTab('files')}
                    className={`flex-1 py-4 px-6 font-semibold transition ${
                      selectedTab === 'files'
                        ? 'bg-green-50 text-green-600 border-b-2 border-green-600'
                        : 'text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    <FileText className="h-5 w-5 inline-block mr-2" />
                    Files
                  </button>
                  <button
                    onClick={() => setSelectedTab('members')}
                    className={`flex-1 py-4 px-6 font-semibold transition ${
                      selectedTab === 'members'
                        ? 'bg-green-50 text-green-600 border-b-2 border-green-600'
                        : 'text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    <Users className="h-5 w-5 inline-block mr-2" />
                    Members
                  </button>
                </div>

                <div className="p-6">
                  {/* Chat Tab */}
                  {selectedTab === 'chat' && (
                    <div>
                      <div className="h-96 overflow-y-auto mb-4 space-y-3">
                        {messages.map((msg) => (
                          <div key={msg.message_id} className="bg-gray-50 rounded-lg p-4">
                            <div className="flex items-center space-x-2 mb-2">
                              <span className="font-semibold text-sm text-gray-900">{msg.sender_name}</span>
                              <span className="text-xs text-gray-500">
                                {new Date(msg.timestamp).toLocaleTimeString()}
                              </span>
                            </div>
                            <p className="text-sm text-gray-700">{msg.message}</p>
                          </div>
                        ))}
                        <div ref={chatEndRef} />
                      </div>
                      <div className="flex space-x-2">
                        <input
                          type="text"
                          value={newMessage}
                          onChange={(e) => setNewMessage(e.target.value)}
                          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                          placeholder="Type a message..."
                          className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                        />
                        <button
                          onClick={sendMessage}
                          className="px-6 py-3 bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-lg hover:shadow-lg transition"
                        >
                          Send
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Files Tab */}
                  {selectedTab === 'files' && (
                    <div>
                      <div className="mb-4">
                        <label className="block w-full px-6 py-4 border-2 border-dashed border-gray-300 rounded-lg text-center cursor-pointer hover:border-green-500 transition">
                          <Upload className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                          <span className="text-sm text-gray-600">Click to upload or drag and drop</span>
                          <input
                            type="file"
                            className="hidden"
                            onChange={(e) => e.target.files?.[0] && uploadFile(e.target.files[0])}
                          />
                        </label>
                      </div>
                      <div className="space-y-2">
                        {files.map((file) => (
                          <div key={file.file_id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition">
                            <div className="flex items-center space-x-3">
                              <FileText className="h-8 w-8 text-green-600" />
                              <div>
                                <div className="font-semibold text-sm text-gray-900">{file.name}</div>
                                <div className="text-xs text-gray-500">
                                  {(file.size / 1024).toFixed(2)} KB • {file.uploaded_by}
                                </div>
                              </div>
                            </div>
                            <button className="text-green-600 hover:text-green-700">
                              <Download className="h-5 w-5" />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Members Tab */}
                  {selectedTab === 'members' && (
                    <div className="space-y-3">
                      {members.map((member) => (
                        <div key={member.user_id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                          <div className="flex items-center space-x-3">
                            <div className="relative">
                              <div className="w-10 h-10 bg-gradient-to-br from-green-400 to-teal-500 rounded-full flex items-center justify-center text-white font-bold">
                                {member.username.charAt(0).toUpperCase()}
                              </div>
                              {member.is_online && (
                                <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></div>
                              )}
                            </div>
                            <div>
                              <div className="font-semibold text-sm text-gray-900">{member.username}</div>
                              <div className="text-xs text-gray-500">{member.role} • {member.contributions} contributions</div>
                            </div>
                          </div>
                          <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                            member.is_online ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                          }`}>
                            {member.is_online ? 'Online' : 'Offline'}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Project Info */}
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="font-bold text-gray-900 mb-4">Project Details</h3>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Type:</span>
                    <span className="font-semibold text-gray-900">{activeProject.project_type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Status:</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                      activeProject.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                    }`}>
                      {activeProject.status}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Created:</span>
                    <span className="font-semibold text-gray-900">
                      {new Date(activeProject.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>

              {/* Activity Feed */}
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="font-bold text-gray-900 mb-4 flex items-center">
                  <Clock className="h-5 w-5 mr-2 text-green-600" />
                  Recent Activity
                </h3>
                <div className="space-y-3 text-sm">
                  {messages.slice(-5).map((msg) => (
                    <div key={msg.message_id} className="flex items-start space-x-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full mt-1.5"></div>
                      <div>
                        <div className="text-gray-900">{msg.sender_name} sent a message</div>
                        <div className="text-xs text-gray-500">{new Date(msg.timestamp).toLocaleTimeString()}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-teal-50">
      {/* Header */}
      <div className="bg-white shadow-md border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/" className="text-gray-600 hover:text-green-600 transition">
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <Users className="h-8 w-8 text-green-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Collaboration Hub</h1>
                <p className="text-sm text-gray-500">Real-time collaboration • Shared workspace • Team chat</p>
              </div>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-xl hover:shadow-lg transition"
            >
              <UserPlus className="h-5 w-5" />
              <span>New Project</span>
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Projects Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <div key={project.project_id} className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition cursor-pointer"
                 onClick={() => setActiveProject(project)}>
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-gray-900 mb-2">{project.name}</h3>
                  <p className="text-sm text-gray-600 mb-3">{project.description}</p>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                      project.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                    }`}>
                      {project.status}
                    </span>
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-semibold">
                      {project.project_type}
                    </span>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t">
                <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                  <span>Progress</span>
                  <span className="font-semibold">{project.progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-green-600 to-teal-600 h-2 rounded-full transition-all"
                    style={{ width: `${project.progress}%` }}
                  />
                </div>
                <div className="flex items-center justify-between mt-3 text-xs text-gray-500">
                  <span className="flex items-center">
                    <Users className="h-4 w-4 mr-1" />
                    {project.creators.length} members
                  </span>
                  <span>{new Date(project.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Create Project Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-2xl p-8 max-w-md w-full mx-4">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Create Collaboration Project</h2>
            
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Project Name</label>
                <input
                  type="text"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="Enter project name"
                />
              </div>
              
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Description</label>
                <textarea
                  value={projectDescription}
                  onChange={(e) => setProjectDescription(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  rows={3}
                  placeholder="Describe your project"
                />
              </div>
              
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Project Type</label>
                <select
                  value={projectType}
                  onChange={(e) => setProjectType(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  {projectTypes.map((type) => (
                    <option key={type} value={type}>
                      {type.charAt(0).toUpperCase() + type.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="flex space-x-4">
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
              >
                Cancel
              </button>
              <button
                onClick={createProject}
                disabled={!projectName.trim()}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-lg hover:shadow-lg transition disabled:opacity-50"
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
