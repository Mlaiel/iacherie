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
  type: 'subscription' | 'purchase' | 'licensing' | 'advertising';
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