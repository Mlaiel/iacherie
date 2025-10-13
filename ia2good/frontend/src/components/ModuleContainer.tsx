/**
 * Module Container Component
 * Wraps individual module content with common layout
 */
import { ReactNode } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { LucideIcon } from 'lucide-react';

interface ModuleContainerProps {
  moduleId: string;
  moduleName: string;
  moduleIcon: LucideIcon;
  moduleColor: string;
  children: ReactNode;
}

export function ModuleContainer({
  moduleId,
  moduleName,
  moduleIcon: Icon,
  moduleColor,
  children
}: ModuleContainerProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Module Header */}
      <div className={`${moduleColor} py-6`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="h-12 w-12 rounded-lg bg-white/20 backdrop-blur-sm flex items-center justify-center">
              <Icon className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">{moduleName}</h1>
              <Badge className="mt-1 bg-white/20 text-white border-white/30">
                Active Module
              </Badge>
            </div>
          </div>
        </div>
      </div>

      {/* Module Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {children}
      </div>
    </div>
  );
}
