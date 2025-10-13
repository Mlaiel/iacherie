/**
 * Unified Navigation Component
 * Navigation across all 4 modules: IA2GOOD, Guardian, EduVerify, MedCare
 */
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Heart,
  Shield,
  GraduationCap,
  Stethoscope,
  User,
  Bell,
  Settings,
  Search,
  Menu,
  X
} from 'lucide-react';

interface UnifiedNavigationProps {
  activeModule: 'ia2good' | 'guardian' | 'eduverify' | 'medcare';
  onModuleChange: (module: string) => void;
  notifications?: number;
}

const modules = [
  {
    id: 'ia2good',
    name: 'IA2GOOD',
    icon: Heart,
    color: 'text-blue-600 bg-blue-100',
    description: 'Solidarity & Volunteering'
  },
  {
    id: 'guardian',
    name: 'Guardian',
    icon: Shield,
    color: 'text-green-600 bg-green-100',
    description: 'Emergency SOS & Safety'
  },
  {
    id: 'eduverify',
    name: 'EduVerify',
    icon: GraduationCap,
    color: 'text-purple-600 bg-purple-100',
    description: 'Education & Fact-Checking'
  },
  {
    id: 'medcare',
    name: 'MedCare',
    icon: Stethoscope,
    color: 'text-red-600 bg-red-100',
    description: 'Telemedicine & Diagnosis'
  }
];

export function UnifiedNavigation({ activeModule, onModuleChange, notifications = 0 }: UnifiedNavigationProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <>
      {/* Top Navigation Bar */}
      <div className="bg-white shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center space-x-2">
              <Heart className="h-8 w-8 text-blue-600" />
              <span className="text-xl font-bold text-gray-900">iAcherie</span>
            </div>

            {/* Desktop Module Navigation */}
            <div className="hidden md:flex space-x-2">
              {modules.map((module) => {
                const Icon = module.icon;
                const isActive = activeModule === module.id;
                
                return (
                  <Button
                    key={module.id}
                    variant={isActive ? "default" : "ghost"}
                    size="sm"
                    onClick={() => onModuleChange(module.id)}
                    className={`flex items-center gap-2 ${!isActive && module.color}`}
                  >
                    <Icon className="h-4 w-4" />
                    <span className="hidden lg:inline">{module.name}</span>
                  </Button>
                );
              })}
            </div>

            {/* Right Actions */}
            <div className="flex items-center space-x-4">
              {/* Global Search */}
              <div className="hidden sm:block">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search across all modules..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm w-64"
                  />
                </div>
              </div>

              {/* Notifications */}
              <Button variant="ghost" size="icon" className="relative">
                <Bell className="h-5 w-5" />
                {notifications > 0 && (
                  <Badge className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-xs">
                    {notifications}
                  </Badge>
                )}
              </Button>

              {/* Profile */}
              <Button variant="ghost" size="icon">
                <User className="h-5 w-5" />
              </Button>

              {/* Settings */}
              <Button variant="ghost" size="icon">
                <Settings className="h-5 w-5" />
              </Button>

              {/* Mobile Menu Toggle */}
              <Button
                variant="ghost"
                size="icon"
                className="md:hidden"
                onClick={() => setIsMenuOpen(!isMenuOpen)}
              >
                {isMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <div className="md:hidden bg-white border-b shadow-lg">
          <div className="px-4 py-4 space-y-2">
            {modules.map((module) => {
              const Icon = module.icon;
              const isActive = activeModule === module.id;
              
              return (
                <button
                  key={module.id}
                  onClick={() => {
                    onModuleChange(module.id);
                    setIsMenuOpen(false);
                  }}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive 
                      ? 'bg-blue-50 text-blue-600 font-medium' 
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <div className="text-left">
                    <div className="font-medium">{module.name}</div>
                    <div className="text-xs text-gray-500">{module.description}</div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </>
  );
}
