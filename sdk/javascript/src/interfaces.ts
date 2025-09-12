/**
 * API Interface Definitions for Ainflue SDK
 * 
 * Multi-expert implementation:
 * - Backend Senior: Robust API interface design with type safety
 * - Lead Dev IA: Intelligent API patterns and optimization
 * - DBA: Optimized data structure interfaces
 * - DevOps: Monitoring and metrics interfaces
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 */

import { AinflueConfig, APIResponse, PaginationOptions, SortOptions } from './types';

/**
 * Base API interface with common methods
 */
export interface BaseAPI {
  readonly config: AinflueConfig;
  readonly baseUrl: string;
  
  /**
   * Health check endpoint
   */
  healthCheck(): Promise<APIResponse<{ status: string; timestamp: string }>>;
  
  /**
   * Get API version information
   */
  getVersion(): Promise<APIResponse<{ version: string; build: string }>>;
}

/**
 * Authentication API interface (Security expertise)
 */
export interface AuthAPI extends BaseAPI {
  /**
   * Login with username/password
   */
  login(username: string, password: string): Promise<APIResponse<{
    accessToken: string;
    refreshToken: string;
    expiresIn: number;
    user: UserProfile;
  }>>;
  
  /**
   * Login with OAuth provider
   */
  loginWithOAuth(provider: string, code: string, state?: string): Promise<APIResponse<{
    accessToken: string;
    refreshToken: string;
    expiresIn: number;
    user: UserProfile;
  }>>;
  
  /**
   * Refresh access token
   */
  refreshToken(refreshToken: string): Promise<APIResponse<{
    accessToken: string;
    expiresIn: number;
  }>>;
  
  /**
   * Logout and invalidate tokens
   */
  logout(): Promise<APIResponse<void>>;
  
  /**
   * Get current user profile
   */
  getCurrentUser(): Promise<APIResponse<UserProfile>>;
  
  /**
   * Update user profile
   */
  updateProfile(profile: Partial<UserProfile>): Promise<APIResponse<UserProfile>>;
  
  /**
   * Change password
   */
  changePassword(oldPassword: string, newPassword: string): Promise<APIResponse<void>>;
  
  /**
   * Request password reset
   */
  requestPasswordReset(email: string): Promise<APIResponse<void>>;
  
  /**
   * Reset password with token
   */
  resetPassword(token: string, newPassword: string): Promise<APIResponse<void>>;
  
  /**
   * Enable two-factor authentication
   */
  enableTwoFactor(): Promise<APIResponse<{
    qrCode: string;
    backupCodes: string[];
  }>>;
  
  /**
   * Verify two-factor authentication setup
   */
  verifyTwoFactor(code: string): Promise<APIResponse<void>>;
  
  /**
   * Disable two-factor authentication
   */
  disableTwoFactor(code: string): Promise<APIResponse<void>>;
}

/**
 * Content API interface (Audio Engineer + ML Engineer expertise)
 */
export interface ContentAPI extends BaseAPI {
  /**
   * Upload audio content
   */
  uploadAudio(file: File | Blob, metadata?: AudioMetadata): Promise<APIResponse<UploadResult>>;
  
  /**
   * Upload video content
   */
  uploadVideo(file: File | Blob, metadata?: VideoMetadata): Promise<APIResponse<UploadResult>>;
  
  /**
   * Upload image content
   */
  uploadImage(file: File | Blob, metadata?: ImageMetadata): Promise<APIResponse<UploadResult>>;
  
  /**
   * Get content by ID
   */
  getContent(contentId: string): Promise<APIResponse<ContentItem>>;
  
  /**
   * List content with pagination
   */
  listContent(options?: ContentListOptions): Promise<APIResponse<PaginatedResponse<ContentItem>>>;
  
  /**
   * Update content metadata
   */
  updateContent(contentId: string, updates: Partial<ContentItem>): Promise<APIResponse<ContentItem>>;
  
  /**
   * Delete content
   */
  deleteContent(contentId: string): Promise<APIResponse<void>>;
  
  /**
   * Search content
   */
  searchContent(query: string, options?: SearchOptions): Promise<APIResponse<PaginatedResponse<ContentItem>>>;
  
  /**
   * Get content analytics
   */
  getContentAnalytics(contentId: string, timeframe?: TimeframeOptions): Promise<APIResponse<ContentAnalytics>>;
  
  /**
   * Process content with AI
   */
  processWithAI(contentId: string, processors: AIProcessor[]): Promise<APIResponse<ProcessingResult>>;
  
  /**
   * Get processing status
   */
  getProcessingStatus(jobId: string): Promise<APIResponse<ProcessingStatus>>;
  
  /**
   * Generate content thumbnail
   */
  generateThumbnail(contentId: string, options?: ThumbnailOptions): Promise<APIResponse<{ thumbnailUrl: string }>>;
  
  /**
   * Get content download URL
   */
  getDownloadUrl(contentId: string, format?: string): Promise<APIResponse<{ downloadUrl: string; expiresAt: string }>>;
}

/**
 * AI Processing API interface (Lead Dev IA + ML Engineer expertise)
 */
export interface AIAPI extends BaseAPI {
  /**
   * Analyze content for copyright infringement
   */
  analyzeCopyright(contentId: string): Promise<APIResponse<CopyrightAnalysis>>;
  
  /**
   * Generate content tags automatically
   */
  generateTags(contentId: string): Promise<APIResponse<{ tags: string[]; confidence: number[] }>>;
  
  /**
   * Transcribe audio/video content
   */
  transcribe(contentId: string, language?: string): Promise<APIResponse<TranscriptionResult>>;
  
  /**
   * Translate content
   */
  translate(contentId: string, targetLanguage: string): Promise<APIResponse<TranslationResult>>;
  
  /**
   * Generate content summary
   */
  summarize(contentId: string, length?: 'short' | 'medium' | 'long'): Promise<APIResponse<{ summary: string }>>;
  
  /**
   * Detect content sentiment
   */
  analyzeSentiment(contentId: string): Promise<APIResponse<SentimentAnalysis>>;
  
  /**
   * Generate content recommendations
   */
  getRecommendations(userId: string, count?: number): Promise<APIResponse<ContentRecommendation[]>>;
  
  /**
   * Train custom AI model
   */
  trainModel(trainingData: TrainingData): Promise<APIResponse<{ modelId: string; trainingJobId: string }>>;
  
  /**
   * Get model training status
   */
  getTrainingStatus(trainingJobId: string): Promise<APIResponse<TrainingStatus>>;
  
  /**
   * Use custom AI model
   */
  useCustomModel(modelId: string, input: any): Promise<APIResponse<ModelPrediction>>;
}

/**
 * Analytics API interface (DevOps + DBA expertise)
 */
export interface AnalyticsAPI extends BaseAPI {
  /**
   * Get user analytics
   */
  getUserAnalytics(timeframe?: TimeframeOptions): Promise<APIResponse<UserAnalytics>>;
  
  /**
   * Get content performance metrics
   */
  getContentMetrics(contentId?: string, timeframe?: TimeframeOptions): Promise<APIResponse<ContentMetrics>>;
  
  /**
   * Get platform usage statistics
   */
  getPlatformStats(timeframe?: TimeframeOptions): Promise<APIResponse<PlatformStats>>;
  
  /**
   * Get real-time metrics
   */
  getRealTimeMetrics(): Promise<APIResponse<RealTimeMetrics>>;
  
  /**
   * Generate analytics report
   */
  generateReport(reportType: ReportType, options?: ReportOptions): Promise<APIResponse<{ reportId: string }>>;
  
  /**
   * Get report status
   */
  getReportStatus(reportId: string): Promise<APIResponse<ReportStatus>>;
  
  /**
   * Download report
   */
  downloadReport(reportId: string, format: 'pdf' | 'xlsx' | 'csv'): Promise<APIResponse<{ downloadUrl: string }>>;
  
  /**
   * Track custom event
   */
  trackEvent(event: CustomEvent): Promise<APIResponse<void>>;
  
  /**
   * Get event analytics
   */
  getEventAnalytics(eventType: string, timeframe?: TimeframeOptions): Promise<APIResponse<EventAnalytics>>;
}

/**
 * Collaboration API interface (Microservices expertise)
 */
export interface CollaborationAPI extends BaseAPI {
  /**
   * Create collaboration project
   */
  createProject(project: CreateProjectRequest): Promise<APIResponse<Project>>;
  
  /**
   * Get project details
   */
  getProject(projectId: string): Promise<APIResponse<Project>>;
  
  /**
   * List user projects
   */
  listProjects(options?: ProjectListOptions): Promise<APIResponse<PaginatedResponse<Project>>>;
  
  /**
   * Update project
   */
  updateProject(projectId: string, updates: Partial<Project>): Promise<APIResponse<Project>>;
  
  /**
   * Delete project
   */
  deleteProject(projectId: string): Promise<APIResponse<void>>;
  
  /**
   * Invite collaborator
   */
  inviteCollaborator(projectId: string, invitation: CollaboratorInvitation): Promise<APIResponse<void>>;
  
  /**
   * Accept collaboration invitation
   */
  acceptInvitation(invitationId: string): Promise<APIResponse<void>>;
  
  /**
   * Decline collaboration invitation
   */
  declineInvitation(invitationId: string): Promise<APIResponse<void>>;
  
  /**
   * Remove collaborator
   */
  removeCollaborator(projectId: string, userId: string): Promise<APIResponse<void>>;
  
  /**
   * Update collaborator role
   */
  updateCollaboratorRole(projectId: string, userId: string, role: CollaboratorRole): Promise<APIResponse<void>>;
  
  /**
   * Get project activity
   */
  getProjectActivity(projectId: string, options?: ActivityOptions): Promise<APIResponse<PaginatedResponse<Activity>>>;
  
  /**
   * Add comment to content
   */
  addComment(contentId: string, comment: string): Promise<APIResponse<Comment>>;
  
  /**
   * Get content comments
   */
  getComments(contentId: string, options?: CommentOptions): Promise<APIResponse<PaginatedResponse<Comment>>>;
  
  /**
   * Update comment
   */
  updateComment(commentId: string, comment: string): Promise<APIResponse<Comment>>;
  
  /**
   * Delete comment
   */
  deleteComment(commentId: string): Promise<APIResponse<void>>;
  
  /**
   * Create content version
   */
  createVersion(contentId: string, version: VersionData): Promise<APIResponse<ContentVersion>>;
  
  /**
   * Get content versions
   */
  getVersions(contentId: string): Promise<APIResponse<ContentVersion[]>>;
  
  /**
   * Restore content version
   */
  restoreVersion(contentId: string, versionId: string): Promise<APIResponse<ContentItem>>;
}

/**
 * Monetization API interface (Business Logic expertise)
 */
export interface MonetizationAPI extends BaseAPI {
  /**
   * Get subscription plans
   */
  getSubscriptionPlans(): Promise<APIResponse<SubscriptionPlan[]>>;
  
  /**
   * Get current subscription
   */
  getCurrentSubscription(): Promise<APIResponse<Subscription>>;
  
  /**
   * Subscribe to plan
   */
  subscribe(planId: string, paymentMethod?: PaymentMethod): Promise<APIResponse<Subscription>>;
  
  /**
   * Cancel subscription
   */
  cancelSubscription(): Promise<APIResponse<void>>;
  
  /**
   * Update payment method
   */
  updatePaymentMethod(paymentMethod: PaymentMethod): Promise<APIResponse<void>>;
  
  /**
   * Get payment history
   */
  getPaymentHistory(options?: PaginationOptions): Promise<APIResponse<PaginatedResponse<Payment>>>;
  
  /**
   * Get usage statistics
   */
  getUsageStats(timeframe?: TimeframeOptions): Promise<APIResponse<UsageStats>>;
  
  /**
   * Create one-time payment
   */
  createPayment(amount: number, description: string): Promise<APIResponse<{ paymentId: string; paymentUrl: string }>>;
  
  /**
   * Get payment status
   */
  getPaymentStatus(paymentId: string): Promise<APIResponse<PaymentStatus>>;
  
  /**
   * Request payout
   */
  requestPayout(amount: number, method: PayoutMethod): Promise<APIResponse<{ payoutId: string }>>;
  
  /**
   * Get payout history
   */
  getPayoutHistory(options?: PaginationOptions): Promise<APIResponse<PaginatedResponse<Payout>>>;
  
  /**
   * Get earnings dashboard
   */
  getEarningsDashboard(timeframe?: TimeframeOptions): Promise<APIResponse<EarningsDashboard>>;
}

/**
 * Notifications API interface (DevOps expertise)
 */
export interface NotificationsAPI extends BaseAPI {
  /**
   * Get user notifications
   */
  getNotifications(options?: NotificationOptions): Promise<APIResponse<PaginatedResponse<Notification>>>;
  
  /**
   * Mark notification as read
   */
  markAsRead(notificationId: string): Promise<APIResponse<void>>;
  
  /**
   * Mark all notifications as read
   */
  markAllAsRead(): Promise<APIResponse<void>>;
  
  /**
   * Delete notification
   */
  deleteNotification(notificationId: string): Promise<APIResponse<void>>;
  
  /**
   * Get notification preferences
   */
  getNotificationPreferences(): Promise<APIResponse<NotificationPreferences>>;
  
  /**
   * Update notification preferences
   */
  updateNotificationPreferences(preferences: Partial<NotificationPreferences>): Promise<APIResponse<NotificationPreferences>>;
  
  /**
   * Subscribe to push notifications
   */
  subscribeToPush(subscription: PushSubscription): Promise<APIResponse<void>>;
  
  /**
   * Unsubscribe from push notifications
   */
  unsubscribeFromPush(): Promise<APIResponse<void>>;
  
  /**
   * Send test notification
   */
  sendTestNotification(type: NotificationType): Promise<APIResponse<void>>;
}

/**
 * Administration API interface (Security + DevOps expertise)
 */
export interface AdminAPI extends BaseAPI {
  /**
   * Get system status
   */
  getSystemStatus(): Promise<APIResponse<SystemStatus>>;
  
  /**
   * Get system metrics
   */
  getSystemMetrics(timeframe?: TimeframeOptions): Promise<APIResponse<SystemMetrics>>;
  
  /**
   * Get user management
   */
  getUsers(options?: UserListOptions): Promise<APIResponse<PaginatedResponse<UserProfile>>>;
  
  /**
   * Get user details
   */
  getUser(userId: string): Promise<APIResponse<UserProfile>>;
  
  /**
   * Update user
   */
  updateUser(userId: string, updates: Partial<UserProfile>): Promise<APIResponse<UserProfile>>;
  
  /**
   * Suspend user
   */
  suspendUser(userId: string, reason: string): Promise<APIResponse<void>>;
  
  /**
   * Unsuspend user
   */
  unsuspendUser(userId: string): Promise<APIResponse<void>>;
  
  /**
   * Delete user
   */
  deleteUser(userId: string): Promise<APIResponse<void>>;
  
  /**
   * Get audit logs
   */
  getAuditLogs(options?: AuditLogOptions): Promise<APIResponse<PaginatedResponse<AuditLog>>>;
  
  /**
   * Get security events
   */
  getSecurityEvents(options?: SecurityEventOptions): Promise<APIResponse<PaginatedResponse<SecurityEvent>>>;
  
  /**
   * Update system configuration
   */
  updateConfiguration(config: Partial<SystemConfiguration>): Promise<APIResponse<SystemConfiguration>>;
  
  /**
   * Run system maintenance
   */
  runMaintenance(maintenanceType: MaintenanceType): Promise<APIResponse<{ jobId: string }>>;
  
  /**
   * Get maintenance status
   */
  getMaintenanceStatus(jobId: string): Promise<APIResponse<MaintenanceStatus>>;
}

// Supporting types for API interfaces

export interface UserProfile {
  id: string;
  username: string;
  email: string;
  displayName: string;
  avatar?: string;
  bio?: string;
  website?: string;
  location?: string;
  createdAt: string;
  updatedAt: string;
  verified: boolean;
  subscription?: Subscription;
  preferences: UserPreferences;
  stats: UserStats;
}

export interface ContentItem {
  id: string;
  title: string;
  description?: string;
  type: 'audio' | 'video' | 'image' | 'document';
  format: string;
  size: number;
  duration?: number;
  dimensions?: { width: number; height: number };
  url: string;
  thumbnailUrl?: string;
  tags: string[];
  metadata: Record<string, any>;
  visibility: 'public' | 'private' | 'unlisted';
  status: 'processing' | 'ready' | 'failed';
  createdAt: string;
  updatedAt: string;
  ownerId: string;
  analytics: ContentAnalytics;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

export interface ProcessingResult {
  jobId: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress: number;
  results?: Record<string, any>;
  error?: string;
  startedAt: string;
  completedAt?: string;
}

export interface AIProcessor {
  type: 'copyright' | 'transcription' | 'translation' | 'tagging' | 'sentiment' | 'summary';
  config?: Record<string, any>;
}

export interface CopyrightAnalysis {
  matches: CopyrightMatch[];
  confidence: number;
  riskLevel: 'low' | 'medium' | 'high';
  recommendations: string[];
}

export interface CopyrightMatch {
  sourceId: string;
  title: string;
  owner: string;
  similarity: number;
  matchedSegments: TimeSegment[];
}

export interface TimeSegment {
  start: number;
  end: number;
  confidence: number;
}

export type ReportType = 'user_activity' | 'content_performance' | 'revenue' | 'system_usage';
export type CollaboratorRole = 'viewer' | 'editor' | 'admin';
export type NotificationType = 'content_uploaded' | 'comment_added' | 'collaboration_invite' | 'payment_received';
export type MaintenanceType = 'cleanup' | 'backup' | 'optimization' | 'security_scan';

// Additional interfaces for completeness
export interface AudioMetadata {
  title?: string;
  artist?: string;
  album?: string;
  genre?: string;
  year?: number;
  bitrate?: number;
  sampleRate?: number;
  channels?: number;
}

export interface VideoMetadata {
  title?: string;
  description?: string;
  tags?: string[];
  thumbnail?: File | Blob;
  resolution?: { width: number; height: number };
  frameRate?: number;
  bitrate?: number;
}

export interface ImageMetadata {
  title?: string;
  description?: string;
  tags?: string[];
  location?: { latitude: number; longitude: number };
  camera?: string;
  lens?: string;
  settings?: Record<string, any>;
}

export interface UploadResult {
  contentId: string;
  uploadId: string;
  status: 'uploading' | 'processing' | 'completed' | 'failed';
  progress: number;
  url?: string;
  error?: string;
}

export interface SearchOptions extends PaginationOptions {
  filters?: Record<string, any>;
  sort?: SortOptions;
  facets?: string[];
}

export interface ContentListOptions extends PaginationOptions {
  type?: string;
  status?: string;
  tags?: string[];
  sort?: SortOptions;
  dateRange?: { start: string; end: string };
}

export interface TimeframeOptions {
  start: string;
  end: string;
  granularity?: 'hour' | 'day' | 'week' | 'month';
}

export interface ContentAnalytics {
  views: number;
  downloads: number;
  shares: number;
  likes: number;
  comments: number;
  totalWatchTime?: number;
  averageWatchTime?: number;
  retention?: number[];
  demographics?: Record<string, any>;
  traffic?: Record<string, number>;
}

export interface UserAnalytics {
  totalViews: number;
  totalDownloads: number;
  totalUploads: number;
  storageUsed: number;
  bandwidthUsed: number;
  engagement: EngagementMetrics;
  topContent: ContentItem[];
  audienceInsights: AudienceInsights;
}

export interface EngagementMetrics {
  likes: number;
  comments: number;
  shares: number;
  followers: number;
  following: number;
  engagementRate: number;
}

export interface AudienceInsights {
  demographics: Record<string, number>;
  locations: Record<string, number>;
  devices: Record<string, number>;
  referrers: Record<string, number>;
}

export interface Subscription {
  id: string;
  planId: string;
  plan: SubscriptionPlan;
  status: 'active' | 'canceled' | 'past_due' | 'incomplete';
  currentPeriodStart: string;
  currentPeriodEnd: string;
  cancelAtPeriodEnd: boolean;
  trialEnd?: string;
}

export interface SubscriptionPlan {
  id: string;
  name: string;
  description: string;
  price: number;
  currency: string;
  interval: 'month' | 'year';
  features: string[];
  limits: PlanLimits;
}

export interface PlanLimits {
  storage: number; // GB
  bandwidth: number; // GB
  uploads: number; // per month
  collaborators: number;
  projects: number;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  ownerId: string;
  collaborators: Collaborator[];
  settings: ProjectSettings;
  stats: ProjectStats;
  createdAt: string;
  updatedAt: string;
}

export interface Collaborator {
  userId: string;
  user: UserProfile;
  role: CollaboratorRole;
  permissions: string[];
  invitedAt: string;
  joinedAt?: string;
}

export interface ProjectSettings {
  visibility: 'public' | 'private';
  allowComments: boolean;
  allowDownloads: boolean;
  requireApproval: boolean;
  autoBackup: boolean;
}

export interface ProjectStats {
  totalContent: number;
  totalSize: number;
  totalViews: number;
  lastActivity: string;
  contentTypes: Record<string, number>;
}

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  data?: Record<string, any>;
  read: boolean;
  createdAt: string;
  expiresAt?: string;
}

export interface SystemStatus {
  status: 'healthy' | 'degraded' | 'down';
  version: string;
  uptime: number;
  services: ServiceStatus[];
  lastUpdate: string;
}

export interface ServiceStatus {
  name: string;
  status: 'healthy' | 'degraded' | 'down';
  responseTime: number;
  lastCheck: string;
  error?: string;
}

export interface AuditLog {
  id: string;
  userId: string;
  action: string;
  resource: string;
  resourceId: string;
  details: Record<string, any>;
  ipAddress: string;
  userAgent: string;
  timestamp: string;
}

export interface SecurityEvent {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  source: string;
  description: string;
  blocked: boolean;
  data: Record<string, any>;
  timestamp: string;
}