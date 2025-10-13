import { useState } from 'react';

const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000';

// Types
export interface Content {
  id: string;
  title: string;
  content_type: string;
  subject?: string;
  topic?: string;
  language: string;
  processing_status: string;
  created_at: string;
}

export interface Quiz {
  id: string;
  title: string;
  subject: string;
  difficulty: string;
  questions: any[];
  total_questions: number;
  total_points: number;
  passing_score: number;
}

export interface FactCheck {
  id: string;
  claim: string;
  verdict: string;
  confidence: number;
  sources: any[];
  explanation: string;
  context?: string;
  ai_reasoning: string;
}

// Content Upload Hooks
export const useContentUpload = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const uploadContent = async (formData: FormData): Promise<Content | null> => {
    setIsUploading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/eduverify/content/upload`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const content = await response.json();
      return content;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return null;
    } finally {
      setIsUploading(false);
    }
  };

  return { uploadContent, isUploading, error };
};

export const useContentList = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchContent = async (params?: {
    subject?: string;
    language?: string;
    page?: number;
  }): Promise<Content[]> => {
    setIsLoading(true);
    setError(null);

    try {
      const queryParams = new URLSearchParams();
      if (params?.subject) queryParams.append('subject', params.subject);
      if (params?.language) queryParams.append('language', params.language);
      if (params?.page) queryParams.append('page', params.page.toString());

      const response = await fetch(
        `${API_BASE_URL}/eduverify/content?${queryParams.toString()}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch content');
      }

      const content = await response.json();
      return content;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return [];
    } finally {
      setIsLoading(false);
    }
  };

  return { fetchContent, isLoading, error };
};

// Quiz Hooks
export const useQuizGeneration = () => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateQuiz = async (data: {
    content_id: string;
    num_questions: number;
    difficulty: string;
    language?: string;
  }): Promise<Quiz | null> => {
    setIsGenerating(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/eduverify/quizzes/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error('Quiz generation failed');
      }

      const quiz = await response.json();
      return quiz;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return null;
    } finally {
      setIsGenerating(false);
    }
  };

  return { generateQuiz, isGenerating, error };
};

export const useQuizSubmission = () => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submitQuiz = async (quizId: string, answers: Record<string, number>) => {
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/eduverify/quizzes/${quizId}/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ answers }),
      });

      if (!response.ok) {
        throw new Error('Quiz submission failed');
      }

      const result = await response.json();
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return null;
    } finally {
      setIsSubmitting(false);
    }
  };

  return { submitQuiz, isSubmitting, error };
};

export const useQuizList = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchQuizzes = async (params?: {
    subject?: string;
    difficulty?: string;
  }): Promise<Quiz[]> => {
    setIsLoading(true);
    setError(null);

    try {
      const queryParams = new URLSearchParams();
      if (params?.subject) queryParams.append('subject', params.subject);
      if (params?.difficulty) queryParams.append('difficulty', params.difficulty);

      const response = await fetch(
        `${API_BASE_URL}/eduverify/quizzes?${queryParams.toString()}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch quizzes');
      }

      const quizzes = await response.json();
      return quizzes;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return [];
    } finally {
      setIsLoading(false);
    }
  };

  return { fetchQuizzes, isLoading, error };
};

// Fact-Checking Hooks
export const useFactCheck = () => {
  const [isChecking, setIsChecking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const checkFact = async (claim: string, contentId?: string): Promise<FactCheck | null> => {
    setIsChecking(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/eduverify/fact-check`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ claim, content_id: contentId }),
      });

      if (!response.ok) {
        throw new Error('Fact check failed');
      }

      const result = await response.json();
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return null;
    } finally {
      setIsChecking(false);
    }
  };

  const batchCheckFacts = async (
    claims: string[],
    contentId?: string
  ): Promise<FactCheck[]> => {
    setIsChecking(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/eduverify/fact-check/batch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ claims, content_id: contentId }),
      });

      if (!response.ok) {
        throw new Error('Batch fact check failed');
      }

      const results = await response.json();
      return results;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return [];
    } finally {
      setIsChecking(false);
    }
  };

  return { checkFact, batchCheckFacts, isChecking, error };
};

// Analytics Hooks
export const useAnalytics = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchUserAnalytics = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/eduverify/analytics/user`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch analytics');
      }

      const analytics = await response.json();
      return analytics;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  const fetchProgress = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/eduverify/analytics/progress`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch progress');
      }

      const progress = await response.json();
      return progress;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  const fetchRecommendations = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/eduverify/analytics/recommendations`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch recommendations');
      }

      const recommendations = await response.json();
      return recommendations;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  return { fetchUserAnalytics, fetchProgress, fetchRecommendations, isLoading, error };
};

// Explanation Hooks
export const useExplanations = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateExplanation = async (data: {
    topic: string;
    academic_level: string;
    language?: string;
  }) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/eduverify/explanations/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error('Explanation generation failed');
      }

      const explanation = await response.json();
      return explanation;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  const searchExplanations = async (query: string, academicLevel?: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const queryParams = new URLSearchParams({ q: query });
      if (academicLevel) queryParams.append('academic_level', academicLevel);

      const response = await fetch(
        `${API_BASE_URL}/eduverify/explanations?${queryParams.toString()}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Search failed');
      }

      const results = await response.json();
      return results;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return [];
    } finally {
      setIsLoading(false);
    }
  };

  return { generateExplanation, searchExplanations, isLoading, error };
};
