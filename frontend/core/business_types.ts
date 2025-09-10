/**
 * 🏢 Business Logic Types - Enterprise Business Domain Types
 * 
 * @fileoverview Core business logic types for Ainflue creator economy platform
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

// ====================================================================
// SEO CONFIGURATION TYPES
// ====================================================================

export interface SEOConfiguration {
  enabled: boolean;
  providers: SEOProvider[];
  defaultSettings: SEOSettings;
  platformConfigs: Record<string, PlatformSEOConfig>;
  analytics: SEOAnalyticsConfig;
  automation: SEOAutomationConfig;
}

export interface SEOProvider {
  id: string;
  name: string;
  type: 'search' | 'social' | 'video' | 'blog';
  apiKey?: string;
  config: Record<string, any>;
}

export interface SEOSettings {
  autoOptimize: boolean;
  keywordDensity: [number, number]; // [min, max]
  titleLength: [number, number];
  descriptionLength: [number, number];
  language: string;
  region: string;
}

export interface PlatformSEOConfig {
  platformId: string;
  enabled: boolean;
  titleTemplate: string;
  descriptionTemplate: string;
  hashtagStrategy: HashtagStrategy;
  customFields: Record<string, any>;
}

export interface HashtagStrategy {
  count: [number, number]; // [min, max]
  trending: boolean;
  niche: boolean;
  branded: boolean;
  location: boolean;
}

export interface SEOAnalyticsConfig {
  tracking: boolean;
  providers: string[];
  metrics: string[];
  reporting: ReportingConfig;
}

export interface ReportingConfig {
  frequency: 'daily' | 'weekly' | 'monthly';
  recipients: string[];
  format: 'pdf' | 'json' | 'csv';
}

export interface SEOAutomationConfig {
  contentOptimization: boolean;
  keywordSuggestions: boolean;
  performanceTracking: boolean;
  competitorAnalysis: boolean;
}

export interface SEOAnalysis {
  wordCount: number;
  sentenceCount: number;
  readabilityScore: number;
  keywords: string[];
  keywordDensity: number;
  sentiment: 'positive' | 'neutral' | 'negative';
  topics: string[];
  recommendations: string[];
}

export interface PlatformSEOStrategy {
  platformId: string;
  title: string;
  description: string;
  keywords: string[];
  hashtags: string[];
  optimizations: SEOOptimization[];
}

export interface SEOOptimization {
  type: 'title' | 'description' | 'keywords' | 'hashtags' | 'content';
  original: string;
  optimized: string;
  improvement: number;
  reason: string;
}

export interface ContentOptimization {
  title: string;
  description: string;
  keywords: string[];
  hashtags: string[];
  customFields: Record<string, any>;
}

// ====================================================================
// UPLOAD CONFIGURATION TYPES
// ====================================================================

export interface UploadConfiguration {
  maxFileSize: number;
  allowedTypes: string[];
  chunkSize: number;
  concurrentUploads: number;
  autoProcessing: boolean;
  compression: CompressionConfig;
  security: UploadSecurityConfig;
  storage: StorageConfig;
  cdn: CDNConfig;
}

export interface CompressionConfig {
  enabled: boolean;
  quality: number; // 0-100
  formats: Record<string, CompressionFormat>;
}

export interface CompressionFormat {
  enabled: boolean;
  quality: number;
  maxSize: number;
  targetFormat?: string;
}

export interface UploadSecurityConfig {
  virusScanning: boolean;
  contentModeration: boolean;
  encryption: boolean;
  watermarking: boolean;
  accessControl: AccessControlConfig;
}

export interface AccessControlConfig {
  defaultPrivacy: 'public' | 'private' | 'unlisted';
  allowGuests: boolean;
  requireVerification: boolean;
  ipWhitelist: string[];
}

export interface StorageConfig {
  provider: 'aws' | 'gcp' | 'azure' | 'local';
  bucket: string;
  region: string;
  redundancy: boolean;
  lifecycle: LifecycleConfig;
}

export interface LifecycleConfig {
  archiveAfter: number; // days
  deleteAfter: number; // days
  compressionAfter: number; // days
}

export interface CDNConfig {
  enabled: boolean;
  provider: string;
  domains: string[];
  caching: CachingConfig;
  optimization: CDNOptimizationConfig;
}

export interface CachingConfig {
  ttl: number; // seconds
  strategy: 'aggressive' | 'balanced' | 'conservative';
  purgeOnUpdate: boolean;
}

export interface CDNOptimizationConfig {
  imageOptimization: boolean;
  videoOptimization: boolean;
  gzipCompression: boolean;
  brotliCompression: boolean;
}

export interface UploadProgress {
  current: number;
  total: number;
  percentage: number;
}

export interface FileMetadata {
  name: string;
  size: number;
  type: string;
  lastModified: number;
  extension: string;
  uploadTime: number;
  checksum?: string;
  encoding?: string;
  dimensions?: {
    width: number;
    height: number;
  };
  duration?: number; // for media files
  [key: string]: any;
}

// ====================================================================
// MONETIZATION TYPES
// ====================================================================

export interface MonetizationConfig {
  enabled: boolean;
  strategies: MonetizationStrategy[];
  paymentProviders: PaymentProvider[];
  pricing: PricingConfig;
  subscriptions: SubscriptionConfig;
  marketplace: MarketplaceConfig;
}

export interface MonetizationStrategy {
  id: string;
  name: string;
  type: 'subscription' | 'one-time' | 'tips' | 'advertising' | 'affiliate' | 'licensing';
  enabled: boolean;
  config: Record<string, any>;
}

export interface PaymentProvider {
  id: string;
  name: string;
  type: 'stripe' | 'paypal' | 'crypto' | 'bank';
  apiKey: string;
  config: Record<string, any>;
  fees: FeeStructure;
}

export interface FeeStructure {
  percentage: number;
  fixed: number;
  currency: string;
  minimumAmount: number;
  maximumAmount?: number;
}

export interface PricingConfig {
  currency: string;
  tiers: PricingTier[];
  discounts: DiscountConfig[];
  localPricing: boolean;
}

export interface PricingTier {
  id: string;
  name: string;
  price: number;
  features: string[];
  limitations: Record<string, number>;
  popular: boolean;
}

export interface DiscountConfig {
  type: 'percentage' | 'fixed' | 'trial';
  value: number;
  conditions: DiscountCondition[];
  duration?: number;
}

export interface DiscountCondition {
  type: 'new_user' | 'bulk' | 'loyalty' | 'referral' | 'seasonal';
  value: any;
  description: string;
}

export interface SubscriptionConfig {
  enabled: boolean;
  plans: SubscriptionPlan[];
  billing: BillingConfig;
  management: SubscriptionManagement;
}

export interface SubscriptionPlan {
  id: string;
  name: string;
  price: number;
  interval: 'month' | 'year' | 'week';
  features: PlanFeature[];
  limitations: PlanLimitation[];
  trial: TrialConfig;
}

export interface PlanFeature {
  name: string;
  description: string;
  included: boolean;
  value?: number | string;
}

export interface PlanLimitation {
  resource: string;
  limit: number;
  unit: string;
}

export interface TrialConfig {
  enabled: boolean;
  duration: number; // days
  features: string[];
  requirePayment: boolean;
}

export interface BillingConfig {
  automatic: boolean;
  invoicing: boolean;
  reminders: ReminderConfig[];
  gracePeriod: number; // days
}

export interface ReminderConfig {
  type: 'email' | 'sms' | 'push';
  timing: number; // days before/after
  template: string;
}

export interface SubscriptionManagement {
  selfService: boolean;
  upgrades: boolean;
  downgrades: boolean;
  cancellation: CancellationConfig;
}

export interface CancellationConfig {
  immediate: boolean;
  endOfPeriod: boolean;
  retentionOffers: boolean;
  feedbackRequired: boolean;
}

export interface MarketplaceConfig {
  enabled: boolean;
  commission: number; // percentage
  categories: MarketplaceCategory[];
  curation: CurationConfig;
  promotion: PromotionConfig;
}

export interface MarketplaceCategory {
  id: string;
  name: string;
  description: string;
  commission: number;
  requirements: string[];
}

export interface CurationConfig {
  automatic: boolean;
  manual: boolean;
  criteria: CurationCriteria[];
}

export interface CurationCriteria {
  type: 'quality' | 'relevance' | 'popularity' | 'safety';
  weight: number;
  threshold: number;
}

export interface PromotionConfig {
  featured: boolean;
  recommendations: boolean;
  crossPromotion: boolean;
  algorithms: string[];
}

// ====================================================================
// COLLABORATION TYPES
// ====================================================================

export interface CollaborationConfig {
  enabled: boolean;
  types: CollaborationType[];
  matching: MatchingConfig;
  communication: CommunicationConfig;
  workflow: WorkflowConfig;
}

export interface CollaborationType {
  id: string;
  name: string;
  description: string;
  roles: CollaborationRole[];
  workflow: string[];
  compensation: CompensationModel;
}

export interface CollaborationRole {
  id: string;
  name: string;
  permissions: string[];
  responsibilities: string[];
  skillsRequired: string[];
}

export interface CompensationModel {
  type: 'split' | 'fixed' | 'hybrid' | 'equity';
  structure: CompensationStructure;
  terms: CompensationTerms;
}

export interface CompensationStructure {
  baseAmount?: number;
  percentage?: number;
  bonuses: BonusStructure[];
  equity?: EquityStructure;
}

export interface BonusStructure {
  trigger: string;
  amount: number;
  type: 'fixed' | 'percentage';
  conditions: string[];
}

export interface EquityStructure {
  percentage: number;
  vestingPeriod: number; // months
  cliffPeriod: number; // months
  conditions: string[];
}

export interface CompensationTerms {
  paymentSchedule: 'immediate' | 'milestone' | 'completion' | 'revenue';
  currency: string;
  minimumPayout: number;
  maximumPayout?: number;
}

export interface MatchingConfig {
  algorithm: 'manual' | 'ai' | 'hybrid';
  criteria: MatchingCriteria[];
  scoring: ScoringConfig;
}

export interface MatchingCriteria {
  factor: string;
  weight: number;
  required: boolean;
  preferences: any;
}

export interface ScoringConfig {
  method: 'weighted' | 'ml' | 'composite';
  factors: ScoringFactor[];
  threshold: number;
}

export interface ScoringFactor {
  name: string;
  weight: number;
  normalization: 'linear' | 'log' | 'sigmoid';
}

export interface CommunicationConfig {
  channels: CommunicationChannel[];
  moderation: ModerationConfig;
  translation: TranslationConfig;
}

export interface CommunicationChannel {
  type: 'chat' | 'video' | 'voice' | 'comments' | 'reviews';
  enabled: boolean;
  features: string[];
  restrictions: ChannelRestriction[];
}

export interface ChannelRestriction {
  type: 'time' | 'participants' | 'content' | 'frequency';
  value: any;
  reason: string;
}

export interface ModerationConfig {
  automatic: boolean;
  manual: boolean;
  rules: ModerationRule[];
  actions: ModerationAction[];
}

export interface ModerationRule {
  trigger: string;
  condition: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  action: string;
}

export interface ModerationAction {
  type: 'warn' | 'mute' | 'restrict' | 'ban' | 'escalate';
  duration?: number;
  automatic: boolean;
  appealable: boolean;
}

export interface TranslationConfig {
  enabled: boolean;
  automatic: boolean;
  languages: string[];
  provider: string;
  confidence: number;
}

export interface WorkflowConfig {
  templates: WorkflowTemplate[];
  customization: boolean;
  automation: WorkflowAutomation;
}

export interface WorkflowTemplate {
  id: string;
  name: string;
  type: string;
  stages: WorkflowStage[];
  roles: string[];
  duration: number; // days
}

export interface WorkflowStage {
  id: string;
  name: string;
  description: string;
  order: number;
  requirements: StageRequirement[];
  deliverables: string[];
  duration: number; // days
  dependencies: string[];
}

export interface StageRequirement {
  type: 'approval' | 'deliverable' | 'milestone' | 'payment';
  description: string;
  required: boolean;
  validator: string;
}

export interface WorkflowAutomation {
  enabled: boolean;
  triggers: AutomationTrigger[];
  actions: AutomationAction[];
  conditions: AutomationCondition[];
}

export interface AutomationTrigger {
  event: string;
  source: string;
  conditions: string[];
}

export interface AutomationAction {
  type: string;
  target: string;
  parameters: Record<string, any>;
  delay?: number;
}

export interface AutomationCondition {
  field: string;
  operator: string;
  value: any;
  logic: 'and' | 'or';
}

// ====================================================================
// DISTRIBUTION TYPES
// ====================================================================

export interface DistributionConfig {
  platforms: DistributionPlatform[];
  scheduling: SchedulingConfig;
  optimization: DistributionOptimization;
  analytics: DistributionAnalytics;
}

export interface DistributionPlatform {
  id: string;
  name: string;
  type: 'social' | 'video' | 'audio' | 'blog' | 'marketplace';
  enabled: boolean;
  credentials: PlatformCredentials;
  settings: PlatformSettings;
  quotas: PlatformQuotas;
}

export interface PlatformCredentials {
  oauth?: OAuthCredentials;
  apiKey?: string;
  webhook?: string;
  refreshToken?: string;
  expiresAt?: number;
}

export interface OAuthCredentials {
  clientId: string;
  clientSecret: string;
  accessToken: string;
  scope: string[];
  redirectUri: string;
}

export interface PlatformSettings {
  autoPublish: boolean;
  optimization: boolean;
  cropping: CroppingSettings;
  formatting: FormattingSettings;
  metadata: MetadataSettings;
}

export interface CroppingSettings {
  enabled: boolean;
  aspectRatios: string[];
  smartCrop: boolean;
  faceDetection: boolean;
}

export interface FormattingSettings {
  autoFormat: boolean;
  supportedFormats: string[];
  qualitySettings: QualitySettings;
  compressionSettings: CompressionSettings;
}

export interface QualitySettings {
  video: VideoQuality;
  audio: AudioQuality;
  image: ImageQuality;
}

export interface VideoQuality {
  resolution: string;
  bitrate: number;
  fps: number;
  codec: string;
}

export interface AudioQuality {
  bitrate: number;
  sampleRate: number;
  channels: number;
  codec: string;
}

export interface ImageQuality {
  resolution: [number, number];
  quality: number;
  format: string;
  compression: string;
}

export interface CompressionSettings {
  enabled: boolean;
  quality: number;
  maxSize: number;
  preserveMetadata: boolean;
}

export interface MetadataSettings {
  title: MetadataField;
  description: MetadataField;
  tags: MetadataField;
  category: MetadataField;
  thumbnail: MetadataField;
  custom: Record<string, MetadataField>;
}

export interface MetadataField {
  enabled: boolean;
  required: boolean;
  maxLength?: number;
  format?: string;
  validation?: string;
}

export interface PlatformQuotas {
  daily: QuotaLimit;
  weekly: QuotaLimit;
  monthly: QuotaLimit;
  concurrent: QuotaLimit;
}

export interface QuotaLimit {
  posts: number;
  uploads: number;
  apiCalls: number;
  bandwidth: number; // MB
}

export interface SchedulingConfig {
  enabled: boolean;
  timezone: string;
  slots: SchedulingSlot[];
  optimization: SchedulingOptimization;
}

export interface SchedulingSlot {
  platform: string;
  dayOfWeek: number; // 0-6
  time: string; // HH:MM
  priority: number;
  conditions?: SchedulingCondition[];
}

export interface SchedulingCondition {
  type: 'audience' | 'engagement' | 'competition' | 'trending';
  operator: string;
  value: any;
}

export interface SchedulingOptimization {
  aiOptimization: boolean;
  audienceAnalysis: boolean;
  competitorTracking: boolean;
  engagementPrediction: boolean;
}

export interface DistributionOptimization {
  contentAdaptation: boolean;
  platformSpecific: boolean;
  audienceTargeting: boolean;
  performanceOptimization: boolean;
}

export interface DistributionAnalytics {
  realTime: boolean;
  metrics: AnalyticsMetric[];
  reporting: AnalyticsReporting;
  integration: AnalyticsIntegration;
}

export interface AnalyticsMetric {
  name: string;
  type: 'counter' | 'gauge' | 'histogram' | 'rate';
  aggregation: 'sum' | 'avg' | 'max' | 'min' | 'count';
  retention: number; // days
}

export interface AnalyticsReporting {
  frequency: 'real-time' | 'hourly' | 'daily' | 'weekly' | 'monthly';
  format: 'dashboard' | 'email' | 'api' | 'webhook';
  recipients: string[];
  customization: boolean;
}

export interface AnalyticsIntegration {
  googleAnalytics: boolean;
  facebookPixel: boolean;
  customTracking: boolean;
  dataExport: DataExportConfig;
}

export interface DataExportConfig {
  enabled: boolean;
  formats: string[];
  frequency: string;
  destination: ExportDestination;
}

export interface ExportDestination {
  type: 's3' | 'ftp' | 'email' | 'webhook';
  config: Record<string, any>;
  credentials: Record<string, string>;
}

// ====================================================================
// CONTENT TYPES
// ====================================================================

export interface ContentType {
  id: string;
  name: string;
  category: 'text' | 'image' | 'video' | 'audio' | 'document' | 'interactive';
  formats: string[];
  processing: ProcessingConfig;
  validation: ValidationConfig;
}

export interface ProcessingConfig {
  required: ProcessingStep[];
  optional: ProcessingStep[];
  automation: boolean;
  quality: QualityConfig;
}

export interface ProcessingStep {
  id: string;
  name: string;
  type: 'compression' | 'conversion' | 'enhancement' | 'analysis' | 'watermarking';
  config: Record<string, any>;
  duration: number; // estimated seconds
}

export interface QualityConfig {
  minimum: number; // 0-100
  target: number; // 0-100
  enhancement: boolean;
  validation: QualityValidation;
}

export interface QualityValidation {
  enabled: boolean;
  criteria: QualityCriteria[];
  actions: QualityAction[];
}

export interface QualityCriteria {
  metric: string;
  threshold: number;
  weight: number;
}

export interface QualityAction {
  trigger: string;
  action: 'accept' | 'enhance' | 'reject' | 'manual_review';
  parameters: Record<string, any>;
}

export interface ValidationConfig {
  rules: ValidationRule[];
  sanitization: SanitizationConfig;
  scanning: ScanningConfig;
}

export interface ValidationRule {
  field: string;
  type: 'required' | 'format' | 'size' | 'content' | 'metadata';
  value: any;
  message: string;
}

export interface SanitizationConfig {
  enabled: boolean;
  rules: SanitizationRule[];
  preserveOriginal: boolean;
}

export interface SanitizationRule {
  type: 'remove' | 'replace' | 'encode' | 'validate';
  pattern: string;
  replacement?: string;
  description: string;
}

export interface ScanningConfig {
  virus: boolean;
  malware: boolean;
  content: boolean;
  metadata: boolean;
  providers: ScanningProvider[];
}

export interface ScanningProvider {
  name: string;
  type: 'virus' | 'content' | 'metadata';
  apiKey: string;
  config: Record<string, any>;
}