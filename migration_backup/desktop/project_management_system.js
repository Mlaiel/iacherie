/**
 * Ainflue Desktop - Project Management System
 * 
 * Advanced project state management and persistence for creator workflows
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This software is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

const { EventEmitter } = require('events');
const path = require('path');
const fs = require('fs').promises;
const log = require('electron-log');
const crypto = require('crypto');

class ProjectManagementSystem extends EventEmitter {
  constructor() {
    super();
    this.projects = new Map();
    this.activeProject = null;
    this.projectsPath = path.join(process.cwd(), 'data', 'projects');
    this.backupPath = path.join(process.cwd(), 'data', 'backups');
    this.templates = new Map();
    this.recentProjects = [];
    this.maxRecentProjects = 10;
    this.autoSaveInterval = 30000; // 30 seconds
    this.autoSaveTimer = null;
  }

  async initialize() {
    try {
      log.info('Initializing Project Management System...');
      
      // Setup project directories
      await this.setupDirectories();
      
      // Load project templates
      await this.loadProjectTemplates();
      
      // Load recent projects
      await this.loadRecentProjects();
      
      // Load existing projects metadata
      await this.loadProjectsMetadata();
      
      // Setup auto-save
      this.setupAutoSave();
      
      log.info('Project Management System initialized successfully');
      this.emit('system:ready');
      
    } catch (error) {
      log.error('Failed to initialize Project Management System:', error);
      throw error;
    }
  }

  async setupDirectories() {
    const directories = [
      this.projectsPath,
      this.backupPath,
      path.join(this.projectsPath, 'templates'),
      path.join(this.projectsPath, 'exports'),
      path.join(this.projectsPath, 'assets')
    ];

    for (const dir of directories) {
      try {
        await fs.mkdir(dir, { recursive: true });
        log.debug(`Created project directory: ${dir}`);
      } catch (error) {
        log.warn(`Failed to create directory ${dir}:`, error);
      }
    }
  }

  async loadProjectTemplates() {
    this.templates.set('music_album', {
      id: 'music_album',
      name: 'Music Album Project',
      description: 'Professional music album production workflow',
      category: 'music',
      structure: {
        tracks: [],
        artwork: null,
        metadata: {
          title: '',
          artist: '',
          genre: '',
          releaseDate: null,
          label: ''
        },
        workflow: {
          stages: ['composition', 'recording', 'mixing', 'mastering', 'distribution'],
          currentStage: 'composition'
        }
      },
      settings: {
        audioFormat: 'wav',
        sampleRate: 48000,
        bitDepth: 24,
        collaborationEnabled: true,
        aiProcessingEnabled: true
      }
    });

    this.templates.set('video_series', {
      id: 'video_series',
      name: 'Video Series Project',
      description: 'Multi-episode video content creation',
      category: 'video',
      structure: {
        episodes: [],
        series_metadata: {
          title: '',
          description: '',
          category: '',
          tags: []
        },
        workflow: {
          stages: ['scripting', 'filming', 'editing', 'post_production', 'publishing'],
          currentStage: 'scripting'
        }
      },
      settings: {
        videoFormat: 'mp4',
        resolution: '1080p',
        frameRate: 30,
        collaborationEnabled: true,
        aiProcessingEnabled: true
      }
    });

    this.templates.set('podcast_show', {
      id: 'podcast_show',
      name: 'Podcast Show Project',
      description: 'Professional podcast production workflow',
      category: 'audio',
      structure: {
        episodes: [],
        show_metadata: {
          title: '',
          description: '',
          category: '',
          hosts: [],
          tags: []
        },
        workflow: {
          stages: ['planning', 'recording', 'editing', 'post_production', 'distribution'],
          currentStage: 'planning'
        }
      },
      settings: {
        audioFormat: 'mp3',
        sampleRate: 44100,
        bitrate: 192,
        collaborationEnabled: true,
        aiProcessingEnabled: true
      }
    });

    this.templates.set('social_campaign', {
      id: 'social_campaign',
      name: 'Social Media Campaign',
      description: 'Multi-platform social media content campaign',
      category: 'social',
      structure: {
        platforms: ['instagram', 'tiktok', 'youtube', 'twitter'],
        content_items: [],
        campaign_metadata: {
          title: '',
          objective: '',
          target_audience: '',
          duration: 30,
          budget: 0
        },
        workflow: {
          stages: ['strategy', 'content_creation', 'scheduling', 'publishing', 'analytics'],
          currentStage: 'strategy'
        }
      },
      settings: {
        autoPosting: false,
        aiOptimization: true,
        collaborationEnabled: true,
        analyticsEnabled: true
      }
    });

    log.info(`Loaded ${this.templates.size} project templates`);
  }

  async createProject(templateId, projectData) {
    try {
      const template = this.templates.get(templateId);
      if (!template) {
        throw new Error(`Unknown template: ${templateId}`);
      }

      const projectId = crypto.randomUUID();
      const timestamp = new Date().toISOString();
      
      const project = {
        id: projectId,
        name: projectData.name || `New ${template.name}`,
        description: projectData.description || '',
        template: templateId,
        created: timestamp,
        modified: timestamp,
        version: '1.0.0',
        status: 'active',
        owner: projectData.owner || 'local_user',
        collaborators: projectData.collaborators || [],
        structure: JSON.parse(JSON.stringify(template.structure)),
        settings: { ...template.settings, ...projectData.settings },
        metadata: {
          totalAssets: 0,
          totalSize: 0,
          lastBackup: null,
          tags: projectData.tags || []
        },
        timeline: {
          milestones: [],
          deadlines: [],
          events: []
        },
        assets: {
          media: [],
          documents: [],
          exports: []
        },
        workflow: {
          ...template.structure.workflow,
          history: [{
            stage: template.structure.workflow.currentStage,
            timestamp,
            user: projectData.owner || 'local_user',
            action: 'project_created'
          }]
        }
      };

      // Create project directory
      const projectPath = path.join(this.projectsPath, projectId);
      await fs.mkdir(projectPath, { recursive: true });
      
      // Create project subdirectories
      const subdirs = ['assets', 'exports', 'backups', 'temp'];
      for (const subdir of subdirs) {
        await fs.mkdir(path.join(projectPath, subdir), { recursive: true });
      }

      // Save project file
      const projectFile = path.join(projectPath, 'project.json');
      await fs.writeFile(projectFile, JSON.stringify(project, null, 2));

      // Add to active projects
      this.projects.set(projectId, project);
      
      // Update recent projects
      this.addToRecentProjects(project);
      
      // Set as active project
      this.activeProject = project;

      log.info(`Created new project: ${project.name} (${projectId})`);
      this.emit('project:created', { project });
      
      return project;
      
    } catch (error) {
      log.error('Failed to create project:', error);
      throw error;
    }
  }

  async loadProject(projectId) {
    try {
      const projectPath = path.join(this.projectsPath, projectId, 'project.json');
      const projectData = await fs.readFile(projectPath, 'utf8');
      const project = JSON.parse(projectData);
      
      // Validate project structure
      if (!this.validateProjectStructure(project)) {
        throw new Error('Invalid project structure');
      }
      
      // Load project assets metadata
      await this.loadProjectAssets(project);
      
      // Add to active projects
      this.projects.set(projectId, project);
      
      // Update recent projects
      this.addToRecentProjects(project);
      
      log.info(`Loaded project: ${project.name} (${projectId})`);
      this.emit('project:loaded', { project });
      
      return project;
      
    } catch (error) {
      log.error(`Failed to load project ${projectId}:`, error);
      throw error;
    }
  }

  async saveProject(projectId, updateData = {}) {
    try {
      const project = this.projects.get(projectId);
      if (!project) {
        throw new Error(`Project not found: ${projectId}`);
      }

      // Update project data
      Object.assign(project, updateData);
      project.modified = new Date().toISOString();
      project.version = this.incrementVersion(project.version);

      // Save to file
      const projectPath = path.join(this.projectsPath, projectId, 'project.json');
      await fs.writeFile(projectPath, JSON.stringify(project, null, 2));

      log.debug(`Saved project: ${project.name} (${projectId})`);
      this.emit('project:saved', { project });
      
      return project;
      
    } catch (error) {
      log.error(`Failed to save project ${projectId}:`, error);
      throw error;
    }
  }

  async deleteProject(projectId, permanent = false) {
    try {
      const project = this.projects.get(projectId);
      if (!project) {
        throw new Error(`Project not found: ${projectId}`);
      }

      if (permanent) {
        // Permanently delete project directory
        const projectPath = path.join(this.projectsPath, projectId);
        await fs.rm(projectPath, { recursive: true, force: true });
        log.info(`Permanently deleted project: ${project.name} (${projectId})`);
      } else {
        // Move to trash (mark as deleted)
        project.status = 'deleted';
        project.deletedAt = new Date().toISOString();
        await this.saveProject(projectId);
        log.info(`Moved project to trash: ${project.name} (${projectId})`);
      }

      // Remove from active projects
      this.projects.delete(projectId);
      
      // Remove from recent projects
      this.recentProjects = this.recentProjects.filter(p => p.id !== projectId);
      await this.saveRecentProjects();

      this.emit('project:deleted', { projectId, permanent });
      
    } catch (error) {
      log.error(`Failed to delete project ${projectId}:`, error);
      throw error;
    }
  }

  async setActiveProject(projectId) {
    try {
      let project = this.projects.get(projectId);
      
      if (!project) {
        project = await this.loadProject(projectId);
      }

      this.activeProject = project;
      this.emit('project:activated', { project });
      
      log.info(`Set active project: ${project.name} (${projectId})`);
      return project;
      
    } catch (error) {
      log.error(`Failed to set active project ${projectId}:`, error);
      throw error;
    }
  }

  getActiveProject() {
    return this.activeProject;
  }

  getAllProjects() {
    return Array.from(this.projects.values()).filter(p => p.status !== 'deleted');
  }

  getRecentProjects() {
    return [...this.recentProjects];
  }

  getProjectTemplates() {
    return Array.from(this.templates.values());
  }

  async addAssetToProject(projectId, assetData) {
    try {
      const project = this.projects.get(projectId);
      if (!project) {
        throw new Error(`Project not found: ${projectId}`);
      }

      const asset = {
        id: crypto.randomUUID(),
        name: assetData.name,
        type: assetData.type,
        path: assetData.path,
        size: assetData.size,
        mimeType: assetData.mimeType,
        added: new Date().toISOString(),
        metadata: assetData.metadata || {},
        tags: assetData.tags || []
      };

      // Add to appropriate asset category
      if (['image', 'video', 'audio'].includes(asset.type)) {
        project.assets.media.push(asset);
      } else {
        project.assets.documents.push(asset);
      }

      // Update project metadata
      project.metadata.totalAssets++;
      project.metadata.totalSize += asset.size;

      await this.saveProject(projectId);
      
      log.info(`Added asset to project ${projectId}: ${asset.name}`);
      this.emit('project:asset_added', { projectId, asset });
      
      return asset;
      
    } catch (error) {
      log.error(`Failed to add asset to project ${projectId}:`, error);
      throw error;
    }
  }

  async removeAssetFromProject(projectId, assetId) {
    try {
      const project = this.projects.get(projectId);
      if (!project) {
        throw new Error(`Project not found: ${projectId}`);
      }

      // Find and remove asset
      let removedAsset = null;
      
      for (const category of ['media', 'documents']) {
        const assetIndex = project.assets[category].findIndex(a => a.id === assetId);
        if (assetIndex !== -1) {
          removedAsset = project.assets[category].splice(assetIndex, 1)[0];
          break;
        }
      }

      if (!removedAsset) {
        throw new Error(`Asset not found: ${assetId}`);
      }

      // Update project metadata
      project.metadata.totalAssets--;
      project.metadata.totalSize -= removedAsset.size;

      await this.saveProject(projectId);
      
      log.info(`Removed asset from project ${projectId}: ${removedAsset.name}`);
      this.emit('project:asset_removed', { projectId, assetId });
      
    } catch (error) {
      log.error(`Failed to remove asset from project ${projectId}:`, error);
      throw error;
    }
  }

  async updateProjectWorkflow(projectId, stage, action, metadata = {}) {
    try {
      const project = this.projects.get(projectId);
      if (!project) {
        throw new Error(`Project not found: ${projectId}`);
      }

      // Update current stage
      project.workflow.currentStage = stage;
      
      // Add workflow history entry
      const historyEntry = {
        stage,
        action,
        timestamp: new Date().toISOString(),
        user: metadata.user || 'local_user',
        metadata
      };
      
      project.workflow.history.push(historyEntry);

      await this.saveProject(projectId);
      
      log.info(`Updated workflow for project ${projectId}: ${stage} -> ${action}`);
      this.emit('project:workflow_updated', { projectId, stage, action });
      
    } catch (error) {
      log.error(`Failed to update workflow for project ${projectId}:`, error);
      throw error;
    }
  }

  async createProjectBackup(projectId) {
    try {
      const project = this.projects.get(projectId);
      if (!project) {
        throw new Error(`Project not found: ${projectId}`);
      }

      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const backupName = `${project.name}-${timestamp}`;
      const backupPath = path.join(this.backupPath, `${backupName}.zip`);

      // Implementation for creating ZIP backup
      // This would use archiver or similar library to create project backup
      
      project.metadata.lastBackup = new Date().toISOString();
      await this.saveProject(projectId);

      log.info(`Created backup for project ${projectId}: ${backupPath}`);
      this.emit('project:backup_created', { projectId, backupPath });
      
      return backupPath;
      
    } catch (error) {
      log.error(`Failed to create backup for project ${projectId}:`, error);
      throw error;
    }
  }

  async exportProject(projectId, format, options = {}) {
    try {
      const project = this.projects.get(projectId);
      if (!project) {
        throw new Error(`Project not found: ${projectId}`);
      }

      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const exportName = `${project.name}-export-${timestamp}`;
      const exportPath = path.join(this.projectsPath, projectId, 'exports', exportName);

      await fs.mkdir(exportPath, { recursive: true });

      // Implementation for different export formats
      switch (format) {
        case 'json':
          await this.exportAsJSON(project, exportPath, options);
          break;
        case 'zip':
          await this.exportAsZIP(project, exportPath, options);
          break;
        case 'package':
          await this.exportAsPackage(project, exportPath, options);
          break;
        default:
          throw new Error(`Unsupported export format: ${format}`);
      }

      // Add to project exports
      const exportRecord = {
        id: crypto.randomUUID(),
        name: exportName,
        format,
        path: exportPath,
        created: new Date().toISOString(),
        options
      };
      
      project.assets.exports.push(exportRecord);
      await this.saveProject(projectId);

      log.info(`Exported project ${projectId} as ${format}: ${exportPath}`);
      this.emit('project:exported', { projectId, format, exportPath });
      
      return exportPath;
      
    } catch (error) {
      log.error(`Failed to export project ${projectId}:`, error);
      throw error;
    }
  }

  async exportAsJSON(project, exportPath, options) {
    const exportData = {
      project,
      exportInfo: {
        timestamp: new Date().toISOString(),
        version: '1.0.0',
        options
      }
    };
    
    const filePath = path.join(exportPath, 'project.json');
    await fs.writeFile(filePath, JSON.stringify(exportData, null, 2));
  }

  async exportAsZIP(project, exportPath, options) {
    // Implementation for ZIP export
    log.info(`ZIP export for project ${project.id} not yet implemented`);
  }

  async exportAsPackage(project, exportPath, options) {
    // Implementation for package export
    log.info(`Package export for project ${project.id} not yet implemented`);
  }

  // Utility methods
  validateProjectStructure(project) {
    const requiredFields = ['id', 'name', 'template', 'created', 'structure', 'settings'];
    return requiredFields.every(field => project.hasOwnProperty(field));
  }

  incrementVersion(version) {
    const parts = version.split('.');
    const patch = parseInt(parts[2]) + 1;
    return `${parts[0]}.${parts[1]}.${patch}`;
  }

  async loadProjectAssets(project) {
    // Load asset metadata and verify file existence
    for (const category of ['media', 'documents']) {
      for (const asset of project.assets[category]) {
        try {
          const stats = await fs.stat(asset.path);
          asset.exists = true;
          asset.lastModified = stats.mtime.toISOString();
        } catch (error) {
          asset.exists = false;
          log.warn(`Asset file not found: ${asset.path}`);
        }
      }
    }
  }

  addToRecentProjects(project) {
    // Remove if already exists
    this.recentProjects = this.recentProjects.filter(p => p.id !== project.id);
    
    // Add to beginning
    this.recentProjects.unshift({
      id: project.id,
      name: project.name,
      template: project.template,
      modified: project.modified
    });
    
    // Limit to max recent projects
    if (this.recentProjects.length > this.maxRecentProjects) {
      this.recentProjects = this.recentProjects.slice(0, this.maxRecentProjects);
    }
    
    this.saveRecentProjects();
  }

  async loadRecentProjects() {
    try {
      const recentPath = path.join(this.projectsPath, 'recent.json');
      const data = await fs.readFile(recentPath, 'utf8');
      this.recentProjects = JSON.parse(data);
    } catch (error) {
      log.debug('No recent projects file found, starting fresh');
      this.recentProjects = [];
    }
  }

  async saveRecentProjects() {
    try {
      const recentPath = path.join(this.projectsPath, 'recent.json');
      await fs.writeFile(recentPath, JSON.stringify(this.recentProjects, null, 2));
    } catch (error) {
      log.warn('Failed to save recent projects:', error);
    }
  }

  async loadProjectsMetadata() {
    try {
      const projectDirs = await fs.readdir(this.projectsPath);
      
      for (const dir of projectDirs) {
        if (dir === 'templates' || dir === 'recent.json') continue;
        
        try {
          const projectPath = path.join(this.projectsPath, dir, 'project.json');
          const stats = await fs.stat(projectPath);
          
          if (stats.isFile()) {
            // Load project metadata only (not full project)
            const data = await fs.readFile(projectPath, 'utf8');
            const project = JSON.parse(data);
            
            if (project.status !== 'deleted') {
              this.projects.set(project.id, project);
            }
          }
        } catch (error) {
          log.warn(`Failed to load project metadata from ${dir}:`, error);
        }
      }
      
      log.info(`Loaded metadata for ${this.projects.size} projects`);
      
    } catch (error) {
      log.warn('Failed to load projects metadata:', error);
    }
  }

  setupAutoSave() {
    if (this.autoSaveTimer) {
      clearInterval(this.autoSaveTimer);
    }
    
    this.autoSaveTimer = setInterval(async () => {
      if (this.activeProject) {
        try {
          await this.saveProject(this.activeProject.id);
          log.debug(`Auto-saved active project: ${this.activeProject.name}`);
        } catch (error) {
          log.warn('Auto-save failed:', error);
        }
      }
    }, this.autoSaveInterval);
  }

  async cleanup() {
    try {
      // Clear auto-save timer
      if (this.autoSaveTimer) {
        clearInterval(this.autoSaveTimer);
        this.autoSaveTimer = null;
      }
      
      // Save active project
      if (this.activeProject) {
        await this.saveProject(this.activeProject.id);
      }
      
      // Save recent projects
      await this.saveRecentProjects();
      
      log.info('Project Management System cleanup completed');
      
    } catch (error) {
      log.error('Error during Project Management System cleanup:', error);
    }
  }
}

module.exports = ProjectManagementSystem;