/**
 * 🎯 LAYOUT PRINCIPAL DASHBOARD
 * Interface de navigation pour tous les 57 modules
 * 
 * @author Fahed Mlaiel - Expert Multi-Role Implementation
 */

'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { 
  Brain,
  BarChart3,
  Globe,
  Shield,
  Database,
  Users,
  DollarSign,
  Cog,
  Search,
  Menu,
  Bell,
  Settings,
  LogOut,
  ChevronDown,
  ChevronRight,
  Activity,
  Zap,
  Network,
  HardDrive,
  Cpu,
  Server,
  Cloud,
  Lock,
  Smartphone,
  Monitor,
  Headphones,
  Image,
  Video,
  FileText,
  TrendingUp,
  MessageSquare,
  Calendar,
  MapPin,
  Star,
  Briefcase,
  GamepadIcon,
  Palette,
  Languages,
  Eye,
  Code,
  TestTube,
  Wrench,
  AlertCircle
} from 'lucide-react';

interface ModuleConfig {
  id: string;
  name: string;
  path: string;
  icon: React.ReactNode;
  category: string;
  status: 'active' | 'inactive' | 'maintenance' | 'error';
  badge?: string;
  description: string;
  implemented: boolean;
}

// Configuration complète des 57 modules
const MODULE_CATEGORIES = {
  microservices: {
    name: 'Microservices (15)',
    color: 'bg-blue-50 border-blue-200',
    icon: <Server className="w-4 h-4 text-blue-600" />
  },
  'backend-core': {
    name: 'Backend Core (42)',
    color: 'bg-green-50 border-green-200',
    icon: <Database className="w-4 h-4 text-green-600" />
  },
  complementary: {
    name: 'Complémentaires (7)',
    color: 'bg-purple-50 border-purple-200',
    icon: <Wrench className="w-4 h-4 text-purple-600" />
  }
};

const MODULES_CONFIG: ModuleConfig[] = [
  // PHASE 1: MICROSERVICES ARCHITECTURE (15 MODULES)
  {
    id: 'ai-services',
    name: 'AI Services',
    path: '/dashboard/ai-services',
    icon: <Brain className="w-4 h-4" />,
    category: 'microservices',
    status: 'active',
    badge: '53 Agents',
    description: '53 AI Agents + orchestration temps réel',
    implemented: true
  },
  {
    id: 'analytics-services',
    name: 'Analytics Services',
    path: '/dashboard/analytics',
    icon: <BarChart3 className="w-4 h-4" />,
    category: 'microservices',
    status: 'active',
    badge: 'BI',
    description: 'Business Intelligence + métriques temps réel',
    implemented: true
  },
  {
    id: 'api-gateway',
    name: 'API Gateway',
    path: '/dashboard/api-gateway',
    icon: <Globe className="w-4 h-4" />,
    category: 'microservices',
    status: 'inactive',
    badge: '16 Services',
    description: 'Gateway management + rate limiting',
    implemented: true
  },
  {
    id: 'business-services',
    name: 'Business Services',
    path: '/dashboard/business',
    icon: <Briefcase className="w-4 h-4" />,
    category: 'microservices',
    status: 'inactive',
    description: 'Business logic + workflow automation',
    implemented: false
  },
  {
    id: 'communication-services',
    name: 'Communication',
    path: '/dashboard/communication',
    icon: <MessageSquare className="w-4 h-4" />,
    category: 'microservices',
    status: 'inactive',
    description: 'Event streaming + notifications',
    implemented: false
  },
  {
    id: 'content-services',
    name: 'Content Services',
    path: '/dashboard/content',
    icon: <FileText className="w-4 h-4" />,
    category: 'microservices',
    status: 'inactive',
    description: 'Content processing + optimization',
    implemented: false
  },
  {
    id: 'data-services',
    name: 'Data Services',
    path: '/dashboard/data',
    icon: <Database className="w-4 h-4" />,
    category: 'microservices',
    status: 'inactive',
    description: 'ETL Pipeline + Data Warehouse',
    implemented: false
  },
  {
    id: 'financial-services',
    name: 'Financial Services',
    path: '/dashboard/financial',
    icon: <DollarSign className="w-4 h-4" />,
    category: 'microservices',
    status: 'inactive',
    description: 'Payment processing + billing',
    implemented: false
  },
  {
    id: 'infrastructure-services',
    name: 'Infrastructure',
    path: '/dashboard/infrastructure',
    icon: <Server className="w-4 h-4" />,
    category: 'microservices',
    status: 'inactive',
    description: 'System health + scaling controls',
    implemented: false
  },
  {
    id: 'platform-services',
    name: 'Platform Services',
    path: '/dashboard/platforms',
    icon: <Network className="w-4 h-4" />,
    category: 'microservices',
    status: 'inactive',
    badge: '65+ Platforms',
    description: '65+ platforms integration hub',
    implemented: false
  },
  {
    id: 'security-services',
    name: 'Security Services',
    path: '/dashboard/security',
    icon: <Shield className="w-4 h-4" />,
    category: 'microservices',
    status: 'inactive',
    description: 'Zero Trust + compliance monitoring',
    implemented: false
  },
  {
    id: 'seo-services',
    name: 'SEO Services',
    path: '/dashboard/seo',
    icon: <TrendingUp className="w-4 h-4" />,
    category: 'microservices',
    status: 'inactive',
    description: 'SEO automation + optimization',
    implemented: false
  },
  {
    id: 'service-mesh',
    name: 'Service Mesh',
    path: '/dashboard/service-mesh',
    icon: <Network className="w-4 h-4" />,
    category: 'microservices',
    status: 'inactive',
    description: 'Istio/Linkerd management',
    implemented: false
  },
  {
    id: 'testing-services',
    name: 'Testing Services',
    path: '/dashboard/testing',
    icon: <TestTube className="w-4 h-4" />,
    category: 'microservices',
    status: 'inactive',
    description: 'Automated testing + QA',
    implemented: false
  },
  {
    id: 'marketing-services',
    name: 'Marketing Services',
    path: '/dashboard/marketing',
    icon: <TrendingUp className="w-4 h-4" />,
    category: 'microservices',
    status: 'inactive',
    description: 'Campaign management + analytics',
    implemented: false
  },

  // PHASE 2: BACKEND CORE MODULES (42 MODULES) - Échantillon
  {
    id: 'core-infrastructure',
    name: 'Core Infrastructure',
    path: '/dashboard/core-infrastructure',
    icon: <Cpu className="w-4 h-4" />,
    category: 'backend-core',
    status: 'inactive',
    description: 'System architecture overview',
    implemented: false
  },
  {
    id: 'database-management',
    name: 'Database Management',
    path: '/dashboard/database',
    icon: <HardDrive className="w-4 h-4" />,
    category: 'backend-core',
    status: 'inactive',
    description: 'Database operations center',
    implemented: false
  },
  {
    id: 'ai-intelligence-core',
    name: 'AI Intelligence Core',
    path: '/dashboard/ai-core',
    icon: <Brain className="w-4 h-4" />,
    category: 'backend-core',
    status: 'inactive',
    badge: '53 Agents',
    description: '53 AI Agents status + orchestration',
    implemented: false
  },
  {
    id: 'ai-model-management',
    name: 'AI Model Management',
    path: '/dashboard/ai-models',
    icon: <Brain className="w-4 h-4" />,
    category: 'backend-core',
    status: 'inactive',
    description: 'Model lifecycle management',
    implemented: false
  },
  {
    id: 'prompt-engineering',
    name: 'Prompt Engineering',
    path: '/dashboard/prompts',
    icon: <Code className="w-4 h-4" />,
    category: 'backend-core',
    status: 'inactive',
    description: 'Prompt engineering studio',
    implemented: false
  },
  {
    id: 'advanced-audio-processing',
    name: 'Audio Processing',
    path: '/dashboard/audio',
    icon: <Headphones className="w-4 h-4" />,
    category: 'backend-core',
    status: 'inactive',
    description: 'Audio production studio',
    implemented: false
  },
  {
    id: 'media-processing-storage',
    name: 'Media Processing',
    path: '/dashboard/media',
    icon: <Image className="w-4 h-4" />,
    category: 'backend-core',
    status: 'inactive',
    description: 'Media management center',
    implemented: false
  },
  {
    id: 'advanced-media-processing',
    name: 'Advanced Media',
    path: '/dashboard/advanced-media',
    icon: <Video className="w-4 h-4" />,
    category: 'backend-core',
    status: 'inactive',
    description: 'Advanced media studio',
    implemented: false
  },
  {
    id: 'multi-platform-distribution',
    name: 'Multi-Platform Distribution',
    path: '/dashboard/distribution',
    icon: <Network className="w-4 h-4" />,
    category: 'backend-core',
    status: 'inactive',
    description: 'Distribution network control',
    implemented: false
  },
  {
    id: 'business-intelligence',
    name: 'Business Intelligence',
    path: '/dashboard/business-intelligence',
    icon: <BarChart3 className="w-4 h-4" />,
    category: 'backend-core',
    status: 'inactive',
    description: 'BI analytics center',
    implemented: false
  },
  {
    id: 'system-monitoring',
    name: 'System Monitoring',
    path: '/dashboard/monitoring',
    icon: <Activity className="w-4 h-4" />,
    category: 'backend-core',
    status: 'inactive',
    description: 'System health monitor',
    implemented: false
  },
  {
    id: 'mobile-api-services',
    name: 'Mobile API',
    path: '/dashboard/mobile',
    icon: <Smartphone className="w-4 h-4" />,
    category: 'backend-core',
    status: 'inactive',
    description: 'Mobile services console',
    implemented: false
  },
  {
    id: 'web-services',
    name: 'Web Services',
    path: '/dashboard/web',
    icon: <Monitor className="w-4 h-4" />,
    category: 'backend-core',
    status: 'inactive',
    description: 'Web services hub',
    implemented: false
  },
  {
    id: 'creator-marketplace',
    name: 'Creator Marketplace',
    path: '/dashboard/marketplace',
    icon: <Users className="w-4 h-4" />,
    category: 'backend-core',
    status: 'inactive',
    description: 'Marketplace console',
    implemented: false
  },
  {
    id: 'multi-language-support',
    name: 'Multi-Language',
    path: '/dashboard/languages',
    icon: <Languages className="w-4 h-4" />,
    category: 'backend-core',
    status: 'inactive',
    description: 'Localization center',
    implemented: false
  },
  {
    id: 'ai-avatar-generation',
    name: 'AI Avatar Generation',
    path: '/dashboard/avatars',
    icon: <Palette className="w-4 h-4" />,
    category: 'backend-core',
    status: 'inactive',
    description: 'Avatar creation studio',
    implemented: false
  },

  // PHASE 3: MODULES COMPLÉMENTAIRES (7 MODULES)
  {
    id: 'templates-documentation',
    name: 'Templates & Docs',
    path: '/dashboard/templates',
    icon: <FileText className="w-4 h-4" />,
    category: 'complementary',
    status: 'inactive',
    description: 'Template management',
    implemented: false
  },
  {
    id: 'testing-framework',
    name: 'Testing Framework',
    path: '/dashboard/test-framework',
    icon: <TestTube className="w-4 h-4" />,
    category: 'complementary',
    status: 'inactive',
    description: 'Testing console',
    implemented: false
  },
  {
    id: 'automation-scripts',
    name: 'Automation Scripts',
    path: '/dashboard/automation',
    icon: <Zap className="w-4 h-4" />,
    category: 'complementary',
    status: 'inactive',
    description: 'Automation hub',
    implemented: false
  },
  {
    id: 'business-workflows',
    name: 'Business Workflows',
    path: '/dashboard/workflows',
    icon: <Calendar className="w-4 h-4" />,
    category: 'complementary',
    status: 'inactive',
    description: 'Workflow management',
    implemented: false
  },
  {
    id: 'validation-systems',
    name: 'Validation Systems',
    path: '/dashboard/validation',
    icon: <Eye className="w-4 h-4" />,
    category: 'complementary',
    status: 'inactive',
    description: 'Validation console',
    implemented: false
  },
  {
    id: 'reporting-engine',
    name: 'Reporting Engine',
    path: '/dashboard/reports',
    icon: <BarChart3 className="w-4 h-4" />,
    category: 'complementary',
    status: 'inactive',
    description: 'Reports center',
    implemented: false
  },
  {
    id: 'utility-functions',
    name: 'Utility Functions',
    path: '/dashboard/utils',
    icon: <Wrench className="w-4 h-4" />,
    category: 'complementary',
    status: 'inactive',
    description: 'Utilities panel',
    implemented: false
  }
];

interface DashboardLayoutProps {
  children: React.ReactNode;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedCategories, setExpandedCategories] = useState<Record<string, boolean>>({
    microservices: true,
    'backend-core': false,
    complementary: false
  });

  const pathname = usePathname();

  // Filtrage des modules
  const filteredModules = MODULES_CONFIG.filter(module =>
    module.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    module.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Groupement par catégorie
  const modulesByCategory = filteredModules.reduce((acc, module) => {
    if (!acc[module.category]) {
      acc[module.category] = [];
    }
    acc[module.category].push(module);
    return acc;
  }, {} as Record<string, ModuleConfig[]>);

  // Stats globales
  const totalModules = MODULES_CONFIG.length;
  const implementedModules = MODULES_CONFIG.filter(m => m.implemented).length;
  const activeModules = MODULES_CONFIG.filter(m => m.status === 'active').length;

  const toggleCategory = (category: string) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <div className="w-2 h-2 rounded-full bg-green-500" />;
      case 'inactive':
        return <div className="w-2 h-2 rounded-full bg-gray-400" />;
      case 'maintenance':
        return <div className="w-2 h-2 rounded-full bg-yellow-500" />;
      case 'error':
        return <div className="w-2 h-2 rounded-full bg-red-500" />;
      default:
        return <div className="w-2 h-2 rounded-full bg-gray-300" />;
    }
  };

  const SidebarContent = () => (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b">
        <h2 className="text-lg font-semibold text-gray-900">
          Dashboard Enterprise
        </h2>
        <p className="text-sm text-gray-600">57 Modules Intégrés</p>
      </div>

      {/* Stats rapides */}
      <div className="p-4 border-b">
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Implémentés:</span>
            <Badge variant="secondary">{implementedModules}/{totalModules}</Badge>
          </div>
          <div className="flex justify-between text-sm">
            <span>Actifs:</span>
            <Badge variant="default">{activeModules}</Badge>
          </div>
        </div>
      </div>

      {/* Recherche */}
      <div className="p-4 border-b">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            placeholder="Rechercher un module..."
            value={searchTerm}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Navigation des modules */}
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {Object.entries(modulesByCategory).map(([category, modules]) => {
            const categoryConfig = MODULE_CATEGORIES[category as keyof typeof MODULE_CATEGORIES];
            const isExpanded = expandedCategories[category];

            return (
              <div key={category} className="space-y-2">
                <Button
                  variant="ghost"
                  onClick={() => toggleCategory(category)}
                  className="w-full justify-between p-2 h-auto"
                >
                  <div className="flex items-center space-x-2">
                    {categoryConfig.icon}
                    <span className="text-sm font-medium">
                      {categoryConfig.name}
                    </span>
                  </div>
                  {isExpanded ? (
                    <ChevronDown className="w-4 h-4" />
                  ) : (
                    <ChevronRight className="w-4 h-4" />
                  )}
                </Button>

                {isExpanded && (
                  <div className="ml-2 space-y-1">
                    {modules.map((module) => {
                      const isActive = pathname === module.path;
                      const isImplemented = module.implemented;

                      return (
                        <div key={module.id} className="relative">
                          {isImplemented ? (
                            <Link href={module.path}>
                              <Button
                                variant={isActive ? "default" : "ghost"}
                                className={`w-full justify-start p-2 h-auto text-left ${
                                  !isImplemented && 'opacity-50 cursor-not-allowed'
                                }`}
                                disabled={!isImplemented}
                              >
                                <div className="flex items-center space-x-3 w-full">
                                  <div className="flex items-center space-x-2">
                                    {getStatusIcon(module.status)}
                                    {module.icon}
                                  </div>
                                  <div className="flex-1 min-w-0">
                                    <div className="flex items-center space-x-2">
                                      <span className="text-sm font-medium truncate">
                                        {module.name}
                                      </span>
                                      {module.badge && (
                                        <Badge variant="secondary" className="text-xs">
                                          {module.badge}
                                        </Badge>
                                      )}
                                    </div>
                                    <p className="text-xs text-gray-500 truncate">
                                      {module.description}
                                    </p>
                                  </div>
                                </div>
                              </Button>
                            </Link>
                          ) : (
                            <div className="w-full p-2 rounded-md border border-dashed border-gray-300 opacity-50">
                              <div className="flex items-center space-x-3">
                                <div className="flex items-center space-x-2">
                                  {getStatusIcon(module.status)}
                                  {module.icon}
                                </div>
                                <div className="flex-1 min-w-0">
                                  <div className="flex items-center space-x-2">
                                    <span className="text-sm font-medium text-gray-600 truncate">
                                      {module.name}
                                    </span>
                                    <Badge variant="outline" className="text-xs">
                                      À Implémenter
                                    </Badge>
                                  </div>
                                  <p className="text-xs text-gray-400 truncate">
                                    {module.description}
                                  </p>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </ScrollArea>

      {/* Footer */}
      <div className="p-4 border-t">
        <div className="flex items-center justify-between">
          <Button variant="ghost" size="sm">
            <Settings className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Bell className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <LogOut className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar Desktop */}
      {sidebarOpen && (
        <div className="hidden lg:flex lg:w-80 lg:flex-col lg:fixed lg:inset-y-0 bg-white border-r">
          <SidebarContent />
        </div>
      )}

      {/* Sidebar Mobile */}
      <Sheet>
        <SheetTrigger>
          <Button variant="ghost" size="sm" className="lg:hidden fixed top-4 left-4 z-50">
            <Menu className="w-5 h-5" />
          </Button>
        </SheetTrigger>
        <SheetContent className="w-80 p-0">
          <SidebarContent />
        </SheetContent>
      </Sheet>

      {/* Main Content */}
      <div className={`flex-1 ${sidebarOpen ? 'lg:pl-80' : ''}`}>
        <div className="flex flex-col h-full">
          {/* Top Bar */}
          <div className="bg-white border-b px-4 py-3 flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="hidden lg:flex"
              >
                <Menu className="w-5 h-5" />
              </Button>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">
                  Enterprise Dashboard
                </h1>
                <p className="text-sm text-gray-600">
                  Plateforme AInfluencer - 57 Modules Intégrés
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <Button variant="outline" size="sm">
                <AlertCircle className="w-4 h-4 mr-2" />
                Status
              </Button>
              <Button size="sm">
                <Activity className="w-4 h-4 mr-2" />
                Monitoring
              </Button>
            </div>
          </div>

          {/* Page Content */}
          <div className="flex-1 overflow-auto">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardLayout;