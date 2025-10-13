/**
 * Analytics Panel - Tableaux de bord et statistiques
 * Interface avec graphiques et tendances d'apprentissage
 */
import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Award, Clock, Download, RefreshCw, Loader2 } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';

interface AnalyticsStats {
  total_quizzes_completed: number;
  average_score: number;
  total_time_spent: number;
  improvement_rate: number;
  current_streak: number;
}

interface SubjectPerformance {
  subject: string;
  quizzes_completed: number;
  average_score: number;
  improvement: number;
}

interface QuizHistory {
  quiz_id: string;
  quiz_title: string;
  score: number;
  total_points: number;
  completed_at: string;
  time_spent: number;
}

const AnalyticsPanel: React.FC = () => {
  const [stats, setStats] = useState<AnalyticsStats | null>(null);
  const [subjectPerformance, setSubjectPerformance] = useState<SubjectPerformance[]>([]);
  const [quizHistory, setQuizHistory] = useState<QuizHistory[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [timeRange, setTimeRange] = useState('30days');

  useEffect(() => {
    fetchAnalytics();
  }, [timeRange]);

  const fetchAnalytics = async () => {
    setIsLoading(true);
    try {
      // Fetch overall stats
      const statsResponse = await fetch(`http://localhost:8002/eduverify/analytics/stats?time_range=${timeRange}`);
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats(statsData);
      }

      // Fetch subject performance
      const subjectsResponse = await fetch(`http://localhost:8002/eduverify/analytics/subjects?time_range=${timeRange}`);
      if (subjectsResponse.ok) {
        const subjectsData = await subjectsResponse.json();
        setSubjectPerformance(subjectsData.subjects || []);
      }

      // Fetch quiz history
      const historyResponse = await fetch(`http://localhost:8002/eduverify/analytics/history?limit=10`);
      if (historyResponse.ok) {
        const historyData = await historyResponse.json();
        setQuizHistory(historyData.history || []);
      }
    } catch (err) {
      console.error('Failed to fetch analytics:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const exportData = () => {
    const data = {
      stats,
      subjectPerformance,
      quizHistory,
      exported_at: new Date().toISOString(),
    };
    
    const dataStr = JSON.stringify(data, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `analytics_${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const formatTime = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}h ${mins}min` : `${mins}min`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">Analytics</h2>
          <p className="text-gray-600 dark:text-gray-400">Suivez vos progrès et performances</p>
        </div>
        <div className="flex items-center space-x-2">
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-[180px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7days">7 derniers jours</SelectItem>
              <SelectItem value="30days">30 derniers jours</SelectItem>
              <SelectItem value="90days">90 derniers jours</SelectItem>
              <SelectItem value="all">Tout le temps</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" size="icon" onClick={fetchAnalytics} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
          <Button variant="outline" size="icon" onClick={exportData}>
            <Download className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-12 w-12 text-blue-600 animate-spin" />
        </div>
      ) : (
        <>
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="shadow-xl bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 border-blue-200">
              <CardHeader>
                <CardTitle className="text-blue-900 dark:text-blue-100 text-sm flex items-center space-x-2">
                  <BarChart3 className="h-4 w-4" />
                  <span>Quiz Complétés</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-blue-900 dark:text-blue-100">
                  {stats?.total_quizzes_completed || 0}
                </div>
                <p className="text-xs text-blue-700 dark:text-blue-300 mt-1">
                  Total depuis le début
                </p>
              </CardContent>
            </Card>

            <Card className="shadow-xl bg-gradient-to-br from-green-50 to-teal-50 dark:from-green-900/20 dark:to-teal-900/20 border-green-200">
              <CardHeader>
                <CardTitle className="text-green-900 dark:text-green-100 text-sm flex items-center space-x-2">
                  <Award className="h-4 w-4" />
                  <span>Score Moyen</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-900 dark:text-green-100">
                  {stats?.average_score?.toFixed(1) || 0}%
                </div>
                <Progress value={stats?.average_score || 0} className="mt-2 h-2" />
              </CardContent>
            </Card>

            <Card className="shadow-xl bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border-purple-200">
              <CardHeader>
                <CardTitle className="text-purple-900 dark:text-purple-100 text-sm flex items-center space-x-2">
                  <TrendingUp className="h-4 w-4" />
                  <span>Amélioration</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-purple-900 dark:text-purple-100">
                  +{stats?.improvement_rate?.toFixed(1) || 0}%
                </div>
                <p className="text-xs text-purple-700 dark:text-purple-300 mt-1">
                  Progression sur la période
                </p>
              </CardContent>
            </Card>

            <Card className="shadow-xl bg-gradient-to-br from-orange-50 to-yellow-50 dark:from-orange-900/20 dark:to-yellow-900/20 border-orange-200">
              <CardHeader>
                <CardTitle className="text-orange-900 dark:text-orange-100 text-sm flex items-center space-x-2">
                  <Clock className="h-4 w-4" />
                  <span>Temps Total</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-orange-900 dark:text-orange-100">
                  {formatTime(stats?.total_time_spent || 0)}
                </div>
                <p className="text-xs text-orange-700 dark:text-orange-300 mt-1">
                  Temps d'apprentissage
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Performance by Subject */}
          <Card className="shadow-xl">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BarChart3 className="h-6 w-6 text-purple-600" />
                <span>Performance par Matière</span>
              </CardTitle>
              <CardDescription>
                Scores moyens et nombre de quiz complétés
              </CardDescription>
            </CardHeader>
            <CardContent>
              {subjectPerformance.length === 0 ? (
                <p className="text-gray-600 text-center py-8">
                  Aucune donnée disponible pour cette période
                </p>
              ) : (
                <div className="space-y-4">
                  {subjectPerformance.map((subject, index) => (
                    <div key={index} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-semibold text-gray-900 dark:text-white">
                            {subject.subject}
                          </h4>
                          <p className="text-xs text-gray-600">
                            {subject.quizzes_completed} quiz complété{subject.quizzes_completed > 1 ? 's' : ''}
                          </p>
                        </div>
                        <div className="flex items-center space-x-3">
                          <Badge
                            variant="outline"
                            className={
                              subject.improvement >= 0
                                ? 'border-green-500 text-green-700'
                                : 'border-red-500 text-red-700'
                            }
                          >
                            {subject.improvement >= 0 ? '+' : ''}{subject.improvement.toFixed(1)}%
                          </Badge>
                          <span className="text-lg font-bold text-gray-900 dark:text-white">
                            {subject.average_score.toFixed(1)}%
                          </span>
                        </div>
                      </div>
                      <Progress value={subject.average_score} className="h-2" />
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Quiz History */}
          <Card className="shadow-xl">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Clock className="h-6 w-6 text-blue-600" />
                <span>Historique des Quiz</span>
              </CardTitle>
              <CardDescription>
                Derniers quiz complétés
              </CardDescription>
            </CardHeader>
            <CardContent>
              {quizHistory.length === 0 ? (
                <p className="text-gray-600 text-center py-8">
                  Aucun quiz complété
                </p>
              ) : (
                <div className="space-y-3">
                  {quizHistory.map((quiz) => (
                    <Card key={quiz.quiz_id} className="border-l-4 border-l-blue-500">
                      <CardContent className="pt-4">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <h4 className="font-semibold text-gray-900 dark:text-white">
                              {quiz.quiz_title}
                            </h4>
                            <div className="flex items-center space-x-4 mt-1 text-xs text-gray-600">
                              <span>
                                {new Date(quiz.completed_at).toLocaleDateString('fr-FR', {
                                  day: '2-digit',
                                  month: 'short',
                                  year: 'numeric',
                                })}
                              </span>
                              <span>⏱️ {formatTime(quiz.time_spent)}</span>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-2xl font-bold text-gray-900 dark:text-white">
                              {quiz.score}/{quiz.total_points}
                            </div>
                            <Badge
                              variant="outline"
                              className={
                                (quiz.score / quiz.total_points) * 100 >= 60
                                  ? 'border-green-500 text-green-700'
                                  : 'border-red-500 text-red-700'
                              }
                            >
                              {((quiz.score / quiz.total_points) * 100).toFixed(0)}%
                            </Badge>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Streak Card */}
          {stats && stats.current_streak > 0 && (
            <Card className="shadow-xl bg-gradient-to-r from-yellow-100 to-orange-100 dark:from-yellow-900/20 dark:to-orange-900/20 border-yellow-300">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-xl font-bold text-yellow-900 dark:text-yellow-100">
                      🔥 Série en cours!
                    </h3>
                    <p className="text-yellow-800 dark:text-yellow-200 mt-1">
                      Continuez comme ça pour maintenir votre série
                    </p>
                  </div>
                  <div className="text-6xl font-bold text-yellow-900 dark:text-yellow-100">
                    {stats.current_streak}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
};

export default AnalyticsPanel;
