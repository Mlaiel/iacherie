/**
 * Ainflue Desktop - License Manager
 * 
 * Advanced license management system for content and software licensing
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * @license Proprietary - Unauthorized use prohibited
 */

const crypto = require('crypto');
const fs = require('fs').promises;
const path = require('path');

class LicenseManager {
    constructor(options = {}) {
        this.licenseDirectory = options.licenseDirectory || path.join(__dirname, '..', 'licenses');
        this.masterKey = options.masterKey || this.generateMasterKey();
        
        this.activeLicenses = new Map();
        this.licenseTemplates = new Map();
        this.validationCache = new Map();
        this.auditLog = [];
        
        this.initializeLicenseManager();
    }

    /**
     * Initialize license management system
     */
    async initializeLicenseManager() {
        try {
            await fs.mkdir(this.licenseDirectory, { recursive: true });
            await this.loadLicenseTemplates();
            await this.loadExistingLicenses();
            
            console.log('📄 License Manager initialized');
        } catch (error) {
            console.error('Failed to initialize License Manager:', error);
            throw new Error('License Manager initialization failed');
        }
    }

    /**
     * Load predefined license templates
     */
    async loadLicenseTemplates() {
        // Creative Commons Licenses
        this.licenseTemplates.set('cc-by', {
            name: 'Creative Commons Attribution 4.0',
            shortName: 'CC BY 4.0',
            permissions: ['commercial-use', 'modification', 'distribution', 'private-use'],
            conditions: ['include-copyright', 'include-license', 'document-changes'],
            limitations: ['trademark-use', 'warranty', 'liability'],
            url: 'https://creativecommons.org/licenses/by/4.0/',
            description: 'Permits almost any use subject to providing credit and license notice.'
        });

        this.licenseTemplates.set('cc-by-sa', {
            name: 'Creative Commons Attribution-ShareAlike 4.0',
            shortName: 'CC BY-SA 4.0',
            permissions: ['commercial-use', 'modification', 'distribution', 'private-use'],
            conditions: ['include-copyright', 'include-license', 'document-changes', 'same-license'],
            limitations: ['trademark-use', 'warranty', 'liability'],
            url: 'https://creativecommons.org/licenses/by-sa/4.0/',
            description: 'Similar to CC BY but requires derivatives be distributed under same license.'
        });

        this.licenseTemplates.set('cc-by-nc', {
            name: 'Creative Commons Attribution-NonCommercial 4.0',
            shortName: 'CC BY-NC 4.0',
            permissions: ['modification', 'distribution', 'private-use'],
            conditions: ['include-copyright', 'include-license', 'document-changes'],
            limitations: ['commercial-use', 'trademark-use', 'warranty', 'liability'],
            url: 'https://creativecommons.org/licenses/by-nc/4.0/',
            description: 'Allows others to download, share and build upon your work non-commercially.'
        });

        // Proprietary Licenses
        this.licenseTemplates.set('proprietary', {
            name: 'All Rights Reserved',
            shortName: 'Proprietary',
            permissions: [],
            conditions: ['permission-required'],
            limitations: ['commercial-use', 'modification', 'distribution', 'private-use'],
            description: 'Traditional copyright with no permissions granted.'
        });

        this.licenseTemplates.set('ainflue-standard', {
            name: 'Ainflue Standard License',
            shortName: 'Ainflue Std',
            permissions: ['private-use', 'modification'],
            conditions: ['include-copyright', 'include-license', 'no-redistribution'],
            limitations: ['commercial-use', 'distribution', 'warranty', 'liability'],
            description: 'Standard Ainflue platform license for content creators.'
        });

        this.licenseTemplates.set('ainflue-commercial', {
            name: 'Ainflue Commercial License',
            shortName: 'Ainflue Com',
            permissions: ['commercial-use', 'modification', 'distribution', 'private-use'],
            conditions: ['include-copyright', 'payment-required'],
            limitations: ['warranty', 'liability'],
            description: 'Commercial license for business use of Ainflue content.'
        });
    }

    /**
     * Create new license
     */
    async createLicense(templateId, options = {}) {
        try {
            const template = this.licenseTemplates.get(templateId);
            if (!template) {
                throw new Error(`License template '${templateId}' not found`);
            }

            const licenseId = this.generateLicenseId();
            const license = {
                id: licenseId,
                template: templateId,
                templateData: template,
                licensor: options.licensor || {
                    name: 'Fahed Mlaiel',
                    email: 'mlaiel@live.de',
                    organization: 'Ainflue'
                },
                licensee: options.licensee || null,
                subject: options.subject || 'Digital Content',
                terms: {
                    ...template,
                    customTerms: options.customTerms || {},
                    duration: options.duration || 'perpetual',
                    territory: options.territory || 'worldwide',
                    royalty: options.royalty || 0,
                    exclusivity: options.exclusivity || 'non-exclusive'
                },
                metadata: {
                    createdAt: new Date().toISOString(),
                    createdBy: options.createdBy || 'system',
                    version: options.version || '1.0.0',
                    status: 'draft'
                },
                signature: null,
                validation: {
                    isValid: false,
                    validatedAt: null,
                    validatedBy: null
                }
            };

            // Generate license text
            license.fullText = this.generateLicenseText(license);
            
            // Create digital signature
            license.signature = await this.signLicense(license);
            
            // Mark as valid
            license.validation.isValid = true;
            license.validation.validatedAt = new Date().toISOString();
            license.validation.validatedBy = 'system';
            license.metadata.status = 'active';

            // Store license
            this.activeLicenses.set(licenseId, license);
            await this.saveLicense(license);

            // Log creation
            this.logLicenseEvent('license_created', {
                licenseId,
                templateId,
                licensor: license.licensor.name,
                licensee: license.licensee?.name || 'unspecified'
            });

            return {
                success: true,
                licenseId,
                license: this.sanitizeLicenseForExport(license)
            };
        } catch (error) {
            console.error('License creation failed:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Validate license
     */
    async validateLicense(licenseId, context = {}) {
        try {
            // Check cache first
            const cacheKey = `${licenseId}_${JSON.stringify(context)}`;
            if (this.validationCache.has(cacheKey)) {
                return this.validationCache.get(cacheKey);
            }

            const license = this.activeLicenses.get(licenseId);
            if (!license) {
                return {
                    valid: false,
                    reason: 'License not found',
                    licenseId
                };
            }

            const validation = {
                valid: true,
                licenseId,
                license: license.templateData,
                permissions: [],
                violations: [],
                warnings: []
            };

            // Check license signature
            const signatureValid = await this.verifyLicenseSignature(license);
            if (!signatureValid) {
                validation.valid = false;
                validation.violations.push('Invalid license signature');
            }

            // Check expiration
            if (license.terms.duration !== 'perpetual') {
                const expirationDate = this.calculateExpirationDate(license);
                if (new Date() > expirationDate) {
                    validation.valid = false;
                    validation.violations.push('License has expired');
                }
            }

            // Check usage context
            const contextValidation = this.validateUsageContext(license, context);
            validation.permissions = contextValidation.permissions;
            validation.violations.push(...contextValidation.violations);
            validation.warnings.push(...contextValidation.warnings);

            // Overall validity
            validation.valid = validation.valid && validation.violations.length === 0;

            // Cache result
            this.validationCache.set(cacheKey, validation);

            // Log validation
            this.logLicenseEvent('license_validated', {
                licenseId,
                valid: validation.valid,
                context: context.type || 'unknown'
            });

            return validation;
        } catch (error) {
            console.error('License validation failed:', error);
            return {
                valid: false,
                reason: 'Validation process failed',
                error: error.message
            };
        }
    }

    /**
     * Update license terms
     */
    async updateLicense(licenseId, updates = {}) {
        try {
            const license = this.activeLicenses.get(licenseId);
            if (!license) {
                throw new Error('License not found');
            }

            // Create new version
            const newVersion = this.incrementVersion(license.metadata.version);
            const updatedLicense = {
                ...license,
                terms: {
                    ...license.terms,
                    ...updates.terms
                },
                metadata: {
                    ...license.metadata,
                    version: newVersion,
                    updatedAt: new Date().toISOString(),
                    updatedBy: updates.updatedBy || 'system',
                    updateReason: updates.reason || 'Manual update'
                }
            };

            // Regenerate license text and signature
            updatedLicense.fullText = this.generateLicenseText(updatedLicense);
            updatedLicense.signature = await this.signLicense(updatedLicense);

            // Update storage
            this.activeLicenses.set(licenseId, updatedLicense);
            await this.saveLicense(updatedLicense);

            // Clear validation cache
            this.clearValidationCache(licenseId);

            // Log update
            this.logLicenseEvent('license_updated', {
                licenseId,
                oldVersion: license.metadata.version,
                newVersion,
                changes: Object.keys(updates.terms || {})
            });

            return {
                success: true,
                license: this.sanitizeLicenseForExport(updatedLicense)
            };
        } catch (error) {
            console.error('License update failed:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Revoke license
     */
    async revokeLicense(licenseId, reason = 'Manual revocation') {
        try {
            const license = this.activeLicenses.get(licenseId);
            if (!license) {
                throw new Error('License not found');
            }

            // Mark as revoked
            license.metadata.status = 'revoked';
            license.metadata.revokedAt = new Date().toISOString();
            license.metadata.revocationReason = reason;

            // Update storage
            await this.saveLicense(license);

            // Clear validation cache
            this.clearValidationCache(licenseId);

            // Log revocation
            this.logLicenseEvent('license_revoked', {
                licenseId,
                reason
            });

            return {
                success: true,
                message: 'License revoked successfully'
            };
        } catch (error) {
            console.error('License revocation failed:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Generate license compliance report
     */
    generateComplianceReport(options = {}) {
        const licenses = Array.from(this.activeLicenses.values());
        const report = {
            generatedAt: new Date().toISOString(),
            summary: {
                totalLicenses: licenses.length,
                activeLicenses: licenses.filter(l => l.metadata.status === 'active').length,
                expiredLicenses: licenses.filter(l => this.isExpired(l)).length,
                revokedLicenses: licenses.filter(l => l.metadata.status === 'revoked').length
            },
            licensesByTemplate: this.groupLicensesByTemplate(licenses),
            expirationWarnings: this.getExpirationWarnings(licenses),
            complianceIssues: this.identifyComplianceIssues(licenses),
            auditTrail: this.auditLog.slice(-100), // Last 100 events
            recommendations: this.generateComplianceRecommendations(licenses)
        };

        return report;
    }

    /**
     * Export license in various formats
     */
    async exportLicense(licenseId, format = 'json') {
        try {
            const license = this.activeLicenses.get(licenseId);
            if (!license) {
                throw new Error('License not found');
            }

            switch (format.toLowerCase()) {
                case 'json':
                    return {
                        format: 'json',
                        content: JSON.stringify(this.sanitizeLicenseForExport(license), null, 2)
                    };
                
                case 'text':
                    return {
                        format: 'text',
                        content: license.fullText
                    };
                
                case 'html':
                    return {
                        format: 'html',
                        content: this.generateHTMLLicense(license)
                    };
                
                case 'pdf':
                    return {
                        format: 'pdf',
                        content: await this.generatePDFLicense(license)
                    };
                
                default:
                    throw new Error(`Unsupported export format: ${format}`);
            }
        } catch (error) {
            console.error('License export failed:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Helper methods
     */
    generateLicenseText(license) {
        const template = license.templateData;
        const terms = license.terms;
        
        let text = `${template.name}\n\n`;
        text += `Subject: ${license.subject}\n`;
        text += `Licensor: ${license.licensor.name}\n`;
        
        if (license.licensee) {
            text += `Licensee: ${license.licensee.name}\n`;
        }
        
        text += `\nDescription: ${template.description}\n\n`;
        
        text += `PERMISSIONS:\n`;
        template.permissions.forEach(permission => {
            text += `- ${this.formatPermission(permission)}\n`;
        });
        
        text += `\nCONDITIONS:\n`;
        template.conditions.forEach(condition => {
            text += `- ${this.formatCondition(condition)}\n`;
        });
        
        text += `\nLIMITATIONS:\n`;
        template.limitations.forEach(limitation => {
            text += `- ${this.formatLimitation(limitation)}\n`;
        });
        
        text += `\nTERMS:\n`;
        text += `Duration: ${terms.duration}\n`;
        text += `Territory: ${terms.territory}\n`;
        text += `Exclusivity: ${terms.exclusivity}\n`;
        
        if (terms.royalty > 0) {
            text += `Royalty: ${terms.royalty}%\n`;
        }
        
        text += `\nThis license was generated on ${license.metadata.createdAt}\n`;
        text += `License ID: ${license.id}\n`;
        text += `Version: ${license.metadata.version}\n`;
        
        return text;
    }

    async signLicense(license) {
        const licenseString = JSON.stringify({
            id: license.id,
            terms: license.terms,
            metadata: license.metadata
        });
        
        const signature = crypto.createHmac('sha256', this.masterKey)
            .update(licenseString)
            .digest('hex');
        
        return {
            signature,
            algorithm: 'HMAC-SHA256',
            signedAt: new Date().toISOString(),
            signer: 'Ainflue License Manager'
        };
    }

    async verifyLicenseSignature(license) {
        if (!license.signature) return false;
        
        const licenseString = JSON.stringify({
            id: license.id,
            terms: license.terms,
            metadata: license.metadata
        });
        
        const expectedSignature = crypto.createHmac('sha256', this.masterKey)
            .update(licenseString)
            .digest('hex');
        
        return license.signature.signature === expectedSignature;
    }

    validateUsageContext(license, context) {
        const validation = {
            permissions: [],
            violations: [],
            warnings: []
        };

        const template = license.templateData;

        // Check if usage type is permitted
        if (context.type === 'commercial' && !template.permissions.includes('commercial-use')) {
            validation.violations.push('Commercial use not permitted under this license');
        } else if (context.type === 'commercial' && template.permissions.includes('commercial-use')) {
            validation.permissions.push('Commercial use permitted');
        }

        // Check modification permissions
        if (context.modified && !template.permissions.includes('modification')) {
            validation.violations.push('Modification not permitted under this license');
        } else if (context.modified && template.permissions.includes('modification')) {
            validation.permissions.push('Modification permitted');
        }

        // Check distribution permissions
        if (context.distribute && !template.permissions.includes('distribution')) {
            validation.violations.push('Distribution not permitted under this license');
        } else if (context.distribute && template.permissions.includes('distribution')) {
            validation.permissions.push('Distribution permitted');
        }

        // Check attribution requirements
        if (template.conditions.includes('include-copyright') && !context.attribution) {
            validation.warnings.push('Attribution required but not provided');
        }

        return validation;
    }

    calculateExpirationDate(license) {
        const createdAt = new Date(license.metadata.createdAt);
        const duration = license.terms.duration;
        
        if (duration === 'perpetual') {
            return null;
        }
        
        if (duration.includes('year')) {
            const years = parseInt(duration);
            createdAt.setFullYear(createdAt.getFullYear() + years);
        } else if (duration.includes('month')) {
            const months = parseInt(duration);
            createdAt.setMonth(createdAt.getMonth() + months);
        } else if (duration.includes('day')) {
            const days = parseInt(duration);
            createdAt.setDate(createdAt.getDate() + days);
        }
        
        return createdAt;
    }

    formatPermission(permission) {
        const formatMap = {
            'commercial-use': 'Commercial use allowed',
            'modification': 'Modification allowed',
            'distribution': 'Distribution allowed',
            'private-use': 'Private use allowed'
        };
        return formatMap[permission] || permission;
    }

    formatCondition(condition) {
        const formatMap = {
            'include-copyright': 'Must include copyright notice',
            'include-license': 'Must include license notice',
            'document-changes': 'Must document changes made',
            'same-license': 'Must use same license for derivatives',
            'permission-required': 'Permission required before use'
        };
        return formatMap[condition] || condition;
    }

    formatLimitation(limitation) {
        const formatMap = {
            'commercial-use': 'No commercial use',
            'modification': 'No modification allowed',
            'distribution': 'No distribution allowed',
            'warranty': 'No warranty provided',
            'liability': 'Limited liability',
            'trademark-use': 'No trademark rights'
        };
        return formatMap[limitation] || limitation;
    }

    generateLicenseId() {
        return `LIC-${Date.now()}-${crypto.randomBytes(4).toString('hex').toUpperCase()}`;
    }

    generateMasterKey() {
        return crypto.randomBytes(32).toString('hex');
    }

    incrementVersion(version) {
        const parts = version.split('.');
        parts[2] = (parseInt(parts[2]) + 1).toString();
        return parts.join('.');
    }

    sanitizeLicenseForExport(license) {
        // Remove sensitive internal data
        const exported = { ...license };
        delete exported.signature?.algorithm;
        delete exported.validation?.validatedBy;
        return exported;
    }

    async saveLicense(license) {
        const filePath = path.join(this.licenseDirectory, `${license.id}.json`);
        await fs.writeFile(filePath, JSON.stringify(license, null, 2));
    }

    async loadExistingLicenses() {
        try {
            const files = await fs.readdir(this.licenseDirectory);
            const licenseFiles = files.filter(f => f.endsWith('.json'));
            
            for (const file of licenseFiles) {
                try {
                    const content = await fs.readFile(path.join(this.licenseDirectory, file), 'utf8');
                    const license = JSON.parse(content);
                    this.activeLicenses.set(license.id, license);
                } catch (error) {
                    console.warn(`Failed to load license file ${file}:`, error);
                }
            }
        } catch (error) {
            // Directory doesn't exist yet, that's fine
        }
    }

    logLicenseEvent(event, details) {
        const logEntry = {
            timestamp: new Date().toISOString(),
            event,
            details,
            source: 'LicenseManager'
        };
        
        this.auditLog.push(logEntry);
        
        // Keep log size manageable
        if (this.auditLog.length > 1000) {
            this.auditLog = this.auditLog.slice(-500);
        }
    }

    clearValidationCache(licenseId) {
        const keysToDelete = [];
        for (const key of this.validationCache.keys()) {
            if (key.startsWith(licenseId)) {
                keysToDelete.push(key);
            }
        }
        keysToDelete.forEach(key => this.validationCache.delete(key));
    }

    // Additional helper methods for reporting
    groupLicensesByTemplate(licenses) {
        const groups = {};
        for (const license of licenses) {
            const template = license.template;
            groups[template] = (groups[template] || 0) + 1;
        }
        return groups;
    }

    getExpirationWarnings(licenses) {
        const warnings = [];
        const thirtyDaysFromNow = new Date();
        thirtyDaysFromNow.setDate(thirtyDaysFromNow.getDate() + 30);
        
        for (const license of licenses) {
            const expiration = this.calculateExpirationDate(license);
            if (expiration && expiration < thirtyDaysFromNow) {
                warnings.push({
                    licenseId: license.id,
                    expiresAt: expiration.toISOString(),
                    daysRemaining: Math.ceil((expiration - new Date()) / (1000 * 60 * 60 * 24))
                });
            }
        }
        
        return warnings;
    }

    identifyComplianceIssues(licenses) {
        const issues = [];
        
        for (const license of licenses) {
            // Check for missing signatures
            if (!license.signature) {
                issues.push({
                    licenseId: license.id,
                    issue: 'Missing digital signature',
                    severity: 'high'
                });
            }
            
            // Check for invalid status
            if (!['active', 'draft', 'revoked'].includes(license.metadata.status)) {
                issues.push({
                    licenseId: license.id,
                    issue: 'Invalid license status',
                    severity: 'medium'
                });
            }
        }
        
        return issues;
    }

    generateComplianceRecommendations(licenses) {
        const recommendations = [];
        
        const expiringCount = this.getExpirationWarnings(licenses).length;
        if (expiringCount > 0) {
            recommendations.push({
                type: 'renewal',
                message: `${expiringCount} license(s) expiring within 30 days`,
                action: 'Review and renew expiring licenses'
            });
        }
        
        const issuesCount = this.identifyComplianceIssues(licenses).length;
        if (issuesCount > 0) {
            recommendations.push({
                type: 'compliance',
                message: `${issuesCount} compliance issue(s) found`,
                action: 'Address compliance issues immediately'
            });
        }
        
        return recommendations;
    }

    isExpired(license) {
        const expiration = this.calculateExpirationDate(license);
        return expiration && new Date() > expiration;
    }

    generateHTMLLicense(license) {
        return `
            <!DOCTYPE html>
            <html>
            <head>
                <title>License: ${license.id}</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                    .header { border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 20px; }
                    .section { margin-bottom: 20px; }
                    .terms { background: #f5f5f5; padding: 15px; border-radius: 5px; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>${license.templateData.name}</h1>
                    <p>License ID: ${license.id}</p>
                    <p>Version: ${license.metadata.version}</p>
                </div>
                <div class="section">
                    <h2>License Details</h2>
                    <p><strong>Subject:</strong> ${license.subject}</p>
                    <p><strong>Licensor:</strong> ${license.licensor.name}</p>
                    ${license.licensee ? `<p><strong>Licensee:</strong> ${license.licensee.name}</p>` : ''}
                </div>
                <div class="terms">
                    <pre>${license.fullText}</pre>
                </div>
            </body>
            </html>
        `;
    }

    async generatePDFLicense(license) {
        // Simplified PDF generation - in production would use proper PDF library
        return Buffer.from(this.generateHTMLLicense(license));
    }

    /**
     * Get license manager statistics
     */
    getLicenseStats() {
        const licenses = Array.from(this.activeLicenses.values());
        
        return {
            totalLicenses: licenses.length,
            licenseTemplates: this.licenseTemplates.size,
            auditLogEntries: this.auditLog.length,
            cacheEntries: this.validationCache.size,
            licensesByStatus: {
                active: licenses.filter(l => l.metadata.status === 'active').length,
                draft: licenses.filter(l => l.metadata.status === 'draft').length,
                revoked: licenses.filter(l => l.metadata.status === 'revoked').length
            },
            licensesByTemplate: this.groupLicensesByTemplate(licenses)
        };
    }
}

module.exports = LicenseManager;

/**
 * Copyright Notice:
 * This code is the exclusive property of Fahed Mlaiel.
 * Unauthorized use, copying, or distribution is strictly prohibited.
 * Contact: mlaiel@live.de
 */