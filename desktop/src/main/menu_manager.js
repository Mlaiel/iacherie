/**
 * Ainflue Desktop - Menu Manager
 * 
 * Native menu system for cross-platform desktop application
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This software is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

const { Menu, shell, dialog, app } = require('electron');
const log = require('electron-log');

class MenuManager {
  constructor(windowManager) {
    this.windowManager = windowManager;
    this.recentProjects = [];
    this.maxRecentProjects = 10;
  }

  createApplicationMenu() {
    const template = this.getMenuTemplate();
    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
    
    log.info('Application menu created');
    return menu;
  }

  getMenuTemplate() {
    const isMac = process.platform === 'darwin';
    
    const template = [
      // App Menu (macOS only)
      ...(isMac ? [{
        label: app.getName(),
        submenu: [
          { role: 'about' },
          { type: 'separator' },
          { role: 'services' },
          { type: 'separator' },
          { role: 'hide' },
          { role: 'hideothers' },
          { role: 'unhide' },
          { type: 'separator' },
          { role: 'quit' }
        ]
      }] : []),
      
      // File Menu
      {
        label: 'File',
        submenu: [
          {
            label: 'New Project',
            accelerator: 'CmdOrCtrl+N',
            click: () => this.handleNewProject()
          },
          {
            label: 'Open Project',
            accelerator: 'CmdOrCtrl+O',
            click: () => this.handleOpenProject()
          },
          {
            label: 'Open Recent',
            submenu: this.getRecentProjectsMenu()
          },
          { type: 'separator' },
          {
            label: 'Save Project',
            accelerator: 'CmdOrCtrl+S',
            click: () => this.handleSaveProject()
          },
          {
            label: 'Save Project As...',
            accelerator: 'CmdOrCtrl+Shift+S',
            click: () => this.handleSaveProjectAs()
          },
          { type: 'separator' },
          {
            label: 'Import',
            submenu: [
              {
                label: 'Import Audio...',
                click: () => this.handleImportAudio()
              },
              {
                label: 'Import Video...',
                click: () => this.handleImportVideo()
              },
              {
                label: 'Import Images...',
                click: () => this.handleImportImages()
              },
              {
                label: 'Import Project...',
                click: () => this.handleImportProject()
              }
            ]
          },
          {
            label: 'Export',
            submenu: [
              {
                label: 'Export Audio...',
                accelerator: 'CmdOrCtrl+E',
                click: () => this.handleExportAudio()
              },
              {
                label: 'Export Video...',
                click: () => this.handleExportVideo()
              },
              {
                label: 'Export Project...',
                click: () => this.handleExportProject()
              }
            ]
          },
          { type: 'separator' },
          ...(isMac ? [] : [{ role: 'quit' }])
        ]
      },
      
      // Edit Menu
      {
        label: 'Edit',
        submenu: [
          {
            label: 'Undo',
            accelerator: 'CmdOrCtrl+Z',
            click: () => this.handleUndo()
          },
          {
            label: 'Redo',
            accelerator: 'CmdOrCtrl+Shift+Z',
            click: () => this.handleRedo()
          },
          { type: 'separator' },
          { role: 'cut' },
          { role: 'copy' },
          { role: 'paste' },
          { role: 'selectall' },
          { type: 'separator' },
          {
            label: 'Find',
            accelerator: 'CmdOrCtrl+F',
            click: () => this.handleFind()
          },
          {
            label: 'Replace',
            accelerator: 'CmdOrCtrl+H',
            click: () => this.handleReplace()
          },
          { type: 'separator' },
          {
            label: 'Preferences',
            accelerator: 'CmdOrCtrl+,',
            click: () => this.handlePreferences()
          }
        ]
      },
      
      // Project Menu
      {
        label: 'Project',
        submenu: [
          {
            label: 'Project Settings',
            click: () => this.handleProjectSettings()
          },
          { type: 'separator' },
          {
            label: 'Add Track',
            accelerator: 'CmdOrCtrl+T',
            click: () => this.handleAddTrack()
          },
          {
            label: 'Add Audio Effect',
            click: () => this.handleAddAudioEffect()
          },
          {
            label: 'Add Video Effect',
            click: () => this.handleAddVideoEffect()
          },
          { type: 'separator' },
          {
            label: 'AI Analysis',
            submenu: [
              {
                label: 'Analyze Content',
                click: () => this.handleAIAnalysis()
              },
              {
                label: 'Generate Tags',
                click: () => this.handleGenerateTags()
              },
              {
                label: 'Optimize SEO',
                click: () => this.handleOptimizeSEO()
              }
            ]
          },
          { type: 'separator' },
          {
            label: 'Collaboration',
            submenu: [
              {
                label: 'Invite Collaborators',
                click: () => this.handleInviteCollaborators()
              },
              {
                label: 'Join Session',
                click: () => this.handleJoinSession()
              },
              {
                label: 'Share Project',
                click: () => this.handleShareProject()
              }
            ]
          }
        ]
      },
      
      // Tools Menu
      {
        label: 'Tools',
        submenu: [
          {
            label: 'Audio Tools',
            submenu: [
              {
                label: 'Audio Mixer',
                accelerator: 'CmdOrCtrl+M',
                click: () => this.handleOpenMixer()
              },
              {
                label: 'Equalizer',
                click: () => this.handleOpenEqualizer()
              },
              {
                label: 'Noise Reduction',
                click: () => this.handleNoiseReduction()
              }
            ]
          },
          {
            label: 'Video Tools',
            submenu: [
              {
                label: 'Color Correction',
                click: () => this.handleColorCorrection()
              },
              {
                label: 'Video Effects',
                click: () => this.handleVideoEffects()
              },
              {
                label: 'Transitions',
                click: () => this.handleTransitions()
              }
            ]
          },
          {
            label: 'Content Protection',
            submenu: [
              {
                label: 'Add Watermark',
                click: () => this.handleAddWatermark()
              },
              {
                label: 'Digital Signature',
                click: () => this.handleDigitalSignature()
              },
              {
                label: 'Rights Management',
                click: () => this.handleRightsManagement()
              }
            ]
          },
          { type: 'separator' },
          {
            label: 'Analytics Dashboard',
            accelerator: 'CmdOrCtrl+D',
            click: () => this.handleOpenAnalytics()
          },
          {
            label: 'Revenue Tracking',
            click: () => this.handleRevenueTracking()
          }
        ]
      },
      
      // Window Menu
      {
        label: 'Window',
        submenu: [
          {
            label: 'Timeline Editor',
            accelerator: 'CmdOrCtrl+1',
            click: () => this.handleOpenTimeline()
          },
          {
            label: 'Preview Window',
            accelerator: 'CmdOrCtrl+2',
            click: () => this.handleOpenPreview()
          },
          {
            label: 'Collaboration Hub',
            accelerator: 'CmdOrCtrl+3',
            click: () => this.handleOpenCollaboration()
          },
          { type: 'separator' },
          {
            label: 'Arrange Windows',
            submenu: [
              {
                label: 'Studio Layout',
                click: () => this.handleStudioLayout()
              },
              {
                label: 'Collaboration Layout',
                click: () => this.handleCollaborationLayout()
              },
              {
                label: 'Minimize All',
                click: () => this.handleMinimizeAll()
              },
              {
                label: 'Restore All',
                click: () => this.handleRestoreAll()
              }
            ]
          },
          { type: 'separator' },
          { role: 'minimize' },
          { role: 'close' },
          ...(isMac ? [
            { type: 'separator' },
            { role: 'front' },
            { type: 'separator' },
            { role: 'window' }
          ] : [])
        ]
      },
      
      // Help Menu
      {
        role: 'help',
        submenu: [
          {
            label: 'Getting Started',
            click: () => this.handleGettingStarted()
          },
          {
            label: 'User Manual',
            click: () => this.handleUserManual()
          },
          {
            label: 'Video Tutorials',
            click: () => this.handleVideoTutorials()
          },
          {
            label: 'Keyboard Shortcuts',
            accelerator: 'CmdOrCtrl+K',
            click: () => this.handleKeyboardShortcuts()
          },
          { type: 'separator' },
          {
            label: 'Report Issue',
            click: () => this.handleReportIssue()
          },
          {
            label: 'Feature Request',
            click: () => this.handleFeatureRequest()
          },
          { type: 'separator' },
          {
            label: 'Check for Updates',
            click: () => this.handleCheckUpdates()
          },
          {
            label: 'Release Notes',
            click: () => this.handleReleaseNotes()
          },
          { type: 'separator' },
          {
            label: 'About Ainflue Studio',
            click: () => this.handleAbout()
          }
        ]
      }
    ];

    return template;
  }

  getRecentProjectsMenu() {
    if (this.recentProjects.length === 0) {
      return [{ label: 'No Recent Projects', enabled: false }];
    }

    const recentMenu = this.recentProjects.map((project, index) => ({
      label: `${index + 1}. ${project.name}`,
      click: () => this.handleOpenRecentProject(project.path)
    }));

    recentMenu.push(
      { type: 'separator' },
      {
        label: 'Clear Recent Projects',
        click: () => this.handleClearRecentProjects()
      }
    );

    return recentMenu;
  }

  // File Menu Handlers
  async handleNewProject() {
    try {
      const mainWindow = this.windowManager.getWindow('main');
      if (mainWindow) {
        mainWindow.webContents.send('menu:new-project');
      }
    } catch (error) {
      log.error('Error creating new project:', error);
    }
  }

  async handleOpenProject() {
    try {
      const result = await dialog.showOpenDialog({
        title: 'Open Project',
        properties: ['openFile'],
        filters: [
          { name: 'Ainflue Projects', extensions: ['ainflue', 'json'] },
          { name: 'All Files', extensions: ['*'] }
        ]
      });

      if (!result.canceled && result.filePaths.length > 0) {
        const projectPath = result.filePaths[0];
        this.handleOpenRecentProject(projectPath);
      }
    } catch (error) {
      log.error('Error opening project:', error);
    }
  }

  handleOpenRecentProject(projectPath) {
    const mainWindow = this.windowManager.getWindow('main');
    if (mainWindow) {
      mainWindow.webContents.send('menu:open-project', projectPath);
    }
  }

  handleSaveProject() {
    const mainWindow = this.windowManager.getWindow('main');
    if (mainWindow) {
      mainWindow.webContents.send('menu:save-project');
    }
  }

  async handleSaveProjectAs() {
    try {
      const result = await dialog.showSaveDialog({
        title: 'Save Project As',
        defaultPath: 'Untitled Project.ainflue',
        filters: [
          { name: 'Ainflue Projects', extensions: ['ainflue'] },
          { name: 'JSON Files', extensions: ['json'] }
        ]
      });

      if (!result.canceled) {
        const mainWindow = this.windowManager.getWindow('main');
        if (mainWindow) {
          mainWindow.webContents.send('menu:save-project-as', result.filePath);
        }
      }
    } catch (error) {
      log.error('Error saving project:', error);
    }
  }

  // Import Handlers
  async handleImportAudio() {
    try {
      const result = await dialog.showOpenDialog({
        title: 'Import Audio Files',
        properties: ['openFile', 'multiSelections'],
        filters: [
          { name: 'Audio Files', extensions: ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a'] },
          { name: 'All Files', extensions: ['*'] }
        ]
      });

      if (!result.canceled && result.filePaths.length > 0) {
        const mainWindow = this.windowManager.getWindow('main');
        if (mainWindow) {
          mainWindow.webContents.send('menu:import-audio', result.filePaths);
        }
      }
    } catch (error) {
      log.error('Error importing audio:', error);
    }
  }

  async handleImportVideo() {
    try {
      const result = await dialog.showOpenDialog({
        title: 'Import Video Files',
        properties: ['openFile', 'multiSelections'],
        filters: [
          { name: 'Video Files', extensions: ['mp4', 'avi', 'mov', 'mkv', 'webm', 'wmv'] },
          { name: 'All Files', extensions: ['*'] }
        ]
      });

      if (!result.canceled && result.filePaths.length > 0) {
        const mainWindow = this.windowManager.getWindow('main');
        if (mainWindow) {
          mainWindow.webContents.send('menu:import-video', result.filePaths);
        }
      }
    } catch (error) {
      log.error('Error importing video:', error);
    }
  }

  async handleImportImages() {
    try {
      const result = await dialog.showOpenDialog({
        title: 'Import Image Files',
        properties: ['openFile', 'multiSelections'],
        filters: [
          { name: 'Image Files', extensions: ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp'] },
          { name: 'All Files', extensions: ['*'] }
        ]
      });

      if (!result.canceled && result.filePaths.length > 0) {
        const mainWindow = this.windowManager.getWindow('main');
        if (mainWindow) {
          mainWindow.webContents.send('menu:import-images', result.filePaths);
        }
      }
    } catch (error) {
      log.error('Error importing images:', error);
    }
  }

  // Window Handlers
  async handleOpenTimeline() {
    let timelineWindow = this.windowManager.getWindow('timeline');
    if (!timelineWindow || timelineWindow.isDestroyed()) {
      timelineWindow = await this.windowManager.createTimelineWindow();
    } else {
      this.windowManager.focusWindow('timeline');
    }
  }

  async handleOpenMixer() {
    let mixerWindow = this.windowManager.getWindow('mixer');
    if (!mixerWindow || mixerWindow.isDestroyed()) {
      mixerWindow = await this.windowManager.createMixerWindow();
    } else {
      this.windowManager.focusWindow('mixer');
    }
  }

  async handleOpenPreview() {
    let previewWindow = this.windowManager.getWindow('preview');
    if (!previewWindow || previewWindow.isDestroyed()) {
      previewWindow = await this.windowManager.createPreviewWindow();
    } else {
      this.windowManager.focusWindow('preview');
    }
  }

  async handleOpenAnalytics() {
    let analyticsWindow = this.windowManager.getWindow('analytics');
    if (!analyticsWindow || analyticsWindow.isDestroyed()) {
      analyticsWindow = await this.windowManager.createAnalyticsWindow();
    } else {
      this.windowManager.focusWindow('analytics');
    }
  }

  async handleOpenCollaboration() {
    let collaborationWindow = this.windowManager.getWindow('collaboration');
    if (!collaborationWindow || collaborationWindow.isDestroyed()) {
      collaborationWindow = await this.windowManager.createCollaborationWindow();
    } else {
      this.windowManager.focusWindow('collaboration');
    }
  }

  handlePreferences() {
    this.windowManager.createSettingsWindow();
  }

  handleStudioLayout() {
    this.windowManager.arrangeStudioLayout();
  }

  handleCollaborationLayout() {
    this.windowManager.arrangeCollaborationLayout();
  }

  handleMinimizeAll() {
    this.windowManager.minimizeAllWindows();
  }

  handleRestoreAll() {
    this.windowManager.restoreAllWindows();
  }

  // Help Menu Handlers
  handleGettingStarted() {
    shell.openExternal('https://ainflue.com/docs/getting-started');
  }

  handleUserManual() {
    shell.openExternal('https://ainflue.com/docs/user-manual');
  }

  handleVideoTutorials() {
    shell.openExternal('https://ainflue.com/tutorials');
  }

  handleKeyboardShortcuts() {
    const shortcutsWindow = this.windowManager.getWindow('main');
    if (shortcutsWindow) {
      shortcutsWindow.webContents.send('menu:show-shortcuts');
    }
  }

  handleReportIssue() {
    shell.openExternal('https://github.com/Mlaiel/Ainflue/issues/new');
  }

  handleFeatureRequest() {
    shell.openExternal('https://github.com/Mlaiel/Ainflue/discussions/new');
  }

  handleCheckUpdates() {
    const mainWindow = this.windowManager.getWindow('main');
    if (mainWindow) {
      mainWindow.webContents.send('menu:check-updates');
    }
  }

  handleReleaseNotes() {
    shell.openExternal('https://github.com/Mlaiel/Ainflue/releases');
  }

  async handleAbout() {
    await dialog.showMessageBox({
      type: 'info',
      title: 'About Ainflue Studio',
      message: 'Ainflue Studio',
      detail: `Version: ${app.getVersion()}\n\nAI-powered content creation and collaboration platform.\n\n© 2025 Fahed Mlaiel. All rights reserved.\nContact: mlaiel@live.de`,
      buttons: ['OK']
    });
  }

  // Utility methods
  addRecentProject(projectPath, projectName) {
    // Remove if already exists
    this.recentProjects = this.recentProjects.filter(p => p.path !== projectPath);
    
    // Add to beginning
    this.recentProjects.unshift({ path: projectPath, name: projectName });
    
    // Limit to max
    if (this.recentProjects.length > this.maxRecentProjects) {
      this.recentProjects = this.recentProjects.slice(0, this.maxRecentProjects);
    }
    
    // Rebuild menu
    this.updateApplicationMenu();
  }

  handleClearRecentProjects() {
    this.recentProjects = [];
    this.updateApplicationMenu();
  }

  updateApplicationMenu() {
    const template = this.getMenuTemplate();
    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
  }

  // Placeholder handlers for menu items not yet implemented
  handleImportProject() { log.info('Import project not yet implemented'); }
  handleExportAudio() { log.info('Export audio not yet implemented'); }
  handleExportVideo() { log.info('Export video not yet implemented'); }
  handleExportProject() { log.info('Export project not yet implemented'); }
  handleUndo() { log.info('Undo not yet implemented'); }
  handleRedo() { log.info('Redo not yet implemented'); }
  handleFind() { log.info('Find not yet implemented'); }
  handleReplace() { log.info('Replace not yet implemented'); }
  handleProjectSettings() { log.info('Project settings not yet implemented'); }
  handleAddTrack() { log.info('Add track not yet implemented'); }
  handleAddAudioEffect() { log.info('Add audio effect not yet implemented'); }
  handleAddVideoEffect() { log.info('Add video effect not yet implemented'); }
  handleAIAnalysis() { log.info('AI analysis not yet implemented'); }
  handleGenerateTags() { log.info('Generate tags not yet implemented'); }
  handleOptimizeSEO() { log.info('Optimize SEO not yet implemented'); }
  handleInviteCollaborators() { log.info('Invite collaborators not yet implemented'); }
  handleJoinSession() { log.info('Join session not yet implemented'); }
  handleShareProject() { log.info('Share project not yet implemented'); }
  handleOpenEqualizer() { log.info('Open equalizer not yet implemented'); }
  handleNoiseReduction() { log.info('Noise reduction not yet implemented'); }
  handleColorCorrection() { log.info('Color correction not yet implemented'); }
  handleVideoEffects() { log.info('Video effects not yet implemented'); }
  handleTransitions() { log.info('Transitions not yet implemented'); }
  handleAddWatermark() { log.info('Add watermark not yet implemented'); }
  handleDigitalSignature() { log.info('Digital signature not yet implemented'); }
  handleRightsManagement() { log.info('Rights management not yet implemented'); }
  handleRevenueTracking() { log.info('Revenue tracking not yet implemented'); }
}

module.exports = MenuManager;