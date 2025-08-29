/**
 * Components Index - Export all component modules
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

// Export upload components
export { default as UploadWizard } from './upload_wizard';
export { default as ContentLibrary } from './content_library';

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
  }
} as const;