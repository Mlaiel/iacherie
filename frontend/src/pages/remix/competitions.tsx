/**
 * Remix Competitions Page - Ultra-Advanced Enterprise Competition Platform
 * 
 * This page provides comprehensive competition management with community
 * challenges, leaderboards, rewards, and professional judging systems.
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
  TrophyIcon,
  CalendarIcon,
  ClockIcon,
  UserIcon,
  StarIcon,
  GiftIcon,
  PlayIcon,
  PauseIcon,
  HeartIcon,
  ShareIcon,
  EyeIcon,
  ChatBubbleLeftIcon,
  ArrowRightIcon,
  ArrowLeftIcon,
  FireIcon,
  CurrencyDollarIcon,
  MusicalNoteIcon,
  UsersIcon,
  SparklesIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  PlusIcon,
  DocumentTextIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';
import { TrophyIcon as TrophyIconSolid } from '@heroicons/react/24/solid';
import clsx from 'clsx';

interface CompetitionsPageProps {
  params?: { [key: string]: string };
}

interface Competition {
  id: string;
  title: string;
  description: string;
  theme: string;
  organizer: {
    id: string;
    name: string;
    avatar: string;
    verified: boolean;
    type: 'platform' | 'brand' | 'label' | 'artist';
  };
  banner: string;
  startDate: Date;
  endDate: Date;
  submissionDeadline: Date;
  status: 'upcoming' | 'active' | 'judging' | 'completed';
  category: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced' | 'professional';
  maxParticipants: number;
  currentParticipants: number;
  totalSubmissions: number;
  prizes: CompetitionPrize[];
  rules: string[];
  requirements: string[];
  judges: Judge[];
  isParticipating: boolean;
  hasSubmitted: boolean;
  submissionId?: string;
  entryFee?: number;
  sponsorBrands: string[];
  votingEnabled: boolean;
  publicVoting: boolean;
  featured: boolean;
}

interface CompetitionPrize {
  position: number;
  title: string;
  description: string;
  value: number;
  type: 'cash' | 'equipment' | 'contract' | 'exposure' | 'credits';
  sponsor?: string;
}

interface Judge {
  id: string;
  name: string;
  avatar: string;
  title: string;
  bio: string;
  credentials: string[];
  verified: boolean;
}

interface Submission {
  id: string;
  competitionId: string;
  title: string;
  artist: {
    id: string;
    name: string;
    username: string;
    avatar: string;
    verified: boolean;
  };
  thumbnail: string;
  audioUrl: string;
  description: string;
  submittedAt: Date;
  votes: number;
  plays: number;
  likes: number;
  comments: number;
  rank?: number;
  isWinner: boolean;
  awards: string[];
  tags: string[];
  isLiked: boolean;
  hasVoted: boolean;
}

const CompetitionsPage: React.FC<CompetitionsPageProps> = ({ params }) => {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('active');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [competitions, setCompetitions] = useState<Competition[]>([]);
  const [featuredSubmissions, setFeaturedSubmissions] = useState<Submission[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [currentlyPlaying, setCurrentlyPlaying] = useState<string | null>(null);

  const tabs = [
    { id: 'active', label: 'Active', description: 'Currently running competitions you can join' },
    { id: 'upcoming', label: 'Upcoming', description: 'Future competitions to prepare for' },
    { id: 'my-entries', label: 'My Entries', description: 'Your submissions and participation history' },
    { id: 'winners', label: 'Winners', description: 'Past winners and awarded submissions' }
  ];

  const categories = [
    'all',
    'Creative Monthly',
    'Technical SEO', 
    'Technical Revenue',
    'Global Competition',
    'Special Event',
    'Remix Competition',
    'Beat Battle',
    'Vocal Challenge',
    'AI Innovation',
    'Collaboration',
    'Genre Fusion',
    'Sample Flip',
    'Original Track',
    'Sound Design',
    'Live Performance',
    'Fan Favorite'
  ];

  useEffect(() => {
    loadCompetitions();
    loadFeaturedSubmissions();
  }, []);

  const loadCompetitions = async () => {
    try {
      setIsLoading(true);
      await new Promise(resolve => setTimeout(resolve, 1000));

      const mockCompetitions: Competition[] = [
        // 🎨 Creative Monthly Challenge
        {
          id: 'comp-creative-monthly-1',
          title: 'Monthly Creative Masterpiece Challenge',
          description: 'Create your most innovative content piece of the month. Showcase creativity, originality, and artistic vision to win amazing monthly rewards.',
          theme: 'Monthly Creative Excellence',
          organizer: {
            id: 'org-1',
            name: 'Ainflue Platform',
            avatar: '/organizers/ainflue.jpg',
            verified: true,
            type: 'platform'
          },
          banner: '/competitions/creative-monthly.jpg',
          startDate: new Date(Date.now() - 604800000), // 7 days ago
          endDate: new Date(Date.now() + 1900800000), // 22 days from now
          submissionDeadline: new Date(Date.now() + 1728000000), // 20 days from now
          status: 'active',
          category: 'Creative Monthly',
          difficulty: 'intermediate',
          maxParticipants: 2000,
          currentParticipants: 847,
          totalSubmissions: 312,
          prizes: [
            {
              position: 1,
              title: 'Monthly Creative Champion',
              description: 'Premium creative tools + Cash prize + Feature spotlight',
              value: 5000,
              type: 'cash',
              sponsor: 'Ainflue Creative'
            },
            {
              position: 2,
              title: 'Creative Innovator',
              description: 'Creative tools suite + Platform credits',
              value: 3000,
              type: 'equipment',
              sponsor: 'Creative Labs'
            },
            {
              position: 3,
              title: 'Rising Artist',
              description: 'Feature on homepage + Creative mentorship',
              value: 1500,
              type: 'credits',
              sponsor: 'Ainflue'
            }
          ],
          rules: [
            'Original creative content only',
            'Must showcase artistic innovation',
            'Maximum duration: 10 minutes for video/audio',
            'Submit in high quality format',
            'Include creative process documentation'
          ],
          requirements: [
            'Use platform creative tools',
            'Demonstrate artistic originality',
            'Include brief artist statement',
            'Tag submission with #CreativeMonthly2025'
          ],
          judges: [
            {
              id: 'judge-creative-1',
              name: 'Sarah Creative Director',
              avatar: '/judges/sarah.jpg',
              title: 'Award-winning Creative Director',
              bio: 'International creative director with 20+ years experience',
              credentials: ['Cannes Lions Winner', 'Creative Director of the Year', 'Art Innovation Pioneer'],
              verified: true
            }
          ],
          isParticipating: true,
          hasSubmitted: false,
          entryFee: 0,
          sponsorBrands: ['Ainflue Creative', 'Creative Labs', 'Innovation Studios'],
          votingEnabled: true,
          publicVoting: true,
          featured: true
        },

        // 📈 Technical SEO Challenge
        {
          id: 'comp-seo-tech-1',
          title: 'SEO Optimization Master Challenge',
          description: 'Optimize your content for maximum search visibility. Improve SEO metrics by 50% to win technical mastery rewards.',
          theme: 'SEO Excellence & Search Optimization',
          organizer: {
            id: 'org-2',
            name: 'SEO Masters Guild',
            avatar: '/organizers/seo-guild.jpg',
            verified: true,
            type: 'brand'
          },
          banner: '/competitions/seo-challenge.jpg',
          startDate: new Date(Date.now() - 1209600000), // 14 days ago
          endDate: new Date(Date.now() + 1382400000), // 16 days from now
          submissionDeadline: new Date(Date.now() + 1209600000), // 14 days from now
          status: 'active',
          category: 'Technical SEO',
          difficulty: 'advanced',
          maxParticipants: 500,
          currentParticipants: 278,
          totalSubmissions: 156,
          prizes: [
            {
              position: 1,
              title: 'SEO Master Champion',
              description: 'Advanced SEO tools suite + Analytics premium + Cash reward',
              value: 4000,
              type: 'equipment',
              sponsor: 'SEO Pro Tools'
            },
            {
              position: 2,
              title: 'Search Optimization Expert',
              description: 'SEO toolkit + Professional consultation',
              value: 2500,
              type: 'equipment',
              sponsor: 'Search Analytics Co'
            }
          ],
          rules: [
            'Measurable SEO improvements required',
            'Must document optimization strategies',
            'Provide before/after analytics',
            'Follow white-hat SEO practices only'
          ],
          requirements: [
            'Use platform SEO tools',
            'Show minimum 40% improvement in key metrics',
            'Document optimization process',
            'Include analytics reports'
          ],
          judges: [
            {
              id: 'judge-seo-1',
              name: 'Dr. Mark SEO Expert',
              avatar: '/judges/mark-seo.jpg',
              title: 'SEO Strategy Director',
              bio: 'Leading SEO expert with proven track record',
              credentials: ['SEO Industry Leader', 'Google Partner', 'Search Marketing Expert'],
              verified: true
            }
          ],
          isParticipating: false,
          hasSubmitted: false,
          entryFee: 25,
          sponsorBrands: ['SEO Pro Tools', 'Search Analytics Co'],
          votingEnabled: false,
          publicVoting: false,
          featured: true
        },

        // 💰 Revenue Optimization Challenge
        {
          id: 'comp-revenue-tech-1',
          title: 'Revenue Optimization Champion',
          description: 'Maximize your content monetization. Increase monthly revenue by 40% through strategic optimization and engagement.',
          theme: 'Revenue Growth & Monetization Excellence',
          organizer: {
            id: 'org-3',
            name: 'Monetization Masters',
            avatar: '/organizers/monetization.jpg',
            verified: true,
            type: 'brand'
          },
          banner: '/competitions/revenue-optimization.jpg',
          startDate: new Date(Date.now() - 518400000), // 6 days ago
          endDate: new Date(Date.now() + 2073600000), // 24 days from now
          submissionDeadline: new Date(Date.now() + 1900800000), // 22 days from now
          status: 'active',
          category: 'Technical Revenue',
          difficulty: 'expert',
          maxParticipants: 300,
          currentParticipants: 189,
          totalSubmissions: 67,
          prizes: [
            {
              position: 1,
              title: 'Revenue Champion',
              description: 'Monetization suite + Revenue share bonus + Business mentorship',
              value: 7500,
              type: 'cash',
              sponsor: 'Revenue Labs'
            },
            {
              position: 2,
              title: 'Monetization Expert',
              description: 'Premium monetization tools + Analytics access',
              value: 4000,
              type: 'equipment',
              sponsor: 'MonetizePro'
            }
          ],
          rules: [
            'Demonstrate measurable revenue increase',
            'Ethical monetization strategies only',
            'Provide transparent revenue reports',
            'Maintain audience engagement quality'
          ],
          requirements: [
            'Show minimum 35% revenue improvement',
            'Use platform monetization tools',
            'Document revenue optimization strategy',
            'Include audience engagement metrics'
          ],
          judges: [
            {
              id: 'judge-revenue-1',
              name: 'Lisa Business Strategy',
              avatar: '/judges/lisa-business.jpg',
              title: 'Revenue Optimization Specialist',
              bio: 'Expert in digital content monetization strategies',
              credentials: ['Business Strategy Expert', 'Revenue Growth Specialist', 'Digital Monetization Pioneer'],
              verified: true
            }
          ],
          isParticipating: true,
          hasSubmitted: false,
          entryFee: 50,
          sponsorBrands: ['Revenue Labs', 'MonetizePro', 'Business Analytics'],
          votingEnabled: false,
          publicVoting: false,
          featured: true
        },

        // 🌍 Global Competition
        {
          id: 'comp-global-1',
          title: 'Global Creative Championship 2025',
          description: 'The ultimate global creative competition. Creators worldwide compete for the title of Global Creative Champion with massive prizes.',
          theme: 'Global Creative Excellence',
          organizer: {
            id: 'org-4',
            name: 'Global Creative Council',
            avatar: '/organizers/global-council.jpg',
            verified: true,
            type: 'platform'
          },
          banner: '/competitions/global-championship.jpg',
          startDate: new Date(Date.now() + 86400000), // 1 day from now
          endDate: new Date(Date.now() + 3888000000), // 45 days from now
          submissionDeadline: new Date(Date.now() + 3715200000), // 43 days from now
          status: 'upcoming',
          category: 'Global Competition',
          difficulty: 'expert',
          maxParticipants: 10000,
          currentParticipants: 2847,
          totalSubmissions: 0,
          prizes: [
            {
              position: 1,
              title: 'Global Creative Champion',
              description: 'Lifetime premium access + $50,000 cash + Global recognition',
              value: 50000,
              type: 'cash',
              sponsor: 'Ainflue Global'
            },
            {
              position: 2,
              title: 'Global Runner-up',
              description: '$25,000 cash + Premium tools + International exposure',
              value: 25000,
              type: 'cash',
              sponsor: 'Creative Global'
            },
            {
              position: 3,
              title: 'Global Finalist',
              description: '$15,000 cash + Professional development package',
              value: 15000,
              type: 'cash',
              sponsor: 'Innovation Global'
            }
          ],
          rules: [
            'Open to creators worldwide',
            'Professional-quality submissions required',
            'Original content with global appeal',
            'Multi-cultural sensitivity required',
            'Must represent best creative work'
          ],
          requirements: [
            'Portfolio of your best work',
            'Global appeal demonstration',
            'Professional production quality',
            'Cultural diversity consideration',
            'Innovation and creativity showcase'
          ],
          judges: [
            {
              id: 'judge-global-1',
              name: 'International Creative Panel',
              avatar: '/judges/global-panel.jpg',
              title: 'Global Creative Experts',
              bio: 'Panel of international creative industry leaders',
              credentials: ['Global Creative Council', 'International Awards Panel', 'Industry Leaders'],
              verified: true
            }
          ],
          isParticipating: false,
          hasSubmitted: false,
          entryFee: 100,
          sponsorBrands: ['Ainflue Global', 'Creative Global', 'Innovation Global'],
          votingEnabled: true,
          publicVoting: true,
          featured: true
        },

        // Original competition (keeping existing one)
        {
          id: 'comp-1',
          title: 'AI Summer Remix Championship 2025',
          description: 'Create the ultimate summer anthem using AI-powered tools. Transform classic summer hits into modern masterpieces.',
          theme: 'Summer Vibes with AI Enhancement',
          organizer: {
            id: 'org-1',
            name: 'Ainflue Platform',
            avatar: '/organizers/ainflue.jpg',
            verified: true,
            type: 'platform'
          },
          banner: '/competitions/summer-remix.jpg',
          startDate: new Date(Date.now() - 604800000), // 7 days ago
          endDate: new Date(Date.now() + 1209600000), // 14 days from now
          submissionDeadline: new Date(Date.now() + 864000000), // 10 days from now
          status: 'active',
          category: 'Remix Competition',
          difficulty: 'intermediate',
          maxParticipants: 1000,
          currentParticipants: 342,
          totalSubmissions: 156,
          prizes: [
            {
              position: 1,
              title: 'Grand Prize',
              description: 'Cash prize + Recording studio session + Label contract consideration',
              value: 5000,
              type: 'cash',
              sponsor: 'Major Records'
            },
            {
              position: 2,
              title: 'Runner Up',
              description: 'Professional mixing & mastering + Equipment package',
              value: 2500,
              type: 'equipment',
              sponsor: 'Pro Audio Co'
            },
            {
              position: 3,
              title: 'Third Place',
              description: 'Platform credits + Feature on homepage',
              value: 1000,
              type: 'credits',
              sponsor: 'Ainflue'
            }
          ],
          rules: [
            'Original remixes only - no copyrighted material without permission',
            'Must use at least one AI tool from the platform',
            'Maximum duration: 6 minutes',
            'Submit in high quality WAV or FLAC format',
            'One submission per participant'
          ],
          requirements: [
            'Use provided summer-themed sample pack',
            'Include AI-generated elements (minimum 20% of track)',
            'Provide brief description of AI tools used',
            'Tag your submission with #AISummerRemix2025'
          ],
          judges: [
            {
              id: 'judge-1',
              name: 'Dr. Alex Producer',
              avatar: '/judges/alex.jpg',
              title: 'Grammy-winning Producer',
              bio: 'Multi-platinum producer with 15+ years in the industry',
              credentials: ['Grammy Award Winner', '50+ Gold Records', 'AI Music Pioneer'],
              verified: true
            },
            {
              id: 'judge-2',
              name: 'DJ Nova',
              avatar: '/judges/nova.jpg',
              title: 'International DJ & Artist',
              bio: 'World-renowned DJ with global festival experience',
              credentials: ['Top 10 DJ Mag', 'Tomorrowland Headliner', 'Record Label Owner'],
              verified: true
            }
          ],
          isParticipating: true,
          hasSubmitted: false,
          entryFee: 0,
          sponsorBrands: ['Major Records', 'Pro Audio Co', 'AI Music Labs'],
          votingEnabled: true,
          publicVoting: true,
          featured: false
        },
        {
          id: 'comp-2',
          title: 'Beat Battle Championship',
          description: 'The ultimate beat making competition. Create original beats that showcase your production skills and creativity.',
          theme: 'Original Beat Production',
          organizer: {
            id: 'org-2',
            name: 'Beat Collective',
            avatar: '/organizers/beat-collective.jpg',
            verified: true,
            type: 'brand'
          },
          banner: '/competitions/beat-battle.jpg',
          startDate: new Date(Date.now() + 86400000), // 1 day from now
          endDate: new Date(Date.now() + 2592000000), // 30 days from now
          submissionDeadline: new Date(Date.now() + 2419200000), // 28 days from now
          status: 'upcoming',
          category: 'Beat Battle',
          difficulty: 'advanced',
          maxParticipants: 500,
          currentParticipants: 89,
          totalSubmissions: 0,
          prizes: [
            {
              position: 1,
              title: 'Beat Master Champion',
              description: 'Professional studio time + Equipment sponsorship',
              value: 7500,
              type: 'equipment',
              sponsor: 'Studio Pro'
            }
          ],
          rules: [
            'Original beats only',
            'No samples from copyrighted material',
            'Minimum 2 minutes, maximum 4 minutes',
            'Include stems for verification'
          ],
          requirements: [
            'Must be 100% original production',
            'Include brief producer notes',
            'Submit in professional quality'
          ],
          judges: [
            {
              id: 'judge-3',
              name: 'Beat Master Mike',
              avatar: '/judges/mike.jpg',
              title: 'Legendary Hip-Hop Producer',
              bio: 'Producer for top hip-hop artists worldwide',
              credentials: ['Multi-Platinum Producer', 'BET Award Winner'],
              verified: true
            }
          ],
          isParticipating: false,
          hasSubmitted: false,
          entryFee: 25,
          sponsorBrands: ['Studio Pro', 'Beat Labs'],
          votingEnabled: false,
          publicVoting: false,
          featured: false
        },
        {
          id: 'comp-3',
          title: 'Vocal AI Innovation Challenge',
          description: 'Push the boundaries of vocal processing using AI. Create stunning vocal arrangements with cutting-edge technology.',
          theme: 'AI-Enhanced Vocal Production',
          organizer: {
            id: 'org-3',
            name: 'Vocal Tech Labs',
            avatar: '/organizers/vocal-tech.jpg',
            verified: true,
            type: 'brand'
          },
          banner: '/competitions/vocal-ai.jpg',
          startDate: new Date(Date.now() - 1209600000), // 14 days ago
          endDate: new Date(Date.now() - 86400000), // 1 day ago
          submissionDeadline: new Date(Date.now() - 172800000), // 2 days ago
          status: 'judging',
          category: 'Vocal Challenge',
          difficulty: 'professional',
          maxParticipants: 200,
          currentParticipants: 167,
          totalSubmissions: 134,
          prizes: [
            {
              position: 1,
              title: 'Vocal Innovation Award',
              description: 'AI Vocal Processing Suite + Mentorship Program',
              value: 3000,
              type: 'equipment',
              sponsor: 'Vocal Tech Labs'
            }
          ],
          rules: [
            'Must feature human vocals enhanced with AI',
            'Showcase innovative vocal processing',
            'Include before/after demonstration'
          ],
          requirements: [
            'Use platform vocal AI tools',
            'Submit original vocal recording',
            'Document AI enhancement process'
          ],
          judges: [
            {
              id: 'judge-4',
              name: 'Maria Vocal Expert',
              avatar: '/judges/maria.jpg',
              title: 'Vocal Production Specialist',
              bio: 'Expert in vocal processing and AI enhancement',
              credentials: ['Vocal Engineering Expert', 'AI Research Contributor'],
              verified: true
            }
          ],
          isParticipating: true,
          hasSubmitted: true,
          submissionId: 'sub-1',
          entryFee: 15,
          sponsorBrands: ['Vocal Tech Labs', 'AI Vocals Pro'],
          votingEnabled: true,
          publicVoting: false,
          featured: true
        }
      ];

      setCompetitions(mockCompetitions);
    } catch (error) {
      console.error('Failed to load competitions:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadFeaturedSubmissions = async () => {
    try {
      const mockSubmissions: Submission[] = [
        {
          id: 'sub-1',
          competitionId: 'comp-1',
          title: 'Summer AI Dreams',
          artist: {
            id: 'artist-1',
            name: 'AI Creator Pro',
            username: 'ai_creator_pro',
            avatar: '/artists/ai-creator.jpg',
            verified: true
          },
          thumbnail: '/submissions/summer-dreams.jpg',
          audioUrl: '/audio/summer-dreams.mp3',
          description: 'A dreamy summer remix enhanced with cutting-edge AI vocal processing and atmospheric soundscapes.',
          submittedAt: new Date(Date.now() - 172800000),
          votes: 234,
          plays: 1890,
          likes: 445,
          comments: 67,
          rank: 1,
          isWinner: false,
          awards: ['Most Innovative Use of AI'],
          tags: ['summer', 'ai', 'dreamy', 'vocals'],
          isLiked: false,
          hasVoted: false
        },
        {
          id: 'sub-2',
          competitionId: 'comp-1',
          title: 'Electric Sunset Remix',
          artist: {
            id: 'artist-2',
            name: 'Neon Producer',
            username: 'neon_beats',
            avatar: '/artists/neon-producer.jpg',
            verified: false
          },
          thumbnail: '/submissions/electric-sunset.jpg',
          audioUrl: '/audio/electric-sunset.mp3',
          description: 'High-energy electronic remix with AI-generated melodies and professional mixing.',
          submittedAt: new Date(Date.now() - 259200000),
          votes: 189,
          plays: 1567,
          likes: 312,
          comments: 45,
          rank: 2,
          isWinner: false,
          awards: ['Community Favorite'],
          tags: ['electronic', 'energetic', 'ai', 'remix'],
          isLiked: true,
          hasVoted: true
        }
      ];

      setFeaturedSubmissions(mockSubmissions);
    } catch (error) {
      console.error('Failed to load featured submissions:', error);
    }
  };

  const handleJoinCompetition = async (competitionId: string) => {
    try {
      setCompetitions(prev => prev.map(comp =>
        comp.id === competitionId
          ? { 
              ...comp, 
              isParticipating: true,
              currentParticipants: comp.currentParticipants + 1
            }
          : comp
      ));
    } catch (error) {
      console.error('Failed to join competition:', error);
    }
  };

  const handleVote = async (submissionId: string) => {
    try {
      setFeaturedSubmissions(prev => prev.map(sub =>
        sub.id === submissionId
          ? { 
              ...sub, 
              hasVoted: !sub.hasVoted,
              votes: sub.hasVoted ? sub.votes - 1 : sub.votes + 1
            }
          : sub
      ));
    } catch (error) {
      console.error('Failed to vote:', error);
    }
  };

  const handleLike = async (submissionId: string) => {
    try {
      setFeaturedSubmissions(prev => prev.map(sub =>
        sub.id === submissionId
          ? { 
              ...sub, 
              isLiked: !sub.isLiked,
              likes: sub.isLiked ? sub.likes - 1 : sub.likes + 1
            }
          : sub
      ));
    } catch (error) {
      console.error('Failed to like submission:', error);
    }
  };

  const handlePlay = (submissionId: string) => {
    setCurrentlyPlaying(currentlyPlaying === submissionId ? null : submissionId);
  };

  const formatTimeRemaining = (endDate: Date) => {
    const now = new Date();
    const diff = endDate.getTime() - now.getTime();
    
    if (diff <= 0) return 'Ended';
    
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (days > 0) return `${days}d ${hours}h remaining`;
    if (hours > 0) return `${hours}h ${minutes}m remaining`;
    return `${minutes}m remaining`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300';
      case 'upcoming':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300';
      case 'judging':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300';
      case 'completed':
        return 'bg-slate-100 text-slate-800 dark:bg-slate-900 dark:text-slate-300';
      default:
        return 'bg-slate-100 text-slate-800 dark:bg-slate-900 dark:text-slate-300';
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300';
      case 'intermediate':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300';
      case 'advanced':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300';
      case 'professional':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300';
      default:
        return 'bg-slate-100 text-slate-800 dark:bg-slate-900 dark:text-slate-300';
    }
  };

  const filteredCompetitions = competitions.filter(comp => {
    const matchesSearch = comp.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         comp.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         comp.theme.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesCategory = selectedCategory === 'all' || comp.category === selectedCategory;
    
    const matchesTab = activeTab === 'active' && comp.status === 'active' ||
                      activeTab === 'upcoming' && comp.status === 'upcoming' ||
                      activeTab === 'my-entries' && comp.isParticipating ||
                      activeTab === 'winners' && comp.status === 'completed';
    
    return matchesSearch && matchesCategory && matchesTab;
  });

  const renderCompetitionCard = (competition: Competition) => (
    <div key={competition.id} className={clsx(
      studioStyles.container.card,
      "overflow-hidden transition-all duration-200 hover:scale-105 hover:shadow-lg group"
    )}>
      {/* Banner */}
      <div className="relative h-48 bg-gradient-to-br from-purple-500 to-blue-500 overflow-hidden">
        {competition.featured && (
          <div className="absolute top-3 left-3">
            <span className="px-3 py-1 text-xs font-medium bg-yellow-600 text-white rounded-full flex items-center space-x-1">
              <StarIcon className="h-3 w-3" />
              <span>Featured</span>
            </span>
          </div>
        )}
        
        <div className="absolute top-3 right-3 flex flex-col space-y-2">
          <span className={clsx(
            "px-2 py-1 text-xs font-medium rounded-full",
            getStatusColor(competition.status)
          )}>
            {competition.status}
          </span>
          <span className={clsx(
            "px-2 py-1 text-xs font-medium rounded-full",
            getDifficultyColor(competition.difficulty)
          )}>
            {competition.difficulty}
          </span>
        </div>

        <div className="absolute bottom-3 left-3 text-white">
          <p className="text-xs opacity-90">{formatTimeRemaining(competition.endDate)}</p>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {/* Header */}
        <div className="mb-4">
          <h3 className="font-semibold text-slate-900 dark:text-white mb-2 line-clamp-2 group-hover:text-purple-600 transition-colors">
            {competition.title}
          </h3>
          <p className="text-sm text-slate-600 dark:text-slate-400 line-clamp-2 mb-3">
            {competition.description}
          </p>
          
          {/* Organizer */}
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-green-500 to-teal-500 flex items-center justify-center text-xs font-medium text-white">
              {competition.organizer.name.split(' ').map(n => n[0]).join('')}
            </div>
            <span className="text-sm text-slate-600 dark:text-slate-400">
              {competition.organizer.name}
              {competition.organizer.verified && (
                <span className="ml-1 text-blue-500">✓</span>
              )}
            </span>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
          <div className="text-center p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
            <p className="font-semibold text-slate-900 dark:text-white">
              {competition.currentParticipants.toLocaleString()}
            </p>
            <p className="text-xs text-slate-500">Participants</p>
          </div>
          <div className="text-center p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
            <p className="font-semibold text-slate-900 dark:text-white">
              {competition.totalSubmissions.toLocaleString()}
            </p>
            <p className="text-xs text-slate-500">Submissions</p>
          </div>
        </div>

        {/* Top Prize */}
        {competition.prizes.length > 0 && (
          <div className="mb-4 p-3 bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
            <div className="flex items-center space-x-2 mb-1">
              <TrophyIconSolid className="h-4 w-4 text-yellow-600" />
              <span className="font-medium text-yellow-800 dark:text-yellow-300">
                {competition.prizes[0].title}
              </span>
            </div>
            <p className="text-sm text-yellow-700 dark:text-yellow-400">
              ${competition.prizes[0].value.toLocaleString()} + {competition.prizes[0].description}
            </p>
          </div>
        )}

        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex items-center justify-between text-sm mb-1">
            <span className="text-slate-600 dark:text-slate-400">Participation</span>
            <span className="text-slate-900 dark:text-white font-medium">
              {Math.round((competition.currentParticipants / competition.maxParticipants) * 100)}%
            </span>
          </div>
          <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
            <div 
              className="bg-purple-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(competition.currentParticipants / competition.maxParticipants) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => router.push(`/remix/competitions/${competition.id}`)}
            className={clsx(studioStyles.buttons.secondary, "px-4 py-2")}
          >
            View Details
          </button>
          
          {competition.status === 'active' && !competition.isParticipating ? (
            <button
              onClick={() => handleJoinCompetition(competition.id)}
              className={clsx(studioStyles.buttons.primary, "px-4 py-2")}
            >
              {competition.entryFee ? `Join ($${competition.entryFee})` : 'Join Free'}
            </button>
          ) : competition.isParticipating && !competition.hasSubmitted ? (
            <button
              onClick={() => router.push(`/remix/studio?competition=${competition.id}`)}
              className={clsx(studioStyles.buttons.primary, "px-4 py-2")}
            >
              Submit Entry
            </button>
          ) : competition.hasSubmitted ? (
            <span className="flex items-center space-x-1 text-green-600 text-sm font-medium">
              <CheckCircleIcon className="h-4 w-4" />
              <span>Submitted</span>
            </span>
          ) : (
            <span className="text-sm text-slate-500">View Only</span>
          )}
        </div>
      </div>
    </div>
  );

  const renderSubmissionCard = (submission: Submission) => (
    <div key={submission.id} className={clsx(
      studioStyles.container.card,
      "p-4 transition-all duration-200 hover:shadow-lg"
    )}>
      <div className="flex items-start space-x-4">
        {/* Thumbnail with Play Button */}
        <div className="relative w-16 h-16 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg flex-shrink-0 group cursor-pointer">
          <button
            onClick={() => handlePlay(submission.id)}
            className="absolute inset-0 flex items-center justify-center"
          >
            {currentlyPlaying === submission.id ? (
              <PauseIcon className="h-6 w-6 text-white" />
            ) : (
              <PlayIcon className="h-6 w-6 text-white" />
            )}
          </button>
          
          {submission.rank && submission.rank <= 3 && (
            <div className="absolute -top-1 -right-1">
              <div className={clsx(
                "w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white",
                submission.rank === 1 && "bg-yellow-500",
                submission.rank === 2 && "bg-slate-400",
                submission.rank === 3 && "bg-orange-500"
              )}>
                {submission.rank}
              </div>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between mb-2">
            <div className="flex-1 min-w-0">
              <h4 className="font-medium text-slate-900 dark:text-white truncate">
                {submission.title}
              </h4>
              <div className="flex items-center space-x-2 mt-1">
                <div className="w-4 h-4 rounded-full bg-gradient-to-br from-green-500 to-teal-500"></div>
                <span className="text-sm text-slate-600 dark:text-slate-400">
                  {submission.artist.name}
                  {submission.artist.verified && (
                    <span className="ml-1 text-blue-500">✓</span>
                  )}
                </span>
              </div>
            </div>
            
            {submission.awards.length > 0 && (
              <div className="flex items-center space-x-1 ml-2">
                <TrophyIcon className="h-4 w-4 text-yellow-500" />
                <span className="text-xs text-yellow-600">{submission.awards[0]}</span>
              </div>
            )}
          </div>

          {/* Stats */}
          <div className="flex items-center space-x-4 text-sm text-slate-500 mb-2">
            <span className="flex items-center space-x-1">
              <PlayIcon className="h-3 w-3" />
              <span>{submission.plays.toLocaleString()}</span>
            </span>
            <span className="flex items-center space-x-1">
              <HeartIcon className="h-3 w-3" />
              <span>{submission.likes.toLocaleString()}</span>
            </span>
            {submission.votes > 0 && (
              <span className="flex items-center space-x-1">
                <StarIcon className="h-3 w-3" />
                <span>{submission.votes} votes</span>
              </span>
            )}
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => handleLike(submission.id)}
              className={clsx(
                "p-1 rounded transition-colors",
                submission.isLiked ? "text-red-500" : "text-slate-400 hover:text-red-500"
              )}
            >
              <HeartIcon className="h-4 w-4" />
            </button>
            
            {submission.votes > 0 && (
              <button
                onClick={() => handleVote(submission.id)}
                className={clsx(
                  "px-2 py-1 text-xs rounded transition-colors",
                  submission.hasVoted
                    ? "bg-purple-600 text-white"
                    : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-purple-50 dark:hover:bg-purple-900/20"
                )}
              >
                {submission.hasVoted ? 'Voted' : 'Vote'}
              </button>
            )}
            
            <button className="p-1 text-slate-400 hover:text-blue-500 rounded transition-colors">
              <ShareIcon className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'active':
      case 'upcoming':
        return (
          <div className="space-y-6">
            {/* Filters */}
            <div className="flex items-center space-x-4">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search competitions..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                />
              </div>
              
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
            </div>

            {/* Competitions Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredCompetitions.map(renderCompetitionCard)}
            </div>
          </div>
        );
      case 'my-entries':
        return (
          <div className="space-y-6">
            <div className={clsx(studioStyles.container.card, "p-6 text-center")}>
              <TrophyIcon className="h-12 w-12 text-purple-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
                Your Competition Journey
              </h3>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                Track your submissions and competition history
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
                <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
                  <p className="text-2xl font-bold text-purple-600">3</p>
                  <p className="text-sm text-slate-600 dark:text-slate-400">Active Entries</p>
                </div>
                <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
                  <p className="text-2xl font-bold text-green-600">2</p>
                  <p className="text-sm text-slate-600 dark:text-slate-400">Awards Won</p>
                </div>
                <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
                  <p className="text-2xl font-bold text-blue-600">$750</p>
                  <p className="text-sm text-slate-600 dark:text-slate-400">Total Winnings</p>
                </div>
              </div>
            </div>
          </div>
        );
      case 'winners':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
                Featured Winners
              </h3>
              <div className="space-y-4">
                {featuredSubmissions.map(renderSubmissionCard)}
              </div>
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
                  Competitions
                </h1>
                <p className="text-slate-600 dark:text-slate-400 mt-2">
                  Compete with creators worldwide and win amazing prizes
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/remix/studio')}
                className={clsx(studioStyles.buttons.secondary, "px-4 py-2")}
              >
                <MusicalNoteIcon className="h-5 w-5 mr-2" />
                Create Entry
              </button>
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
                <div className="h-48 bg-slate-200 dark:bg-slate-800 rounded-t-lg"></div>
                <div className="p-6">
                  <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded mb-2"></div>
                  <div className="h-3 bg-slate-200 dark:bg-slate-800 rounded w-2/3"></div>
                </div>
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

export default CompetitionsPage;