/**
 * Ainflue Desktop - Secure Storage Manager
 * 
 * Encrypted local storage for sensitive data with key management
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * @license Proprietary - Unauthorized use prohibited
 */

const crypto = require('crypto');
const fs = require('fs').promises;
const path = require('path');
const os = require('os');

class SecureStorageManager {
    constructor(options = {}) {
        this.algorithm = options.algorithm || 'aes-256-gcm';
        this.keyDerivation = options.keyDerivation || 'pbkdf2';
        this.iterations = options.iterations || 100000;
        this.saltLength = options.saltLength || 32;
        this.storageDir = options.storageDir || path.join(os.homedir(), '.ainflue', 'secure');
        
        this.masterKey = null;
        this.storageIndex = new Map();
        
        this.initializeSecureStorage();
    }

    /**
     * Initialize secure storage system
     */
    async initializeSecureStorage() {
        try {
            await fs.mkdir(this.storageDir, { recursive: true, mode: 0o700 });
            await this.loadStorageIndex();
        } catch (error) {
            console.error('Failed to initialize secure storage:', error);
            throw new Error('Secure storage initialization failed');
        }
    }

    /**
     * Initialize master key from password or generate new one
     */
    async initializeMasterKey(password = null) {
        if (password) {
            // Derive key from password
            const salt = await this.getSalt();
            this.masterKey = await this.deriveKey(password, salt);
        } else {
            // Generate random master key for desktop app
            this.masterKey = crypto.randomBytes(32);
        }
        
        return this.masterKey !== null;
    }

    /**
     * Derive encryption key from password
     */
    async deriveKey(password, salt) {
        return new Promise((resolve, reject) => {
            crypto.pbkdf2(password, salt, this.iterations, 32, 'sha256', (err, derivedKey) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(derivedKey);
                }
            });
        });
    }

    /**
     * Get or create salt for key derivation
     */
    async getSalt() {
        const saltPath = path.join(this.storageDir, '.salt');
        
        try {
            const salt = await fs.readFile(saltPath);
            return salt;
        } catch (error) {
            // Generate new salt
            const salt = crypto.randomBytes(this.saltLength);
            await fs.writeFile(saltPath, salt, { mode: 0o600 });
            return salt;
        }
    }

    /**
     * Encrypt and store data securely
     */
    async store(key, data, options = {}) {
        if (!this.masterKey) {
            await this.initializeMasterKey();
        }

        try {
            const serializedData = JSON.stringify(data);
            const encrypted = this.encrypt(serializedData);
            
            const storageEntry = {
                key,
                encrypted,
                timestamp: Date.now(),
                expires: options.expires || null,
                metadata: options.metadata || {},
                version: '1.0.0'
            };

            const entryPath = this.getEntryPath(key);
            await fs.writeFile(entryPath, JSON.stringify(storageEntry), { mode: 0o600 });
            
            // Update index
            this.storageIndex.set(key, {
                path: entryPath,
                timestamp: storageEntry.timestamp,
                expires: storageEntry.expires,
                size: serializedData.length
            });

            await this.saveStorageIndex();
            
            return {
                success: true,
                key,
                timestamp: storageEntry.timestamp
            };
        } catch (error) {
            console.error('Secure storage failed:', error);
            throw new Error('Failed to store data securely');
        }
    }

    /**
     * Retrieve and decrypt stored data
     */
    async retrieve(key, options = {}) {
        if (!this.masterKey) {
            throw new Error('Master key not initialized');
        }

        try {
            const indexEntry = this.storageIndex.get(key);
            if (!indexEntry) {
                return { success: false, reason: 'Key not found' };
            }

            // Check expiration
            if (indexEntry.expires && Date.now() > indexEntry.expires) {
                await this.delete(key);
                return { success: false, reason: 'Data expired' };
            }

            const entryPath = this.getEntryPath(key);
            const storageEntryJson = await fs.readFile(entryPath, 'utf8');
            const storageEntry = JSON.parse(storageEntryJson);

            const decryptedData = this.decrypt(storageEntry.encrypted);
            const data = JSON.parse(decryptedData);

            return {
                success: true,
                data,
                timestamp: storageEntry.timestamp,
                metadata: storageEntry.metadata
            };
        } catch (error) {
            console.error('Secure retrieval failed:', error);
            return { success: false, reason: 'Decryption failed' };
        }
    }

    /**
     * Update existing stored data
     */
    async update(key, data, options = {}) {
        const existing = await this.retrieve(key);
        if (!existing.success) {
            throw new Error('Cannot update non-existent key');
        }

        const updatedData = options.merge ? 
            { ...existing.data, ...data } : data;

        return await this.store(key, updatedData, {
            ...options,
            metadata: {
                ...existing.metadata,
                ...options.metadata,
                lastUpdated: Date.now()
            }
        });
    }

    /**
     * Delete stored data
     */
    async delete(key) {
        try {
            const entryPath = this.getEntryPath(key);
            await fs.unlink(entryPath);
            this.storageIndex.delete(key);
            await this.saveStorageIndex();
            
            return { success: true };
        } catch (error) {
            return { success: false, reason: error.message };
        }
    }

    /**
     * List all stored keys
     */
    listKeys(pattern = null) {
        const keys = Array.from(this.storageIndex.keys());
        
        if (pattern) {
            const regex = new RegExp(pattern);
            return keys.filter(key => regex.test(key));
        }
        
        return keys;
    }

    /**
     * Check if key exists and is valid
     */
    async exists(key) {
        const indexEntry = this.storageIndex.get(key);
        if (!indexEntry) {
            return false;
        }

        // Check expiration
        if (indexEntry.expires && Date.now() > indexEntry.expires) {
            await this.delete(key);
            return false;
        }

        return true;
    }

    /**
     * Encrypt data using AES-256-GCM
     */
    encrypt(data) {
        const iv = crypto.randomBytes(16);
        const cipher = crypto.createCipher(this.algorithm, this.masterKey);
        
        let encrypted = cipher.update(data, 'utf8', 'hex');
        encrypted += cipher.final('hex');
        
        const tag = cipher.getAuthTag ? cipher.getAuthTag() : null;
        
        return {
            iv: iv.toString('hex'),
            data: encrypted,
            tag: tag ? tag.toString('hex') : null,
            algorithm: this.algorithm
        };
    }

    /**
     * Decrypt data using AES-256-GCM
     */
    decrypt(encryptedData) {
        const decipher = crypto.createDecipher(encryptedData.algorithm, this.masterKey);
        
        if (encryptedData.tag && decipher.setAuthTag) {
            decipher.setAuthTag(Buffer.from(encryptedData.tag, 'hex'));
        }
        
        let decrypted = decipher.update(encryptedData.data, 'hex', 'utf8');
        decrypted += decipher.final('utf8');
        
        return decrypted;
    }

    /**
     * Secure file storage
     */
    async storeFile(key, filePath, options = {}) {
        try {
            const fileContent = await fs.readFile(filePath);
            const fileName = path.basename(filePath);
            const fileStats = await fs.stat(filePath);
            
            const fileData = {
                content: fileContent.toString('base64'),
                fileName,
                size: fileStats.size,
                mimeType: options.mimeType || 'application/octet-stream',
                originalPath: filePath
            };

            return await this.store(key, fileData, {
                ...options,
                metadata: {
                    ...options.metadata,
                    type: 'file',
                    fileName,
                    size: fileStats.size
                }
            });
        } catch (error) {
            throw new Error(`Failed to store file: ${error.message}`);
        }
    }

    /**
     * Retrieve and save file
     */
    async retrieveFile(key, outputPath = null) {
        const result = await this.retrieve(key);
        if (!result.success) {
            return result;
        }

        try {
            const fileData = result.data;
            const content = Buffer.from(fileData.content, 'base64');
            
            const savePath = outputPath || path.join(this.storageDir, fileData.fileName);
            await fs.writeFile(savePath, content);
            
            return {
                success: true,
                filePath: savePath,
                fileName: fileData.fileName,
                size: fileData.size
            };
        } catch (error) {
            return { success: false, reason: 'File extraction failed' };
        }
    }

    /**
     * Get storage entry file path
     */
    getEntryPath(key) {
        const hashedKey = crypto.createHash('sha256').update(key).digest('hex');
        return path.join(this.storageDir, `${hashedKey}.enc`);
    }

    /**
     * Load storage index
     */
    async loadStorageIndex() {
        const indexPath = path.join(this.storageDir, '.index');
        
        try {
            const indexData = await fs.readFile(indexPath, 'utf8');
            const index = JSON.parse(indexData);
            
            for (const [key, entry] of Object.entries(index)) {
                this.storageIndex.set(key, entry);
            }
        } catch (error) {
            // Index doesn't exist or is corrupted, start fresh
            this.storageIndex.clear();
        }
    }

    /**
     * Save storage index
     */
    async saveStorageIndex() {
        const indexPath = path.join(this.storageDir, '.index');
        const indexData = Object.fromEntries(this.storageIndex);
        
        await fs.writeFile(indexPath, JSON.stringify(indexData, null, 2), { mode: 0o600 });
    }

    /**
     * Backup encrypted storage
     */
    async createBackup(backupPath) {
        try {
            await fs.mkdir(backupPath, { recursive: true });
            
            const files = await fs.readdir(this.storageDir);
            let backupCount = 0;

            for (const file of files) {
                const sourcePath = path.join(this.storageDir, file);
                const destPath = path.join(backupPath, file);
                await fs.copyFile(sourcePath, destPath);
                backupCount++;
            }

            return {
                success: true,
                filesBackedUp: backupCount,
                backupPath
            };
        } catch (error) {
            return {
                success: false,
                reason: error.message
            };
        }
    }

    /**
     * Restore from backup
     */
    async restoreFromBackup(backupPath) {
        try {
            const files = await fs.readdir(backupPath);
            let restoredCount = 0;

            for (const file of files) {
                const sourcePath = path.join(backupPath, file);
                const destPath = path.join(this.storageDir, file);
                await fs.copyFile(sourcePath, destPath);
                restoredCount++;
            }

            await this.loadStorageIndex();

            return {
                success: true,
                filesRestored: restoredCount
            };
        } catch (error) {
            return {
                success: false,
                reason: error.message
            };
        }
    }

    /**
     * Cleanup expired entries
     */
    async cleanup() {
        const now = Date.now();
        let cleanedCount = 0;

        for (const [key, entry] of this.storageIndex.entries()) {
            if (entry.expires && now > entry.expires) {
                await this.delete(key);
                cleanedCount++;
            }
        }

        return {
            cleaned: cleanedCount,
            remaining: this.storageIndex.size
        };
    }

    /**
     * Get storage statistics
     */
    getStorageStats() {
        const entries = Array.from(this.storageIndex.values());
        
        return {
            totalEntries: entries.length,
            totalSize: entries.reduce((sum, entry) => sum + (entry.size || 0), 0),
            oldestEntry: entries.length > 0 ? 
                Math.min(...entries.map(e => e.timestamp)) : null,
            newestEntry: entries.length > 0 ?
                Math.max(...entries.map(e => e.timestamp)) : null,
            expiredEntries: entries.filter(e => e.expires && Date.now() > e.expires).length,
            storageDirectory: this.storageDir
        };
    }

    /**
     * Destroy all stored data (for security)
     */
    async destroyAllData() {
        try {
            const files = await fs.readdir(this.storageDir);
            
            for (const file of files) {
                const filePath = path.join(this.storageDir, file);
                await fs.unlink(filePath);
            }

            this.storageIndex.clear();
            this.masterKey = null;

            return { success: true, message: 'All data destroyed' };
        } catch (error) {
            return { success: false, reason: error.message };
        }
    }
}

module.exports = SecureStorageManager;

/**
 * Copyright Notice:
 * This code is the exclusive property of Fahed Mlaiel.
 * Unauthorized use, copying, or distribution is strictly prohibited.
 * Contact: mlaiel@live.de
 */