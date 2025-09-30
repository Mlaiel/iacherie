/**
 * Ainflue Desktop - Content Encryption Security Module
 * 
 * Advanced content encryption and security for desktop application
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This software is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

const crypto = require('crypto');
const { EventEmitter } = require('events');
const log = require('electron-log');

class ContentEncryption extends EventEmitter {
  constructor() {
    super();
    this.algorithm = 'aes-256-gcm';
    this.keyLength = 32; // 256 bits
    this.ivLength = 16; // 128 bits
    this.tagLength = 16; // 128 bits
    this.saltLength = 32; // 256 bits
    this.iterations = 100000; // PBKDF2 iterations
    
    // Encryption cache for performance
    this.encryptionCache = new Map();
    this.maxCacheSize = 100;
    
    // Key derivation settings
    this.keyDerivation = {
      algorithm: 'pbkdf2',
      hash: 'sha256',
      iterations: this.iterations
    };
  }

  async initialize() {
    try {
      log.info('Initializing Content Encryption...');
      
      // Validate crypto availability
      this.validateCryptoSupport();
      
      // Setup encryption policies
      this.setupEncryptionPolicies();
      
      log.info('Content Encryption initialized successfully');
      this.emit('encryption:ready');
      
    } catch (error) {
      log.error('Failed to initialize Content Encryption:', error);
      throw error;
    }
  }

  validateCryptoSupport() {
    const requiredAlgorithms = ['aes-256-gcm', 'sha256'];
    
    for (const algorithm of requiredAlgorithms) {
      try {
        const cipher = crypto.createCipher(algorithm, 'test');
        cipher.update('test');
        cipher.final();
      } catch (error) {
        throw new Error(`Crypto algorithm not supported: ${algorithm}`);
      }
    }
    
    log.info('Crypto support validated');
  }

  setupEncryptionPolicies() {
    this.policies = {
      requireEncryption: true,
      allowWeakKeys: false,
      keyRotationInterval: 30 * 24 * 60 * 60 * 1000, // 30 days
      maxKeyAge: 90 * 24 * 60 * 60 * 1000, // 90 days
      auditEncryption: true
    };
    
    log.info('Encryption policies configured');
  }

  async encryptContent(content, password = null, metadata = {}) {
    try {
      const startTime = Date.now();
      
      // Generate encryption key
      const { key, salt } = await this.deriveKey(password);
      
      // Generate IV for this encryption
      const iv = crypto.randomBytes(this.ivLength);
      
      // Create cipher
      const cipher = crypto.createCipher(this.algorithm, key, { iv });
      
      // Encrypt content
      let encrypted = cipher.update(content, 'utf8');
      encrypted = Buffer.concat([encrypted, cipher.final()]);
      
      // Get authentication tag
      const tag = cipher.getAuthTag();
      
      // Create encrypted package
      const encryptedPackage = {
        algorithm: this.algorithm,
        iv: iv.toString('base64'),
        salt: salt.toString('base64'),
        tag: tag.toString('base64'),
        content: encrypted.toString('base64'),
        metadata: {
          ...metadata,
          encrypted: true,
          timestamp: new Date().toISOString(),
          keyDerivation: this.keyDerivation
        }
      };
      
      const encryptionTime = Date.now() - startTime;
      
      log.debug(`Content encrypted successfully (${encryptionTime}ms)`);
      this.emit('content:encrypted', { 
        size: content.length, 
        encryptedSize: encrypted.length,
        encryptionTime 
      });
      
      return encryptedPackage;
      
    } catch (error) {
      log.error('Content encryption failed:', error);
      this.emit('encryption:error', error);
      throw error;
    }
  }

  async decryptContent(encryptedPackage, password = null) {
    try {
      const startTime = Date.now();
      
      // Validate package structure
      this.validateEncryptedPackage(encryptedPackage);
      
      // Derive key using stored salt
      const salt = Buffer.from(encryptedPackage.salt, 'base64');
      const { key } = await this.deriveKey(password, salt);
      
      // Extract encryption parameters
      const iv = Buffer.from(encryptedPackage.iv, 'base64');
      const tag = Buffer.from(encryptedPackage.tag, 'base64');
      const encrypted = Buffer.from(encryptedPackage.content, 'base64');
      
      // Create decipher
      const decipher = crypto.createDecipher(encryptedPackage.algorithm, key, { iv });
      decipher.setAuthTag(tag);
      
      // Decrypt content
      let decrypted = decipher.update(encrypted);
      decrypted = Buffer.concat([decrypted, decipher.final()]);
      
      const decryptionTime = Date.now() - startTime;
      
      log.debug(`Content decrypted successfully (${decryptionTime}ms)`);
      this.emit('content:decrypted', { 
        size: decrypted.length,
        decryptionTime 
      });
      
      return decrypted.toString('utf8');
      
    } catch (error) {
      log.error('Content decryption failed:', error);
      this.emit('decryption:error', error);
      throw error;
    }
  }

  async deriveKey(password = null, salt = null) {
    try {
      // Use provided password or generate secure key
      const keyMaterial = password || crypto.randomBytes(this.keyLength);
      
      // Generate or use provided salt
      const keySalt = salt || crypto.randomBytes(this.saltLength);
      
      // Derive key using PBKDF2
      const key = crypto.pbkdf2Sync(
        keyMaterial, 
        keySalt, 
        this.keyDerivation.iterations, 
        this.keyLength, 
        this.keyDerivation.hash
      );
      
      return { key, salt: keySalt };
      
    } catch (error) {
      log.error('Key derivation failed:', error);
      throw error;
    }
  }

  validateEncryptedPackage(encryptedPackage) {
    const requiredFields = ['algorithm', 'iv', 'salt', 'tag', 'content', 'metadata'];
    
    for (const field of requiredFields) {
      if (!encryptedPackage.hasOwnProperty(field)) {
        throw new Error(`Missing required field: ${field}`);
      }
    }
    
    if (encryptedPackage.algorithm !== this.algorithm) {
      throw new Error(`Unsupported encryption algorithm: ${encryptedPackage.algorithm}`);
    }
    
    if (!encryptedPackage.metadata.encrypted) {
      throw new Error('Package is not marked as encrypted');
    }
  }

  async encryptFile(filePath, outputPath, password = null) {
    try {
      const fs = require('fs').promises;
      
      // Read file content
      const content = await fs.readFile(filePath);
      
      // Encrypt content
      const encryptedPackage = await this.encryptContent(content.toString('base64'), password, {
        originalPath: filePath,
        fileType: 'binary'
      });
      
      // Write encrypted file
      await fs.writeFile(outputPath, JSON.stringify(encryptedPackage, null, 2));
      
      log.info(`File encrypted: ${filePath} -> ${outputPath}`);
      this.emit('file:encrypted', { filePath, outputPath });
      
      return outputPath;
      
    } catch (error) {
      log.error(`File encryption failed: ${filePath}`, error);
      throw error;
    }
  }

  async decryptFile(encryptedFilePath, outputPath, password = null) {
    try {
      const fs = require('fs').promises;
      
      // Read encrypted file
      const encryptedData = await fs.readFile(encryptedFilePath, 'utf8');
      const encryptedPackage = JSON.parse(encryptedData);
      
      // Decrypt content
      const decryptedContent = await this.decryptContent(encryptedPackage, password);
      
      // Handle binary vs text content
      let finalContent;
      if (encryptedPackage.metadata.fileType === 'binary') {
        finalContent = Buffer.from(decryptedContent, 'base64');
      } else {
        finalContent = decryptedContent;
      }
      
      // Write decrypted file
      await fs.writeFile(outputPath, finalContent);
      
      log.info(`File decrypted: ${encryptedFilePath} -> ${outputPath}`);
      this.emit('file:decrypted', { encryptedFilePath, outputPath });
      
      return outputPath;
      
    } catch (error) {
      log.error(`File decryption failed: ${encryptedFilePath}`, error);
      throw error;
    }
  }

  // Digital signatures for content integrity
  async signContent(content, privateKey) {
    try {
      const sign = crypto.createSign('RSA-SHA256');
      sign.update(content);
      
      const signature = sign.sign(privateKey, 'base64');
      
      return {
        content,
        signature,
        algorithm: 'RSA-SHA256',
        timestamp: new Date().toISOString()
      };
      
    } catch (error) {
      log.error('Content signing failed:', error);
      throw error;
    }
  }

  async verifySignature(signedContent, publicKey) {
    try {
      const verify = crypto.createVerify('RSA-SHA256');
      verify.update(signedContent.content);
      
      const isValid = verify.verify(publicKey, signedContent.signature, 'base64');
      
      this.emit('signature:verified', { isValid, timestamp: signedContent.timestamp });
      
      return isValid;
      
    } catch (error) {
      log.error('Signature verification failed:', error);
      throw error;
    }
  }

  // Content hashing for integrity checks
  generateContentHash(content, algorithm = 'sha256') {
    const hash = crypto.createHash(algorithm);
    hash.update(content);
    return hash.digest('hex');
  }

  verifyContentIntegrity(content, expectedHash, algorithm = 'sha256') {
    const actualHash = this.generateContentHash(content, algorithm);
    const isValid = actualHash === expectedHash;
    
    this.emit('integrity:checked', { isValid, expectedHash, actualHash });
    
    return isValid;
  }

  // Secure key storage
  async storeEncryptionKey(keyId, key, metadata = {}) {
    try {
      // In a real implementation, this would use secure key storage
      // For now, we'll simulate secure storage
      const keyRecord = {
        id: keyId,
        key: key.toString('base64'),
        created: new Date().toISOString(),
        metadata,
        encrypted: true
      };
      
      // Store in secure location (simulated)
      this.encryptionCache.set(keyId, keyRecord);
      
      log.info(`Encryption key stored: ${keyId}`);
      this.emit('key:stored', { keyId });
      
      return keyId;
      
    } catch (error) {
      log.error(`Key storage failed: ${keyId}`, error);
      throw error;
    }
  }

  async retrieveEncryptionKey(keyId) {
    try {
      const keyRecord = this.encryptionCache.get(keyId);
      
      if (!keyRecord) {
        throw new Error(`Encryption key not found: ${keyId}`);
      }
      
      const key = Buffer.from(keyRecord.key, 'base64');
      
      log.debug(`Encryption key retrieved: ${keyId}`);
      this.emit('key:retrieved', { keyId });
      
      return key;
      
    } catch (error) {
      log.error(`Key retrieval failed: ${keyId}`, error);
      throw error;
    }
  }

  // Key rotation and management
  async rotateEncryptionKeys() {
    try {
      const now = Date.now();
      let rotatedCount = 0;
      
      for (const [keyId, keyRecord] of this.encryptionCache.entries()) {
        const keyAge = now - new Date(keyRecord.created).getTime();
        
        if (keyAge > this.policies.keyRotationInterval) {
          // Generate new key
          const newKey = crypto.randomBytes(this.keyLength);
          const newKeyId = `${keyId}_rotated_${Date.now()}`;
          
          // Store new key
          await this.storeEncryptionKey(newKeyId, newKey, {
            rotatedFrom: keyId,
            rotationReason: 'scheduled'
          });
          
          // Mark old key for deprecation
          keyRecord.deprecated = true;
          keyRecord.deprecatedAt = new Date().toISOString();
          
          rotatedCount++;
        }
      }
      
      log.info(`Key rotation completed: ${rotatedCount} keys rotated`);
      this.emit('keys:rotated', { count: rotatedCount });
      
      return rotatedCount;
      
    } catch (error) {
      log.error('Key rotation failed:', error);
      throw error;
    }
  }

  // Security audit
  generateSecurityAudit() {
    const audit = {
      timestamp: new Date().toISOString(),
      encryptionAlgorithm: this.algorithm,
      keyDerivation: this.keyDerivation,
      policies: this.policies,
      statistics: {
        keysStored: this.encryptionCache.size,
        keysDeprecated: 0,
        averageKeyAge: 0
      },
      recommendations: []
    };
    
    // Calculate key statistics
    const now = Date.now();
    let totalKeyAge = 0;
    
    for (const keyRecord of this.encryptionCache.values()) {
      const keyAge = now - new Date(keyRecord.created).getTime();
      totalKeyAge += keyAge;
      
      if (keyRecord.deprecated) {
        audit.statistics.keysDeprecated++;
      }
      
      if (keyAge > this.policies.maxKeyAge) {
        audit.recommendations.push(`Key ${keyRecord.id} exceeds maximum age and should be rotated`);
      }
    }
    
    if (this.encryptionCache.size > 0) {
      audit.statistics.averageKeyAge = totalKeyAge / this.encryptionCache.size;
    }
    
    // Generate recommendations
    if (audit.statistics.keysDeprecated > audit.statistics.keysStored * 0.3) {
      audit.recommendations.push('High number of deprecated keys - consider cleanup');
    }
    
    if (audit.statistics.keysStored === 0) {
      audit.recommendations.push('No encryption keys found - initialize key management');
    }
    
    this.emit('audit:generated', audit);
    
    return audit;
  }

  // Utility methods
  isContentEncrypted(content) {
    try {
      const parsed = JSON.parse(content);
      return parsed.metadata && parsed.metadata.encrypted === true;
    } catch {
      return false;
    }
  }

  getEncryptionStrength() {
    return {
      algorithm: this.algorithm,
      keyLength: this.keyLength * 8, // in bits
      ivLength: this.ivLength * 8,
      iterations: this.keyDerivation.iterations,
      strength: 'Enterprise-grade'
    };
  }

  // Performance optimization
  clearEncryptionCache() {
    this.encryptionCache.clear();
    log.info('Encryption cache cleared');
  }

  getCacheStats() {
    return {
      size: this.encryptionCache.size,
      maxSize: this.maxCacheSize,
      memoryUsage: this.encryptionCache.size * 1024 // Estimated bytes
    };
  }

  // Cleanup
  cleanup() {
    this.clearEncryptionCache();
    log.info('Content Encryption cleaned up');
  }
}

module.exports = ContentEncryption;