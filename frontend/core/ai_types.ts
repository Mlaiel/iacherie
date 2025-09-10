/**
 * 🤖 AI Core Types - Enterprise AI System Types
 * 
 * @fileoverview Core TypeScript interfaces and types for AI processing systems
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

// ====================================================================
// AI CONFIGURATION TYPES
// ====================================================================

export interface AIConfiguration {
  providers?: {
    openai?: {
      apiKey: string;
      organization?: string;
      baseURL?: string;
    };
    anthropic?: {
      apiKey: string;
      baseURL?: string;
    };
    midjourney?: {
      apiKey: string;
      serverId?: string;
      channelId?: string;
    };
    elevenlabs?: {
      apiKey: string;
      voiceId?: string;
    };
    replicate?: {
      apiKey: string;
    };
    huggingface?: {
      apiKey: string;
    };
  };
  defaultProvider: string;
  maxConcurrentRequests: number;
  timeout: number;
  retryAttempts: number;
  cacheTTL: number;
  rateLimit: {
    requestsPerMinute: number;
    tokensPerMinute?: number;
  };
}

export interface AIProvider {
  id: string;
  name: string;
  type: 'text' | 'image' | 'audio' | 'video' | 'multimodal';
  capabilities: AICapability[];
  pricing: ProviderPricing;
  rateLimits: RateLimits;
  config: Record<string, any>;
  status?: 'online' | 'offline' | 'limited';
  lastHealthCheck?: number;
}

export type AICapability = 
  | 'text-generation'
  | 'text-completion' 
  | 'text-editing'
  | 'text-summarization'
  | 'text-translation'
  | 'text-analysis'
  | 'sentiment-analysis'
  | 'content-moderation'
  | 'keyword-extraction'
  | 'image-generation'
  | 'image-editing'
  | 'image-analysis'
  | 'image-enhancement'
  | 'image-upscaling'
  | 'audio-generation'
  | 'audio-transcription'
  | 'audio-enhancement'
  | 'audio-separation'
  | 'voice-cloning'
  | 'video-generation'
  | 'video-editing'
  | 'video-analysis'
  | 'object-detection'
  | 'face-recognition'
  | 'code-generation'
  | 'code-analysis';

export interface ProviderPricing {
  model: 'pay-per-use' | 'subscription' | 'freemium';
  costPer1K?: number; // Cost per 1000 tokens/operations
  monthlySubscription?: number;
  freeQuota?: number;
  currency: string;
}

export interface RateLimits {
  requestsPerMinute: number;
  requestsPerHour?: number;
  requestsPerDay?: number;
  tokensPerMinute?: number;
  tokensPerDay?: number;
  concurrentRequests?: number;
  [key: string]: number | undefined;
}

// ====================================================================
// AI PROCESSING TYPES
// ====================================================================

export interface AIProcessingRequest {
  id?: string;
  type: AICapability;
  provider?: string;
  input: any;
  options?: AIProcessingOptions;
  priority?: 'low' | 'normal' | 'high' | 'urgent';
  metadata?: Record<string, any>;
  callback?: string; // Webhook URL for async processing
}

export interface AIProcessingOptions {
  temperature?: number;
  maxTokens?: number;
  topP?: number;
  topK?: number;
  frequencyPenalty?: number;
  presencePenalty?: number;
  stopSequences?: string[];
  seed?: number;
  format?: string;
  quality?: 'low' | 'medium' | 'high' | 'ultra';
  style?: string;
  model?: string;
  language?: string;
  voice?: string;
  speed?: number;
  cache?: boolean;
  stream?: boolean;
  [key: string]: any;
}

export interface AIProcessingResult {
  id: string;
  requestId: string;
  status: 'completed' | 'failed' | 'partial';
  result: any;
  metadata: AIResultMetadata;
  error?: AIError;
  usage?: UsageMetrics;
  processingTime: number;
  providerId: string;
  timestamp: number;
}

export interface AIResultMetadata {
  model: string;
  version: string;
  confidence?: number;
  quality?: number;
  accuracy?: number;
  flags?: string[];
  tokens?: TokenUsage;
  dimensions?: ImageDimensions;
  duration?: number;
  sampleRate?: number;
  format?: string;
  size?: number;
  checksum?: string;
}

export interface TokenUsage {
  prompt: number;
  completion: number;
  total: number;
  estimatedCost?: number;
}

export interface ImageDimensions {
  width: number;
  height: number;
  channels?: number;
  colorSpace?: string;
}

export interface UsageMetrics {
  tokensUsed: number;
  requestsUsed: number;
  processingTime: number;
  cost: number;
  quotaRemaining?: number;
  resetTime?: number;
}

export interface AIError {
  code: string;
  message: string;
  type: 'authentication' | 'quota_exceeded' | 'invalid_request' | 'server_error' | 'timeout' | 'unknown';
  details?: any;
  retryable: boolean;
  retryAfter?: number;
}

// ====================================================================
// CONTENT ANALYSIS TYPES
// ====================================================================

export interface ContentAnalysis {
  type: 'text' | 'image' | 'audio' | 'video';
  content: any;
  analysis: AnalysisResult;
  metadata: ContentMetadata;
  timestamp: number;
}

export interface AnalysisResult {
  sentiment?: SentimentAnalysis;
  topics?: TopicAnalysis;
  entities?: EntityAnalysis;
  keywords?: KeywordAnalysis;
  quality?: QualityAnalysis;
  safety?: SafetyAnalysis;
  objects?: ObjectDetection[];
  faces?: FaceDetection[];
  text?: TextExtraction;
  audio?: AudioAnalysis;
  performance?: PerformanceAnalysis;
}

export interface SentimentAnalysis {
  overall: 'positive' | 'negative' | 'neutral';
  confidence: number;
  scores: {
    positive: number;
    negative: number;
    neutral: number;
  };
  emotions?: EmotionScores;
}

export interface EmotionScores {
  joy: number;
  sadness: number;
  anger: number;
  fear: number;
  surprise: number;
  disgust: number;
  trust: number;
  anticipation: number;
}

export interface TopicAnalysis {
  primaryTopic: string;
  topics: TopicScore[];
  categories: CategoryScore[];
  tags: string[];
}

export interface TopicScore {
  topic: string;
  confidence: number;
  relevance: number;
}

export interface CategoryScore {
  category: string;
  confidence: number;
  subcategories?: string[];
}

export interface EntityAnalysis {
  persons: NamedEntity[];
  organizations: NamedEntity[];
  locations: NamedEntity[];
  products: NamedEntity[];
  events: NamedEntity[];
  other: NamedEntity[];
}

export interface NamedEntity {
  text: string;
  type: string;
  confidence: number;
  mentions: number;
  salience: number;
}

export interface KeywordAnalysis {
  primary: Keyword[];
  secondary: Keyword[];
  longtail: Keyword[];
  density: number;
  distribution: KeywordDistribution;
}

export interface Keyword {
  term: string;
  frequency: number;
  relevance: number;
  position: number[];
  variations: string[];
}

export interface KeywordDistribution {
  title: number;
  beginning: number;
  middle: number;
  end: number;
}

export interface QualityAnalysis {
  overall: number; // 0-100
  readability: number;
  engagement: number;
  originality: number;
  coherence: number;
  completeness: number;
  issues: QualityIssue[];
}

export interface QualityIssue {
  type: 'grammar' | 'spelling' | 'style' | 'structure' | 'clarity';
  severity: 'low' | 'medium' | 'high';
  message: string;
  position?: number;
  suggestions?: string[];
}

export interface SafetyAnalysis {
  overall: 'safe' | 'caution' | 'unsafe';
  categories: SafetyCategory[];
  flags: SafetyFlag[];
  ageRating: string;
  contentWarnings: string[];
}

export interface SafetyCategory {
  category: 'adult' | 'violence' | 'hate' | 'harassment' | 'illegal' | 'spam' | 'medical' | 'financial';
  likelihood: 'very_unlikely' | 'unlikely' | 'possible' | 'likely' | 'very_likely';
  confidence: number;
}

export interface SafetyFlag {
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  action: 'none' | 'warning' | 'review' | 'block';
}

export interface ObjectDetection {
  object: string;
  confidence: number;
  boundingBox: BoundingBox;
  attributes?: Record<string, any>;
}

export interface FaceDetection {
  confidence: number;
  boundingBox: BoundingBox;
  landmarks?: FaceLandmark[];
  attributes?: FaceAttributes;
  emotions?: EmotionScores;
}

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface FaceLandmark {
  type: string;
  x: number;
  y: number;
  confidence: number;
}

export interface FaceAttributes {
  age?: number;
  gender?: string;
  ethnicity?: string;
  expressions?: Record<string, number>;
  accessories?: string[];
}

export interface TextExtraction {
  text: string;
  confidence: number;
  language: string;
  blocks: TextBlock[];
  words: TextWord[];
}

export interface TextBlock {
  text: string;
  boundingBox: BoundingBox;
  confidence: number;
}

export interface TextWord {
  text: string;
  confidence: number;
  boundingBox: BoundingBox;
}

export interface AudioAnalysis {
  duration: number;
  sampleRate: number;
  channels: number;
  bitRate: number;
  format: string;
  loudness: LoudnessAnalysis;
  frequency: FrequencyAnalysis;
  tempo?: TempoAnalysis;
  key?: string;
  energy: number;
  speechSegments?: SpeechSegment[];
  musicSegments?: MusicSegment[];
}

export interface LoudnessAnalysis {
  peak: number;
  rms: number;
  lufs: number;
  dynamic_range: number;
}

export interface FrequencyAnalysis {
  dominant: number;
  spectrum: number[];
  centroid: number;
  rolloff: number;
  zcr: number;
}

export interface TempoAnalysis {
  bpm: number;
  confidence: number;
  beats: number[];
  timeSignature?: string;
}

export interface SpeechSegment {
  start: number;
  end: number;
  text?: string;
  confidence?: number;
  speaker?: string;
  language?: string;
}

export interface MusicSegment {
  start: number;
  end: number;
  genre?: string;
  energy: number;
  valence: number;
  tempo?: number;
}

export interface PerformanceAnalysis {
  processingTime: number;
  memoryUsage: number;
  cpuUsage: number;
  gpuUsage?: number;
  networkUsage: number;
  cacheHits: number;
  errors: number;
  warnings: number[];
}

export interface ContentMetadata {
  source: string;
  format: string;
  size: number;
  created: number;
  modified: number;
  version: string;
  checksum: string;
  encoding?: string;
  compression?: string;
  origin?: string;
  author?: string;
  title?: string;
  description?: string;
  tags?: string[];
  custom?: Record<string, any>;
}

// ====================================================================
// AI OPTIMIZATION TYPES
// ====================================================================

export interface AIOptimization {
  type: 'content' | 'seo' | 'performance' | 'engagement';
  target: OptimizationTarget;
  strategy: OptimizationStrategy;
  metrics: OptimizationMetrics;
  recommendations: Recommendation[];
}

export interface OptimizationTarget {
  platform: string;
  audience: AudienceProfile;
  goals: OptimizationGoal[];
  constraints: OptimizationConstraint[];
}

export interface AudienceProfile {
  demographics: Demographics;
  interests: string[];
  behavior: BehaviorProfile;
  preferences: UserPreferences;
}

export interface Demographics {
  ageRange: [number, number];
  gender: string[];
  location: string[];
  language: string[];
  education: string[];
  income: string[];
}

export interface BehaviorProfile {
  engagementPatterns: EngagementPattern[];
  contentPreferences: ContentPreference[];
  deviceUsage: DeviceUsage;
  timePatterns: TimePattern[];
}

export interface EngagementPattern {
  action: string;
  frequency: number;
  duration: number;
  context: string[];
}

export interface ContentPreference {
  type: string;
  topics: string[];
  formats: string[];
  length: 'short' | 'medium' | 'long';
  style: string[];
}

export interface DeviceUsage {
  mobile: number;
  desktop: number;
  tablet: number;
  smart_tv: number;
  other: number;
}

export interface TimePattern {
  dayOfWeek: string;
  timeRange: [string, string];
  timezone: string;
  activity: number;
}

export interface UserPreferences {
  themes: string[];
  colors: string[];
  fonts: string[];
  layouts: string[];
  interactions: string[];
  accessibility: AccessibilityPreferences;
}

export interface AccessibilityPreferences {
  screenReader: boolean;
  highContrast: boolean;
  largeText: boolean;
  reducedMotion: boolean;
  audioDescriptions: boolean;
  captions: boolean;
}

export interface OptimizationGoal {
  metric: string;
  target: number;
  priority: 'low' | 'medium' | 'high' | 'critical';
  timeline: string;
}

export interface OptimizationConstraint {
  type: string;
  value: any;
  description: string;
}

export interface OptimizationStrategy {
  approach: 'aggressive' | 'balanced' | 'conservative';
  techniques: string[];
  timeline: string;
  phases: StrategyPhase[];
}

export interface StrategyPhase {
  name: string;
  duration: string;
  goals: string[];
  actions: string[];
  metrics: string[];
}

export interface OptimizationMetrics {
  baseline: Record<string, number>;
  target: Record<string, number>;
  current: Record<string, number>;
  improvement: Record<string, number>;
  roi: number;
}

export interface Recommendation {
  id: string;
  type: 'content' | 'technical' | 'strategic';
  priority: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  impact: ImpactAssessment;
  effort: EffortAssessment;
  implementation: ImplementationGuide;
  rationale: string;
  evidence: Evidence[];
}

export interface ImpactAssessment {
  overall: 'low' | 'medium' | 'high';
  metrics: Record<string, number>;
  confidence: number;
  timeline: string;
}

export interface EffortAssessment {
  overall: 'low' | 'medium' | 'high';
  time: string;
  resources: string[];
  complexity: number;
  risk: string;
}

export interface ImplementationGuide {
  steps: ImplementationStep[];
  requirements: string[];
  tools: string[];
  timeline: string;
  validation: ValidationCriteria[];
}

export interface ImplementationStep {
  order: number;
  title: string;
  description: string;
  duration: string;
  dependencies: string[];
  deliverables: string[];
}

export interface ValidationCriteria {
  metric: string;
  method: string;
  threshold: number;
  frequency: string;
}

export interface Evidence {
  type: 'data' | 'research' | 'case_study' | 'benchmark';
  source: string;
  description: string;
  relevance: number;
  credibility: number;
  date: string;
  url?: string;
}

// ====================================================================
// EXPORT ALL TYPES
// ====================================================================

export * from './api.types';
export * from './ui.types';
export * from './business.types';