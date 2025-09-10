/**
 * Ainflue Desktop - File System Manager
 * 
 * Secure file operations and content management for professional workflows
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This software is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

const { app, dialog } = require('electron');
const fs = require('fs').promises;
const fsSync = require('fs');
const path = require('path');
const crypto = require('crypto');
const log = require('electron-log');
const mime = require('mime-types');

class FileSystemManager {
  constructor() {
    this.allowedPaths = new Set();
    this.blockedPaths = new Set();
    this.tempFiles = new Set();
    this.watchedPaths = new Map();
    this.fileOperations = new Map();
    this.maxFileSize = 100 * 1024 * 1024 * 1024; // 100GB default
    this.allowedExtensions = new Set([
      // Audio formats
      '.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma', '.aiff',
      // Video formats
      '.mp4', '.mov', '.avi', '.mkv', '.webm', '.wmv', '.flv', '.m4v',
      // Image formats
      '.jpg', '.jpeg', '.png', '.gif', '.svg', '.bmp', '.tiff', '.webp',
      // Document formats
      '.pdf', '.txt', '.rtf', '.doc', '.docx', '.ppt', '.pptx',
      // Project formats
      '.ainproj', '.json', '.xml'
    ]);
    
    this.isInitialized = false;
    log.info('File System Manager initialized');
  }

  async initialize() {
    try {
      log.info('Initializing File System Manager...');
      
      // Setup safe paths
      this.setupSafePaths();
      
      // Create application directories
      await this.createApplicationDirectories();
      
      // Setup file watchers
      this.setupFileWatchers();
      
      // Configure temporary file cleanup
      this.setupTempFileCleanup();
      
      this.isInitialized = true;
      log.info('✅ File System Manager initialized successfully');
      
    } catch (error) {
      log.error('❌ Failed to initialize File System Manager:', error);
      throw error;
    }
  }

  setupSafePaths() {
    // Add safe application paths
    const appPath = app.getAppPath();
    const userDataPath = app.getPath('userData');
    const documentsPath = app.getPath('documents');
    const desktopPath = app.getPath('desktop');
    const downloadsPath = app.getPath('downloads');
    const tempPath = app.getPath('temp');
    
    this.allowedPaths.add(path.normalize(appPath));
    this.allowedPaths.add(path.normalize(userDataPath));
    this.allowedPaths.add(path.normalize(documentsPath));
    this.allowedPaths.add(path.normalize(desktopPath));
    this.allowedPaths.add(path.normalize(downloadsPath));
    this.allowedPaths.add(path.normalize(tempPath));
    
    // Add platform-specific safe paths
    if (process.platform === 'win32') {
      this.allowedPaths.add('C:\\Users');
      this.allowedPaths.add(path.join(process.env.USERPROFILE, 'Music'));
      this.allowedPaths.add(path.join(process.env.USERPROFILE, 'Videos'));
      this.allowedPaths.add(path.join(process.env.USERPROFILE, 'Pictures'));
    } else if (process.platform === 'darwin') {
      this.allowedPaths.add('/Users');
      this.allowedPaths.add(path.join(require('os').homedir(), 'Music'));
      this.allowedPaths.add(path.join(require('os').homedir(), 'Movies'));
      this.allowedPaths.add(path.join(require('os').homedir(), 'Pictures'));
    } else if (process.platform === 'linux') {
      this.allowedPaths.add('/home');
      this.allowedPaths.add(path.join(require('os').homedir(), 'Music'));
      this.allowedPaths.add(path.join(require('os').homedir(), 'Videos'));
      this.allowedPaths.add(path.join(require('os').homedir(), 'Pictures'));
    }
    
    // Block system paths
    this.blockedPaths.add('/System');
    this.blockedPaths.add('/Windows');
    this.blockedPaths.add('/etc');
    this.blockedPaths.add('/var');
    this.blockedPaths.add('/usr');
    this.blockedPaths.add('/bin');
    this.blockedPaths.add('/sbin');
    
    log.info(`File system security configured with ${this.allowedPaths.size} safe paths`);
  }

  async createApplicationDirectories() {
    const userDataPath = app.getPath('userData');
    const appDirs = [
      'projects',
      'exports',
      'cache',
      'temp',
      'backups',
      'templates',
      'plugins',
      'logs'
    ];
    
    for (const dir of appDirs) {
      const fullPath = path.join(userDataPath, dir);
      try {
        await fs.mkdir(fullPath, { recursive: true });
        this.allowedPaths.add(path.normalize(fullPath));
      } catch (error) {
        log.warn(`Failed to create directory ${fullPath}:`, error.message);
      }
    }
    
    log.info('Application directories created');
  }

  setupFileWatchers() {
    // Watch project directories for changes
    const userDataPath = app.getPath('userData');
    const projectsPath = path.join(userDataPath, 'projects');
    
    try {
      const watcher = fsSync.watch(projectsPath, { recursive: true }, (eventType, filename) => {
        if (filename) {
          const fullPath = path.join(projectsPath, filename);
          log.debug(`File ${eventType}: ${fullPath}`);
          this.emit('file-changed', { eventType, path: fullPath });
        }
      });
      
      this.watchedPaths.set(projectsPath, watcher);
      log.info('File watchers configured');
      
    } catch (error) {
      log.warn('Failed to setup file watchers:', error.message);
    }
  }

  setupTempFileCleanup() {
    // Clean up temp files every hour
    this.tempCleanupInterval = setInterval(() => {
      this.cleanupTempFiles();
    }, 60 * 60 * 1000);
    
    // Clean up on app exit
    app.on('before-quit', () => {
      this.cleanupTempFiles();
    });
    
    log.info('Temporary file cleanup configured');
  }

  // File validation methods
  isPathSafe(filePath) {
    const normalizedPath = path.normalize(path.resolve(filePath));
    
    // Check if path is blocked
    for (const blockedPath of this.blockedPaths) {
      if (normalizedPath.startsWith(blockedPath)) {
        return false;
      }
    }
    
    // Check if path is in allowed paths
    for (const allowedPath of this.allowedPaths) {
      if (normalizedPath.startsWith(allowedPath)) {
        return true;
      }
    }
    
    return false;
  }

  isExtensionAllowed(filePath) {
    const ext = path.extname(filePath).toLowerCase();
    return this.allowedExtensions.has(ext);
  }

  async getFileSize(filePath) {
    try {
      const stats = await fs.stat(filePath);
      return stats.size;
    } catch (error) {
      return 0;
    }
  }

  async isFileSizeAllowed(filePath) {
    const size = await this.getFileSize(filePath);
    return size <= this.maxFileSize;
  }

  // Secure file operations
  async readFile(filePath, options = {}) {
    if (!this.isPathSafe(filePath)) {
      throw new Error(`Access denied: ${filePath}`);
    }
    
    try {
      const operationId = this.generateOperationId();
      this.fileOperations.set(operationId, { type: 'read', path: filePath, startTime: Date.now() });
      
      log.debug(`Reading file: ${filePath}`);
      const content = await fs.readFile(filePath, options);
      
      this.fileOperations.delete(operationId);
      return content;
      
    } catch (error) {
      log.error(`Failed to read file ${filePath}:`, error.message);
      throw error;
    }
  }

  async writeFile(filePath, data, options = {}) {
    if (!this.isPathSafe(filePath)) {
      throw new Error(`Access denied: ${filePath}`);
    }
    
    if (!this.isExtensionAllowed(filePath)) {
      throw new Error(`File type not allowed: ${path.extname(filePath)}`);
    }
    
    try {
      // Create directory if it doesn't exist
      const directory = path.dirname(filePath);
      await fs.mkdir(directory, { recursive: true });
      
      const operationId = this.generateOperationId();
      this.fileOperations.set(operationId, { type: 'write', path: filePath, startTime: Date.now() });
      
      // Create backup if file exists
      if (await this.exists(filePath)) {
        await this.createBackup(filePath);
      }
      
      log.debug(`Writing file: ${filePath}`);
      await fs.writeFile(filePath, data, options);
      
      this.fileOperations.delete(operationId);
      this.emit('file-written', { path: filePath, size: data.length });
      
    } catch (error) {
      log.error(`Failed to write file ${filePath}:`, error.message);
      throw error;
    }
  }

  async copyFile(sourcePath, destPath) {
    if (!this.isPathSafe(sourcePath) || !this.isPathSafe(destPath)) {
      throw new Error('Access denied');
    }
    
    if (!this.isExtensionAllowed(destPath)) {
      throw new Error(`File type not allowed: ${path.extname(destPath)}`);
    }
    
    if (!(await this.isFileSizeAllowed(sourcePath))) {
      throw new Error('File size exceeds limit');
    }
    
    try {
      const operationId = this.generateOperationId();
      this.fileOperations.set(operationId, { type: 'copy', source: sourcePath, dest: destPath, startTime: Date.now() });
      
      log.debug(`Copying file: ${sourcePath} -> ${destPath}`);
      await fs.copyFile(sourcePath, destPath);
      
      this.fileOperations.delete(operationId);
      this.emit('file-copied', { source: sourcePath, dest: destPath });
      
    } catch (error) {
      log.error(`Failed to copy file ${sourcePath} to ${destPath}:`, error.message);
      throw error;
    }
  }

  async moveFile(sourcePath, destPath) {
    if (!this.isPathSafe(sourcePath) || !this.isPathSafe(destPath)) {
      throw new Error('Access denied');
    }
    
    try {
      const operationId = this.generateOperationId();
      this.fileOperations.set(operationId, { type: 'move', source: sourcePath, dest: destPath, startTime: Date.now() });
      
      log.debug(`Moving file: ${sourcePath} -> ${destPath}`);
      await fs.rename(sourcePath, destPath);
      
      this.fileOperations.delete(operationId);
      this.emit('file-moved', { source: sourcePath, dest: destPath });
      
    } catch (error) {
      log.error(`Failed to move file ${sourcePath} to ${destPath}:`, error.message);
      throw error;
    }
  }

  async deleteFile(filePath) {
    if (!this.isPathSafe(filePath)) {
      throw new Error(`Access denied: ${filePath}`);
    }
    
    try {
      const operationId = this.generateOperationId();
      this.fileOperations.set(operationId, { type: 'delete', path: filePath, startTime: Date.now() });
      
      // Create backup before deletion
      await this.createBackup(filePath);
      
      log.debug(`Deleting file: ${filePath}`);
      await fs.unlink(filePath);
      
      this.fileOperations.delete(operationId);
      this.emit('file-deleted', { path: filePath });
      
    } catch (error) {
      log.error(`Failed to delete file ${filePath}:`, error.message);
      throw error;
    }
  }

  async exists(filePath) {
    try {
      await fs.access(filePath);
      return true;
    } catch (error) {
      return false;
    }
  }

  async getFileInfo(filePath) {
    if (!this.isPathSafe(filePath)) {
      throw new Error(`Access denied: ${filePath}`);
    }
    
    try {
      const stats = await fs.stat(filePath);
      const mimeType = mime.lookup(filePath) || 'application/octet-stream';
      
      return {
        path: filePath,
        name: path.basename(filePath),
        ext: path.extname(filePath),
        size: stats.size,
        mimeType,
        isFile: stats.isFile(),
        isDirectory: stats.isDirectory(),
        created: stats.birthtime,
        modified: stats.mtime,
        accessed: stats.atime
      };
    } catch (error) {
      log.error(`Failed to get file info for ${filePath}:`, error.message);
      throw error;
    }
  }

  async listDirectory(dirPath) {
    if (!this.isPathSafe(dirPath)) {
      throw new Error(`Access denied: ${dirPath}`);
    }
    
    try {
      const entries = await fs.readdir(dirPath, { withFileTypes: true });
      const files = [];
      
      for (const entry of entries) {
        const fullPath = path.join(dirPath, entry.name);
        try {
          const info = await this.getFileInfo(fullPath);
          files.push(info);
        } catch (error) {
          log.warn(`Failed to get info for ${fullPath}:`, error.message);
        }
      }
      
      return files;
    } catch (error) {
      log.error(`Failed to list directory ${dirPath}:`, error.message);
      throw error;
    }
  }

  // File dialogs
  async showOpenDialog(options = {}) {
    const defaultOptions = {
      properties: ['openFile'],
      filters: [
        { name: 'All Supported', extensions: Array.from(this.allowedExtensions).map(ext => ext.slice(1)) },
        { name: 'Audio Files', extensions: ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a'] },
        { name: 'Video Files', extensions: ['mp4', 'mov', 'avi', 'mkv', 'webm'] },
        { name: 'Image Files', extensions: ['jpg', 'jpeg', 'png', 'gif', 'svg', 'bmp'] },
        { name: 'Project Files', extensions: ['ainproj', 'json'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    };
    
    const result = await dialog.showOpenDialog({ ...defaultOptions, ...options });
    
    if (!result.canceled && result.filePaths.length > 0) {
      // Validate selected files
      const validFiles = [];
      for (const filePath of result.filePaths) {
        if (this.isPathSafe(filePath) && (await this.isFileSizeAllowed(filePath))) {
          validFiles.push(filePath);
        } else {
          log.warn(`File not allowed: ${filePath}`);
        }
      }
      return validFiles;
    }
    
    return [];
  }

  async showSaveDialog(options = {}) {
    const defaultOptions = {
      filters: [
        { name: 'Project Files', extensions: ['ainproj'] },
        { name: 'JSON Files', extensions: ['json'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    };
    
    const result = await dialog.showSaveDialog({ ...defaultOptions, ...options });
    
    if (!result.canceled && result.filePath) {
      if (this.isPathSafe(result.filePath)) {
        return result.filePath;
      } else {
        throw new Error('Selected path is not allowed');
      }
    }
    
    return null;
  }

  // Temporary files
  async createTempFile(extension = '.tmp') {
    const tempDir = app.getPath('temp');
    const tempName = `ainflue-${crypto.randomUUID()}${extension}`;
    const tempPath = path.join(tempDir, tempName);
    
    // Create empty file
    await fs.writeFile(tempPath, '');
    this.tempFiles.add(tempPath);
    
    log.debug(`Created temp file: ${tempPath}`);
    return tempPath;
  }

  async createTempDirectory() {
    const tempDir = app.getPath('temp');
    const tempName = `ainflue-${crypto.randomUUID()}`;
    const tempPath = path.join(tempDir, tempName);
    
    await fs.mkdir(tempPath, { recursive: true });
    this.tempFiles.add(tempPath);
    
    log.debug(`Created temp directory: ${tempPath}`);
    return tempPath;
  }

  cleanupTempFiles() {
    let cleanedCount = 0;
    
    for (const tempPath of this.tempFiles) {
      try {
        if (fsSync.existsSync(tempPath)) {
          const stats = fsSync.statSync(tempPath);
          if (stats.isDirectory()) {
            fsSync.rmSync(tempPath, { recursive: true, force: true });
          } else {
            fsSync.unlinkSync(tempPath);
          }
          cleanedCount++;
        }
        this.tempFiles.delete(tempPath);
      } catch (error) {
        log.warn(`Failed to cleanup temp file ${tempPath}:`, error.message);
      }
    }
    
    if (cleanedCount > 0) {
      log.info(`Cleaned up ${cleanedCount} temporary files`);
    }
  }

  // Backup functionality
  async createBackup(filePath) {
    if (!await this.exists(filePath)) {
      return null;
    }
    
    const userDataPath = app.getPath('userData');
    const backupDir = path.join(userDataPath, 'backups');
    await fs.mkdir(backupDir, { recursive: true });
    
    const fileName = path.basename(filePath);
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const backupName = `${fileName}.${timestamp}.backup`;
    const backupPath = path.join(backupDir, backupName);
    
    try {
      await fs.copyFile(filePath, backupPath);
      log.debug(`Created backup: ${backupPath}`);
      return backupPath;
    } catch (error) {
      log.warn(`Failed to create backup for ${filePath}:`, error.message);
      return null;
    }
  }

  // File hashing and verification
  async calculateFileHash(filePath, algorithm = 'sha256') {
    if (!this.isPathSafe(filePath)) {
      throw new Error(`Access denied: ${filePath}`);
    }
    
    const hash = crypto.createHash(algorithm);
    const stream = fsSync.createReadStream(filePath);
    
    return new Promise((resolve, reject) => {
      stream.on('error', reject);
      stream.on('data', chunk => hash.update(chunk));
      stream.on('end', () => resolve(hash.digest('hex')));
    });
  }

  async verifyFileIntegrity(filePath, expectedHash, algorithm = 'sha256') {
    const actualHash = await this.calculateFileHash(filePath, algorithm);
    return actualHash === expectedHash;
  }

  // Utility methods
  generateOperationId() {
    return crypto.randomUUID();
  }

  getActiveOperations() {
    return Array.from(this.fileOperations.values());
  }

  addAllowedPath(filePath) {
    this.allowedPaths.add(path.normalize(path.resolve(filePath)));
  }

  removeAllowedPath(filePath) {
    this.allowedPaths.delete(path.normalize(path.resolve(filePath)));
  }

  addAllowedExtension(extension) {
    this.allowedExtensions.add(extension.toLowerCase());
  }

  removeAllowedExtension(extension) {
    this.allowedExtensions.delete(extension.toLowerCase());
  }

  setMaxFileSize(sizeInBytes) {
    this.maxFileSize = sizeInBytes;
  }

  // Cleanup
  cleanup() {
    // Stop file watchers
    for (const [path, watcher] of this.watchedPaths) {
      try {
        watcher.close();
      } catch (error) {
        log.warn(`Failed to close watcher for ${path}:`, error.message);
      }
    }
    this.watchedPaths.clear();
    
    // Clear cleanup interval
    if (this.tempCleanupInterval) {
      clearInterval(this.tempCleanupInterval);
    }
    
    // Cleanup temp files
    this.cleanupTempFiles();
    
    log.info('File System Manager cleaned up');
  }
}

// Event emitter mixin
Object.assign(FileSystemManager.prototype, require('events').EventEmitter.prototype);

module.exports = FileSystemManager;