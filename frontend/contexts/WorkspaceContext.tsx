/**
 * Workspace Context - Workspace and layout management context
 */

import { createContext, useContext, ReactNode, useState } from 'react';

interface Panel {
  id: string;
  type: 'content' | 'properties' | 'timeline' | 'effects';
  position: 'left' | 'right' | 'bottom';
  isVisible: boolean;
  width?: number;
  height?: number;
}

interface WorkspaceContextType {
  panels: Panel[];
  layout: 'default' | 'fullscreen' | 'minimal';
  togglePanel: (id: string) => void;
  resizePanel: (id: string, dimensions: { width?: number; height?: number }) => void;
  setLayout: (layout: 'default' | 'fullscreen' | 'minimal') => void;
  resetLayout: () => void;
}

const defaultPanels: Panel[] = [
  { id: 'content', type: 'content', position: 'left', isVisible: true, width: 300 },
  { id: 'properties', type: 'properties', position: 'right', isVisible: true, width: 250 },
  { id: 'timeline', type: 'timeline', position: 'bottom', isVisible: true, height: 200 },
];

const WorkspaceContext = createContext<WorkspaceContextType | undefined>(undefined);

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const [panels, setPanels] = useState<Panel[]>(defaultPanels);
  const [layout, setLayoutState] = useState<'default' | 'fullscreen' | 'minimal'>('default');

  const togglePanel = (id: string) => {
    setPanels(prev => prev.map(panel =>
      panel.id === id ? { ...panel, isVisible: !panel.isVisible } : panel
    ));
  };

  const resizePanel = (id: string, dimensions: { width?: number; height?: number }) => {
    setPanels(prev => prev.map(panel =>
      panel.id === id ? { ...panel, ...dimensions } : panel
    ));
  };

  const setLayout = (newLayout: 'default' | 'fullscreen' | 'minimal') => {
    setLayoutState(newLayout);
    
    if (newLayout === 'fullscreen') {
      setPanels(prev => prev.map(panel => ({ ...panel, isVisible: false })));
    } else if (newLayout === 'minimal') {
      setPanels(prev => prev.map(panel => 
        panel.type === 'content' ? { ...panel, isVisible: true } : { ...panel, isVisible: false }
      ));
    }
  };

  const resetLayout = () => {
    setPanels(defaultPanels);
    setLayoutState('default');
  };

  return (
    <WorkspaceContext.Provider value={{
      panels,
      layout,
      togglePanel,
      resizePanel,
      setLayout,
      resetLayout,
    }}>
      {children}
    </WorkspaceContext.Provider>
  );
}

export const useWorkspace = () => {
  const context = useContext(WorkspaceContext);
  if (!context) {
    throw new Error('useWorkspace must be used within a WorkspaceProvider');
  }
  return context;
};
