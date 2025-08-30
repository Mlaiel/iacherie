/**
 * Remix Tutorials Page - Ultra-Advanced Enterprise Learning Platform
 * 
 * This page provides comprehensive tutorials, masterclasses, and educational
 * content for AI-powered music creation and remixing techniques.
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️  CRITICAL LEGAL NOTICE:
 * This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
 * Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
 * Contact: mlaiel@live.de for licensing inquiries.
 * 
 * 🏆 Expert Development Team Specialties:
 * - Lead AI Developer: Advanced machine learning and AI systems
 * - Backend Senior Engineer: Enterprise Python/FastAPI architecture
 * - ML Engineer: TensorFlow/PyTorch and neural networks
 * - Database Administrator: PostgreSQL and vector databases
 * - Security Specialist: Enterprise security protocols
 * - Microservices Architect: Scalable distributed systems
 * - Audio Engineer: Professional audio processing
 * - DevOps Engineer: CI/CD and cloud infrastructure
 * - AI Prompt Engineer: Advanced prompt engineering
 */

'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import studioStyles from '@/components/remix_studio/remix_studio.styles';
import { 
  PlayIcon,
  PauseIcon,
  ClockIcon,
  UserIcon,
  StarIcon,
  BookOpenIcon,
  VideoCameraIcon,
  MicrophoneIcon,
  MusicalNoteIcon,
  SparklesIcon,
  AcademicCapIcon,
  TrophyIcon,
  ChartBarIcon,
  LightBulbIcon,
  CogIcon,
  ArrowLeftIcon,
  EyeIcon,
  HeartIcon,
  ShareIcon,
  DocumentTextIcon,
  CheckCircleIcon,
  LockClosedIcon,
  GlobeAltIcon,
  RocketLaunchIcon
} from '@heroicons/react/24/outline';
import { CheckCircleIcon as CheckCircleIconSolid } from '@heroicons/react/24/solid';
import clsx from 'clsx';

interface TutorialPageProps {
  params?: { [key: string]: string };
}

interface Tutorial {
  id: string;
  title: string;
  description: string;
  instructor: {
    id: string;
    name: string;
    avatar: string;
    verified: boolean;
    expertise: string[];
    rating: number;
    followers: number;
  };
  thumbnail: string;
  duration: number;
  difficulty: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  category: string;
  subcategory: string;
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
  views: number;
  likes: number;
  completions: number;
  rating: number;
  isLiked: boolean;
  isCompleted: boolean;
  isPremium: boolean;
  price?: number;
  prerequisites: string[];
  learningObjectives: string[];
  tools: string[];
  chapters: TutorialChapter[];
  resources: TutorialResource[];
  language: string;
  hasSubtitles: boolean;
  isInteractive: boolean;
}

interface TutorialChapter {
  id: string;
  title: string;
  duration: number;
  isCompleted: boolean;
  videoUrl?: string;
  description: string;
  keyPoints: string[];
}

interface TutorialResource {
  id: string;
  title: string;
  type: 'pdf' | 'audio' | 'project' | 'preset' | 'sample';
  url: string;
  size: string;
}

interface LearningPath {
  id: string;
  title: string;
  description: string;
  thumbnail: string;
  difficulty: string;
  estimatedTime: number;
  tutorials: string[];
  completion: number;
  isEnrolled: boolean;
}

const TutorialsPage: React.FC<TutorialPageProps> = ({ params }) => {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('courses');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [tutorials, setTutorials] = useState<Tutorial[]>([]);
  const [learningPaths, setLearningPaths] = useState<LearningPath[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [currentlyPlaying, setCurrentlyPlaying] = useState<string | null>(null);

  const tabs = [
    { id: 'courses', label: 'Courses', description: 'Comprehensive tutorial courses and series' },
    { id: 'paths', label: 'Learning Paths', description: 'Structured learning journeys for specific skills' },
    { id: 'workshops', label: 'Workshops', description: 'Live and recorded masterclasses' },
    { id: 'basics', label: 'Quick Start', description: 'Essential tutorials to get you started' }
  ];

  const categories = [
    'all',
    'AI Music Generation',
    'Audio Mixing',
    'Sound Design',
    'Beat Making',
    'Vocal Processing',
    'Collaboration',
    'Music Theory',
    'Production Techniques',
    'Mastering',
    'Live Performance',
    'Business & Marketing'
  ];

  const difficultyLevels = [
    { value: 'all', label: 'All Levels' },
    { value: 'beginner', label: 'Beginner' },
    { value: 'intermediate', label: 'Intermediate' },
    { value: 'advanced', label: 'Advanced' },
    { value: 'expert', label: 'Expert' }
  ];

  useEffect(() => {
    loadTutorials();
    loadLearningPaths();
  }, []);

  const loadTutorials = async () => {
    try {
      setIsLoading(true);
      await new Promise(resolve => setTimeout(resolve, 1000));

      const mockTutorials: Tutorial[] = [
        {
          id: 'tutorial-1',
          title: 'AI-Powered Remix Creation: Complete Guide',
          description: 'Master the art of creating professional remixes using AI tools and advanced production techniques. Learn from industry experts.',
          instructor: {
            id: 'instructor-1',
            name: 'Dr. Alex Producer',
            avatar: '/instructors/alex.jpg',
            verified: true,
            expertise: ['AI Music', 'Production', 'Mixing'],
            rating: 4.9,
            followers: 125000
          },
          thumbnail: '/tutorials/ai-remix-guide.jpg',
          duration: 7200, // 2 hours
          difficulty: 'intermediate',
          category: 'AI Music Generation',
          subcategory: 'Remix Techniques',
          tags: ['AI', 'remix', 'production', 'advanced'],
          createdAt: new Date(Date.now() - 2592000000), // 30 days ago
          updatedAt: new Date(Date.now() - 86400000), // 1 day ago
          views: 45000,
          likes: 3200,
          completions: 1890,
          rating: 4.8,
          isLiked: false,
          isCompleted: false,
          isPremium: true,
          price: 29.99,
          prerequisites: ['Basic music theory', 'DAW familiarity'],
          learningObjectives: [
            'Understand AI music generation principles',
            'Master remix workflow techniques',
            'Create professional-quality remixes',
            'Apply advanced mixing strategies'
          ],
          tools: ['AI Studio', 'Timeline Editor', 'Effects Panel', 'Style Transfer'],
          chapters: [
            {
              id: 'chapter-1',
              title: 'Introduction to AI Remixing',
              duration: 900,
              isCompleted: false,
              description: 'Understanding the fundamentals of AI-powered music creation',
              keyPoints: ['AI basics', 'Workflow overview', 'Tool introduction']
            },
            {
              id: 'chapter-2',
              title: 'Setting Up Your AI Studio',
              duration: 1200,
              isCompleted: false,
              description: 'Configure your creative environment for optimal results',
              keyPoints: ['Studio setup', 'AI assistant configuration', 'Project templates']
            },
            {
              id: 'chapter-3',
              title: 'Creating Your First AI Remix',
              duration: 1800,
              isCompleted: false,
              description: 'Step-by-step remix creation process',
              keyPoints: ['Source selection', 'AI processing', 'Creative decisions']
            }
          ],
          resources: [
            {
              id: 'resource-1',
              title: 'AI Remix Template Pack',
              type: 'project',
              url: '/resources/ai-remix-templates.zip',
              size: '45MB'
            },
            {
              id: 'resource-2',
              title: 'Professional Mixing Presets',
              type: 'preset',
              url: '/resources/mixing-presets.zip',
              size: '12MB'
            }
          ],
          language: 'English',
          hasSubtitles: true,
          isInteractive: true
        },
        {
          id: 'tutorial-2',
          title: 'Advanced Vocal Processing Masterclass',
          description: 'Professional vocal processing techniques using AI enhancement and traditional methods for stunning results.',
          instructor: {
            id: 'instructor-2',
            name: 'Maria Vocal Coach',
            avatar: '/instructors/maria.jpg',
            verified: true,
            expertise: ['Vocal Production', 'Audio Engineering', 'AI Enhancement'],
            rating: 4.9,
            followers: 89000
          },
          thumbnail: '/tutorials/vocal-processing.jpg',
          duration: 5400, // 1.5 hours
          difficulty: 'advanced',
          category: 'Vocal Processing',
          subcategory: 'Advanced Techniques',
          tags: ['vocals', 'processing', 'AI', 'professional'],
          createdAt: new Date(Date.now() - 1296000000), // 15 days ago
          updatedAt: new Date(Date.now() - 432000000), // 5 days ago
          views: 28000,
          likes: 2100,
          completions: 980,
          rating: 4.9,
          isLiked: true,
          isCompleted: true,
          isPremium: true,
          price: 39.99,
          prerequisites: ['Audio engineering basics', 'DAW experience'],
          learningObjectives: [
            'Master vocal recording techniques',
            'Apply AI vocal enhancement',
            'Create professional vocal chains',
            'Understand vocal mixing theory'
          ],
          tools: ['Vocal Processor', 'AI Assistant', 'Effects Panel'],
          chapters: [
            {
              id: 'chapter-1',
              title: 'Vocal Recording Fundamentals',
              duration: 1200,
              isCompleted: true,
              description: 'Professional vocal recording setup and techniques',
              keyPoints: ['Microphone selection', 'Room acoustics', 'Recording chain']
            },
            {
              id: 'chapter-2',
              title: 'AI Vocal Enhancement',
              duration: 1800,
              isCompleted: true,
              description: 'Using AI tools for vocal improvement',
              keyPoints: ['AI processing', 'Voice modeling', 'Enhancement techniques']
            }
          ],
          resources: [
            {
              id: 'resource-1',
              title: 'Vocal Processing Chain Presets',
              type: 'preset',
              url: '/resources/vocal-presets.zip',
              size: '8MB'
            }
          ],
          language: 'English',
          hasSubtitles: true,
          isInteractive: false
        },
        {
          id: 'tutorial-3',
          title: 'Beat Making for Beginners',
          description: 'Start your music production journey with this comprehensive guide to beat making and rhythm creation.',
          instructor: {
            id: 'instructor-3',
            name: 'Beat Master Pro',
            avatar: '/instructors/beatmaster.jpg',
            verified: false,
            expertise: ['Beat Making', 'Hip-Hop Production', 'Sampling'],
            rating: 4.7,
            followers: 45000
          },
          thumbnail: '/tutorials/beat-making.jpg',
          duration: 3600, // 1 hour
          difficulty: 'beginner',
          category: 'Beat Making',
          subcategory: 'Fundamentals',
          tags: ['beats', 'beginner', 'hip-hop', 'rhythm'],
          createdAt: new Date(Date.now() - 604800000), // 7 days ago
          updatedAt: new Date(Date.now() - 86400000), // 1 day ago
          views: 15000,
          likes: 890,
          completions: 567,
          rating: 4.6,
          isLiked: false,
          isCompleted: false,
          isPremium: false,
          prerequisites: [],
          learningObjectives: [
            'Understand rhythm and timing',
            'Create basic drum patterns',
            'Use sampling techniques',
            'Arrange complete beats'
          ],
          tools: ['Timeline Editor', 'Drum Samples', 'Sequencer'],
          chapters: [
            {
              id: 'chapter-1',
              title: 'Rhythm Basics',
              duration: 900,
              isCompleted: false,
              description: 'Understanding musical rhythm and time signatures',
              keyPoints: ['Time signatures', 'Beat patterns', 'Groove fundamentals']
            }
          ],
          resources: [
            {
              id: 'resource-1',
              title: 'Beginner Drum Sample Pack',
              type: 'sample',
              url: '/resources/beginner-drums.zip',
              size: '25MB'
            }
          ],
          language: 'English',
          hasSubtitles: false,
          isInteractive: true
        }
      ];

      setTutorials(mockTutorials);
    } catch (error) {
      console.error('Failed to load tutorials:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadLearningPaths = async () => {
    try {
      const mockPaths: LearningPath[] = [
        {
          id: 'path-1',
          title: 'Complete AI Music Producer',
          description: 'From beginner to professional AI music producer in 12 weeks',
          thumbnail: '/paths/ai-producer.jpg',
          difficulty: 'beginner-to-advanced',
          estimatedTime: 144000, // 40 hours
          tutorials: ['tutorial-1', 'tutorial-2', 'tutorial-3'],
          completion: 35,
          isEnrolled: true
        },
        {
          id: 'path-2',
          title: 'Professional Mixing Engineer',
          description: 'Master professional mixing techniques and industry standards',
          thumbnail: '/paths/mixing-engineer.jpg',
          difficulty: 'intermediate-to-expert',
          estimatedTime: 108000, // 30 hours
          tutorials: ['tutorial-2'],
          completion: 0,
          isEnrolled: false
        }
      ];

      setLearningPaths(mockPaths);
    } catch (error) {
      console.error('Failed to load learning paths:', error);
    }
  };

  const handlePlay = (tutorialId: string) => {
    setCurrentlyPlaying(currentlyPlaying === tutorialId ? null : tutorialId);
  };

  const handleEnroll = async (pathId: string) => {
    try {
      setLearningPaths(prev => prev.map(path =>
        path.id === pathId ? { ...path, isEnrolled: true } : path
      ));
    } catch (error) {
      console.error('Failed to enroll in learning path:', error);
    }
  };

  const handleLike = async (tutorialId: string) => {
    try {
      setTutorials(prev => prev.map(tutorial =>
        tutorial.id === tutorialId
          ? { 
              ...tutorial, 
              isLiked: !tutorial.isLiked,
              likes: tutorial.isLiked ? tutorial.likes - 1 : tutorial.likes + 1
            }
          : tutorial
      ));
    } catch (error) {
      console.error('Failed to toggle like:', error);
    }
  };

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300';
      case 'intermediate':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300';
      case 'advanced':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300';
      case 'expert':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300';
      default:
        return 'bg-slate-100 text-slate-800 dark:bg-slate-900 dark:text-slate-300';
    }
  };

  const filteredTutorials = tutorials.filter(tutorial => {
    const matchesSearch = tutorial.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         tutorial.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         tutorial.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesCategory = selectedCategory === 'all' || tutorial.category === selectedCategory;
    const matchesDifficulty = selectedDifficulty === 'all' || tutorial.difficulty === selectedDifficulty;
    
    return matchesSearch && matchesCategory && matchesDifficulty;
  });

  const renderTutorialCard = (tutorial: Tutorial) => (
    <div key={tutorial.id} className={clsx(
      studioStyles.container.card,
      "overflow-hidden transition-all duration-200 hover:scale-105 hover:shadow-lg group cursor-pointer"
    )}>
      {/* Thumbnail */}
      <div className="relative aspect-video bg-gradient-to-br from-purple-500 to-blue-500 overflow-hidden">
        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all duration-200 flex items-center justify-center">
          <button
            onClick={() => handlePlay(tutorial.id)}
            className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 p-4 bg-white bg-opacity-20 rounded-full backdrop-blur-sm"
          >
            {currentlyPlaying === tutorial.id ? (
              <PauseIcon className="h-8 w-8 text-white" />
            ) : (
              <PlayIcon className="h-8 w-8 text-white" />
            )}
          </button>
        </div>
        
        {/* Duration */}
        <div className="absolute bottom-3 right-3">
          <span className="px-2 py-1 text-xs font-medium bg-black bg-opacity-50 text-white rounded">
            {formatDuration(tutorial.duration)}
          </span>
        </div>

        {/* Premium Badge */}
        {tutorial.isPremium && (
          <div className="absolute top-3 right-3">
            <span className="px-2 py-1 text-xs font-medium bg-yellow-600 text-white rounded-full">
              Premium
            </span>
          </div>
        )}

        {/* Completion Status */}
        {tutorial.isCompleted && (
          <div className="absolute top-3 left-3">
            <CheckCircleIconSolid className="h-6 w-6 text-green-500" />
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-6">
        {/* Header */}
        <div className="mb-4">
          <div className="flex items-start justify-between mb-2">
            <h3 className="font-semibold text-slate-900 dark:text-white line-clamp-2 group-hover:text-purple-600 transition-colors">
              {tutorial.title}
            </h3>
            <span className={clsx(
              "px-2 py-1 text-xs font-medium rounded-full flex-shrink-0 ml-2",
              getDifficultyColor(tutorial.difficulty)
            )}>
              {tutorial.difficulty}
            </span>
          </div>
          <p className="text-sm text-slate-600 dark:text-slate-400 line-clamp-2 mb-3">
            {tutorial.description}
          </p>
        </div>

        {/* Instructor */}
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-green-500 to-teal-500 flex items-center justify-center text-xs font-medium text-white">
            {tutorial.instructor.name.split(' ').map(n => n[0]).join('')}
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-slate-900 dark:text-white">
              {tutorial.instructor.name}
              {tutorial.instructor.verified && (
                <span className="ml-1 text-blue-500">✓</span>
              )}
            </p>
            <div className="flex items-center space-x-2 text-xs text-slate-500">
              <span className="flex items-center space-x-1">
                <StarIcon className="h-3 w-3" />
                <span>{tutorial.instructor.rating}</span>
              </span>
              <span>•</span>
              <span>{tutorial.instructor.followers.toLocaleString()} followers</span>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="flex items-center justify-between text-sm text-slate-500 dark:text-slate-400 mb-4">
          <div className="flex items-center space-x-4">
            <span className="flex items-center space-x-1">
              <EyeIcon className="h-3 w-3" />
              <span>{tutorial.views.toLocaleString()}</span>
            </span>
            <span className="flex items-center space-x-1">
              <HeartIcon className="h-3 w-3" />
              <span>{tutorial.likes.toLocaleString()}</span>
            </span>
            <span className="flex items-center space-x-1">
              <CheckCircleIcon className="h-3 w-3" />
              <span>{tutorial.completions.toLocaleString()}</span>
            </span>
          </div>
          <div className="flex items-center space-x-1">
            <StarIcon className="h-3 w-3 text-yellow-500" />
            <span>{tutorial.rating}</span>
          </div>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-1 mb-4">
          {tutorial.tags.slice(0, 3).map((tag) => (
            <span
              key={tag}
              className="px-2 py-1 text-xs bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 rounded"
            >
              #{tag}
            </span>
          ))}
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => handleLike(tutorial.id)}
              className={clsx(
                "p-2 rounded-lg transition-colors",
                tutorial.isLiked
                  ? "text-red-500 bg-red-50 dark:bg-red-900/20"
                  : "text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20"
              )}
            >
              <HeartIcon className="h-4 w-4" />
            </button>
            <button className="p-2 text-slate-400 hover:text-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors">
              <ShareIcon className="h-4 w-4" />
            </button>
          </div>
          
          <button
            onClick={() => router.push(`/remix/tutorials/${tutorial.id}`)}
            className={clsx(
              "px-4 py-2 rounded-lg font-medium transition-colors",
              tutorial.isPremium && !tutorial.isCompleted
                ? "bg-yellow-600 text-white hover:bg-yellow-700"
                : tutorial.isCompleted
                ? "bg-green-600 text-white hover:bg-green-700"
                : "bg-purple-600 text-white hover:bg-purple-700"
            )}
          >
            {tutorial.isPremium && !tutorial.isCompleted 
              ? `$${tutorial.price}` 
              : tutorial.isCompleted 
              ? 'Completed' 
              : 'Start Course'
            }
          </button>
        </div>
      </div>
    </div>
  );

  const renderLearningPathCard = (path: LearningPath) => (
    <div key={path.id} className={clsx(
      studioStyles.container.card,
      "p-6 transition-all duration-200 hover:scale-105 hover:shadow-lg"
    )}>
      <div className="flex items-start space-x-4">
        <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg flex-shrink-0"></div>
        <div className="flex-1">
          <h3 className="font-semibold text-slate-900 dark:text-white mb-2">
            {path.title}
          </h3>
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">
            {path.description}
          </p>
          
          <div className="flex items-center space-x-4 text-sm text-slate-500 mb-3">
            <span className="flex items-center space-x-1">
              <ClockIcon className="h-3 w-3" />
              <span>{formatDuration(path.estimatedTime)}</span>
            </span>
            <span className="flex items-center space-x-1">
              <BookOpenIcon className="h-3 w-3" />
              <span>{path.tutorials.length} courses</span>
            </span>
            <span className={clsx(
              "px-2 py-1 text-xs rounded-full",
              getDifficultyColor(path.difficulty)
            )}>
              {path.difficulty}
            </span>
          </div>

          {path.isEnrolled && (
            <div className="mb-3">
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-slate-600 dark:text-slate-400">Progress</span>
                <span className="text-slate-900 dark:text-white font-medium">{path.completion}%</span>
              </div>
              <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
                <div 
                  className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${path.completion}%` }}
                ></div>
              </div>
            </div>
          )}

          <div className="flex items-center justify-between">
            {path.isEnrolled ? (
              <button
                onClick={() => router.push(`/remix/tutorials/path/${path.id}`)}
                className={clsx(studioStyles.buttons.primary, "px-4 py-2")}
              >
                Continue Learning
              </button>
            ) : (
              <button
                onClick={() => handleEnroll(path.id)}
                className={clsx(studioStyles.buttons.secondary, "px-4 py-2")}
              >
                Enroll Now
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'courses':
        return (
          <div className="space-y-6">
            {/* Filters */}
            <div className="flex items-center space-x-4">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              >
                {categories.map((category) => (
                  <option key={category} value={category}>
                    {category === 'all' ? 'All Categories' : category}
                  </option>
                ))}
              </select>

              <select
                value={selectedDifficulty}
                onChange={(e) => setSelectedDifficulty(e.target.value)}
                className="px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              >
                {difficultyLevels.map((level) => (
                  <option key={level.value} value={level.value}>
                    {level.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Tutorials Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredTutorials.map(renderTutorialCard)}
            </div>
          </div>
        );
      case 'paths':
        return (
          <div className="space-y-6">
            {learningPaths.map(renderLearningPathCard)}
          </div>
        );
      case 'workshops':
        return (
          <div className={clsx(studioStyles.container.card, "p-8 text-center")}>
            <VideoCameraIcon className="h-12 w-12 text-purple-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
              Live Workshops Coming Soon
            </h3>
            <p className="text-slate-600 dark:text-slate-400 mb-4">
              Join live masterclasses with industry professionals
            </p>
            <button className={clsx(studioStyles.buttons.primary, "px-6 py-3")}>
              Get Notified
            </button>
          </div>
        );
      case 'basics':
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {tutorials.filter(t => t.difficulty === 'beginner').map(renderTutorialCard)}
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      {/* Header */}
      <div className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
        <div className="px-6 py-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/remix')}
                className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
              >
                <ArrowLeftIcon className="h-5 w-5" />
              </button>
              <div>
                <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
                  Learning Center
                </h1>
                <p className="text-slate-600 dark:text-slate-400 mt-2">
                  Master AI-powered music creation with expert tutorials and courses
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/remix/studio')}
                className={clsx(studioStyles.buttons.secondary, "px-4 py-2")}
              >
                <RocketLaunchIcon className="h-5 w-5 mr-2" />
                Practice Now
              </button>
            </div>
          </div>

          {/* Search Bar */}
          <div className="mt-6">
            <div className="relative max-w-md">
              <input
                type="text"
                placeholder="Search tutorials, topics, instructors..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-4 pr-4 py-3 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              />
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="px-6">
          <div className="flex space-x-8 border-b border-slate-200 dark:border-slate-700">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={clsx(
                  "pb-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200",
                  activeTab === tab.id
                    ? "border-purple-500 text-purple-600 dark:text-purple-400"
                    : "border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300"
                )}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Description */}
        <div className="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
          <div className="px-6 py-3">
            <p className="text-sm text-slate-600 dark:text-slate-400">
              {tabs.find(tab => tab.id === activeTab)?.description}
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="px-6 py-8">
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Array.from({ length: 6 }).map((_, index) => (
              <div key={index} className="animate-pulse">
                <div className="aspect-video bg-slate-200 dark:bg-slate-800 rounded-lg mb-3"></div>
                <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded mb-2"></div>
                <div className="h-3 bg-slate-200 dark:bg-slate-800 rounded w-2/3"></div>
              </div>
            ))}
          </div>
        ) : (
          renderActiveTab()
        )}
      </div>
    </div>
  );
};

export default TutorialsPage;