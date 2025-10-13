/**
 * Quiz Generator Panel - Génération de quiz par IA
 * Interface avec prévisualisation et personnalisation
 */
import React, { useState, useEffect } from 'react';
import { Sparkles, Brain, CheckCircle2, XCircle, AlertCircle, Loader2, RefreshCw, Download } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Slider } from '@/components/ui/slider';
import { Separator } from '@/components/ui/separator';

interface ContentItem {
  id: string;
  title: string;
  subject?: string;
  topic?: string;
  word_count?: number;
}

interface QuizQuestion {
  question_id: string;
  question_text: string;
  question_type: string;
  options?: string[];
  correct_answer: any;
  explanation?: string;
  points: number;
  difficulty?: string;
}

interface GeneratedQuiz {
  id: string;
  title: string;
  difficulty: string;
  questions: QuizQuestion[];
  total_questions: number;
  total_points: number;
  created_at: string;
}

const QuizGeneratorPanel: React.FC = () => {
  const [contentList, setContentList] = useState<ContentItem[]>([]);
  const [isLoadingContent, setIsLoadingContent] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedQuiz, setGeneratedQuiz] = useState<GeneratedQuiz | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Form data
  const [formData, setFormData] = useState({
    content_id: '',
    title: '',
    description: '',
    difficulty: 'medium',
    total_questions: 10,
    language: 'fr',
    time_limit_minutes: 30,
    passing_score: 60
  });

  useEffect(() => {
    fetchContentList();
  }, []);

  const fetchContentList = async () => {
    setIsLoadingContent(true);
    try {
      const response = await fetch('http://localhost:8002/eduverify/content');
      if (response.ok) {
        const data = await response.json();
        setContentList(data.items || []);
      }
    } catch (err) {
      console.error('Failed to fetch content:', err);
    } finally {
      setIsLoadingContent(false);
    }
  };

  const handleGenerate = async () => {
    setError(null);
    setGeneratedQuiz(null);
    setIsGenerating(true);

    try {
      const response = await fetch('http://localhost:8002/eduverify/quizzes/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Quiz generation failed');
      }

      const result = await response.json();
      setGeneratedQuiz(result);
    } catch (err: any) {
      setError(err.message || 'Une erreur est survenue lors de la génération');
    } finally {
      setIsGenerating(false);
    }
  };

  const downloadQuiz = () => {
    if (!generatedQuiz) return;
    
    const dataStr = JSON.stringify(generatedQuiz, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `quiz_${generatedQuiz.id}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Configuration Panel */}
      <div className="space-y-6">
        <Card className="shadow-xl">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Sparkles className="h-6 w-6 text-purple-600" />
              <span>Générateur de Quiz IA</span>
            </CardTitle>
            <CardDescription>
              Génération automatique par GPT-4, Claude, ou Gemini
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Content Selection */}
            <div className="space-y-2">
              <Label htmlFor="content-select">Contenu Source *</Label>
              {isLoadingContent ? (
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Chargement des contenus...</span>
                </div>
              ) : (
                <Select
                  value={formData.content_id}
                  onValueChange={(value) => {
                    const selected = contentList.find(c => c.id === value);
                    setFormData(prev => ({
                      ...prev,
                      content_id: value,
                      title: prev.title || `Quiz - ${selected?.title || ''}`
                    }));
                  }}
                >
                  <SelectTrigger id="content-select">
                    <SelectValue placeholder="Sélectionner un contenu" />
                  </SelectTrigger>
                  <SelectContent>
                    {contentList.map(content => (
                      <SelectItem key={content.id} value={content.id}>
                        <div className="flex flex-col">
                          <span className="font-semibold">{content.title}</span>
                          {content.subject && (
                            <span className="text-xs text-gray-600">
                              {content.subject} {content.topic && `• ${content.topic}`}
                            </span>
                          )}
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
              {contentList.length === 0 && !isLoadingContent && (
                <p className="text-sm text-gray-600">
                  Aucun contenu disponible. Uploadez d'abord un contenu.
                </p>
              )}
            </div>

            {/* Quiz Title */}
            <div className="space-y-2">
              <Label htmlFor="quiz-title">Titre du Quiz *</Label>
              <Input
                id="quiz-title"
                placeholder="ex: Quiz de Mathématiques - Algèbre"
                value={formData.title}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                required
              />
            </div>

            {/* Quiz Description */}
            <div className="space-y-2">
              <Label htmlFor="quiz-description">Description (optionnel)</Label>
              <Input
                id="quiz-description"
                placeholder="Description courte du quiz"
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              />
            </div>

            <Separator />

            {/* Difficulty */}
            <div className="space-y-3">
              <Label>Difficulté</Label>
              <RadioGroup
                value={formData.difficulty}
                onValueChange={(value) => setFormData(prev => ({ ...prev, difficulty: value }))}
                className="grid grid-cols-4 gap-2"
              >
                <div className="relative">
                  <RadioGroupItem value="easy" id="easy" className="peer sr-only" />
                  <Label
                    htmlFor="easy"
                    className="flex items-center justify-center rounded-md border-2 border-muted bg-transparent p-3 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-green-600 peer-data-[state=checked]:bg-green-50 cursor-pointer"
                  >
                    Facile
                  </Label>
                </div>
                <div className="relative">
                  <RadioGroupItem value="medium" id="medium" className="peer sr-only" />
                  <Label
                    htmlFor="medium"
                    className="flex items-center justify-center rounded-md border-2 border-muted bg-transparent p-3 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-blue-600 peer-data-[state=checked]:bg-blue-50 cursor-pointer"
                  >
                    Moyen
                  </Label>
                </div>
                <div className="relative">
                  <RadioGroupItem value="hard" id="hard" className="peer sr-only" />
                  <Label
                    htmlFor="hard"
                    className="flex items-center justify-center rounded-md border-2 border-muted bg-transparent p-3 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-orange-600 peer-data-[state=checked]:bg-orange-50 cursor-pointer"
                  >
                    Difficile
                  </Label>
                </div>
                <div className="relative">
                  <RadioGroupItem value="mixed" id="mixed" className="peer sr-only" />
                  <Label
                    htmlFor="mixed"
                    className="flex items-center justify-center rounded-md border-2 border-muted bg-transparent p-3 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-purple-600 peer-data-[state=checked]:bg-purple-50 cursor-pointer"
                  >
                    Mixte
                  </Label>
                </div>
              </RadioGroup>
            </div>

            {/* Number of Questions */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label htmlFor="questions-slider">Nombre de Questions</Label>
                <Badge variant="outline">{formData.total_questions}</Badge>
              </div>
              <Slider
                id="questions-slider"
                min={5}
                max={50}
                step={5}
                value={[formData.total_questions]}
                onValueChange={(value) => setFormData(prev => ({ ...prev, total_questions: value[0] }))}
                className="w-full"
              />
              <p className="text-xs text-gray-600">Minimum: 5 • Maximum: 50</p>
            </div>

            {/* Time Limit */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="time-limit">Temps (minutes)</Label>
                <Input
                  id="time-limit"
                  type="number"
                  min={5}
                  max={180}
                  value={formData.time_limit_minutes}
                  onChange={(e) => setFormData(prev => ({ ...prev, time_limit_minutes: parseInt(e.target.value) }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="passing-score">Score de Passage (%)</Label>
                <Input
                  id="passing-score"
                  type="number"
                  min={0}
                  max={100}
                  value={formData.passing_score}
                  onChange={(e) => setFormData(prev => ({ ...prev, passing_score: parseInt(e.target.value) }))}
                />
              </div>
            </div>

            {/* Language */}
            <div className="space-y-2">
              <Label htmlFor="language">Langue</Label>
              <Select
                value={formData.language}
                onValueChange={(value) => setFormData(prev => ({ ...prev, language: value }))}
              >
                <SelectTrigger id="language">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="fr">Français</SelectItem>
                  <SelectItem value="en">English</SelectItem>
                  <SelectItem value="es">Español</SelectItem>
                  <SelectItem value="ar">العربية</SelectItem>
                  <SelectItem value="de">Deutsch</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Error Alert */}
            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Generate Button */}
            <Button
              onClick={handleGenerate}
              disabled={isGenerating || !formData.content_id || !formData.title}
              className="w-full"
              size="lg"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                  Génération en cours...
                </>
              ) : (
                <>
                  <Brain className="h-5 w-5 mr-2" />
                  Générer le Quiz avec IA
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* AI Info Card */}
        <Card className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border-purple-200">
          <CardHeader>
            <CardTitle className="text-purple-900 dark:text-purple-100 text-lg flex items-center space-x-2">
              <Sparkles className="h-5 w-5" />
              <span>Intelligence Artificielle</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-purple-800 dark:text-purple-200">
            <div className="flex items-start space-x-2">
              <CheckCircle2 className="h-4 w-4 mt-0.5" />
              <span>Questions générées par GPT-4, Claude, ou Gemini</span>
            </div>
            <div className="flex items-start space-x-2">
              <CheckCircle2 className="h-4 w-4 mt-0.5" />
              <span>Distracteurs intelligents pour les QCM</span>
            </div>
            <div className="flex items-start space-x-2">
              <CheckCircle2 className="h-4 w-4 mt-0.5" />
              <span>Explications détaillées avec références</span>
            </div>
            <div className="flex items-start space-x-2">
              <CheckCircle2 className="h-4 w-4 mt-0.5" />
              <span>Validation qualité {'>'} 85%</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Preview Panel */}
      <div>
        <Card className="shadow-xl h-full">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span className="flex items-center space-x-2">
                <Brain className="h-6 w-6 text-blue-600" />
                <span>Prévisualisation du Quiz</span>
              </span>
              {generatedQuiz && (
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm" onClick={downloadQuiz}>
                    <Download className="h-4 w-4 mr-2" />
                    Télécharger
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => setGeneratedQuiz(null)}>
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Nouveau
                  </Button>
                </div>
              )}
            </CardTitle>
            <CardDescription>
              {generatedQuiz
                ? `${generatedQuiz.total_questions} questions • ${generatedQuiz.total_points} points`
                : 'Générez un quiz pour voir la prévisualisation'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isGenerating ? (
              <div className="flex flex-col items-center justify-center py-12 space-y-4">
                <div className="relative">
                  <Brain className="h-16 w-16 text-purple-600 animate-pulse" />
                  <Sparkles className="h-8 w-8 text-yellow-500 absolute -top-2 -right-2 animate-bounce" />
                </div>
                <p className="text-lg font-semibold text-gray-900">Génération par IA en cours...</p>
                <p className="text-sm text-gray-600">Cela peut prendre 10-30 secondes</p>
              </div>
            ) : generatedQuiz ? (
              <div className="space-y-4 max-h-[calc(100vh-300px)] overflow-y-auto pr-2">
                {/* Quiz Header */}
                <div className="bg-gradient-to-r from-purple-100 to-pink-100 dark:from-purple-900/40 dark:to-pink-900/40 p-4 rounded-lg">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                    {generatedQuiz.title}
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    <Badge variant="outline">{generatedQuiz.difficulty}</Badge>
                    <Badge variant="outline">{generatedQuiz.total_questions} questions</Badge>
                    <Badge variant="outline">{generatedQuiz.total_points} points</Badge>
                  </div>
                </div>

                {/* Questions List */}
                {generatedQuiz.questions.map((question, index) => (
                  <Card key={question.question_id} className="border-l-4 border-l-purple-500">
                    <CardContent className="pt-6">
                      <div className="space-y-3">
                        {/* Question Header */}
                        <div className="flex items-start justify-between">
                          <Badge variant="secondary">Q{index + 1}</Badge>
                          <div className="flex items-center space-x-2 text-sm">
                            <Badge variant="outline">{question.question_type}</Badge>
                            <Badge variant="outline">{question.points} pt{question.points > 1 ? 's' : ''}</Badge>
                            {question.difficulty && (
                              <Badge
                                variant="outline"
                                className={
                                  question.difficulty === 'easy' ? 'border-green-500 text-green-700' :
                                  question.difficulty === 'hard' ? 'border-orange-500 text-orange-700' :
                                  'border-blue-500 text-blue-700'
                                }
                              >
                                {question.difficulty}
                              </Badge>
                            )}
                          </div>
                        </div>

                        {/* Question Text */}
                        <p className="font-semibold text-gray-900 dark:text-white">
                          {question.question_text}
                        </p>

                        {/* Options (for MCQ) */}
                        {question.options && question.options.length > 0 && (
                          <div className="space-y-2 ml-4">
                            {question.options.map((option, optIdx) => {
                              const isCorrect = Array.isArray(question.correct_answer)
                                ? question.correct_answer.includes(option)
                                : question.correct_answer === option;
                              
                              return (
                                <div
                                  key={optIdx}
                                  className={`flex items-center space-x-2 p-2 rounded ${
                                    isCorrect ? 'bg-green-50 dark:bg-green-900/20' : 'bg-gray-50 dark:bg-gray-800'
                                  }`}
                                >
                                  {isCorrect ? (
                                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                                  ) : (
                                    <XCircle className="h-4 w-4 text-gray-400" />
                                  )}
                                  <span className={isCorrect ? 'font-semibold text-green-900' : ''}>
                                    {option}
                                  </span>
                                </div>
                              );
                            })}
                          </div>
                        )}

                        {/* Explanation */}
                        {question.explanation && (
                          <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
                            <p className="text-sm text-blue-900 dark:text-blue-100">
                              <span className="font-semibold">💡 Explication: </span>
                              {question.explanation}
                            </p>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-12 text-center space-y-4">
                <Brain className="h-16 w-16 text-gray-300" />
                <p className="text-gray-600">
                  Configurez les paramètres et cliquez sur "Générer" pour créer un quiz
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default QuizGeneratorPanel;
