/**
 * @fileoverview Business domain types for Ainflue platform
 * @author Fahed Mlaiel <mlaiel@live.de>
 */

// Content types
export interface ContentMetadata {
  id: string;
  title: string;
  description?: string;
  format: string;
  size: number;
  duration?: number;
  dimensions?: { width: number; height: number };
  createdAt: Date;
  updatedAt: Date;
  tags: string[];
  categories: string[];
}

export interface ContentUpload {
  file: File;
  metadata: Partial<ContentMetadata>;
  progress: number;
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'failed';
  fingerprint?: string;
}

// Protection types
export interface ContentFingerprint {
  id: string;
  contentId: string;
  algorithm: string;
  hash: string;
  features: Record<string, any>;
  createdAt: Date;
}

export interface CopyrightInfo {
  id: string;
  contentId: string;
  owner: string;
  licenseType: string;
  expiryDate?: Date;
  permissions: string[];
  restrictions: string[];
}

// Monetization types
export interface RevenueStream {
  id: string;
  contentId: string;
  type: 'subscription' | 'one_time_purchase' | 'licensing' | 'advertising' | 'commission' | 'royalty';
  amount: number;
  currency: string;
  frequency?: 'one-time' | 'monthly' | 'yearly';
  status: 'active' | 'inactive' | 'pending';
}

export interface MarketplaceProduct {
  id: string;
  contentId: string;
  title: string;
  description: string;
  price: number;
  currency: string;
  category: string;
  tags: string[];
  seller: string;
  rating: number;
  downloads: number;
}

// Collaboration types
export interface CollaborationProject {
  id: string;
  title: string;
  description: string;
  owner: string;
  collaborators: string[];
  status: 'draft' | 'active' | 'completed' | 'archived';
  createdAt: Date;
  deadline?: Date;
  budget?: number;
}

export interface MatchingProfile {
  userId: string;
  skills: string[];
  interests: string[];
  experience: number;
  rating: number;
  portfolio: string[];
  availability: boolean;
}

// ====================================================================
// SEO ENGINE TYPES (Missing types for seo_engine.ts)
// ====================================================================

export interface SEOConfiguration {
  platforms: string[];
  targetKeywords: string[];
  contentOptimization: boolean;
  metaGeneration: boolean;
  schemaMarkup: boolean;
  sitemap: boolean;
  robotsTxt: boolean;
  analytics: boolean;
}

export interface SEOAnalysis {
  score?: number;
  keywords: SEOKeywordAnalysis[];
  metadata?: SEOMetadata;
  performance?: SEOPerformance;
  recommendations: string[];
  issues?: SEOIssue[];
  topics: string[];
  wordCount?: number;
  sentenceCount?: number;
  readabilityScore?: number;
  keywordDensity?: number;
  sentiment?: string;
}

export interface SEOKeywordAnalysis {
  keyword: string;
  density: number;
  position: number;
  difficulty: number;
  searchVolume: number;
  competition: 'low' | 'medium' | 'high';
}

export interface SEOMetadata {
  title: string;
  description: string;
  keywords: string[];
  author: string;
  robots: string;
  canonical?: string;
  openGraph: Record<string, string>;
  twitterCard: Record<string, string>;
}

export interface SEOPerformance {
  loadTime: number;
  mobileScore: number;
  desktopScore: number;
  coreWebVitals: {
    lcp: number; // Largest Contentful Paint
    fid: number; // First Input Delay
    cls: number; // Cumulative Layout Shift
  };
}

export interface SEOIssue {
  type: 'error' | 'warning' | 'info';
  message: string;
  element?: string;
  recommendation: string;
}

export interface PlatformSEOStrategy {
  platform: string;
  title: string;
  description: string;
  keywords: string[];
  hashtags: string[];
  optimizations: Record<string, any>;
}

export interface ContentOptimization {
  originalContent: string;
  optimizedContent: string;
  keywords: string[];
  readabilityScore: number;
  seoScore: number;
  changes: string[];
}

// ====================================================================
// UPLOAD ORCHESTRATOR TYPES (Missing types for upload_orchestrator.ts)
// ====================================================================

export interface UploadConfiguration {
  maxFileSize: number;
  supportedFormats: string[];
  chunkSize: number;
  maxConcurrentUploads: number;
  retryAttempts: number;
  enableCompression: boolean;
  enableEncryption: boolean;
  virusScanning: boolean;
}

export interface UploadSession {
  id: string;
  files: UploadFile[];
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'failed';
  progress: number;
  startedAt: Date;
  completedAt?: Date;
  error?: string;
}

export interface UploadFile {
  id: string;
  file: File;
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'failed';
  progress: number;
  uploadedBytes: number;
  totalBytes: number;
  metadata: FileMetadata;
  chunks: UploadChunk[];
  error?: string;
}

export interface UploadChunk {
  id: string;
  index: number;
  data: ArrayBuffer;
  size: number;
  uploaded: boolean;
  retryCount: number;
}

export interface UploadProgress {
  sessionId: string;
  fileId: string;
  progress: number;
  speed: number; // bytes per second
  eta: number; // estimated time remaining in seconds
  stage: 'uploading' | 'processing' | 'finalizing';
}

export interface FileMetadata {
  name: string;
  size: number;
  type: string;
  format: string;
  lastModified: Date;
  checksum: string;
  dimensions?: { width: number; height: number };
  duration?: number;
  bitrate?: number;
  sampleRate?: number;
  channels?: number;
}

export interface FileValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  fileType: string;
  detectedFormat: string;
  virusScanResult: 'clean' | 'infected' | 'suspicious' | 'unknown';
}