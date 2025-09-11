/**
 * Ainflue Desktop - Project Templates Manager
 * 
 * Professional project templates for efficient content creation
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

const { EventEmitter } = require('events');
const fs = require('fs').promises;
const path = require('path');

class ProjectTemplates extends EventEmitter {
  constructor() {
    super();
    this.templates = new Map();
    this.categories = new Map();
    this.customTemplates = new Map();
    this.templatePath = path.join(__dirname, '../../assets/templates');
    
    this.initializeDefaultTemplates();
    this.initializeCategories();
  }

  /**
   * Initialize default project templates
   */
  initializeDefaultTemplates() {
    // Audio templates
    this.templates.set('podcast', {
      id: 'podcast',
      name: 'Podcast Episode',
      category: 'audio',
      description: 'Professional podcast recording template with intro/outro',
      thumbnail: 'podcast_template.png',
      settings: {
        audio: {
          sampleRate: 48000,
          bitDepth: 24,
          channels: 2,
          format: 'WAV'
        },
        tracks: [
          { name: 'Host', type: 'audio', color: '#3498db' },
          { name: 'Guest', type: 'audio', color: '#e74c3c' },
          { name: 'Intro Music', type: 'audio', color: '#f39c12' },
          { name: 'Outro Music', type: 'audio', color: '#27ae60' }
        ],
        effects: ['EQ', 'Compressor', 'Noise Gate', 'Reverb'],
        duration: 3600 // 1 hour
      },
      assets: {
        intro: 'podcast_intro.wav',
        outro: 'podcast_outro.wav',
        jingle: 'podcast_jingle.wav',
        background: 'podcast_bg.wav'
      }
    });

    this.templates.set('music_single', {
      id: 'music_single',
      name: 'Music Single',
      category: 'audio',
      description: 'Professional music production template',
      thumbnail: 'music_single_template.png',
      settings: {
        audio: {
          sampleRate: 96000,
          bitDepth: 32,
          channels: 2,
          format: 'WAV'
        },
        tracks: [
          { name: 'Drums', type: 'audio', color: '#e74c3c' },
          { name: 'Bass', type: 'audio', color: '#9b59b6' },
          { name: 'Guitar', type: 'audio', color: '#f39c12' },
          { name: 'Keys', type: 'audio', color: '#3498db' },
          { name: 'Vocals', type: 'audio', color: '#27ae60' },
          { name: 'Harmony', type: 'audio', color: '#e67e22' }
        ],
        effects: ['EQ', 'Compressor', 'Reverb', 'Delay', 'Chorus', 'Distortion'],
        duration: 240 // 4 minutes
      },
      assets: {
        metronome: 'metronome_120bpm.wav',
        reference: 'reference_track.wav'
      }
    });

    // Video templates
    this.templates.set('youtube_video', {
      id: 'youtube_video',
      name: 'YouTube Video',
      category: 'video',
      description: 'Optimized template for YouTube content creation',
      thumbnail: 'youtube_template.png',
      settings: {
        video: {
          resolution: '1920x1080',
          frameRate: 30,
          codec: 'H.264',
          bitrate: 8000
        },
        audio: {
          sampleRate: 48000,
          bitDepth: 16,
          channels: 2,
          codec: 'AAC'
        },
        tracks: [
          { name: 'Main Video', type: 'video', color: '#ff0000' },
          { name: 'B-Roll', type: 'video', color: '#ff6b6b' },
          { name: 'Graphics', type: 'video', color: '#4ecdc4' },
          { name: 'Main Audio', type: 'audio', color: '#45b7d1' },
          { name: 'Background Music', type: 'audio', color: '#96ceb4' }
        ],
        duration: 600 // 10 minutes
      },
      assets: {
        intro: 'youtube_intro.mp4',
        outro: 'youtube_outro.mp4',
        subscribe: 'subscribe_animation.mp4',
        lower_thirds: 'lower_thirds.png'
      }
    });

    this.templates.set('instagram_reel', {
      id: 'instagram_reel',
      name: 'Instagram Reel',
      category: 'video',
      description: 'Vertical video template for Instagram Reels',
      thumbnail: 'instagram_reel_template.png',
      settings: {
        video: {
          resolution: '1080x1920',
          frameRate: 30,
          codec: 'H.264',
          bitrate: 3500
        },
        audio: {
          sampleRate: 44100,
          bitDepth: 16,
          channels: 2,
          codec: 'AAC'
        },
        tracks: [
          { name: 'Main Video', type: 'video', color: '#e1306c' },
          { name: 'Text Overlay', type: 'video', color: '#833ab4' },
          { name: 'Effects', type: 'video', color: '#fd1d1d' },
          { name: 'Audio', type: 'audio', color: '#f56040' }
        ],
        duration: 30 // 30 seconds
      },
      assets: {
        transitions: 'reel_transitions.mp4',
        effects: 'reel_effects.png',
        fonts: 'instagram_fonts.ttf'
      }
    });

    // Live streaming templates
    this.templates.set('live_stream', {
      id: 'live_stream',
      name: 'Live Stream',
      category: 'streaming',
      description: 'Multi-platform live streaming setup',
      thumbnail: 'live_stream_template.png',
      settings: {
        video: {
          resolution: '1920x1080',
          frameRate: 30,
          codec: 'H.264',
          bitrate: 5000
        },
        audio: {
          sampleRate: 48000,
          bitDepth: 16,
          channels: 2,
          codec: 'AAC'
        },
        scenes: [
          { name: 'Main Camera', layout: 'fullscreen' },
          { name: 'Screen Share', layout: 'fullscreen' },
          { name: 'Camera + Screen', layout: 'pip' },
          { name: 'Be Right Back', layout: 'static' }
        ],
        overlays: [
          { name: 'Chat', position: 'bottom-right' },
          { name: 'Donation Alert', position: 'top-center' },
          { name: 'Recent Follower', position: 'top-left' }
        ]
      },
      assets: {
        brb_screen: 'be_right_back.mp4',
        starting_soon: 'starting_soon.mp4',
        donation_sound: 'donation_alert.wav',
        follow_sound: 'follow_alert.wav'
      }
    });

    // Image templates
    this.templates.set('social_post', {
      id: 'social_post',
      name: 'Social Media Post',
      category: 'image',
      description: 'Multi-platform social media graphics template',
      thumbnail: 'social_post_template.png',
      settings: {
        canvas: {
          width: 1080,
          height: 1080,
          resolution: 300,
          colorSpace: 'sRGB'
        },
        layers: [
          { name: 'Background', type: 'fill', color: '#ffffff' },
          { name: 'Image', type: 'image', opacity: 100 },
          { name: 'Text', type: 'text', font: 'Arial Bold' },
          { name: 'Logo', type: 'image', opacity: 80 }
        ]
      },
      assets: {
        backgrounds: 'social_backgrounds/',
        overlays: 'social_overlays/',
        fonts: 'social_fonts/'
      }
    });

    this.templates.set('thumbnail', {
      id: 'thumbnail',
      name: 'Video Thumbnail',
      category: 'image',
      description: 'Eye-catching thumbnail template for videos',
      thumbnail: 'thumbnail_template.png',
      settings: {
        canvas: {
          width: 1280,
          height: 720,
          resolution: 72,
          colorSpace: 'sRGB'
        },
        layers: [
          { name: 'Background', type: 'gradient' },
          { name: 'Main Image', type: 'image' },
          { name: 'Title Text', type: 'text', font: 'Impact' },
          { name: 'Face Circle', type: 'shape' },
          { name: 'Arrow', type: 'shape' }
        ]
      },
      assets: {
        backgrounds: 'thumbnail_backgrounds/',
        arrows: 'thumbnail_arrows/',
        faces: 'thumbnail_faces/'
      }
    });

    // Blog templates
    this.templates.set('blog_post', {
      id: 'blog_post',
      name: 'Blog Post',
      category: 'text',
      description: 'Professional blog post template with SEO optimization',
      thumbnail: 'blog_post_template.png',
      settings: {
        format: 'markdown',
        structure: [
          { section: 'title', required: true },
          { section: 'meta_description', required: true },
          { section: 'introduction', required: true },
          { section: 'main_content', required: true },
          { section: 'conclusion', required: true },
          { section: 'call_to_action', required: false }
        ],
        seo: {
          title_length: { min: 30, max: 60 },
          meta_length: { min: 120, max: 160 },
          heading_structure: true,
          keyword_density: { min: 1, max: 3 }
        }
      },
      assets: {
        templates: 'blog_templates/',
        images: 'blog_images/',
        style: 'blog_styles.css'
      }
    });
  }

  /**
   * Initialize template categories
   */
  initializeCategories() {
    this.categories.set('audio', {
      name: 'Audio Production',
      description: 'Templates for podcasts, music, and audio content',
      icon: 'audio.svg',
      color: '#3498db'
    });

    this.categories.set('video', {
      name: 'Video Production',
      description: 'Templates for video content and editing',
      icon: 'video.svg',
      color: '#e74c3c'
    });

    this.categories.set('streaming', {
      name: 'Live Streaming',
      description: 'Templates for live streaming and broadcasting',
      icon: 'streaming.svg',
      color: '#9b59b6'
    });

    this.categories.set('image', {
      name: 'Image Design',
      description: 'Templates for graphics and image creation',
      icon: 'image.svg',
      color: '#f39c12'
    });

    this.categories.set('text', {
      name: 'Text Content',
      description: 'Templates for written content and blogs',
      icon: 'text.svg',
      color: '#27ae60'
    });

    this.categories.set('custom', {
      name: 'Custom Templates',
      description: 'User-created custom templates',
      icon: 'custom.svg',
      color: '#34495e'
    });
  }

  /**
   * Get all available templates
   */
  getAllTemplates() {
    return Array.from(this.templates.values());
  }

  /**
   * Get templates by category
   */
  getTemplatesByCategory(categoryId) {
    return Array.from(this.templates.values()).filter(template => template.category === categoryId);
  }

  /**
   * Get template by ID
   */
  getTemplate(templateId) {
    return this.templates.get(templateId) || null;
  }

  /**
   * Create project from template
   */
  async createProjectFromTemplate(templateId, projectName, customSettings = {}) {
    try {
      const template = this.getTemplate(templateId);
      if (!template) {
        throw new Error(`Template not found: ${templateId}`);
      }

      const projectId = Date.now().toString();
      const project = {
        id: projectId,
        name: projectName,
        templateId,
        created: new Date(),
        modified: new Date(),
        settings: {
          ...template.settings,
          ...customSettings
        },
        assets: { ...template.assets },
        status: 'created',
        progress: 0
      };

      // Copy template assets if they exist
      if (template.assets) {
        project.assetPaths = await this.copyTemplateAssets(templateId, projectId, template.assets);
      }

      this.emit('projectCreated', project);
      return project;
    } catch (error) {
      this.emit('error', new Error(`Failed to create project from template: ${error.message}`));
      return null;
    }
  }

  /**
   * Copy template assets to project directory
   */
  async copyTemplateAssets(templateId, projectId, assets) {
    const assetPaths = {};
    const templateAssetPath = path.join(this.templatePath, templateId);
    const projectAssetPath = path.join(this.templatePath, '../../projects', projectId, 'assets');

    try {
      // Ensure project asset directory exists
      await fs.mkdir(projectAssetPath, { recursive: true });

      for (const [key, assetPath] of Object.entries(assets)) {
        const sourcePath = path.join(templateAssetPath, assetPath);
        const targetPath = path.join(projectAssetPath, assetPath);

        try {
          // Check if source exists
          await fs.access(sourcePath);
          
          // Copy asset
          await fs.copyFile(sourcePath, targetPath);
          assetPaths[key] = targetPath;
        } catch (error) {
          // Asset doesn't exist, create placeholder
          assetPaths[key] = null;
        }
      }

      return assetPaths;
    } catch (error) {
      this.emit('error', new Error(`Failed to copy template assets: ${error.message}`));
      return {};
    }
  }

  /**
   * Create custom template from project
   */
  async createCustomTemplate(project, templateData) {
    try {
      const templateId = `custom_${Date.now()}`;
      const customTemplate = {
        id: templateId,
        name: templateData.name || `Custom Template ${templateId}`,
        category: 'custom',
        description: templateData.description || 'User-created custom template',
        thumbnail: templateData.thumbnail || 'custom_template.png',
        created: new Date(),
        creator: templateData.creator || 'User',
        settings: { ...project.settings },
        assets: { ...project.assets },
        tags: templateData.tags || [],
        isCustom: true
      };

      this.customTemplates.set(templateId, customTemplate);
      this.templates.set(templateId, customTemplate);

      // Save template to disk
      await this.saveCustomTemplate(customTemplate);

      this.emit('customTemplateCreated', customTemplate);
      return templateId;
    } catch (error) {
      this.emit('error', new Error(`Failed to create custom template: ${error.message}`));
      return null;
    }
  }

  /**
   * Save custom template to disk
   */
  async saveCustomTemplate(template) {
    try {
      const customTemplatePath = path.join(this.templatePath, 'custom');
      await fs.mkdir(customTemplatePath, { recursive: true });

      const templateFile = path.join(customTemplatePath, `${template.id}.json`);
      await fs.writeFile(templateFile, JSON.stringify(template, null, 2));

      return true;
    } catch (error) {
      this.emit('error', new Error(`Failed to save custom template: ${error.message}`));
      return false;
    }
  }

  /**
   * Load custom templates from disk
   */
  async loadCustomTemplates() {
    try {
      const customTemplatePath = path.join(this.templatePath, 'custom');
      
      try {
        const files = await fs.readdir(customTemplatePath);
        const jsonFiles = files.filter(file => file.endsWith('.json'));

        for (const file of jsonFiles) {
          const templateFile = path.join(customTemplatePath, file);
          const templateData = await fs.readFile(templateFile, 'utf8');
          const template = JSON.parse(templateData);

          this.customTemplates.set(template.id, template);
          this.templates.set(template.id, template);
        }

        this.emit('customTemplatesLoaded', this.customTemplates.size);
        return this.customTemplates.size;
      } catch (error) {
        // Directory doesn't exist yet
        return 0;
      }
    } catch (error) {
      this.emit('error', new Error(`Failed to load custom templates: ${error.message}`));
      return 0;
    }
  }

  /**
   * Delete custom template
   */
  async deleteCustomTemplate(templateId) {
    try {
      if (!this.customTemplates.has(templateId)) {
        throw new Error('Template not found or not a custom template');
      }

      // Remove from memory
      this.customTemplates.delete(templateId);
      this.templates.delete(templateId);

      // Remove from disk
      const templateFile = path.join(this.templatePath, 'custom', `${templateId}.json`);
      await fs.unlink(templateFile);

      this.emit('customTemplateDeleted', templateId);
      return true;
    } catch (error) {
      this.emit('error', new Error(`Failed to delete custom template: ${error.message}`));
      return false;
    }
  }

  /**
   * Search templates
   */
  searchTemplates(query, filters = {}) {
    const searchTerm = query.toLowerCase();
    let results = Array.from(this.templates.values());

    // Text search
    if (searchTerm) {
      results = results.filter(template => 
        template.name.toLowerCase().includes(searchTerm) ||
        template.description.toLowerCase().includes(searchTerm) ||
        (template.tags && template.tags.some(tag => tag.toLowerCase().includes(searchTerm)))
      );
    }

    // Category filter
    if (filters.category) {
      results = results.filter(template => template.category === filters.category);
    }

    // Custom filter
    if (filters.customOnly) {
      results = results.filter(template => template.isCustom);
    }

    // Sort results
    if (filters.sortBy) {
      results.sort((a, b) => {
        switch (filters.sortBy) {
          case 'name':
            return a.name.localeCompare(b.name);
          case 'created':
            return new Date(b.created || 0) - new Date(a.created || 0);
          case 'category':
            return a.category.localeCompare(b.category);
          default:
            return 0;
        }
      });
    }

    this.emit('searchResults', { query, filters, results: results.length });
    return results;
  }

  /**
   * Get template preview
   */
  async getTemplatePreview(templateId) {
    try {
      const template = this.getTemplate(templateId);
      if (!template) {
        throw new Error('Template not found');
      }

      const preview = {
        id: templateId,
        name: template.name,
        description: template.description,
        thumbnail: template.thumbnail,
        category: template.category,
        settings: template.settings,
        estimatedDuration: this.estimateProjectDuration(template),
        complexity: this.assessTemplateComplexity(template),
        tags: template.tags || [],
        assets: Object.keys(template.assets || {}).length
      };

      this.emit('previewGenerated', preview);
      return preview;
    } catch (error) {
      this.emit('error', new Error(`Failed to generate template preview: ${error.message}`));
      return null;
    }
  }

  /**
   * Estimate project duration based on template
   */
  estimateProjectDuration(template) {
    let duration = 60; // Base 1 hour

    // Audio templates typically take longer
    if (template.category === 'audio') {
      duration += 120; // +2 hours
    }

    // Video templates are complex
    if (template.category === 'video') {
      duration += 180; // +3 hours
    }

    // More tracks = more time
    if (template.settings.tracks) {
      duration += template.settings.tracks.length * 15; // +15 minutes per track
    }

    // More effects = more time
    if (template.settings.effects) {
      duration += template.settings.effects.length * 10; // +10 minutes per effect
    }

    return Math.round(duration);
  }

  /**
   * Assess template complexity
   */
  assessTemplateComplexity(template) {
    let complexity = 1; // Base complexity

    // Count elements
    const trackCount = template.settings.tracks ? template.settings.tracks.length : 0;
    const effectCount = template.settings.effects ? template.settings.effects.length : 0;
    const layerCount = template.settings.layers ? template.settings.layers.length : 0;
    const assetCount = Object.keys(template.assets || {}).length;

    const totalElements = trackCount + effectCount + layerCount + assetCount;

    if (totalElements <= 5) complexity = 1; // Beginner
    else if (totalElements <= 10) complexity = 2; // Intermediate
    else if (totalElements <= 20) complexity = 3; // Advanced
    else complexity = 4; // Expert

    return {
      level: complexity,
      label: ['Beginner', 'Intermediate', 'Advanced', 'Expert'][complexity - 1],
      elements: totalElements
    };
  }

  /**
   * Get all categories
   */
  getAllCategories() {
    return Array.from(this.categories.values());
  }

  /**
   * Get template statistics
   */
  getTemplateStatistics() {
    const stats = {
      total: this.templates.size,
      custom: this.customTemplates.size,
      byCategory: {},
      mostUsed: [],
      recentlyCreated: []
    };

    // Count by category
    for (const template of this.templates.values()) {
      stats.byCategory[template.category] = (stats.byCategory[template.category] || 0) + 1;
    }

    // Get recently created custom templates
    stats.recentlyCreated = Array.from(this.customTemplates.values())
      .sort((a, b) => new Date(b.created) - new Date(a.created))
      .slice(0, 5);

    this.emit('statisticsCalculated', stats);
    return stats;
  }

  /**
   * Validate template structure
   */
  validateTemplate(template) {
    const errors = [];

    // Required fields
    if (!template.id) errors.push('Template ID is required');
    if (!template.name) errors.push('Template name is required');
    if (!template.category) errors.push('Template category is required');
    if (!template.settings) errors.push('Template settings are required');

    // Category validation
    if (template.category && !this.categories.has(template.category)) {
      errors.push(`Invalid category: ${template.category}`);
    }

    // Settings validation based on category
    if (template.settings) {
      switch (template.category) {
        case 'audio':
          if (!template.settings.audio) errors.push('Audio settings required for audio template');
          break;
        case 'video':
          if (!template.settings.video) errors.push('Video settings required for video template');
          break;
        case 'image':
          if (!template.settings.canvas) errors.push('Canvas settings required for image template');
          break;
      }
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * Export template
   */
  async exportTemplate(templateId, exportPath) {
    try {
      const template = this.getTemplate(templateId);
      if (!template) {
        throw new Error('Template not found');
      }

      const exportData = {
        template,
        exported: new Date(),
        version: '1.0',
        aiflueVersion: '1.0.0'
      };

      await fs.writeFile(exportPath, JSON.stringify(exportData, null, 2));
      
      this.emit('templateExported', { templateId, exportPath });
      return true;
    } catch (error) {
      this.emit('error', new Error(`Failed to export template: ${error.message}`));
      return false;
    }
  }

  /**
   * Import template
   */
  async importTemplate(importPath) {
    try {
      const importData = await fs.readFile(importPath, 'utf8');
      const { template } = JSON.parse(importData);

      // Validate template
      const validation = this.validateTemplate(template);
      if (!validation.isValid) {
        throw new Error(`Invalid template: ${validation.errors.join(', ')}`);
      }

      // Generate new ID if template already exists
      let templateId = template.id;
      if (this.templates.has(templateId)) {
        templateId = `imported_${Date.now()}`;
        template.id = templateId;
      }

      // Mark as custom template
      template.isCustom = true;
      template.imported = new Date();

      this.templates.set(templateId, template);
      this.customTemplates.set(templateId, template);

      // Save to disk
      await this.saveCustomTemplate(template);

      this.emit('templateImported', template);
      return templateId;
    } catch (error) {
      this.emit('error', new Error(`Failed to import template: ${error.message}`));
      return null;
    }
  }
}

module.exports = ProjectTemplates;