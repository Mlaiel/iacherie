/**
 * Components Index - Consolidated Exports (Max 12 Groups)
 * 
 * This file provides the main consolidated component exports following
 * the new structure that limits exports to 12 logical groups maximum.
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

// Export existing components for backward compatibility
export { default as UploadWizard } from './upload_wizard';
export { default as ContentLibrary } from './content_library';

// Export advanced components
export { default as MediaUploader } from './MediaUploader';
export { default as AIProtection } from './AIProtection';
export { default as CollaborationHub } from './CollaborationHub';
export { default as Analytics } from './Analytics';
export { default as Monetization } from './Monetization';

// ============================================================================
// CONSOLIDATED COMPONENT GROUPS (12 MAX EXPORTS)
// ============================================================================

// Re-export all consolidated groups from src/components
export {
  // 12 Consolidated Component Groups
  Forms,
  Charts,
  Layout,
  Media,
  Dashboards,
  Protection,
  Monetization as MonetizationGroup,
  Content,
  Social,
  Monitoring,
  Tables,
  Modals,
  
  // Metadata exports
  CONSOLIDATED_GROUPS,
  CONSOLIDATION_SUMMARY
} from '../src/components';

// Component metadata for documentation and routing
export const COMPONENT_METADATA = {
  'upload_wizard': {
    name: 'Upload Wizard',
    description: 'Multi-step content upload interface with protection settings',
    features: [
      'Drag and drop file upload',
      'Multiple file format support',
      'Protection configuration',
      'Platform distribution settings',
      'Progress tracking'
    ],
    platforms: ['web', 'mobile'],
    version: '1.0.0'
  },
  'content_library': {
    name: 'Content Library',
    description: 'Content management and organization interface',
    features: [
      'Grid and list view modes',
      'Advanced filtering and search',
      'Bulk operations',
      'Performance analytics',
      'Content organization'
    ],
    platforms: ['web', 'mobile'],
    version: '1.0.0'
  },
  'media_uploader': {
    name: 'Media Uploader',
    description: 'Advanced multi-format drag & drop upload component',
    features: [
      'Multi-format file support',
      'Drag & drop interface',
      'Upload progress tracking',
      'File validation and preview',
      'Batch operations'
    ],
    platforms: ['web', 'mobile'],
    version: '1.0.0'
  },
  'ai_protection': {
    name: 'AI Protection',
    description: 'AI-powered content protection and monitoring interface',
    features: [
      'Real-time threat detection',
      'AI-powered monitoring',
      'Protection level management',
      'Alert management',
      'Analytics dashboard'
    ],
    platforms: ['web'],
    version: '1.0.0'
  },
  'collaboration_hub': {
    name: 'Collaboration Hub',
    description: 'Advanced collaboration and team management interface',
    features: [
      'Project management',
      'Team collaboration',
      'AI-powered matching',
      'Real-time messaging',
      'Video conferencing'
    ],
    platforms: ['web', 'mobile'],
    version: '1.0.0'
  },
  'analytics': {
    name: 'Analytics Dashboard',
    description: 'Comprehensive real-time analytics and insights',
    features: [
      'Real-time metrics',
      'Interactive charts',
      'Platform comparisons',
      'Performance insights',
      'Export capabilities'
    ],
    platforms: ['web'],
    version: '1.0.0'
  },
  'monetization': {
    name: 'Monetization Center',
    description: 'Revenue management and monetization interface',
    features: [
      'Revenue tracking',
      'Payment management',
      'Subscription tiers',
      'Financial analytics',
      'Payout management'
    ],
    platforms: ['web'],
    version: '1.0.0'
  }
} as const;