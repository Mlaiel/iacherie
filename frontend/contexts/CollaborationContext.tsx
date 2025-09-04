/**
 * Collaboration Context - Team collaboration context
 */

import { createContext, useContext, ReactNode, useState } from 'react';

interface TeamMember {
  id: string;
  name: string;
  email: string;
  role: 'owner' | 'admin' | 'member' | 'viewer';
  status: 'active' | 'pending' | 'inactive';
}

interface Project {
  id: string;
  name: string;
  description: string;
  members: string[];
  status: 'active' | 'completed' | 'paused';
}

interface CollaborationContextType {
  team: TeamMember[];
  projects: Project[];
  inviteMember: (email: string, role: TeamMember['role']) => void;
  updateMemberRole: (id: string, role: TeamMember['role']) => void;
  removeMember: (id: string) => void;
  createProject: (project: Omit<Project, 'id'>) => void;
  updateProject: (id: string, updates: Partial<Project>) => void;
}

const CollaborationContext = createContext<CollaborationContextType | undefined>(undefined);

export function CollaborationProvider({ children }: { children: ReactNode }) {
  const [team, setTeam] = useState<TeamMember[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);

  const inviteMember = (email: string, role: TeamMember['role']) => {
    const newMember: TeamMember = {
      id: `member_${Date.now()}`,
      name: email.split('@')[0],
      email,
      role,
      status: 'pending',
    };
    setTeam(prev => [...prev, newMember]);
  };

  const updateMemberRole = (id: string, role: TeamMember['role']) => {
    setTeam(prev => prev.map(member =>
      member.id === id ? { ...member, role } : member
    ));
  };

  const removeMember = (id: string) => {
    setTeam(prev => prev.filter(member => member.id !== id));
  };

  const createProject = (project: Omit<Project, 'id'>) => {
    const newProject: Project = {
      ...project,
      id: `project_${Date.now()}`,
    };
    setProjects(prev => [...prev, newProject]);
  };

  const updateProject = (id: string, updates: Partial<Project>) => {
    setProjects(prev => prev.map(project =>
      project.id === id ? { ...project, ...updates } : project
    ));
  };

  return (
    <CollaborationContext.Provider value={{
      team,
      projects,
      inviteMember,
      updateMemberRole,
      removeMember,
      createProject,
      updateProject,
    }}>
      {children}
    </CollaborationContext.Provider>
  );
}

export const useCollaboration = () => {
  const context = useContext(CollaborationContext);
  if (!context) {
    throw new Error('useCollaboration must be used within a CollaborationProvider');
  }
  return context;
};
