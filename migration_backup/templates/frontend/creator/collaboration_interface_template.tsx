/**
 * 🤝 Collaboration Interface Template - Enterprise Component
 * =========================================================
 * 
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS
 * 
 * @author Fahed Mlaiel
 * @role Lead Dev IA + Backend Senior + Creator Economy Expert + Collaboration Architect
 * @description Enterprise collaboration interface with real-time communication,
 *              project management, revenue sharing, and multi-format content creation
 */

import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import styled, { ThemeProvider, keyframes } from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';

// ===========================
// 🎨 STYLED COMPONENTS & ANIMATIONS
// ===========================

const pulseAnimation = keyframes`
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
`;

const slideIn = keyframes`
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
`;

const CollaborationContainer = styled(motion.div)`
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
  padding: 24px;
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  min-height: 100vh;
  color: white;
`;

const Header = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid rgba(255, 255, 255, 0.2);
`;

const ProjectTitle = styled.h1`
  font-size: 28px;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(135deg, #60a5fa, #a78bfa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const ProjectStatus = styled.div<{ status: string }>`
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  
  ${props => {
    switch (props.status) {
      case 'active':
        return 'background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3);';
      case 'planning':
        return 'background: rgba(251, 191, 36, 0.2); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.3);';
      case 'review':
        return 'background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3);';
      default:
        return 'background: rgba(148, 163, 184, 0.2); color: #94a3b8; border: 1px solid rgba(148, 163, 184, 0.3);';
    }
  }}
`;

const MainGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 350px;
  gap: 24px;
  
  @media (max-width: 1200px) {
    grid-template-columns: 1fr;
  }
`;

const ContentArea = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const TabNavigation = styled.div`
  display: flex;
  gap: 8px;
  background: rgba(255, 255, 255, 0.05);
  padding: 8px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const Tab = styled.button<{ active?: boolean }>`
  padding: 12px 20px;
  border: none;
  border-radius: 12px;
  background: ${props => props.active ? 'rgba(96, 165, 250, 0.2)' : 'transparent'};
  color: ${props => props.active ? '#60a5fa' : '#94a3b8'};
  font-weight: ${props => props.active ? '600' : '400'};
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  
  &:hover {
    background: rgba(96, 165, 250, 0.1);
    color: #60a5fa;
  }
`;

const TabContent = styled(motion.div)`
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 32px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  min-height: 600px;
`;

const CollaboratorsList = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
`;

const CollaboratorCard = styled(motion.div)`
  background: rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.12);
    transform: translateY(-2px);
  }
`;

const CollaboratorHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
`;

const Avatar = styled.img`
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(96, 165, 250, 0.3);
`;

const CollaboratorInfo = styled.div`
  flex: 1;
`;

const CollaboratorName = styled.h3`
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 4px 0;
  color: white;
`;

const CollaboratorRole = styled.div`
  font-size: 14px;
  color: #94a3b8;
`;

const OnlineStatus = styled.div<{ online?: boolean }>`
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: ${props => props.online ? '#4ade80' : '#64748b'};
  animation: ${props => props.online ? pulseAnimation : 'none'} 2s infinite;
`;

const TasksList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const TaskItem = styled(motion.div)<{ priority?: 'low' | 'medium' | 'high' }>`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 16px;
  border-left: 4px solid ${props => {
    switch (props.priority) {
      case 'high': return '#ef4444';
      case 'medium': return '#f59e0b';
      default: return '#22c55e';
    }
  }};
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }
`;

const TaskHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
`;

const TaskTitle = styled.h4`
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: white;
`;

const TaskMeta = styled.div`
  font-size: 12px;
  color: #94a3b8;
`;

const TaskDescription = styled.p`
  font-size: 14px;
  color: #cbd5e1;
  margin: 0 0 12px 0;
  line-height: 1.5;
`;

const TaskProgress = styled.div`
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
`;

const TaskProgressBar = styled.div<{ progress: number }>`
  height: 100%;
  width: ${props => props.progress}%;
  background: linear-gradient(90deg, #60a5fa, #a78bfa);
  transition: width 0.3s ease;
`;

const Sidebar = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const SidebarSection = styled.div`
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const SectionTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 16px 0;
  color: white;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ChatArea = styled.div`
  height: 400px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-right: 8px;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(96, 165, 250, 0.3);
    border-radius: 3px;
  }
`;

const ChatMessage = styled(motion.div)<{ own?: boolean }>`
  display: flex;
  flex-direction: column;
  align-items: ${props => props.own ? 'flex-end' : 'flex-start'};
  max-width: 80%;
  align-self: ${props => props.own ? 'flex-end' : 'flex-start'};
`;

const MessageBubble = styled.div<{ own?: boolean }>`
  background: ${props => props.own 
    ? 'linear-gradient(135deg, #60a5fa, #a78bfa)' 
    : 'rgba(255, 255, 255, 0.1)'};
  padding: 12px 16px;
  border-radius: 16px;
  border-bottom-${props => props.own ? 'right' : 'left'}-radius: 4px;
  font-size: 14px;
  line-height: 1.5;
  word-wrap: break-word;
`;

const MessageMeta = styled.div`
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
  padding: 0 4px;
`;

const ChatInput = styled.div`
  display: flex;
  gap: 12px;
  margin-top: 16px;
`;

const Input = styled.input`
  flex: 1;
  padding: 12px 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  color: white;
  font-size: 14px;
  
  &::placeholder {
    color: #94a3b8;
  }
  
  &:focus {
    outline: none;
    border-color: #60a5fa;
    background: rgba(255, 255, 255, 0.08);
  }
`;

const SendButton = styled(motion.button)`
  padding: 12px 16px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #60a5fa, #a78bfa);
  color: white;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  
  &:hover {
    transform: translateY(-1px);
  }
`;

const FileUploadArea = styled.div`
  border: 2px dashed rgba(96, 165, 250, 0.3);
  border-radius: 16px;
  padding: 32px;
  text-align: center;
  background: rgba(96, 165, 250, 0.05);
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: rgba(96, 165, 250, 0.5);
    background: rgba(96, 165, 250, 0.1);
  }
`;

const RevenueChart = styled.div`
  height: 200px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  font-size: 16px;
  margin-bottom: 16px;
`;

const RevenueMetrics = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const MetricItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
`;

const MetricLabel = styled.span`
  color: #94a3b8;
  font-size: 14px;
`;

const MetricValue = styled.span`
  font-weight: 600;
  color: #60a5fa;
  font-size: 16px;
`;

// ===========================
// 🎯 INTERFACES & TYPES
// ===========================

interface Collaborator {
  id: string;
  name: string;
  avatar: string;
  role: string;
  isOnline: boolean;
  lastSeen?: Date;
  skills: string[];
  revenueShare: number;
}

interface Task {
  id: string;
  title: string;
  description: string;
  assignedTo: string;
  priority: 'low' | 'medium' | 'high';
  progress: number;
  dueDate: Date;
  status: 'todo' | 'inprogress' | 'review' | 'done';
}

interface ChatMessage {
  id: string;
  senderId: string;
  senderName: string;
  content: string;
  timestamp: Date;
  type: 'text' | 'file' | 'image';
  fileUrl?: string;
}

interface Project {
  id: string;
  title: string;
  description: string;
  status: 'planning' | 'active' | 'review' | 'completed';
  startDate: Date;
  deadline: Date;
  budget: number;
  currentRevenue: number;
  collaborators: Collaborator[];
  tasks: Task[];
  files: File[];
}

interface RevenueData {
  totalRevenue: number;
  projectedRevenue: number;
  revenueShares: { [collaboratorId: string]: number };
  expenses: number;
}

interface CollaborationInterfaceProps {
  project: Project;
  currentUserId: string;
  onTaskUpdate?: (taskId: string, updates: Partial<Task>) => void;
  onMessageSend?: (message: string) => void;
  onFileUpload?: (files: FileList) => void;
  onRevenueUpdate?: (updates: Partial<RevenueData>) => void;
  theme?: any;
}

// ===========================
// 🚀 MAIN COMPONENT
// ===========================

export const CollaborationInterfaceTemplate: React.FC<CollaborationInterfaceProps> = ({
  project,
  currentUserId,
  onTaskUpdate,
  onMessageSend,
  onFileUpload,
  onRevenueUpdate,
  theme = defaultTheme
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'tasks' | 'files' | 'revenue'>('overview');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Sample chat messages
  useEffect(() => {
    setChatMessages([
      {
        id: '1',
        senderId: 'user1',
        senderName: 'Alex',
        content: 'Hey everyone! Just uploaded the latest video draft.',
        timestamp: new Date(Date.now() - 3600000),
        type: 'text'
      },
      {
        id: '2',
        senderId: currentUserId,
        senderName: 'You',
        content: 'Looks great! I\'ll review it now.',
        timestamp: new Date(Date.now() - 1800000),
        type: 'text'
      },
      {
        id: '3',
        senderId: 'user2',
        senderName: 'Sarah',
        content: 'The audio quality is excellent this time!',
        timestamp: new Date(Date.now() - 900000),
        type: 'text'
      }
    ]);
  }, [currentUserId]);

  // Auto-scroll chat to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  // Handle send message
  const handleSendMessage = useCallback(() => {
    if (newMessage.trim()) {
      const message: ChatMessage = {
        id: Date.now().toString(),
        senderId: currentUserId,
        senderName: 'You',
        content: newMessage,
        timestamp: new Date(),
        type: 'text'
      };
      setChatMessages(prev => [...prev, message]);
      setNewMessage('');
      onMessageSend?.(newMessage);
    }
  }, [newMessage, currentUserId, onMessageSend]);

  // Handle task progress update
  const handleTaskClick = useCallback((task: Task) => {
    const newProgress = Math.min(task.progress + 25, 100);
    onTaskUpdate?.(task.id, { progress: newProgress });
  }, [onTaskUpdate]);

  // Format currency
  const formatCurrency = useCallback((amount: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  }, []);

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring",
        stiffness: 100
      }
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CollaborationContainer
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Header */}
        <motion.div variants={itemVariants}>
          <Header>
            <div>
              <ProjectTitle>{project.title}</ProjectTitle>
              <div style={{ fontSize: '14px', color: '#94a3b8', marginTop: '4px' }}>
                {project.collaborators.length} collaborators • {project.tasks.length} tasks
              </div>
            </div>
            <ProjectStatus status={project.status}>
              {project.status}
            </ProjectStatus>
          </Header>
        </motion.div>

        <MainGrid>
          {/* Main Content Area */}
          <ContentArea>
            <motion.div variants={itemVariants}>
              <TabNavigation>
                <Tab
                  active={activeTab === 'overview'}
                  onClick={() => setActiveTab('overview')}
                >
                  📊 Overview
                </Tab>
                <Tab
                  active={activeTab === 'tasks'}
                  onClick={() => setActiveTab('tasks')}
                >
                  ✅ Tasks
                </Tab>
                <Tab
                  active={activeTab === 'files'}
                  onClick={() => setActiveTab('files')}
                >
                  📁 Files
                </Tab>
                <Tab
                  active={activeTab === 'revenue'}
                  onClick={() => setActiveTab('revenue')}
                >
                  💰 Revenue
                </Tab>
              </TabNavigation>
            </motion.div>

            <motion.div variants={itemVariants}>
              <TabContent>
                <AnimatePresence mode="wait">
                  {activeTab === 'overview' && (
                    <motion.div
                      key="overview"
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -20 }}
                    >
                      <h2 style={{ margin: '0 0 24px 0', color: 'white' }}>
                        Project Collaborators
                      </h2>
                      <CollaboratorsList>
                        {project.collaborators.map((collaborator, index) => (
                          <CollaboratorCard
                            key={collaborator.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                          >
                            <CollaboratorHeader>
                              <Avatar src={collaborator.avatar} alt={collaborator.name} />
                              <CollaboratorInfo>
                                <CollaboratorName>{collaborator.name}</CollaboratorName>
                                <CollaboratorRole>{collaborator.role}</CollaboratorRole>
                              </CollaboratorInfo>
                              <OnlineStatus online={collaborator.isOnline} />
                            </CollaboratorHeader>
                            <div style={{ fontSize: '14px', color: '#cbd5e1' }}>
                              Revenue Share: {collaborator.revenueShare}%
                            </div>
                            <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '8px' }}>
                              Skills: {collaborator.skills.join(', ')}
                            </div>
                          </CollaboratorCard>
                        ))}
                      </CollaboratorsList>
                    </motion.div>
                  )}

                  {activeTab === 'tasks' && (
                    <motion.div
                      key="tasks"
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -20 }}
                    >
                      <h2 style={{ margin: '0 0 24px 0', color: 'white' }}>
                        Project Tasks
                      </h2>
                      <TasksList>
                        {project.tasks.map((task, index) => (
                          <TaskItem
                            key={task.id}
                            priority={task.priority}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                            onClick={() => handleTaskClick(task)}
                          >
                            <TaskHeader>
                              <TaskTitle>{task.title}</TaskTitle>
                              <TaskMeta>
                                {task.progress}% • {task.priority}
                              </TaskMeta>
                            </TaskHeader>
                            <TaskDescription>{task.description}</TaskDescription>
                            <TaskProgress>
                              <TaskProgressBar progress={task.progress} />
                            </TaskProgress>
                          </TaskItem>
                        ))}
                      </TasksList>
                    </motion.div>
                  )}

                  {activeTab === 'files' && (
                    <motion.div
                      key="files"
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -20 }}
                    >
                      <h2 style={{ margin: '0 0 24px 0', color: 'white' }}>
                        Project Files
                      </h2>
                      <FileUploadArea>
                        <div style={{ fontSize: '48px', marginBottom: '16px' }}>📁</div>
                        <div style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>
                          Drop files here or click to upload
                        </div>
                        <div style={{ color: '#94a3b8', fontSize: '14px' }}>
                          Support for images, videos, audio, and documents
                        </div>
                      </FileUploadArea>
                    </motion.div>
                  )}

                  {activeTab === 'revenue' && (
                    <motion.div
                      key="revenue"
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -20 }}
                    >
                      <h2 style={{ margin: '0 0 24px 0', color: 'white' }}>
                        Revenue Overview
                      </h2>
                      <RevenueChart>
                        📈 Revenue Analytics Chart
                      </RevenueChart>
                      <RevenueMetrics>
                        <MetricItem>
                          <MetricLabel>Current Revenue</MetricLabel>
                          <MetricValue>{formatCurrency(project.currentRevenue)}</MetricValue>
                        </MetricItem>
                        <MetricItem>
                          <MetricLabel>Project Budget</MetricLabel>
                          <MetricValue>{formatCurrency(project.budget)}</MetricValue>
                        </MetricItem>
                        <MetricItem>
                          <MetricLabel>Completion</MetricLabel>
                          <MetricValue>
                            {Math.round((project.currentRevenue / project.budget) * 100)}%
                          </MetricValue>
                        </MetricItem>
                      </RevenueMetrics>
                    </motion.div>
                  )}
                </AnimatePresence>
              </TabContent>
            </motion.div>
          </ContentArea>

          {/* Sidebar */}
          <motion.div variants={itemVariants}>
            <Sidebar>
              {/* Real-time Chat */}
              <SidebarSection>
                <SectionTitle>💬 Team Chat</SectionTitle>
                <ChatArea>
                  {chatMessages.map((message) => (
                    <ChatMessage
                      key={message.id}
                      own={message.senderId === currentUserId}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                    >
                      <MessageBubble own={message.senderId === currentUserId}>
                        {message.content}
                      </MessageBubble>
                      <MessageMeta>
                        {message.senderName} • {message.timestamp.toLocaleTimeString()}
                      </MessageMeta>
                    </ChatMessage>
                  ))}
                  <div ref={chatEndRef} />
                </ChatArea>
                <ChatInput>
                  <Input
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Type a message..."
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  />
                  <SendButton
                    onClick={handleSendMessage}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    Send
                  </SendButton>
                </ChatInput>
              </SidebarSection>

              {/* Quick Stats */}
              <SidebarSection>
                <SectionTitle>📊 Quick Stats</SectionTitle>
                <RevenueMetrics>
                  <MetricItem>
                    <MetricLabel>Tasks Completed</MetricLabel>
                    <MetricValue>
                      {project.tasks.filter(t => t.status === 'done').length}/{project.tasks.length}
                    </MetricValue>
                  </MetricItem>
                  <MetricItem>
                    <MetricLabel>Active Collaborators</MetricLabel>
                    <MetricValue>
                      {project.collaborators.filter(c => c.isOnline).length}
                    </MetricValue>
                  </MetricItem>
                  <MetricItem>
                    <MetricLabel>Project Progress</MetricLabel>
                    <MetricValue>
                      {Math.round(
                        project.tasks.reduce((acc, task) => acc + task.progress, 0) / project.tasks.length
                      )}%
                    </MetricValue>
                  </MetricItem>
                </RevenueMetrics>
              </SidebarSection>
            </Sidebar>
          </motion.div>
        </MainGrid>
      </CollaborationContainer>
    </ThemeProvider>
  );
};

// ===========================
// 🎨 DEFAULT THEME
// ===========================

const defaultTheme = {
  colors: {
    primary: '#60a5fa',
    secondary: '#a78bfa',
    background: '#1e293b',
    surface: 'rgba(255, 255, 255, 0.05)',
    text: '#ffffff',
    textSecondary: '#94a3b8',
    success: '#4ade80',
    warning: '#fbbf24',
    error: '#ef4444',
    online: '#4ade80',
  },
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px',
  },
  borderRadius: {
    sm: '8px',
    md: '12px',
    lg: '16px',
    xl: '20px',
  },
};

// ===========================
// 🧪 USAGE EXAMPLES
// ===========================

export const CollaborationExamples = {
  videoProject: {
    id: '1',
    title: 'Educational Video Series',
    description: 'Creating a comprehensive video series about modern web development',
    status: 'active' as const,
    startDate: new Date('2025-01-01'),
    deadline: new Date('2025-03-01'),
    budget: 50000,
    currentRevenue: 32500,
    collaborators: [
      {
        id: '1',
        name: 'Alex Producer',
        avatar: '/api/placeholder/48/48',
        role: 'Video Producer',
        isOnline: true,
        skills: ['Video Editing', 'Motion Graphics'],
        revenueShare: 40
      },
      {
        id: '2',
        name: 'Sarah Writer',
        avatar: '/api/placeholder/48/48',
        role: 'Content Writer',
        isOnline: false,
        skills: ['Technical Writing', 'Script Writing'],
        revenueShare: 30
      }
    ],
    tasks: [
      {
        id: '1',
        title: 'Script for Episode 1',
        description: 'Write the script for the introduction episode',
        assignedTo: '2',
        priority: 'high' as const,
        progress: 85,
        dueDate: new Date('2025-01-15'),
        status: 'inprogress' as const
      }
    ],
    files: []
  }
};

export default CollaborationInterfaceTemplate;