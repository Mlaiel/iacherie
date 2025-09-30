/**
 * Ainflue Desktop - Backup Manager
 * 
 * Automated backup and recovery system for creative projects
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

const { EventEmitter } = require('events');
const fs = require('fs').promises;
const path = require('path');
const crypto = require('crypto');
const zlib = require('zlib');
const { promisify } = require('util');

const gzip = promisify(zlib.gzip);
const gunzip = promisify(zlib.gunzip);

class BackupManager extends EventEmitter {
  constructor() {
    super();
    this.backups = new Map();
    this.schedules = new Map();
    this.backupPath = null;
    this.retention = {
      daily: 7,
      weekly: 4,
      monthly: 12,
      yearly: 5
    };
    this.isRunning = false;
    this.activeBackup = null;
    
    this.initializeDefaultSchedules();
  }

  /**
   * Initialize default backup schedules
   */
  initializeDefaultSchedules() {
    this.schedules.set('auto_save', {
      id: 'auto_save',
      name: 'Auto Save',
      type: 'incremental',
      frequency: 'every_5_minutes',
      enabled: true,
      destinations: ['local'],
      compression: true,
      encryption: false
    });

    this.schedules.set('daily_backup', {
      id: 'daily_backup',
      name: 'Daily Backup',
      type: 'full',
      frequency: 'daily',
      time: '02:00',
      enabled: true,
      destinations: ['local', 'cloud'],
      compression: true,
      encryption: true
    });

    this.schedules.set('weekly_archive', {
      id: 'weekly_archive',
      name: 'Weekly Archive',
      type: 'archive',
      frequency: 'weekly',
      day: 'sunday',
      time: '03:00',
      enabled: true,
      destinations: ['cloud', 'external'],
      compression: true,
      encryption: true
    });
  }

  /**
   * Configure backup settings
   */
  configureBackup(projectPath, settings = {}) {
    this.backupPath = path.join(projectPath, '.backups');
    this.settings = {
      compression: true,
      encryption: false,
      maxBackups: 50,
      excludePatterns: ['*.tmp', '*.log', 'node_modules/', '.git/'],
      includeHidden: false,
      verifyIntegrity: true,
      ...settings
    };

    this.emit('backupConfigured', this.settings);
    return true;
  }

  /**
   * Create manual backup
   */
  async createBackup(projectPath, options = {}) {
    if (this.isRunning) {
      throw new Error('Another backup is already running');
    }

    try {
      this.isRunning = true;
      const backupId = this.generateBackupId();
      
      const backup = {
        id: backupId,
        type: options.type || 'manual',
        created: new Date(),
        projectPath,
        status: 'running',
        progress: 0,
        files: [],
        size: 0,
        compressed: options.compression !== false,
        encrypted: options.encryption === true,
        metadata: {
          name: options.name || `Backup ${new Date().toLocaleString()}`,
          description: options.description || '',
          tags: options.tags || []
        }
      };

      this.activeBackup = backup;
      this.backups.set(backupId, backup);
      
      this.emit('backupStarted', backup);

      // Ensure backup directory exists
      await fs.mkdir(this.backupPath, { recursive: true });

      // Scan project files
      const files = await this.scanProjectFiles(projectPath);
      backup.files = files;
      backup.progress = 10;
      this.emit('backupProgress', backup);

      // Create backup archive
      const archivePath = await this.createBackupArchive(backup, files);
      backup.archivePath = archivePath;
      backup.progress = 90;
      this.emit('backupProgress', backup);

      // Verify backup integrity
      if (this.settings.verifyIntegrity) {
        const isValid = await this.verifyBackup(backup);
        backup.verified = isValid;
      }

      backup.status = 'completed';
      backup.progress = 100;
      backup.completed = new Date();
      backup.duration = backup.completed - backup.created;

      this.emit('backupCompleted', backup);
      return backup;

    } catch (error) {
      if (this.activeBackup) {
        this.activeBackup.status = 'failed';
        this.activeBackup.error = error.message;
        this.emit('backupFailed', { backup: this.activeBackup, error });
      }
      throw error;
    } finally {
      this.isRunning = false;
      this.activeBackup = null;
    }
  }

  /**
   * Restore from backup
   */
  async restoreBackup(backupId, targetPath, options = {}) {
    try {
      const backup = this.backups.get(backupId);
      if (!backup) {
        throw new Error('Backup not found');
      }

      if (backup.status !== 'completed') {
        throw new Error('Cannot restore from incomplete backup');
      }

      this.emit('restoreStarted', { backup, targetPath });

      // Create target directory
      await fs.mkdir(targetPath, { recursive: true });

      // Extract backup archive
      await this.extractBackupArchive(backup, targetPath);

      // Verify restored files
      if (options.verify !== false) {
        const verification = await this.verifyRestoration(backup, targetPath);
        if (!verification.success) {
          throw new Error(`Restoration verification failed: ${verification.errors.join(', ')}`);
        }
      }

      this.emit('restoreCompleted', { backup, targetPath });
      return true;

    } catch (error) {
      this.emit('restoreFailed', { backupId, error });
      throw error;
    }
  }

  /**
   * Scan project files for backup
   */
  async scanProjectFiles(projectPath) {
    const files = [];
    
    const scanDirectory = async (dir, relativePath = '') => {
      const entries = await fs.readdir(dir, { withFileTypes: true });
      
      for (const entry of entries) {
        const entryPath = path.join(dir, entry.name);
        const relativeEntryPath = path.join(relativePath, entry.name);
        
        // Check exclude patterns
        if (this.isExcluded(relativeEntryPath)) {
          continue;
        }

        if (entry.isDirectory()) {
          await scanDirectory(entryPath, relativeEntryPath);
        } else {
          const stats = await fs.stat(entryPath);
          const file = {
            path: relativeEntryPath,
            fullPath: entryPath,
            size: stats.size,
            modified: stats.mtime,
            checksum: await this.calculateFileChecksum(entryPath)
          };
          files.push(file);
        }
      }
    };

    await scanDirectory(projectPath);
    return files;
  }

  /**
   * Check if file should be excluded
   */
  isExcluded(filePath) {
    if (!this.settings.includeHidden && filePath.startsWith('.')) {
      return true;
    }

    for (const pattern of this.settings.excludePatterns) {
      if (this.matchPattern(filePath, pattern)) {
        return true;
      }
    }

    return false;
  }

  /**
   * Match file against pattern
   */
  matchPattern(filePath, pattern) {
    // Simple pattern matching
    if (pattern.endsWith('/')) {
      return filePath.startsWith(pattern) || filePath.includes('/' + pattern);
    }
    
    if (pattern.startsWith('*.')) {
      const extension = pattern.slice(1);
      return filePath.endsWith(extension);
    }
    
    return filePath.includes(pattern);
  }

  /**
   * Create backup archive
   */
  async createBackupArchive(backup, files) {
    const archiveName = `${backup.id}.backup`;
    const archivePath = path.join(this.backupPath, archiveName);
    
    const archiveData = {
      metadata: backup.metadata,
      created: backup.created,
      type: backup.type,
      files: [],
      manifest: {
        version: '1.0',
        totalFiles: files.length,
        totalSize: 0
      }
    };

    let processedFiles = 0;
    const fileContents = new Map();

    // Process each file
    for (const file of files) {
      try {
        const content = await fs.readFile(file.fullPath);
        let processedContent = content;

        // Compress if enabled
        if (backup.compressed) {
          processedContent = await gzip(content);
        }

        // Store file content
        fileContents.set(file.path, processedContent);
        
        archiveData.files.push({
          path: file.path,
          size: file.size,
          compressedSize: processedContent.length,
          modified: file.modified,
          checksum: file.checksum,
          compressed: backup.compressed
        });

        archiveData.manifest.totalSize += file.size;
        processedFiles++;

        // Update progress
        backup.progress = 10 + Math.round((processedFiles / files.length) * 70);
        this.emit('backupProgress', backup);

      } catch (error) {
        console.warn(`Failed to process file ${file.path}: ${error.message}`);
      }
    }

    // Create archive structure
    const archive = {
      header: archiveData,
      files: Object.fromEntries(fileContents)
    };

    // Save archive
    let archiveContent = JSON.stringify(archive);
    
    // Encrypt if enabled
    if (backup.encrypted && this.settings.encryptionKey) {
      archiveContent = await this.encryptData(archiveContent);
    }

    await fs.writeFile(archivePath, archiveContent);
    backup.size = archiveContent.length;

    return archivePath;
  }

  /**
   * Extract backup archive
   */
  async extractBackupArchive(backup, targetPath) {
    try {
      let archiveContent = await fs.readFile(backup.archivePath, 'utf8');
      
      // Decrypt if encrypted
      if (backup.encrypted) {
        archiveContent = await this.decryptData(archiveContent);
      }

      const archive = JSON.parse(archiveContent);
      const { header, files } = archive;

      // Extract files
      for (const fileInfo of header.files) {
        const filePath = path.join(targetPath, fileInfo.path);
        const fileDir = path.dirname(filePath);
        
        // Ensure directory exists
        await fs.mkdir(fileDir, { recursive: true });
        
        // Get file content
        let content = Buffer.from(files[fileInfo.path], 'base64');
        
        // Decompress if compressed
        if (fileInfo.compressed) {
          content = await gunzip(content);
        }
        
        // Write file
        await fs.writeFile(filePath, content);
        
        // Restore file timestamps
        const stats = await fs.stat(filePath);
        await fs.utimes(filePath, stats.atime, new Date(fileInfo.modified));
      }

      return true;
    } catch (error) {
      throw new Error(`Failed to extract backup: ${error.message}`);
    }
  }

  /**
   * Verify backup integrity
   */
  async verifyBackup(backup) {
    try {
      // Check if archive file exists and is readable
      await fs.access(backup.archivePath);
      
      // Read and parse archive
      let archiveContent = await fs.readFile(backup.archivePath, 'utf8');
      
      if (backup.encrypted) {
        archiveContent = await this.decryptData(archiveContent);
      }
      
      const archive = JSON.parse(archiveContent);
      
      // Verify structure
      if (!archive.header || !archive.files) {
        return false;
      }
      
      // Verify file count
      if (archive.header.files.length !== Object.keys(archive.files).length) {
        return false;
      }
      
      backup.verification = {
        verified: true,
        timestamp: new Date(),
        fileCount: archive.header.files.length,
        totalSize: archive.header.manifest.totalSize
      };
      
      return true;
    } catch (error) {
      backup.verification = {
        verified: false,
        timestamp: new Date(),
        error: error.message
      };
      return false;
    }
  }

  /**
   * Verify restoration
   */
  async verifyRestoration(backup, targetPath) {
    const errors = [];
    let verifiedFiles = 0;
    
    try {
      // Read backup manifest
      let archiveContent = await fs.readFile(backup.archivePath, 'utf8');
      
      if (backup.encrypted) {
        archiveContent = await this.decryptData(archiveContent);
      }
      
      const archive = JSON.parse(archiveContent);
      
      // Verify each file
      for (const fileInfo of archive.header.files) {
        const restoredPath = path.join(targetPath, fileInfo.path);
        
        try {
          // Check if file exists
          await fs.access(restoredPath);
          
          // Verify checksum
          const restoredChecksum = await this.calculateFileChecksum(restoredPath);
          if (restoredChecksum !== fileInfo.checksum) {
            errors.push(`Checksum mismatch for ${fileInfo.path}`);
          } else {
            verifiedFiles++;
          }
        } catch (error) {
          errors.push(`Missing file: ${fileInfo.path}`);
        }
      }
      
      return {
        success: errors.length === 0,
        verifiedFiles,
        totalFiles: archive.header.files.length,
        errors
      };
    } catch (error) {
      return {
        success: false,
        verifiedFiles: 0,
        totalFiles: 0,
        errors: [error.message]
      };
    }
  }

  /**
   * Schedule automatic backup
   */
  scheduleBackup(projectPath, scheduleId) {
    const schedule = this.schedules.get(scheduleId);
    if (!schedule || !schedule.enabled) {
      return false;
    }

    // Calculate next run time
    const nextRun = this.calculateNextRun(schedule);
    
    schedule.nextRun = nextRun;
    schedule.projectPath = projectPath;
    
    // Set timeout for next backup
    const delay = nextRun - new Date();
    if (delay > 0) {
      schedule.timeoutId = setTimeout(() => {
        this.executeScheduledBackup(scheduleId);
      }, delay);
    }

    this.emit('backupScheduled', schedule);
    return true;
  }

  /**
   * Execute scheduled backup
   */
  async executeScheduledBackup(scheduleId) {
    try {
      const schedule = this.schedules.get(scheduleId);
      if (!schedule) return;

      await this.createBackup(schedule.projectPath, {
        type: schedule.type,
        name: `${schedule.name} - ${new Date().toLocaleString()}`,
        compression: schedule.compression,
        encryption: schedule.encryption
      });

      // Schedule next backup
      this.scheduleBackup(schedule.projectPath, scheduleId);

    } catch (error) {
      this.emit('scheduledBackupFailed', { scheduleId, error });
    }
  }

  /**
   * Calculate next run time for schedule
   */
  calculateNextRun(schedule) {
    const now = new Date();
    const nextRun = new Date(now);

    switch (schedule.frequency) {
      case 'every_5_minutes':
        nextRun.setMinutes(now.getMinutes() + 5);
        break;
      case 'hourly':
        nextRun.setHours(now.getHours() + 1, 0, 0, 0);
        break;
      case 'daily':
        const [hours, minutes] = schedule.time.split(':');
        nextRun.setHours(parseInt(hours), parseInt(minutes), 0, 0);
        if (nextRun <= now) {
          nextRun.setDate(nextRun.getDate() + 1);
        }
        break;
      case 'weekly':
        // Implementation for weekly schedules
        nextRun.setDate(now.getDate() + 7);
        break;
      default:
        nextRun.setHours(now.getHours() + 1);
    }

    return nextRun;
  }

  /**
   * Clean old backups based on retention policy
   */
  async cleanOldBackups() {
    try {
      const backupList = Array.from(this.backups.values())
        .filter(backup => backup.status === 'completed')
        .sort((a, b) => new Date(b.created) - new Date(a.created));

      const toDelete = [];
      const now = new Date();

      // Apply retention policy
      let dailyCount = 0;
      let weeklyCount = 0;
      let monthlyCount = 0;
      let yearlyCount = 0;

      for (const backup of backupList) {
        const age = now - new Date(backup.created);
        const days = age / (1000 * 60 * 60 * 24);

        let shouldKeep = false;

        if (days <= 1 && dailyCount < this.retention.daily) {
          shouldKeep = true;
          dailyCount++;
        } else if (days <= 7 && weeklyCount < this.retention.weekly) {
          shouldKeep = true;
          weeklyCount++;
        } else if (days <= 30 && monthlyCount < this.retention.monthly) {
          shouldKeep = true;
          monthlyCount++;
        } else if (days <= 365 && yearlyCount < this.retention.yearly) {
          shouldKeep = true;
          yearlyCount++;
        }

        if (!shouldKeep) {
          toDelete.push(backup);
        }
      }

      // Delete old backups
      for (const backup of toDelete) {
        await this.deleteBackup(backup.id);
      }

      this.emit('oldBackupsCleaned', { deleted: toDelete.length });
      return toDelete.length;

    } catch (error) {
      this.emit('error', new Error(`Failed to clean old backups: ${error.message}`));
      return 0;
    }
  }

  /**
   * Delete backup
   */
  async deleteBackup(backupId) {
    try {
      const backup = this.backups.get(backupId);
      if (!backup) {
        throw new Error('Backup not found');
      }

      // Delete archive file
      if (backup.archivePath) {
        await fs.unlink(backup.archivePath);
      }

      // Remove from memory
      this.backups.delete(backupId);

      this.emit('backupDeleted', backup);
      return true;

    } catch (error) {
      this.emit('error', new Error(`Failed to delete backup: ${error.message}`));
      return false;
    }
  }

  /**
   * Calculate file checksum
   */
  async calculateFileChecksum(filePath) {
    const content = await fs.readFile(filePath);
    return crypto.createHash('sha256').update(content).digest('hex');
  }

  /**
   * Generate backup ID
   */
  generateBackupId() {
    return `backup_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Encrypt data
   */
  async encryptData(data) {
    // Simplified encryption - in production, use proper encryption
    return Buffer.from(data).toString('base64');
  }

  /**
   * Decrypt data
   */
  async decryptData(encryptedData) {
    // Simplified decryption - in production, use proper decryption
    return Buffer.from(encryptedData, 'base64').toString();
  }

  /**
   * Get all backups
   */
  getAllBackups() {
    return Array.from(this.backups.values());
  }

  /**
   * Get backup by ID
   */
  getBackup(backupId) {
    return this.backups.get(backupId);
  }

  /**
   * Get backup statistics
   */
  getBackupStatistics() {
    const backups = Array.from(this.backups.values());
    const completed = backups.filter(b => b.status === 'completed');
    
    return {
      totalBackups: backups.length,
      completedBackups: completed.length,
      totalSize: completed.reduce((sum, b) => sum + b.size, 0),
      averageSize: completed.length > 0 ? completed.reduce((sum, b) => sum + b.size, 0) / completed.length : 0,
      oldestBackup: completed.length > 0 ? new Date(Math.min(...completed.map(b => new Date(b.created)))) : null,
      newestBackup: completed.length > 0 ? new Date(Math.max(...completed.map(b => new Date(b.created)))) : null,
      schedules: this.schedules.size,
      activeSchedules: Array.from(this.schedules.values()).filter(s => s.enabled).length
    };
  }

  /**
   * Get active schedules
   */
  getActiveSchedules() {
    return Array.from(this.schedules.values()).filter(s => s.enabled);
  }

  /**
   * Update schedule
   */
  updateSchedule(scheduleId, updates) {
    const schedule = this.schedules.get(scheduleId);
    if (!schedule) return false;

    // Clear existing timeout
    if (schedule.timeoutId) {
      clearTimeout(schedule.timeoutId);
    }

    // Update schedule
    Object.assign(schedule, updates);
    this.schedules.set(scheduleId, schedule);

    // Reschedule if enabled
    if (schedule.enabled && schedule.projectPath) {
      this.scheduleBackup(schedule.projectPath, scheduleId);
    }

    this.emit('scheduleUpdated', schedule);
    return true;
  }
}

module.exports = BackupManager;