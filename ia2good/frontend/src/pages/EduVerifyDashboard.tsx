/**
 * EduVerify Dashboard - Page principale
 * Interface complète pour la plateforme éducative IA
 */
import React, { useState, useEffect } from 'react';
import { 
  BookOpen, Brain, CheckCircle, MessageSquare, 
  Upload, BarChart3, Sparkles, Globe, ShieldCheck 
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import ContentUploadPanel from './eduverify/ContentUploadPanel';
import QuizGeneratorPanel from './eduverify/QuizGeneratorPanel';
import FactCheckingPanel from './eduverify/FactCheckingPanel';
import ChatroomPanel from './eduverify/ChatroomPanel';
import AnalyticsPanel from './eduverify/AnalyticsPanel';

interface DashboardStats {
  totalContent: number;
  quizzesGenerated: number;
  factChecksPerformed: number;
  activeChatrooms: number;
  languagesSupported: number;
  averageAccuracy: number;
}

const EduVerifyDashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalContent: 0,
    quizzesGenerated: 0,
    factChecksPerformed: 0,
    activeChatrooms: 0,
    languagesSupported: 100,
    averageAccuracy: 92.5
  });

  const [activeTab, setActiveTab] = useState('dashboard');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const response = await fetch('http://localhost:8002/eduverify/analytics/dashboard');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-blue-900 dark:to-indigo-900">
      {/* Header */}
      <header className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="bg-gradient-to-br from-blue-600 to-indigo-600 p-3 rounded-xl shadow-lg">
                <Brain className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  EduVerify
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-300">
                  Plateforme Éducative IA Avancée
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <Badge variant="outline" className="flex items-center space-x-2">
                <Globe className="h-4 w-4" />
                <span>{stats.languagesSupported}+ Langues</span>
              </Badge>
              <Badge variant="outline" className="flex items-center space-x-2">
                <ShieldCheck className="h-4 w-4" />
                <span>{stats.averageAccuracy}% Précision</span>
              </Badge>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          {/* Tab Navigation */}
          <TabsList className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md p-2 rounded-xl shadow-lg">
            <TabsTrigger value="dashboard" className="flex items-center space-x-2">
              <BarChart3 className="h-4 w-4" />
              <span>Tableau de bord</span>
            </TabsTrigger>
            <TabsTrigger value="upload" className="flex items-center space-x-2">
              <Upload className="h-4 w-4" />
              <span>Upload Contenu</span>
            </TabsTrigger>
            <TabsTrigger value="quiz" className="flex items-center space-x-2">
              <Sparkles className="h-4 w-4" />
              <span>Génération Quiz</span>
            </TabsTrigger>
            <TabsTrigger value="factcheck" className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4" />
              <span>Fact-Checking</span>
            </TabsTrigger>
            <TabsTrigger value="chatroom" className="flex items-center space-x-2">
              <MessageSquare className="h-4 w-4" />
              <span>Chatroom</span>
            </TabsTrigger>
            <TabsTrigger value="analytics" className="flex items-center space-x-2">
              <BarChart3 className="h-4 w-4" />
              <span>Analytics</span>
            </TabsTrigger>
          </TabsList>

          {/* Dashboard Overview */}
          <TabsContent value="dashboard" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white border-0 shadow-xl">
                <CardHeader className="pb-2">
                  <CardTitle className="flex items-center justify-between">
                    <span>Contenu Uploadé</span>
                    <BookOpen className="h-5 w-5 opacity-80" />
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-4xl font-bold">{stats.totalContent}</div>
                  <p className="text-blue-100 text-sm mt-2">PDF, Vidéos, Audio, Texte</p>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white border-0 shadow-xl">
                <CardHeader className="pb-2">
                  <CardTitle className="flex items-center justify-between">
                    <span>Quiz Générés</span>
                    <Sparkles className="h-5 w-5 opacity-80" />
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-4xl font-bold">{stats.quizzesGenerated}</div>
                  <p className="text-purple-100 text-sm mt-2">Par IA (GPT-4, Claude)</p>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white border-0 shadow-xl">
                <CardHeader className="pb-2">
                  <CardTitle className="flex items-center justify-between">
                    <span>Fact-Checks</span>
                    <CheckCircle className="h-5 w-5 opacity-80" />
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-4xl font-bold">{stats.factChecksPerformed}</div>
                  <p className="text-green-100 text-sm mt-2">{stats.averageAccuracy}% Précision</p>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-orange-500 to-orange-600 text-white border-0 shadow-xl">
                <CardHeader className="pb-2">
                  <CardTitle className="flex items-center justify-between">
                    <span>Chatrooms Actifs</span>
                    <MessageSquare className="h-5 w-5 opacity-80" />
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-4xl font-bold">{stats.activeChatrooms}</div>
                  <p className="text-orange-100 text-sm mt-2">Avec accessibilité</p>
                </CardContent>
              </Card>
            </div>

            {/* Features Overview */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="shadow-xl">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Brain className="h-5 w-5 text-blue-600" />
                    <span>Fonctionnalités IA</span>
                  </CardTitle>
                  <CardDescription>
                    Capacités d'intelligence artificielle avancées
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-start space-x-3">
                    <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                    <div>
                      <p className="font-semibold">Génération de Quiz Intelligente</p>
                      <p className="text-sm text-gray-600">Questions adaptatives par GPT-4/Claude</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                    <div>
                      <p className="font-semibold">Fact-Checking Temps Réel</p>
                      <p className="text-sm text-gray-600">Vérification avec sources multiples</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                    <div>
                      <p className="font-semibold">Support 100+ Langues</p>
                      <p className="text-sm text-gray-600">Avec détection de dialectes</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="shadow-xl">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Globe className="h-5 w-5 text-purple-600" />
                    <span>Accessibilité Universelle</span>
                  </CardTitle>
                  <CardDescription>
                    Pour tous, sans exception
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-start space-x-3">
                    <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                    <div>
                      <p className="font-semibold">Pour Aveugles</p>
                      <p className="text-sm text-gray-600">TTS, Screen readers, Audio descriptions</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                    <div>
                      <p className="font-semibold">Pour Sourds</p>
                      <p className="text-sm text-gray-600">Captions auto, Alertes visuelles, Transcriptions</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                    <div>
                      <p className="font-semibold">Orchestrateur Central</p>
                      <p className="text-sm text-gray-600">Coordination des services d'accessibilité</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Content Upload Tab */}
          <TabsContent value="upload">
            <ContentUploadPanel />
          </TabsContent>

          {/* Quiz Generator Tab */}
          <TabsContent value="quiz">
            <QuizGeneratorPanel />
          </TabsContent>

          {/* Fact-Checking Tab */}
          <TabsContent value="factcheck">
            <FactCheckingPanel />
          </TabsContent>

          {/* Chatroom Tab */}
          <TabsContent value="chatroom">
            <ChatroomPanel />
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics">
            <AnalyticsPanel />
          </TabsContent>
        </Tabs>
      </main>

      {/* Footer */}
      <footer className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md border-t border-gray-200 dark:border-gray-700 mt-12">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600 dark:text-gray-300">
              © 2025 EduVerify - Plateforme Éducative IA by Fahed Mlaiel
            </p>
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <span>Backend: Port 8002</span>
              <span>•</span>
              <span>PostgreSQL</span>
              <span>•</span>
              <span>WebSocket Ready</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default EduVerifyDashboard;
