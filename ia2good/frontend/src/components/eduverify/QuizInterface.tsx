import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { CheckCircle2, XCircle, Clock, Trophy, BookOpen } from 'lucide-react';

export type QuizDifficulty = 'easy' | 'medium' | 'hard' | 'mixed';

export interface QuizQuestion {
  id: string;
  question: string;
  options: string[];
  correct_answer: number;
  explanation: string;
  points: number;
}

export interface Quiz {
  id: string;
  title: string;
  subject: string;
  difficulty: QuizDifficulty;
  questions: QuizQuestion[];
  total_questions: number;
  total_points: number;
  time_limit_minutes?: number;
  passing_score: number;
}

interface QuizInterfaceProps {
  quiz: Quiz;
  onSubmit: (answers: Record<string, number>) => void;
}

export const QuizInterface: React.FC<QuizInterfaceProps> = ({ quiz, onSubmit }) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [showResults, setShowResults] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(
    quiz.time_limit_minutes ? quiz.time_limit_minutes * 60 : null
  );

  const currentQuestion = quiz.questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / quiz.total_questions) * 100;

  // Timer effect
  React.useEffect(() => {
    if (timeRemaining !== null && timeRemaining > 0 && !showResults) {
      const timer = setTimeout(() => setTimeRemaining(timeRemaining - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeRemaining === 0) {
      handleSubmit();
    }
  }, [timeRemaining, showResults]);

  const handleAnswerSelect = (questionId: string, answerIndex: number) => {
    setAnswers({ ...answers, [questionId]: answerIndex });
  };

  const handleNext = () => {
    if (currentQuestionIndex < quiz.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleSubmit = () => {
    setShowResults(true);
    onSubmit(answers);
  };

  const calculateResults = () => {
    let correct = 0;
    let points = 0;

    quiz.questions.forEach((question) => {
      if (answers[question.id] === question.correct_answer) {
        correct++;
        points += question.points;
      }
    });

    const score = (points / quiz.total_points) * 100;
    return { correct, points, score, passed: score >= quiz.passing_score };
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (showResults) {
    const results = calculateResults();
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle className="text-3xl text-center">
            {results.passed ? '🎉 Félicitations!' : '📚 Continuez vos efforts!'}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="text-center space-y-4">
            <div className="flex justify-center">
              <div
                className={`w-32 h-32 rounded-full flex items-center justify-center text-4xl font-bold ${
                  results.passed ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-700'
                }`}
              >
                {results.score.toFixed(0)}%
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 max-w-2xl mx-auto">
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="text-sm text-gray-600">Questions correctes</p>
                <p className="text-3xl font-bold text-blue-700">
                  {results.correct}/{quiz.total_questions}
                </p>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg">
                <p className="text-sm text-gray-600">Points obtenus</p>
                <p className="text-3xl font-bold text-purple-700">
                  {results.points}/{quiz.total_points}
                </p>
              </div>
              <div className="p-4 bg-yellow-50 rounded-lg">
                <p className="text-sm text-gray-600">Note minimale</p>
                <p className="text-3xl font-bold text-yellow-700">{quiz.passing_score}%</p>
              </div>
            </div>

            {results.passed && (
              <div className="flex items-center justify-center gap-2 text-green-700 text-xl">
                <Trophy className="w-8 h-8" />
                <span className="font-bold">Quiz réussi!</span>
              </div>
            )}
          </div>

          {/* Detailed Review */}
          <div className="space-y-4 mt-8">
            <h3 className="text-xl font-bold mb-4">Révision détaillée</h3>
            {quiz.questions.map((question, index) => {
              const userAnswer = answers[question.id];
              const isCorrect = userAnswer === question.correct_answer;

              return (
                <div
                  key={question.id}
                  className={`p-4 border-2 rounded-lg ${
                    isCorrect ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {isCorrect ? (
                      <CheckCircle2 className="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
                    ) : (
                      <XCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-1" />
                    )}
                    <div className="flex-1">
                      <p className="font-medium mb-2">
                        Question {index + 1}: {question.question}
                      </p>
                      <p className="text-sm text-gray-600 mb-2">
                        Votre réponse:{' '}
                        <span className={isCorrect ? 'text-green-700' : 'text-red-700'}>
                          {userAnswer !== undefined ? question.options[userAnswer] : 'Non répondu'}
                        </span>
                      </p>
                      {!isCorrect && (
                        <p className="text-sm text-gray-600 mb-2">
                          Bonne réponse:{' '}
                          <span className="text-green-700">
                            {question.options[question.correct_answer]}
                          </span>
                        </p>
                      )}
                      <div className="mt-2 p-3 bg-white rounded border">
                        <p className="text-sm font-medium text-gray-700 mb-1">Explication:</p>
                        <p className="text-sm text-gray-600">{question.explanation}</p>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="flex gap-4 justify-center mt-8">
            <Button variant="outline" size="lg" onClick={() => window.location.reload()}>
              Refaire le quiz
            </Button>
            <Button size="lg" onClick={() => (window.location.href = '/eduverify')}>
              Retour au tableau de bord
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <div className="flex items-center justify-between mb-2">
          <Badge variant="outline" className="text-base">
            <BookOpen className="w-4 h-4 mr-2" />
            {quiz.subject}
          </Badge>
          {timeRemaining !== null && (
            <Badge
              variant={timeRemaining < 60 ? 'destructive' : 'secondary'}
              className="text-base"
            >
              <Clock className="w-4 h-4 mr-2" />
              {formatTime(timeRemaining)}
            </Badge>
          )}
        </div>
        <CardTitle className="text-2xl">{quiz.title}</CardTitle>
        <div className="flex items-center gap-4 text-sm text-gray-600">
          <span>Difficulté: {quiz.difficulty}</span>
          <span>•</span>
          <span>
            Question {currentQuestionIndex + 1} sur {quiz.total_questions}
          </span>
        </div>
        <Progress value={progress} className="mt-2" />
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Question */}
        <div className="space-y-4">
          <div className="p-6 bg-blue-50 rounded-lg">
            <p className="text-xl font-medium">{currentQuestion.question}</p>
            <p className="text-sm text-gray-600 mt-2">{currentQuestion.points} points</p>
          </div>

          {/* Options */}
          <RadioGroup
            value={answers[currentQuestion.id]?.toString()}
            onValueChange={(value) =>
              handleAnswerSelect(currentQuestion.id, parseInt(value))
            }
            className="space-y-3"
          >
            {currentQuestion.options.map((option, index) => (
              <div
                key={index}
                className={`flex items-center space-x-3 p-4 rounded-lg border-2 cursor-pointer transition-colors ${
                  answers[currentQuestion.id] === index
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                }`}
                onClick={() => handleAnswerSelect(currentQuestion.id, index)}
              >
                <RadioGroupItem value={index.toString()} id={`option-${index}`} />
                <Label
                  htmlFor={`option-${index}`}
                  className="flex-1 cursor-pointer text-base"
                >
                  {option}
                </Label>
              </div>
            ))}
          </RadioGroup>
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-between pt-6 border-t">
          <Button
            variant="outline"
            onClick={handlePrevious}
            disabled={currentQuestionIndex === 0}
          >
            ← Précédent
          </Button>

          <div className="flex gap-2">
            {quiz.questions.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentQuestionIndex(index)}
                className={`w-8 h-8 rounded-full text-sm font-medium transition-colors ${
                  index === currentQuestionIndex
                    ? 'bg-blue-600 text-white'
                    : answers[quiz.questions[index].id] !== undefined
                      ? 'bg-green-100 text-green-700 border-2 border-green-300'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {index + 1}
              </button>
            ))}
          </div>

          {currentQuestionIndex === quiz.questions.length - 1 ? (
            <Button onClick={handleSubmit} className="bg-green-600 hover:bg-green-700">
              Soumettre le quiz
            </Button>
          ) : (
            <Button onClick={handleNext}>Suivant →</Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
