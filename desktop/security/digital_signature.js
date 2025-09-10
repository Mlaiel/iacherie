/**
 * Ainflue Desktop - Digital Signature Management
 * 
 * Advanced digital signature system for content authentication and legal protection
 * Implements cryptographic signatures with certificate validation and audit trails
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This code is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

const crypto = require('crypto');
const fs = require('fs').promises;
const path = require('path');

class DigitalSignatureManager {
  constructor(options = {}) {
    this.options = {
      algorithm: 'RSA-SHA256',
      keySize: 2048,
      certificateStore: path.join(process.cwd(), 'certificates'),
      auditLog: true,
      timestamping: true,
      validityPeriod: 365 * 24 * 60 * 60 * 1000, // 1 year
      ...options
    };

    this.certificates = new Map();
    this.signatures = new Map();
    this.auditTrail = [];
    this.keyPairs = new Map();
    this.revocationList = new Set();
    this.trustedAuthorities = new Set();

    this.initialize();
  }

  async initialize() {
    await this.ensureCertificateDirectory();
    await this.loadCertificates();
    await this.setupDefaultCA();
    this.startMaintenanceTasks();
    
    console.log('🔏 Digital Signature Manager initialized');
  }

  async ensureCertificateDirectory() {
    try {
      await fs.access(this.options.certificateStore);
    } catch {
      await fs.mkdir(this.options.certificateStore, { recursive: true });
    }
  }

  async loadCertificates() {
    try {
      const files = await fs.readdir(this.options.certificateStore);
      const certFiles = files.filter(f => f.endsWith('.pem') || f.endsWith('.crt'));
      
      for (const file of certFiles) {
        const certPath = path.join(this.options.certificateStore, file);
        const certData = await fs.readFile(certPath, 'utf8');
        const certificate = this.parseCertificate(certData);
        
        if (certificate) {
          this.certificates.set(certificate.id, certificate);
          console.log(`📜 Loaded certificate: ${certificate.subject}`);
        }
      }
    } catch (error) {
      console.warn('⚠️ Failed to load certificates:', error.message);
    }
  }

  async setupDefaultCA() {
    // Setup Ainflue Certificate Authority
    const caId = 'ainflue-ca';
    
    if (!this.certificates.has(caId)) {
      const caCert = await this.createCertificateAuthority();
      this.certificates.set(caId, caCert);
      this.trustedAuthorities.add(caId);
      
      await this.saveCertificate(caCert);
      console.log('🏛️ Created Ainflue Certificate Authority');
    }
  }

  startMaintenanceTasks() {
    // Check certificate validity every hour
    setInterval(() => {
      this.validateCertificates();
    }, 60 * 60 * 1000);

    // Cleanup expired signatures daily
    setInterval(() => {
      this.cleanupExpiredSignatures();
    }, 24 * 60 * 60 * 1000);
  }

  // Certificate Management
  async createCertificateAuthority() {
    const keyPair = await this.generateKeyPair();
    
    const certificate = {
      id: 'ainflue-ca',
      type: 'CA',
      subject: 'CN=Ainflue Certificate Authority, O=Ainflue, C=DE',
      issuer: 'CN=Ainflue Certificate Authority, O=Ainflue, C=DE',
      publicKey: keyPair.publicKey,
      privateKey: keyPair.privateKey,
      serialNumber: this.generateSerialNumber(),
      notBefore: new Date(),
      notAfter: new Date(Date.now() + (10 * 365 * 24 * 60 * 60 * 1000)), // 10 years
      keyUsage: ['digitalSignature', 'keyCertSign', 'cRLSign'],
      extensions: {
        basicConstraints: 'CA:TRUE',
        keyUsage: 'digitalSignature, keyCertSign, cRLSign',
        subjectKeyIdentifier: this.calculateKeyIdentifier(keyPair.publicKey)
      },
      fingerprint: this.calculateFingerprint(keyPair.publicKey),
      status: 'valid',
      createdAt: new Date().toISOString()
    };

    // Self-sign the CA certificate
    certificate.signature = await this.signData(
      this.serializeCertificate(certificate),
      keyPair.privateKey
    );

    this.keyPairs.set(certificate.id, keyPair);
    return certificate;
  }

  async createUserCertificate(userInfo) {
    const caId = 'ainflue-ca';
    const ca = this.certificates.get(caId);
    
    if (!ca) {
      throw new Error('Certificate Authority not available');
    }

    const keyPair = await this.generateKeyPair();
    const certificateId = crypto.randomUUID();
    
    const certificate = {
      id: certificateId,
      type: 'User',
      subject: `CN=${userInfo.name}, O=${userInfo.organization || 'Ainflue'}, C=${userInfo.country || 'DE'}`,
      issuer: ca.subject,
      publicKey: keyPair.publicKey,
      serialNumber: this.generateSerialNumber(),
      notBefore: new Date(),
      notAfter: new Date(Date.now() + this.options.validityPeriod),
      keyUsage: ['digitalSignature', 'nonRepudiation'],
      extensions: {
        basicConstraints: 'CA:FALSE',
        keyUsage: 'digitalSignature, nonRepudiation',
        extKeyUsage: 'clientAuth, emailProtection',
        subjectKeyIdentifier: this.calculateKeyIdentifier(keyPair.publicKey),
        authorityKeyIdentifier: ca.extensions.subjectKeyIdentifier,
        subjectAltName: userInfo.email ? `email:${userInfo.email}` : null
      },
      fingerprint: this.calculateFingerprint(keyPair.publicKey),
      status: 'valid',
      createdAt: new Date().toISOString(),
      userInfo: userInfo
    };

    // Sign with CA private key
    const caKeyPair = this.keyPairs.get(caId);
    certificate.signature = await this.signData(
      this.serializeCertificate(certificate),
      caKeyPair.privateKey
    );

    this.keyPairs.set(certificateId, keyPair);
    this.certificates.set(certificateId, certificate);
    
    await this.saveCertificate(certificate);
    this.logAuditEvent('certificate_created', {
      certificateId: certificateId,
      subject: certificate.subject,
      userInfo: userInfo
    });

    console.log(`📜 Created user certificate: ${certificate.subject}`);
    return certificate;
  }

  async revokeCertificate(certificateId, reason = 'unspecified') {
    const certificate = this.certificates.get(certificateId);
    if (!certificate) {
      throw new Error('Certificate not found');
    }

    certificate.status = 'revoked';
    certificate.revokedAt = new Date().toISOString();
    certificate.revocationReason = reason;

    this.revocationList.add(certificateId);
    
    this.logAuditEvent('certificate_revoked', {
      certificateId: certificateId,
      subject: certificate.subject,
      reason: reason
    });

    console.log(`🚫 Revoked certificate: ${certificate.subject}`);
    return true;
  }

  // Content Signing
  async signContent(contentPath, certificateId, options = {}) {
    try {
      const certificate = this.certificates.get(certificateId);
      if (!certificate) {
        throw new Error('Certificate not found');
      }

      if (!this.isCertificateValid(certificate)) {
        throw new Error('Certificate is not valid');
      }

      const keyPair = this.keyPairs.get(certificateId);
      if (!keyPair) {
        throw new Error('Private key not available');
      }

      // Read content
      const content = await fs.readFile(contentPath);
      const contentHash = this.calculateHash(content);

      // Create signature metadata
      const signatureData = {
        contentPath: contentPath,
        contentHash: contentHash,
        contentSize: content.length,
        timestamp: new Date().toISOString(),
        certificateId: certificateId,
        algorithm: this.options.algorithm,
        options: options
      };

      // Add timestamping if enabled
      if (this.options.timestamping) {
        signatureData.timestamp = await this.getTimestamp();
      }

      // Create signature
      const dataToSign = JSON.stringify(signatureData);
      const signature = await this.signData(dataToSign, keyPair.privateKey);

      const signatureRecord = {
        id: crypto.randomUUID(),
        ...signatureData,
        signature: signature,
        status: 'valid',
        createdAt: new Date().toISOString()
      };

      this.signatures.set(signatureRecord.id, signatureRecord);

      // Save signature file
      if (options.saveSignatureFile) {
        const signatureFile = contentPath + '.sig';
        await this.saveSignatureFile(signatureFile, signatureRecord);
      }

      this.logAuditEvent('content_signed', {
        contentPath: contentPath,
        signatureId: signatureRecord.id,
        certificateId: certificateId
      });

      console.log(`✍️ Signed content: ${path.basename(contentPath)}`);
      return signatureRecord;

    } catch (error) {
      this.logAuditEvent('signing_failed', {
        contentPath: contentPath,
        certificateId: certificateId,
        error: error.message
      });
      throw error;
    }
  }

  async verifyContentSignature(contentPath, signatureData) {
    try {
      let signature;
      
      if (typeof signatureData === 'string') {
        // Load signature from file
        signature = await this.loadSignatureFile(signatureData);
      } else {
        signature = signatureData;
      }

      // Get certificate
      const certificate = this.certificates.get(signature.certificateId);
      if (!certificate) {
        throw new Error('Certificate not found');
      }

      // Check certificate validity
      if (!this.isCertificateValid(certificate)) {
        throw new Error('Certificate is not valid');
      }

      // Check if certificate is revoked
      if (this.revocationList.has(signature.certificateId)) {
        throw new Error('Certificate has been revoked');
      }

      // Read and hash content
      const content = await fs.readFile(contentPath);
      const contentHash = this.calculateHash(content);

      // Verify content hash
      if (contentHash !== signature.contentHash) {
        throw new Error('Content has been modified');
      }

      // Verify signature
      const signatureData = {
        contentPath: signature.contentPath,
        contentHash: signature.contentHash,
        contentSize: signature.contentSize,
        timestamp: signature.timestamp,
        certificateId: signature.certificateId,
        algorithm: signature.algorithm,
        options: signature.options
      };

      const dataToVerify = JSON.stringify(signatureData);
      const isValid = await this.verifySignature(
        dataToVerify,
        signature.signature,
        certificate.publicKey
      );

      const verificationResult = {
        valid: isValid,
        certificate: certificate,
        signature: signature,
        contentIntegrity: contentHash === signature.contentHash,
        certificateValid: this.isCertificateValid(certificate),
        timestampValid: this.verifyTimestamp(signature.timestamp),
        verifiedAt: new Date().toISOString()
      };

      this.logAuditEvent('signature_verified', {
        contentPath: contentPath,
        signatureId: signature.id,
        valid: isValid,
        certificateId: signature.certificateId
      });

      console.log(`🔍 Verified signature: ${isValid ? 'Valid' : 'Invalid'}`);
      return verificationResult;

    } catch (error) {
      this.logAuditEvent('verification_failed', {
        contentPath: contentPath,
        error: error.message
      });
      throw error;
    }
  }

  // Cryptographic Operations
  async generateKeyPair() {
    return new Promise((resolve, reject) => {
      crypto.generateKeyPair('rsa', {
        modulusLength: this.options.keySize,
        publicKeyEncoding: {
          type: 'spki',
          format: 'pem'
        },
        privateKeyEncoding: {
          type: 'pkcs8',
          format: 'pem'
        }
      }, (err, publicKey, privateKey) => {
        if (err) reject(err);
        else resolve({ publicKey, privateKey });
      });
    });
  }

  async signData(data, privateKey) {
    const sign = crypto.createSign(this.options.algorithm);
    sign.update(data);
    return sign.sign(privateKey, 'base64');
  }

  async verifySignature(data, signature, publicKey) {
    try {
      const verify = crypto.createVerify(this.options.algorithm);
      verify.update(data);
      return verify.verify(publicKey, signature, 'base64');
    } catch (error) {
      return false;
    }
  }

  calculateHash(data) {
    return crypto.createHash('sha256').update(data).digest('hex');
  }

  calculateFingerprint(publicKey) {
    return crypto.createHash('sha1').update(publicKey).digest('hex').toUpperCase();
  }

  calculateKeyIdentifier(publicKey) {
    const hash = crypto.createHash('sha1').update(publicKey).digest('hex');
    return hash.substring(0, 40);
  }

  generateSerialNumber() {
    return crypto.randomBytes(16).toString('hex').toUpperCase();
  }

  // Certificate Validation
  isCertificateValid(certificate) {
    const now = new Date();
    const notBefore = new Date(certificate.notBefore);
    const notAfter = new Date(certificate.notAfter);

    return (
      certificate.status === 'valid' &&
      now >= notBefore &&
      now <= notAfter &&
      !this.revocationList.has(certificate.id)
    );
  }

  validateCertificates() {
    let expiredCount = 0;
    
    for (const [id, certificate] of this.certificates) {
      if (!this.isCertificateValid(certificate) && certificate.status === 'valid') {
        certificate.status = 'expired';
        expiredCount++;
        
        this.logAuditEvent('certificate_expired', {
          certificateId: id,
          subject: certificate.subject
        });
      }
    }

    if (expiredCount > 0) {
      console.log(`⏰ Marked ${expiredCount} certificates as expired`);
    }
  }

  verifyTimestamp(timestamp) {
    // Basic timestamp validation
    const timestampDate = new Date(timestamp);
    const now = new Date();
    const tolerance = 5 * 60 * 1000; // 5 minutes

    return Math.abs(now.getTime() - timestampDate.getTime()) < tolerance;
  }

  async getTimestamp() {
    // In production, this would contact a trusted timestamp authority
    return new Date().toISOString();
  }

  // File Operations
  async saveCertificate(certificate) {
    const filename = `${certificate.id}.pem`;
    const filePath = path.join(this.options.certificateStore, filename);
    
    const certPem = this.encodeCertificatePEM(certificate);
    await fs.writeFile(filePath, certPem);
  }

  async saveSignatureFile(filePath, signature) {
    const signatureJson = JSON.stringify(signature, null, 2);
    await fs.writeFile(filePath, signatureJson);
  }

  async loadSignatureFile(filePath) {
    const content = await fs.readFile(filePath, 'utf8');
    return JSON.parse(content);
  }

  // Certificate Parsing and Encoding
  parseCertificate(pemData) {
    // Simplified certificate parsing
    // In production, use a proper ASN.1 parser
    try {
      const lines = pemData.split('\n');
      const certData = lines.slice(1, -2).join('');
      
      // Mock certificate object
      return {
        id: crypto.randomUUID(),
        type: 'parsed',
        publicKey: pemData,
        status: 'valid',
        createdAt: new Date().toISOString()
      };
    } catch (error) {
      console.error('Failed to parse certificate:', error);
      return null;
    }
  }

  encodeCertificatePEM(certificate) {
    // Simplified PEM encoding
    const certData = JSON.stringify({
      subject: certificate.subject,
      publicKey: certificate.publicKey,
      serialNumber: certificate.serialNumber,
      notBefore: certificate.notBefore,
      notAfter: certificate.notAfter
    });

    const base64Data = Buffer.from(certData).toString('base64');
    const pemLines = base64Data.match(/.{1,64}/g);
    
    return [
      '-----BEGIN CERTIFICATE-----',
      ...pemLines,
      '-----END CERTIFICATE-----'
    ].join('\n');
  }

  serializeCertificate(certificate) {
    // Create deterministic serialization for signing
    return JSON.stringify({
      subject: certificate.subject,
      publicKey: certificate.publicKey,
      serialNumber: certificate.serialNumber,
      notBefore: certificate.notBefore,
      notAfter: certificate.notAfter,
      keyUsage: certificate.keyUsage,
      extensions: certificate.extensions
    });
  }

  // Audit and Logging
  logAuditEvent(eventType, data) {
    if (!this.options.auditLog) return;

    const auditEntry = {
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      eventType: eventType,
      data: data,
      severity: this.getEventSeverity(eventType)
    };

    this.auditTrail.push(auditEntry);
    
    // Keep only last 1000 entries
    if (this.auditTrail.length > 1000) {
      this.auditTrail = this.auditTrail.slice(-1000);
    }

    console.log(`📋 Audit: ${eventType}`, data);
  }

  getEventSeverity(eventType) {
    const highSeverity = ['certificate_revoked', 'signing_failed', 'verification_failed'];
    const mediumSeverity = ['certificate_expired', 'certificate_created'];
    
    if (highSeverity.includes(eventType)) return 'high';
    if (mediumSeverity.includes(eventType)) return 'medium';
    return 'low';
  }

  cleanupExpiredSignatures() {
    const cutoff = Date.now() - (30 * 24 * 60 * 60 * 1000); // 30 days
    let cleanedCount = 0;

    for (const [id, signature] of this.signatures) {
      const signatureDate = new Date(signature.createdAt).getTime();
      if (signatureDate < cutoff) {
        this.signatures.delete(id);
        cleanedCount++;
      }
    }

    if (cleanedCount > 0) {
      console.log(`🧹 Cleaned up ${cleanedCount} expired signatures`);
    }
  }

  // Public API
  getCertificates() {
    return Array.from(this.certificates.values()).map(cert => ({
      id: cert.id,
      subject: cert.subject,
      fingerprint: cert.fingerprint,
      status: cert.status,
      notBefore: cert.notBefore,
      notAfter: cert.notAfter,
      type: cert.type
    }));
  }

  getSignatures() {
    return Array.from(this.signatures.values()).map(sig => ({
      id: sig.id,
      contentPath: path.basename(sig.contentPath),
      certificateId: sig.certificateId,
      timestamp: sig.timestamp,
      status: sig.status
    }));
  }

  getAuditTrail() {
    return this.auditTrail.slice().reverse(); // Most recent first
  }

  async exportCertificate(certificateId, format = 'pem') {
    const certificate = this.certificates.get(certificateId);
    if (!certificate) {
      throw new Error('Certificate not found');
    }

    switch (format) {
      case 'pem':
        return this.encodeCertificatePEM(certificate);
      case 'json':
        return JSON.stringify(certificate, null, 2);
      default:
        throw new Error('Unsupported export format');
    }
  }

  getStatistics() {
    const validCerts = Array.from(this.certificates.values()).filter(c => c.status === 'valid');
    const expiredCerts = Array.from(this.certificates.values()).filter(c => c.status === 'expired');
    const revokedCerts = Array.from(this.certificates.values()).filter(c => c.status === 'revoked');

    return {
      certificates: {
        total: this.certificates.size,
        valid: validCerts.length,
        expired: expiredCerts.length,
        revoked: revokedCerts.length
      },
      signatures: {
        total: this.signatures.size,
        recent: this.signatures.size // All signatures are considered recent for now
      },
      auditEvents: {
        total: this.auditTrail.length,
        highSeverity: this.auditTrail.filter(e => e.severity === 'high').length
      }
    };
  }
}

module.exports = DigitalSignatureManager;