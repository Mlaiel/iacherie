/**
 * @fileoverview User role and permission enumerations
 * @author Fahed Mlaiel <mlaiel@live.de>
 */

export enum UserRole {
  ADMIN = 'admin',
  CREATOR = 'creator',
  COLLABORATOR = 'collaborator',
  VIEWER = 'viewer',
  MODERATOR = 'moderator',
}

export enum UserStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  SUSPENDED = 'suspended',
  PENDING_VERIFICATION = 'pending_verification',
  DELETED = 'deleted',
}

export enum Permission {
  // Content permissions
  CREATE_CONTENT = 'create_content',
  EDIT_CONTENT = 'edit_content',
  DELETE_CONTENT = 'delete_content',
  VIEW_CONTENT = 'view_content',
  PUBLISH_CONTENT = 'publish_content',
  
  // Collaboration permissions
  CREATE_PROJECT = 'create_project',
  JOIN_PROJECT = 'join_project',
  INVITE_COLLABORATORS = 'invite_collaborators',
  MANAGE_PROJECT = 'manage_project',
  
  // Monetization permissions
  SET_PRICING = 'set_pricing',
  VIEW_ANALYTICS = 'view_analytics',
  MANAGE_PAYOUTS = 'manage_payouts',
  CREATE_MARKETPLACE_LISTING = 'create_marketplace_listing',
  
  // Admin permissions
  MANAGE_USERS = 'manage_users',
  MANAGE_PLATFORM = 'manage_platform',
  VIEW_ALL_CONTENT = 'view_all_content',
  MODERATE_CONTENT = 'moderate_content',
}

export enum SubscriptionTier {
  FREE = 'free',
  STANDARD = 'standard',
  PREMIUM = 'premium',
  ENTERPRISE = 'enterprise',
}

export enum AccountVerificationStatus {
  UNVERIFIED = 'unverified',
  EMAIL_VERIFIED = 'email_verified',
  PHONE_VERIFIED = 'phone_verified',
  IDENTITY_VERIFIED = 'identity_verified',
  FULLY_VERIFIED = 'fully_verified',
}