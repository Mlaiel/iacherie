/**
 * Protection Context - Content protection management context
 */

import { createContext, useContext, ReactNode, useState } from 'react';

interface ProtectionRule {
  id: string;
  name: string;
  type: 'fingerprint' | 'watermark' | 'drm';
  status: 'active' | 'inactive';
}

interface Violation {
  id: string;
  contentId: string;
  platform: string;
  severity: 'low' | 'medium' | 'high';
  status: 'detected' | 'reported' | 'resolved';
  timestamp: string;
}

interface ProtectionContextType {
  rules: ProtectionRule[];
  violations: Violation[];
  isLoading: boolean;
  addRule: (rule: Omit<ProtectionRule, 'id'>) => void;
  updateRule: (id: string, updates: Partial<ProtectionRule>) => void;
  deleteRule: (id: string) => void;
  reportViolation: (violation: Omit<Violation, 'id' | 'timestamp'>) => void;
}

const ProtectionContext = createContext<ProtectionContextType | undefined>(undefined);

export function ProtectionProvider({ children }: { children: ReactNode }) {
  const [rules, setRules] = useState<ProtectionRule[]>([]);
  const [violations, setViolations] = useState<Violation[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const addRule = (rule: Omit<ProtectionRule, 'id'>) => {
    const newRule: ProtectionRule = {
      ...rule,
      id: `rule_${Date.now()}`,
    };
    setRules(prev => [...prev, newRule]);
  };

  const updateRule = (id: string, updates: Partial<ProtectionRule>) => {
    setRules(prev => prev.map(rule =>
      rule.id === id ? { ...rule, ...updates } : rule
    ));
  };

  const deleteRule = (id: string) => {
    setRules(prev => prev.filter(rule => rule.id !== id));
  };

  const reportViolation = (violation: Omit<Violation, 'id' | 'timestamp'>) => {
    const newViolation: Violation = {
      ...violation,
      id: `violation_${Date.now()}`,
      timestamp: new Date().toISOString(),
    };
    setViolations(prev => [newViolation, ...prev]);
  };

  return (
    <ProtectionContext.Provider value={{
      rules,
      violations,
      isLoading,
      addRule,
      updateRule,
      deleteRule,
      reportViolation,
    }}>
      {children}
    </ProtectionContext.Provider>
  );
}

export const useProtection = () => {
  const context = useContext(ProtectionContext);
  if (!context) {
    throw new Error('useProtection must be used within a ProtectionProvider');
  }
  return context;
};
