import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Upload,
  FileText,
  CheckSquare,
  TrendingUp,
  BookOpen,
  Award,
  Clock,
  Target,
} from 'lucide-react';

interface EduVerifyDashboardProps {
  userId: string;
}

interface UserStats {
  totalContent: number;
  totalQuizzes: number;
  averageScore: number;
  factChecksPerformed: number;
  studyStreak: number;
  pointsEarned: number;
}

interface RecentContent {
  id: string;
  title: string;
  subject: string;
  created_at: string;
  processing_status: string;
}

interface RecentQuiz {
  id: string;
  title: string;
  score?: number;
  completed_at?: string;
  status: 'not_started' | 'in_progress' | 'completed';
}

export const EduVerifyDashboard: React.FC<EduVerifyDashboardProps> = ({ userId }) => {
  const [stats, setStats] = useState<UserStats>({
    totalContent: 0,
    totalQuizzes: 0,
    averageScore: 0,
    factChecksPerformed: 0,
    studyStreak: 0,
    pointsEarned: 0,
  });

  const [recentContent, setRecentContent] = useState<RecentContent[]>([]);
  const [recentQuizzes, setRecentQuizzes] = useState<RecentQuiz[]>([]);

  // Mock data - replace with real API calls
  useEffect(() => {
    setStats({
      totalContent: 12,
      totalQuizzes: 8,
      averageScore: 84.5,
      factChecksPerformed: 34,
      studyStreak: 7,
      pointsEarned: 1250,
    });

    setRecentContent([
      {
        id: '1',
        title: 'Cours de Photosynthèse',
        subject: 'Biologie',
        created_at: new Date().toISOString(),
        processing_status: 'completed',
      },
      {
        id: '2',
        title: 'Introduction à la Révolution Française',
        subject: 'Histoire',
        created_at: new Date(Date.now() - 86400000).toISOString(),
        processing_status: 'completed',
      },
    ]);

    setRecentQuizzes([
      {
        id: '1',
        title: 'Quiz: Photosynthèse',
        score: 92,
        completed_at: new Date().toISOString(),
        status: 'completed',
      },
      {
        id: '2',
        title: 'Quiz: Révolution Française',
        status: 'not_started',
      },
    ]);
  }, [userId]);

  return (
    <div className="container mx-auto p-4 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold mb-2">📚 EduVerify Interactive</h1>
          <p className="text-gray-600 text-lg">
            Plateforme éducative IA avec génération de quiz et fact-checking
          </p>
        </div>
        <Badge variant="outline" className="text-lg px-4 py-2">
          <Award className="w-4 h-4 mr-2" />
          {stats.pointsEarned} points
        </Badge>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <FileText className="w-8 h-8 mx-auto mb-2 text-blue-600" />
            <p className="text-2xl font-bold">{stats.totalContent}</p>
            <p className="text-sm text-gray-600">Contenus</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <CheckSquare className="w-8 h-8 mx-auto mb-2 text-green-600" />
            <p className="text-2xl font-bold">{stats.totalQuizzes}</p>
            <p className="text-sm text-gray-600">Quiz</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <Target className="w-8 h-8 mx-auto mb-2 text-purple-600" />
            <p className="text-2xl font-bold">{stats.averageScore}%</p>
            <p className="text-sm text-gray-600">Score moyen</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <TrendingUp className="w-8 h-8 mx-auto mb-2 text-orange-600" />
            <p className="text-2xl font-bold">{stats.factChecksPerformed}</p>
            <p className="text-sm text-gray-600">Fact-checks</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <Clock className="w-8 h-8 mx-auto mb-2 text-red-600" />
            <p className="text-2xl font-bold">{stats.studyStreak}</p>
            <p className="text-sm text-gray-600">Jours consécutifs</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <Award className="w-8 h-8 mx-auto mb-2 text-yellow-600" />
            <p className="text-2xl font-bold">{stats.pointsEarned}</p>
            <p className="text-sm text-gray-600">Points totaux</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Actions */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Actions Rapides</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button className="w-full justify-start" size="lg" asChild>
              <a href="/eduverify/upload">
                <Upload className="w-5 h-5 mr-3" />
                Upload du contenu
              </a>
            </Button>

            <Button className="w-full justify-start" size="lg" variant="outline" asChild>
              <a href="/eduverify/quizzes">
                <CheckSquare className="w-5 h-5 mr-3" />
                Mes quiz
              </a>
            </Button>

            <Button className="w-full justify-start" size="lg" variant="outline" asChild>
              <a href="/eduverify/fact-check">
                <TrendingUp className="w-5 h-5 mr-3" />
                Fact-checking
              </a>
            </Button>

            <Button className="w-full justify-start" size="lg" variant="outline" asChild>
              <a href="/eduverify/analytics">
                <Target className="w-5 h-5 mr-3" />
                Mes progrès
              </a>
            </Button>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Activité Récente</CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="content">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="content">Contenus</TabsTrigger>
                <TabsTrigger value="quizzes">Quiz</TabsTrigger>
              </TabsList>

              <TabsContent value="content" className="space-y-3 mt-4">
                {recentContent.map((content) => (
                  <div
                    key={content.id}
                    className="p-4 border rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-lg">{content.title}</h4>
                        <div className="flex items-center gap-3 mt-1">
                          <Badge variant="outline">{content.subject}</Badge>
                          <span className="text-sm text-gray-500">
                            {new Date(content.created_at).toLocaleDateString('fr-FR')}
                          </span>
                        </div>
                      </div>
                      <Badge
                        variant={
                          content.processing_status === 'completed' ? 'default' : 'secondary'
                        }
                      >
                        {content.processing_status}
                      </Badge>
                    </div>
                  </div>
                ))}

                {recentContent.length === 0 && (
                  <div className="text-center py-12 text-gray-500">
                    <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p>Aucun contenu récent</p>
                    <Button className="mt-4" asChild>
                      <a href="/eduverify/upload">Uploader du contenu</a>
                    </Button>
                  </div>
                )}
              </TabsContent>

              <TabsContent value="quizzes" className="space-y-3 mt-4">
                {recentQuizzes.map((quiz) => (
                  <div
                    key={quiz.id}
                    className="p-4 border rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-lg">{quiz.title}</h4>
                        <div className="flex items-center gap-3 mt-1">
                          {quiz.status === 'completed' && quiz.score !== undefined && (
                            <>
                              <Badge
                                variant={quiz.score >= 60 ? 'default' : 'destructive'}
                              >
                                Score: {quiz.score}%
                              </Badge>
                              <span className="text-sm text-gray-500">
                                {new Date(quiz.completed_at!).toLocaleDateString('fr-FR')}
                              </span>
                            </>
                          )}
                          {quiz.status === 'not_started' && (
                            <Badge variant="outline">Non commencé</Badge>
                          )}
                        </div>
                      </div>
                      <Button
                        size="sm"
                        variant={quiz.status === 'completed' ? 'outline' : 'default'}
                      >
                        {quiz.status === 'completed' ? 'Réviser' : 'Commencer'}
                      </Button>
                    </div>
                  </div>
                ))}

                {recentQuizzes.length === 0 && (
                  <div className="text-center py-12 text-gray-500">
                    <CheckSquare className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p>Aucun quiz disponible</p>
                    <Button className="mt-4" asChild>
                      <a href="/eduverify/upload">Générer un quiz</a>
                    </Button>
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>

      {/* Learning Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="w-6 h-6" />
            Recommandations d'Apprentissage
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 border rounded-lg bg-blue-50">
              <h4 className="font-medium mb-2">📖 Continuez votre lecture</h4>
              <p className="text-sm text-gray-600 mb-3">
                Vous avez bien progressé en Biologie. Essayez ce nouveau cours!
              </p>
              <Button size="sm" variant="outline" className="w-full">
                Voir la suggestion
              </Button>
            </div>

            <div className="p-4 border rounded-lg bg-purple-50">
              <h4 className="font-medium mb-2">🎯 Révisez vos points faibles</h4>
              <p className="text-sm text-gray-600 mb-3">
                Améliorez votre score en Histoire avec des quiz ciblés
              </p>
              <Button size="sm" variant="outline" className="w-full">
                Commencer la révision
              </Button>
            </div>

            <div className="p-4 border rounded-lg bg-green-50">
              <h4 className="font-medium mb-2">🏆 Défi du jour</h4>
              <p className="text-sm text-gray-600 mb-3">
                Complétez 3 quiz aujourd'hui pour gagner 50 points bonus!
              </p>
              <Button size="sm" variant="outline" className="w-full">
                Accepter le défi
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
