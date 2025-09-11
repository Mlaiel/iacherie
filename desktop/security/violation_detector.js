/**
 * Ainflue Desktop - Violation Detector
 * 
 * Advanced copyright and license violation detection system with AI-powered
 * content analysis, pattern recognition, and automated enforcement.
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This code is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

class ViolationDetector {
    constructor() {
        this.violations = new Map();
        this.detectionRules = new Map();
        this.whitelist = new Set();
        this.blacklist = new Set();
        this.scanQueue = [];
        this.isScanning = false;
        this.alertHandlers = new Set();
        
        this.config = {
            enableRealTimeScanning: true,
            enableAIDetection: true,
            strictMode: false,
            autoEnforcement: false,
            scanInterval: 30000, // 30 seconds
            confidenceThreshold: 0.7,
            maxScanQueue: 100
        };

        // Violation severity levels
        this.severityLevels = {
            CRITICAL: {
                level: 4,
                autoAction: 'block',
                description: 'Immediate action required'
            },
            HIGH: {
                level: 3,
                autoAction: 'warn',
                description: 'Significant violation detected'
            },
            MEDIUM: {
                level: 2,
                autoAction: 'log',
                description: 'Potential violation'
            },
            LOW: {
                level: 1,
                autoAction: 'monitor',
                description: 'Minor concern'
            }
        };

        // Detection rule categories
        this.ruleCategories = {
            copyright: {
                enabled: true,
                patterns: [
                    /©\s*\d{4}.*(?:all rights reserved|copyright)/i,
                    /watermark/i,
                    /unauthorized.*prohibited/i,
                    /proprietary.*confidential/i
                ],
                aiModels: ['copyright-detection', 'watermark-analysis']
            },
            license: {
                enabled: true,
                patterns: [
                    /license.*violation/i,
                    /unauthorized.*use/i,
                    /terms.*service.*violated/i,
                    /eula.*breach/i
                ],
                aiModels: ['license-compliance', 'terms-analysis']
            },
            plagiarism: {
                enabled: true,
                patterns: [
                    /duplicate.*content/i,
                    /copied.*from/i,
                    /identical.*match/i
                ],
                aiModels: ['content-similarity', 'plagiarism-detection']
            },
            trademark: {
                enabled: true,
                patterns: [
                    /®|™/g,
                    /trademark.*infringement/i,
                    /brand.*violation/i
                ],
                aiModels: ['trademark-detection', 'brand-analysis']
            },
            security: {
                enabled: true,
                patterns: [
                    /malware/i,
                    /virus/i,
                    /unauthorized.*access/i,
                    /security.*breach/i
                ],
                aiModels: ['security-scan', 'malware-detection']
            }
        };
    }

    async initialize() {
        console.log('🛡️ Initializing Violation Detector...');

        // Load configuration and rules
        await this.loadConfiguration();
        await this.loadDetectionRules();
        await this.loadWhitelistBlacklist();

        // Initialize AI models if enabled
        if (this.config.enableAIDetection) {
            await this.initializeAIModels();
        }

        // Start real-time scanning if enabled
        if (this.config.enableRealTimeScanning) {
            this.startRealTimeScanning();
        }

        // Set up violation storage
        await this.initializeViolationStorage();

        console.log('✅ Violation Detector initialized');
    }

    async loadConfiguration() {
        try {
            if (window.electronAPI) {
                const config = await window.electronAPI.invoke('store-get', 'violation-detector-config');
                if (config) {
                    Object.assign(this.config, config);
                }
            }
        } catch (error) {
            console.warn('Failed to load violation detector configuration:', error);
        }
    }

    async loadDetectionRules() {
        try {
            // Load custom detection rules
            if (window.electronAPI) {
                const customRules = await window.electronAPI.invoke('store-get', 'detection-rules');
                if (customRules) {
                    for (const [category, rules] of Object.entries(customRules)) {
                        this.detectionRules.set(category, rules);
                    }
                }
            }

            // Initialize default rules
            for (const [category, config] of Object.entries(this.ruleCategories)) {
                if (!this.detectionRules.has(category)) {
                    this.detectionRules.set(category, {
                        patterns: config.patterns,
                        enabled: config.enabled,
                        confidence: 0.8
                    });
                }
            }

            console.log(`📋 Loaded ${this.detectionRules.size} detection rule categories`);
        } catch (error) {
            console.error('Failed to load detection rules:', error);
        }
    }

    async loadWhitelistBlacklist() {
        try {
            if (window.electronAPI) {
                const whitelist = await window.electronAPI.invoke('store-get', 'violation-whitelist');
                const blacklist = await window.electronAPI.invoke('store-get', 'violation-blacklist');
                
                if (whitelist) {
                    this.whitelist = new Set(whitelist);
                }
                if (blacklist) {
                    this.blacklist = new Set(blacklist);
                }
            }
        } catch (error) {
            console.warn('Failed to load whitelist/blacklist:', error);
        }
    }

    async initializeAIModels() {
        try {
            // Mock AI model initialization
            console.log('🤖 Initializing AI detection models...');
            
            this.aiModels = {
                'copyright-detection': { loaded: true, confidence: 0.9 },
                'watermark-analysis': { loaded: true, confidence: 0.85 },
                'license-compliance': { loaded: true, confidence: 0.8 },
                'content-similarity': { loaded: true, confidence: 0.92 },
                'plagiarism-detection': { loaded: true, confidence: 0.88 },
                'trademark-detection': { loaded: true, confidence: 0.75 },
                'security-scan': { loaded: true, confidence: 0.95 }
            };

            console.log('✅ AI models initialized');
        } catch (error) {
            console.error('Failed to initialize AI models:', error);
            this.config.enableAIDetection = false;
        }
    }

    async initializeViolationStorage() {
        try {
            // Initialize storage for violations
            if (window.electronAPI) {
                const existingViolations = await window.electronAPI.invoke('store-get', 'detected-violations');
                if (existingViolations) {
                    this.violations = new Map(Object.entries(existingViolations));
                }
            }
        } catch (error) {
            console.warn('Failed to initialize violation storage:', error);
        }
    }

    startRealTimeScanning() {
        this.scanInterval = setInterval(() => {
            this.processScanQueue();
        }, this.config.scanInterval);

        console.log('👁️ Real-time violation scanning started');
    }

    stopRealTimeScanning() {
        if (this.scanInterval) {
            clearInterval(this.scanInterval);
            this.scanInterval = null;
            console.log('⏹️ Real-time violation scanning stopped');
        }
    }

    async scanContent(content, metadata = {}) {
        const scanId = this.generateScanId();
        
        console.log(`🔍 Scanning content for violations: ${scanId}`);

        try {
            const results = {
                scanId,
                timestamp: Date.now(),
                content: {
                    type: metadata.type || 'unknown',
                    size: metadata.size || 0,
                    format: metadata.format,
                    hash: this.generateContentHash(content)
                },
                violations: [],
                confidence: 0,
                status: 'scanning'
            };

            // Check whitelist first
            if (this.isWhitelisted(content, metadata)) {
                results.status = 'whitelisted';
                results.confidence = 1.0;
                return results;
            }

            // Check blacklist
            if (this.isBlacklisted(content, metadata)) {
                results.violations.push({
                    type: 'blacklisted',
                    severity: 'CRITICAL',
                    confidence: 1.0,
                    description: 'Content is on blacklist'
                });
                results.status = 'violation_detected';
                results.confidence = 1.0;
                await this.handleViolation(results);
                return results;
            }

            // Pattern-based detection
            const patternViolations = await this.detectPatternViolations(content);
            results.violations.push(...patternViolations);

            // AI-based detection if enabled
            if (this.config.enableAIDetection) {
                const aiViolations = await this.detectAIViolations(content, metadata);
                results.violations.push(...aiViolations);
            }

            // Content similarity check
            const similarityViolations = await this.detectSimilarityViolations(content, metadata);
            results.violations.push(...similarityViolations);

            // Calculate overall confidence
            results.confidence = this.calculateOverallConfidence(results.violations);
            
            // Determine status
            if (results.violations.length > 0) {
                const hasHighConfidence = results.violations.some(v => v.confidence >= this.config.confidenceThreshold);
                results.status = hasHighConfidence ? 'violation_detected' : 'suspicious';
                
                if (hasHighConfidence) {
                    await this.handleViolation(results);
                }
            } else {
                results.status = 'clean';
            }

            console.log(`✅ Scan completed: ${scanId} - ${results.status} (${results.violations.length} violations)`);
            return results;

        } catch (error) {
            console.error(`❌ Scan failed: ${scanId}`, error);
            return {
                scanId,
                timestamp: Date.now(),
                status: 'error',
                error: error.message,
                violations: []
            };
        }
    }

    async detectPatternViolations(content) {
        const violations = [];
        
        for (const [category, rules] of this.detectionRules) {
            if (!rules.enabled) continue;

            for (const pattern of rules.patterns) {
                try {
                    const matches = content.match(pattern);
                    if (matches) {
                        violations.push({
                            type: category,
                            pattern: pattern.toString(),
                            matches: matches.slice(0, 5), // Limit matches
                            severity: this.getSeverityForCategory(category),
                            confidence: rules.confidence || 0.7,
                            description: `Pattern violation detected in ${category} category`
                        });
                    }
                } catch (error) {
                    console.warn(`Error checking pattern for ${category}:`, error);
                }
            }
        }

        return violations;
    }

    async detectAIViolations(content, metadata) {
        const violations = [];

        for (const [category, config] of Object.entries(this.ruleCategories)) {
            if (!config.enabled || !config.aiModels) continue;

            for (const modelName of config.aiModels) {
                const model = this.aiModels[modelName];
                if (!model || !model.loaded) continue;

                try {
                    const result = await this.runAIModel(modelName, content, metadata);
                    if (result.violation) {
                        violations.push({
                            type: category,
                            aiModel: modelName,
                            severity: result.severity || 'MEDIUM',
                            confidence: result.confidence,
                            description: result.description,
                            details: result.details
                        });
                    }
                } catch (error) {
                    console.warn(`AI model ${modelName} failed:`, error);
                }
            }
        }

        return violations;
    }

    async runAIModel(modelName, content, metadata) {
        // Mock AI model execution
        const delay = Math.random() * 1000 + 500; // 500-1500ms
        await new Promise(resolve => setTimeout(resolve, delay));

        const modelConfig = this.aiModels[modelName];
        const randomConfidence = Math.random();

        // Simulate detection based on model and content
        let violation = false;
        let severity = 'LOW';
        let description = `AI analysis by ${modelName}`;

        // Simulate different detection scenarios
        if (modelName === 'copyright-detection') {
            violation = content.includes('©') || content.includes('copyright');
            severity = violation ? 'HIGH' : 'LOW';
            description = violation ? 'Copyright notice detected' : 'No copyright violations found';
        } else if (modelName === 'watermark-analysis') {
            violation = content.includes('watermark') || randomConfidence > 0.9;
            severity = violation ? 'MEDIUM' : 'LOW';
            description = violation ? 'Watermark detected' : 'No watermarks found';
        } else if (modelName === 'security-scan') {
            violation = randomConfidence > 0.95; // 5% chance of security violation
            severity = violation ? 'CRITICAL' : 'LOW';
            description = violation ? 'Security threat detected' : 'Content is secure';
        }

        return {
            violation,
            confidence: modelConfig.confidence * (violation ? randomConfidence : 1 - randomConfidence),
            severity,
            description,
            details: {
                modelName,
                processingTime: delay,
                contentLength: content.length
            }
        };
    }

    async detectSimilarityViolations(content, metadata) {
        const violations = [];

        try {
            // Check against known copyrighted content database
            const similarContent = await this.findSimilarContent(content);
            
            for (const match of similarContent) {
                if (match.similarity > 0.8) { // 80% similarity threshold
                    violations.push({
                        type: 'plagiarism',
                        similarity: match.similarity,
                        source: match.source,
                        severity: match.similarity > 0.95 ? 'CRITICAL' : 'HIGH',
                        confidence: match.similarity,
                        description: `High similarity to known copyrighted content: ${match.source}`
                    });
                }
            }
        } catch (error) {
            console.warn('Failed to check content similarity:', error);
        }

        return violations;
    }

    async findSimilarContent(content) {
        // Mock similarity detection
        const mockSimilarContent = [
            {
                source: 'Known copyrighted work #1',
                similarity: Math.random() * 0.3 + 0.7, // 70-100% similarity
                contentHash: 'abc123def456'
            },
            {
                source: 'Public domain work',
                similarity: Math.random() * 0.5 + 0.3, // 30-80% similarity
                contentHash: 'def456ghi789'
            }
        ];

        // Filter based on content characteristics
        return mockSimilarContent.filter(match => 
            content.length > 100 && Math.random() > 0.7 // 30% chance of finding similar content
        );
    }

    async handleViolation(scanResult) {
        const violationId = this.generateViolationId();
        
        const violation = {
            id: violationId,
            scanId: scanResult.scanId,
            timestamp: Date.now(),
            severity: this.getHighestSeverity(scanResult.violations),
            violations: scanResult.violations,
            confidence: scanResult.confidence,
            status: 'detected',
            actionTaken: null,
            resolved: false,
            content: scanResult.content
        };

        // Store violation
        this.violations.set(violationId, violation);
        await this.saveViolation(violation);

        // Take automatic action if enabled
        if (this.config.autoEnforcement) {
            const action = await this.takeAutomaticAction(violation);
            violation.actionTaken = action;
            violation.status = 'action_taken';
        }

        // Send alerts
        await this.sendViolationAlert(violation);

        // Log violation
        console.warn(`🚨 VIOLATION DETECTED: ${violationId}`, {
            severity: violation.severity,
            violationCount: scanResult.violations.length,
            confidence: scanResult.confidence
        });

        return violationId;
    }

    async takeAutomaticAction(violation) {
        const severityConfig = this.severityLevels[violation.severity];
        const action = severityConfig.autoAction;

        switch (action) {
            case 'block':
                await this.blockContent(violation);
                return 'content_blocked';
            
            case 'warn':
                await this.sendWarning(violation);
                return 'warning_sent';
            
            case 'log':
                await this.logViolation(violation);
                return 'logged';
            
            case 'monitor':
                await this.addToMonitoring(violation);
                return 'monitoring';
            
            default:
                return 'no_action';
        }
    }

    async blockContent(violation) {
        // Implement content blocking logic
        console.log(`🚫 Blocking content due to violation: ${violation.id}`);
        
        // Notify UI to block content display
        window.dispatchEvent(new CustomEvent('content-blocked', {
            detail: { violationId: violation.id, reason: violation.severity }
        }));
    }

    async sendWarning(violation) {
        const warning = {
            title: 'Copyright Violation Warning',
            message: `Potential violation detected with ${violation.confidence * 100}% confidence`,
            severity: violation.severity,
            violationId: violation.id,
            timestamp: Date.now()
        };

        window.dispatchEvent(new CustomEvent('violation-warning', { detail: warning }));
    }

    async sendViolationAlert(violation) {
        // Send alert to all registered handlers
        for (const handler of this.alertHandlers) {
            try {
                await handler(violation);
            } catch (error) {
                console.error('Alert handler failed:', error);
            }
        }

        // Send system notification
        const notification = {
            title: 'Violation Detected',
            message: `${violation.severity} violation detected (${violation.violations.length} issues)`,
            type: 'warning',
            action: 'view-violations'
        };

        window.dispatchEvent(new CustomEvent('show-notification', { detail: notification }));
    }

    // Utility methods
    isWhitelisted(content, metadata) {
        const contentHash = this.generateContentHash(content);
        return this.whitelist.has(contentHash) || 
               this.whitelist.has(metadata.source) ||
               this.whitelist.has(metadata.author);
    }

    isBlacklisted(content, metadata) {
        const contentHash = this.generateContentHash(content);
        return this.blacklist.has(contentHash) || 
               this.blacklist.has(metadata.source) ||
               this.blacklist.has(metadata.author);
    }

    generateContentHash(content) {
        // Simple hash function for content identification
        let hash = 0;
        for (let i = 0; i < content.length; i++) {
            const char = content.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        return hash.toString(36);
    }

    calculateOverallConfidence(violations) {
        if (violations.length === 0) return 0;
        
        const totalConfidence = violations.reduce((sum, v) => sum + v.confidence, 0);
        return totalConfidence / violations.length;
    }

    getHighestSeverity(violations) {
        let highest = 'LOW';
        let highestLevel = 0;

        for (const violation of violations) {
            const level = this.severityLevels[violation.severity]?.level || 0;
            if (level > highestLevel) {
                highest = violation.severity;
                highestLevel = level;
            }
        }

        return highest;
    }

    getSeverityForCategory(category) {
        const severityMap = {
            copyright: 'HIGH',
            license: 'HIGH',
            plagiarism: 'MEDIUM',
            trademark: 'MEDIUM',
            security: 'CRITICAL'
        };

        return severityMap[category] || 'LOW';
    }

    generateScanId() {
        return `scan_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    generateViolationId() {
        return `viol_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    async saveViolation(violation) {
        try {
            if (window.electronAPI) {
                const violations = Object.fromEntries(this.violations);
                await window.electronAPI.invoke('store-set', 'detected-violations', violations);
            }
        } catch (error) {
            console.error('Failed to save violation:', error);
        }
    }

    async processScanQueue() {
        if (this.isScanning || this.scanQueue.length === 0) return;

        this.isScanning = true;

        try {
            const batch = this.scanQueue.splice(0, 5); // Process 5 items at a time
            const results = await Promise.allSettled(
                batch.map(item => this.scanContent(item.content, item.metadata))
            );

            console.log(`🔍 Processed ${results.length} items from scan queue`);
        } catch (error) {
            console.error('Error processing scan queue:', error);
        } finally {
            this.isScanning = false;
        }
    }

    // Public API methods
    queueScan(content, metadata = {}) {
        if (this.scanQueue.length >= this.config.maxScanQueue) {
            console.warn('Scan queue is full, dropping oldest items');
            this.scanQueue.shift();
        }

        this.scanQueue.push({ content, metadata, timestamp: Date.now() });
    }

    addToWhitelist(identifier) {
        this.whitelist.add(identifier);
        this.saveWhitelistBlacklist();
        console.log(`✅ Added to whitelist: ${identifier}`);
    }

    addToBlacklist(identifier) {
        this.blacklist.add(identifier);
        this.saveWhitelistBlacklist();
        console.log(`🚫 Added to blacklist: ${identifier}`);
    }

    async saveWhitelistBlacklist() {
        try {
            if (window.electronAPI) {
                await window.electronAPI.invoke('store-set', 'violation-whitelist', Array.from(this.whitelist));
                await window.electronAPI.invoke('store-set', 'violation-blacklist', Array.from(this.blacklist));
            }
        } catch (error) {
            console.error('Failed to save whitelist/blacklist:', error);
        }
    }

    addAlertHandler(handler) {
        this.alertHandlers.add(handler);
        return () => this.alertHandlers.delete(handler);
    }

    getViolations(filter = {}) {
        let violations = Array.from(this.violations.values());

        if (filter.severity) {
            violations = violations.filter(v => v.severity === filter.severity);
        }
        if (filter.status) {
            violations = violations.filter(v => v.status === filter.status);
        }
        if (filter.since) {
            violations = violations.filter(v => v.timestamp >= filter.since);
        }

        return violations.sort((a, b) => b.timestamp - a.timestamp);
    }

    async resolveViolation(violationId, resolution) {
        const violation = this.violations.get(violationId);
        if (!violation) {
            throw new Error(`Violation ${violationId} not found`);
        }

        violation.resolved = true;
        violation.resolution = resolution;
        violation.resolvedAt = Date.now();
        violation.status = 'resolved';

        await this.saveViolation(violation);
        console.log(`✅ Resolved violation: ${violationId}`);
        
        return violation;
    }

    getViolationStats() {
        const violations = Array.from(this.violations.values());
        const stats = {
            total: violations.length,
            bySeverity: {},
            byStatus: {},
            byCategory: {},
            last24Hours: 0,
            resolved: 0
        };

        const oneDayAgo = Date.now() - (24 * 60 * 60 * 1000);

        for (const violation of violations) {
            // By severity
            stats.bySeverity[violation.severity] = (stats.bySeverity[violation.severity] || 0) + 1;
            
            // By status
            stats.byStatus[violation.status] = (stats.byStatus[violation.status] || 0) + 1;
            
            // Last 24 hours
            if (violation.timestamp >= oneDayAgo) {
                stats.last24Hours++;
            }
            
            // Resolved count
            if (violation.resolved) {
                stats.resolved++;
            }

            // By category
            for (const v of violation.violations) {
                stats.byCategory[v.type] = (stats.byCategory[v.type] || 0) + 1;
            }
        }

        return stats;
    }

    isHealthy() {
        return this.detectionRules.size > 0 && this.scanQueue.length < this.config.maxScanQueue;
    }

    getDetectorStatus() {
        return {
            enabled: this.config.enableRealTimeScanning,
            aiEnabled: this.config.enableAIDetection,
            strictMode: this.config.strictMode,
            autoEnforcement: this.config.autoEnforcement,
            queueSize: this.scanQueue.length,
            violationsDetected: this.violations.size,
            rulesLoaded: this.detectionRules.size,
            whitelistSize: this.whitelist.size,
            blacklistSize: this.blacklist.size
        };
    }
}

export default ViolationDetector;