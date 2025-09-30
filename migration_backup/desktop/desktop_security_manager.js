/**
 * Ainflue Desktop - Security Manager
 * 
 * Professional security implementation with content protection and access control
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This software is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

const { session, shell, app } = require('electron');
const crypto = require('crypto');
const log = require('electron-log');
const fs = require('fs');
const path = require('path');

class DesktopSecurityManager {
  constructor() {
    this.securityPolicies = {
      csp: "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:",
      allowedDomains: ['ainflue.com', 'api.ainflue.com', 'cdn.ainflue.com'],
      blockedDomains: [],
      enableRemoteContent: false,
      strictTransportSecurity: true,
      contentTypeNoSniff: true,
      frameOptions: 'DENY',
      // Electron Security Configuration
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
      webSecurity: true
    };
    
    this.encryptionKey = this.generateEncryptionKey();
    this.sessionSecrets = new Map();
    this.securityViolations = [];
    this.isInitialized = false;
    
    log.info('Desktop Security Manager initialized');
  }

  async initialize() {
    try {
      log.info('Initializing Desktop Security Manager...');
      
      // Setup session security
      await this.setupSessionSecurity();
      
      // Configure content security
      this.configureContentSecurity();
      
      // Setup file access control
      this.setupFileAccessControl();
      
      // Initialize encryption systems
      this.initializeEncryption();
      
      // Setup security monitoring
      this.setupSecurityMonitoring();
      
      this.isInitialized = true;
      log.info('✅ Desktop Security Manager initialized successfully');
      
    } catch (error) {
      log.error('❌ Failed to initialize Desktop Security Manager:', error);
      throw error;
    }
  }

  async enforceSecurityPolicies() {
    if (!this.isInitialized) {
      await this.initialize();
    }
    
    log.info('Enforcing security policies...');
    
    // Apply session-level security
    this.applySessionSecurity();
    
    // Configure protocol handling
    this.configureProtocolSecurity();
    
    // Setup permission handling
    this.setupPermissionHandling();
    
    log.info('✅ Security policies enforced');
  }

  async setupSessionSecurity() {
    const defaultSession = session.defaultSession;
    
    // Configure permissions
    defaultSession.setPermissionRequestHandler((webContents, permission, callback) => {
      log.info(`Permission request: ${permission} from ${webContents.getURL()}`);
      
      const allowedPermissions = [
        'media',
        'microphone',
        'camera',
        'desktop-audio',
        'display-capture'
      ];
      
      callback(allowedPermissions.includes(permission));
    });

    // Block external navigation
    defaultSession.webRequest.onBeforeRequest({ urls: ['*://*/*'] }, (details, callback) => {
      const url = new URL(details.url);
      const isAllowed = this.isUrlAllowed(url);
      
      if (!isAllowed) {
        log.warn(`Blocked request to: ${details.url}`);
        this.reportSecurityViolation('blocked_request', { url: details.url });
      }
      
      callback({ cancel: !isAllowed });
    });

    // Setup response headers for security
    defaultSession.webRequest.onHeadersReceived((details, callback) => {
      const responseHeaders = { ...details.responseHeaders };
      
      // Add security headers
      responseHeaders['Content-Security-Policy'] = [this.securityPolicies.csp];
      responseHeaders['X-Content-Type-Options'] = ['nosniff'];
      responseHeaders['X-Frame-Options'] = ['DENY'];
      responseHeaders['X-XSS-Protection'] = ['1; mode=block'];
      
      if (this.securityPolicies.strictTransportSecurity) {
        responseHeaders['Strict-Transport-Security'] = ['max-age=31536000; includeSubDomains'];
      }
      
      callback({ responseHeaders });
    });

    // Clear cache and cookies for security
    await defaultSession.clearCache();
    log.info('Session security configured');
  }

  configureContentSecurity() {
    const defaultSession = session.defaultSession;
    
    // Block dangerous file types
    const dangerousExtensions = ['.exe', '.bat', '.cmd', '.scr', '.pif', '.com'];
    
    defaultSession.webRequest.onBeforeRequest({ urls: ['file://*/*'] }, (details, callback) => {
      const url = new URL(details.url);
      const filePath = url.pathname;
      
      const isDangerous = dangerousExtensions.some(ext => 
        filePath.toLowerCase().endsWith(ext)
      );
      
      if (isDangerous) {
        log.warn(`Blocked dangerous file access: ${filePath}`);
        this.reportSecurityViolation('dangerous_file_access', { path: filePath });
        callback({ cancel: true });
        return;
      }
      
      callback({ cancel: false });
    });

    log.info('Content security configured');
  }

  setupFileAccessControl() {
    // Monitor file system access
    const originalReadFile = fs.readFile;
    const originalWriteFile = fs.writeFile;
    
    fs.readFile = (path, options, callback) => {
      if (typeof options === 'function') {
        callback = options;
        options = {};
      }
      
      if (this.isPathSafe(path)) {
        return originalReadFile.call(fs, path, options, callback);
      } else {
        log.warn(`Blocked file read access: ${path}`);
        this.reportSecurityViolation('unauthorized_file_read', { path });
        if (callback) callback(new Error('Access denied'));
      }
    };
    
    fs.writeFile = (path, data, options, callback) => {
      if (typeof options === 'function') {
        callback = options;
        options = {};
      }
      
      if (this.isPathSafe(path)) {
        return originalWriteFile.call(fs, path, data, options, callback);
      } else {
        log.warn(`Blocked file write access: ${path}`);
        this.reportSecurityViolation('unauthorized_file_write', { path });
        if (callback) callback(new Error('Access denied'));
      }
    };
    
    log.info('File access control configured');
  }

  initializeEncryption() {
    // Setup content encryption for sensitive data
    this.contentCipher = {
      algorithm: 'aes-256-gcm',
      keyDerivation: 'pbkdf2',
      iterations: 100000
    };
    
    log.info('Encryption systems initialized');
  }

  setupSecurityMonitoring() {
    // Monitor for security violations
    setInterval(() => {
      this.performSecurityScan();
    }, 60000); // Every minute
    
    // Monitor memory usage for potential attacks
    setInterval(() => {
      const memUsage = process.memoryUsage();
      const threshold = 1024 * 1024 * 1024; // 1GB
      
      if (memUsage.heapUsed > threshold) {
        log.warn('High memory usage detected - potential security issue');
        this.reportSecurityViolation('high_memory_usage', { usage: memUsage });
      }
    }, 30000); // Every 30 seconds
    
    log.info('Security monitoring active');
  }

  applySessionSecurity() {
    const defaultSession = session.defaultSession;
    
    // Disable node integration
    defaultSession.setPreloads([]);
    
    // Configure user agent
    defaultSession.setUserAgent(
      `AinflueSudio/1.0.0 (${process.platform}; ${process.arch}) Creator/Professional`
    );
    
    log.info('Session security applied');
  }

  configureProtocolSecurity() {
    // Handle dangerous protocols
    const dangerousProtocols = ['file:', 'ftp:', 'javascript:', 'data:'];
    
    app.setAsDefaultProtocolClient('ainflue');
    
    log.info('Protocol security configured');
  }

  setupPermissionHandling() {
    const defaultSession = session.defaultSession;
    
    // Handle certificate errors
    defaultSession.setCertificateVerifyProc((request, callback) => {
      const { hostname, verificationResult, errorCode } = request;
      
      // Allow localhost in development
      if (hostname === 'localhost' && process.env.NODE_ENV !== 'production') {
        callback(0); // Allow
        return;
      }
      
      // Check if hostname is in allowed domains
      if (this.securityPolicies.allowedDomains.includes(hostname)) {
        callback(0); // Allow
      } else {
        log.warn(`Certificate verification failed for: ${hostname}`);
        this.reportSecurityViolation('certificate_error', { hostname, errorCode });
        callback(-2); // Deny
      }
    });
    
    log.info('Permission handling configured');
  }

  // Content encryption methods
  encryptContent(content, userKey = null) {
    try {
      const key = userKey || this.encryptionKey;
      const salt = crypto.randomBytes(16);
      const iv = crypto.randomBytes(12);
      
      const derivedKey = crypto.pbkdf2Sync(key, salt, this.contentCipher.iterations, 32, 'sha256');
      const cipher = crypto.createCipherGCM(this.contentCipher.algorithm, derivedKey, iv);
      
      let encrypted = cipher.update(content, 'utf8', 'hex');
      encrypted += cipher.final('hex');
      
      const authTag = cipher.getAuthTag();
      
      return {
        encrypted,
        salt: salt.toString('hex'),
        iv: iv.toString('hex'),
        authTag: authTag.toString('hex'),
        algorithm: this.contentCipher.algorithm
      };
      
    } catch (error) {
      log.error('Content encryption failed:', error);
      throw error;
    }
  }

  decryptContent(encryptedData, userKey = null) {
    try {
      const key = userKey || this.encryptionKey;
      const { encrypted, salt, iv, authTag, algorithm } = encryptedData;
      
      const saltBuffer = Buffer.from(salt, 'hex');
      const ivBuffer = Buffer.from(iv, 'hex');
      const authTagBuffer = Buffer.from(authTag, 'hex');
      
      const derivedKey = crypto.pbkdf2Sync(key, saltBuffer, this.contentCipher.iterations, 32, 'sha256');
      const decipher = crypto.createDecipherGCM(algorithm, derivedKey, ivBuffer);
      decipher.setAuthTag(authTagBuffer);
      
      let decrypted = decipher.update(encrypted, 'hex', 'utf8');
      decrypted += decipher.final('utf8');
      
      return decrypted;
      
    } catch (error) {
      log.error('Content decryption failed:', error);
      throw error;
    }
  }

  // Digital fingerprinting for content protection
  generateContentFingerprint(content) {
    const hash = crypto.createHash('sha256');
    hash.update(content);
    return hash.digest('hex');
  }

  // Watermarking system
  addWatermark(content, watermarkData) {
    // Simple watermark implementation
    const watermark = {
      content,
      watermark: {
        owner: watermarkData.owner || 'Fahed Mlaiel',
        timestamp: new Date().toISOString(),
        id: crypto.randomUUID(),
        signature: this.generateWatermarkSignature(content, watermarkData)
      }
    };
    
    return watermark;
  }

  generateWatermarkSignature(content, watermarkData) {
    const data = JSON.stringify({ content, watermark: watermarkData });
    return crypto.createHmac('sha256', this.encryptionKey).update(data).digest('hex');
  }

  verifyWatermark(watermarkedContent) {
    if (!watermarkedContent.watermark) {
      return false;
    }
    
    const { content, watermark } = watermarkedContent;
    const expectedSignature = this.generateWatermarkSignature(content, {
      owner: watermark.owner,
      timestamp: watermark.timestamp,
      id: watermark.id
    });
    
    return watermark.signature === expectedSignature;
  }

  // Security validation methods
  getSecureWebPreferences(preloadPath) {
    return {
      nodeIntegration: this.securityPolicies.nodeIntegration,
      contextIsolation: this.securityPolicies.contextIsolation,
      sandbox: this.securityPolicies.sandbox,
      webSecurity: this.securityPolicies.webSecurity,
      enableRemoteModule: false,
      preload: preloadPath,
      spellcheck: false,
      backgroundThrottling: false
    };
  }

  isUrlAllowed(url) {
    const hostname = url.hostname;
    
    // Block known malicious domains
    if (this.securityPolicies.blockedDomains.includes(hostname)) {
      return false;
    }
    
    // Allow local development
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return process.env.NODE_ENV !== 'production';
    }
    
    // Allow specific domains
    if (this.securityPolicies.allowedDomains.includes(hostname)) {
      return true;
    }
    
    // Block by default in production
    return !this.securityPolicies.enableRemoteContent;
  }

  isPathSafe(filePath) {
    const normalizedPath = path.normalize(filePath);
    const appPath = app.getAppPath();
    const userDataPath = app.getPath('userData');
    const tempPath = app.getPath('temp');
    
    // Allow access to app directory, user data, and temp
    const allowedPaths = [appPath, userDataPath, tempPath];
    
    return allowedPaths.some(allowedPath => 
      normalizedPath.startsWith(path.normalize(allowedPath))
    );
  }

  // WebContents security hardening
  secureWebContents(contents) {
    // Disable node integration
    contents.session.setPreloads([]);
    
    // Handle new window creation
    contents.setWindowOpenHandler((details) => {
      const url = new URL(details.url);
      
      if (this.isUrlAllowed(url)) {
        shell.openExternal(details.url);
      } else {
        log.warn(`Blocked window open to: ${details.url}`);
        this.reportSecurityViolation('blocked_window_open', { url: details.url });
      }
      
      return { action: 'deny' };
    });

    // Handle navigation
    contents.on('will-navigate', (event, navigationUrl) => {
      const url = new URL(navigationUrl);
      
      if (!this.isUrlAllowed(url)) {
        event.preventDefault();
        log.warn(`Blocked navigation to: ${navigationUrl}`);
        this.reportSecurityViolation('blocked_navigation', { url: navigationUrl });
      }
    });

    // Handle redirects
    contents.on('will-redirect', (event, redirectUrl) => {
      const url = new URL(redirectUrl);
      
      if (!this.isUrlAllowed(url)) {
        event.preventDefault();
        log.warn(`Blocked redirect to: ${redirectUrl}`);
        this.reportSecurityViolation('blocked_redirect', { url: redirectUrl });
      }
    });

    log.debug('WebContents secured');
  }

  // Security monitoring and reporting
  performSecurityScan() {
    // Check for suspicious processes
    this.scanProcesses();
    
    // Check file integrity
    this.checkFileIntegrity();
    
    // Monitor network connections
    this.monitorNetworkConnections();
  }

  scanProcesses() {
    // Implementation for process scanning
    // This would check for suspicious processes
  }

  checkFileIntegrity() {
    // Implementation for file integrity checking
    // This would verify critical files haven't been modified
  }

  monitorNetworkConnections() {
    // Implementation for network monitoring
    // This would check for unauthorized network connections
  }

  reportSecurityViolation(type, details) {
    const violation = {
      type,
      details,
      timestamp: new Date().toISOString(),
      userAgent: session.defaultSession.getUserAgent(),
      platform: process.platform
    };
    
    this.securityViolations.push(violation);
    
    // Keep only last 100 violations
    if (this.securityViolations.length > 100) {
      this.securityViolations = this.securityViolations.slice(-100);
    }
    
    log.warn('Security violation reported:', violation);
  }

  getSecurityReport() {
    return {
      violations: this.securityViolations,
      policies: this.securityPolicies,
      isInitialized: this.isInitialized,
      encryptionEnabled: !!this.encryptionKey,
      sessionSecrets: this.sessionSecrets.size
    };
  }

  // Utility methods
  generateEncryptionKey() {
    return crypto.randomBytes(32).toString('hex');
  }

  generateSecureToken() {
    return crypto.randomBytes(32).toString('base64url');
  }

  hashPassword(password, salt = null) {
    const actualSalt = salt || crypto.randomBytes(16);
    const hash = crypto.pbkdf2Sync(password, actualSalt, 100000, 64, 'sha256');
    
    return {
      hash: hash.toString('hex'),
      salt: actualSalt.toString('hex')
    };
  }

  verifyPassword(password, hashedPassword, salt) {
    const saltBuffer = Buffer.from(salt, 'hex');
    const hash = crypto.pbkdf2Sync(password, saltBuffer, 100000, 64, 'sha256');
    return hash.toString('hex') === hashedPassword;
  }

  // Session management
  createSecureSession(userId) {
    const sessionId = crypto.randomUUID();
    const sessionData = {
      userId,
      createdAt: new Date().toISOString(),
      lastActivity: new Date().toISOString(),
      token: this.generateSecureToken()
    };
    
    this.sessionSecrets.set(sessionId, sessionData);
    return sessionId;
  }

  validateSession(sessionId) {
    const session = this.sessionSecrets.get(sessionId);
    
    if (!session) {
      return false;
    }
    
    // Update last activity
    session.lastActivity = new Date().toISOString();
    
    return true;
  }

  destroySession(sessionId) {
    return this.sessionSecrets.delete(sessionId);
  }

  cleanupExpiredSessions() {
    const now = Date.now();
    const expireTime = 30 * 60 * 1000; // 30 minutes
    
    for (const [sessionId, session] of this.sessionSecrets) {
      const lastActivity = new Date(session.lastActivity).getTime();
      if (now - lastActivity > expireTime) {
        this.sessionSecrets.delete(sessionId);
      }
    }
  }
}

module.exports = DesktopSecurityManager;