/**
 * Ainflue Desktop - Legal Compliance Tools
 * 
 * Comprehensive legal compliance management system for copyright, licensing,
 * GDPR, international regulations, and automated compliance monitoring.
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This code is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

class LegalComplianceTools {
    constructor() {
        this.complianceRules = new Map();
        this.violations = new Map();
        this.auditLog = [];
        this.licenseRegistry = new Map();
        this.consentRecords = new Map();
        this.legalNotices = new Map();
        
        this.config = {
            strictMode: true,
            autoEnforcement: false,
            auditRetentionDays: 2555, // 7 years for legal compliance
            gdprCompliance: true,
            ccpaCompliance: true,
            copyrightEnforcement: true,
            internationalCompliance: true
        };

        // Legal frameworks and their requirements
        this.frameworks = {
            gdpr: {
                name: 'General Data Protection Regulation',
                region: 'EU',
                enabled: true,
                requirements: [
                    'explicit_consent',
                    'data_portability',
                    'right_to_deletion',
                    'privacy_by_design',
                    'data_breach_notification'
                ]
            },
            ccpa: {
                name: 'California Consumer Privacy Act',
                region: 'California, US',
                enabled: true,
                requirements: [
                    'right_to_know',
                    'right_to_delete',
                    'right_to_opt_out',
                    'non_discrimination'
                ]
            },
            dmca: {
                name: 'Digital Millennium Copyright Act',
                region: 'US',
                enabled: true,
                requirements: [
                    'takedown_notices',
                    'counter_notices',
                    'safe_harbor_compliance',
                    'repeat_infringer_policy'
                ]
            },
            copyrightDirective: {
                name: 'EU Copyright Directive',
                region: 'EU',
                enabled: true,
                requirements: [
                    'upload_filters',
                    'licensing_obligations',
                    'transparency_reports',
                    'complaint_mechanisms'
                ]
            }
        };

        // License types and their compliance requirements
        this.licenseTypes = {
            proprietary: {
                name: 'Proprietary License',
                requirements: ['explicit_permission', 'usage_tracking', 'violation_monitoring'],
                enforcement: 'strict'
            },
            creative_commons: {
                name: 'Creative Commons',
                subtypes: {
                    'cc-by': { attribution: true, commercial: true, derivatives: true },
                    'cc-by-sa': { attribution: true, commercial: true, derivatives: true, share_alike: true },
                    'cc-by-nc': { attribution: true, commercial: false, derivatives: true },
                    'cc-by-nd': { attribution: true, commercial: true, derivatives: false }
                },
                enforcement: 'moderate'
            },
            mit: {
                name: 'MIT License',
                requirements: ['attribution', 'license_inclusion'],
                enforcement: 'minimal'
            },
            gpl: {
                name: 'GNU General Public License',
                requirements: ['source_disclosure', 'copyleft', 'license_compatibility'],
                enforcement: 'strict'
            }
        };
    }

    async initialize() {
        console.log('⚖️ Initializing Legal Compliance Tools...');

        // Load compliance configuration
        await this.loadComplianceConfiguration();

        // Initialize legal frameworks
        await this.initializeLegalFrameworks();

        // Load license registry
        await this.loadLicenseRegistry();

        // Set up compliance monitoring
        this.setupComplianceMonitoring();

        // Initialize audit logging
        await this.initializeAuditLog();

        // Load consent records
        await this.loadConsentRecords();

        console.log('✅ Legal Compliance Tools initialized');
    }

    async loadComplianceConfiguration() {
        try {
            if (window.electronAPI) {
                const config = await window.electronAPI.invoke('store-get', 'legal-compliance-config');
                if (config) {
                    Object.assign(this.config, config);
                }
            }
        } catch (error) {
            console.warn('Failed to load compliance configuration:', error);
        }
    }

    async initializeLegalFrameworks() {
        for (const [framework, config] of Object.entries(this.frameworks)) {
            if (config.enabled) {
                await this.initializeFramework(framework, config);
            }
        }
    }

    async initializeFramework(framework, config) {
        console.log(`⚖️ Initializing ${config.name} compliance`);
        
        const complianceRules = {
            framework,
            name: config.name,
            region: config.region,
            requirements: config.requirements.map(req => ({
                requirement: req,
                status: 'pending',
                implemented: false,
                lastChecked: null
            })),
            violations: [],
            lastAudit: null
        };

        this.complianceRules.set(framework, complianceRules);
        
        // Initialize framework-specific rules
        switch (framework) {
            case 'gdpr':
                await this.initializeGDPRCompliance();
                break;
            case 'ccpa':
                await this.initializeCCPACompliance();
                break;
            case 'dmca':
                await this.initializeDMCACompliance();
                break;
            case 'copyrightDirective':
                await this.initializeCopyrightDirectiveCompliance();
                break;
        }
    }

    async initializeGDPRCompliance() {
        // GDPR-specific initialization
        const gdprRules = {
            dataProcessingBasis: ['consent', 'contract', 'legal_obligation', 'vital_interests', 'public_task', 'legitimate_interests'],
            consentRequirements: {
                explicit: true,
                informed: true,
                freely_given: true,
                specific: true,
                withdrawable: true
            },
            dataSubjectRights: [
                'right_of_access',
                'right_to_rectification',
                'right_to_erasure',
                'right_to_restrict_processing',
                'right_to_data_portability',
                'right_to_object',
                'rights_related_to_automated_decision_making'
            ],
            breachNotificationTime: 72 * 60 * 60 * 1000 // 72 hours in milliseconds
        };

        this.complianceRules.get('gdpr').specificRules = gdprRules;
    }

    async initializeCCPACompliance() {
        // CCPA-specific initialization
        const ccpaRules = {
            consumerRights: [
                'right_to_know_categories',
                'right_to_know_specific_pieces',
                'right_to_delete',
                'right_to_opt_out',
                'right_to_non_discrimination'
            ],
            disclosureRequirements: {
                categories_collected: true,
                sources: true,
                business_purposes: true,
                third_parties: true
            },
            responseTime: 45 * 24 * 60 * 60 * 1000 // 45 days in milliseconds
        };

        this.complianceRules.get('ccpa').specificRules = ccpaRules;
    }

    async initializeDMCACompliance() {
        // DMCA-specific initialization
        const dmcaRules = {
            takedownProcedure: {
                notice_requirements: [
                    'identification_of_work',
                    'identification_of_infringing_material',
                    'contact_information',
                    'good_faith_statement',
                    'accuracy_statement',
                    'authorization_statement'
                ],
                response_time: 24 * 60 * 60 * 1000 // 24 hours
            },
            counterNotice: {
                requirements: [
                    'identification_of_material',
                    'contact_information',
                    'good_faith_statement',
                    'consent_to_jurisdiction'
                ],
                processing_time: 10 * 24 * 60 * 60 * 1000 // 10-14 days
            },
            safeHarbor: {
                requirements: [
                    'designated_agent',
                    'notice_takedown_policy',
                    'repeat_infringer_policy',
                    'no_actual_knowledge'
                ]
            }
        };

        this.complianceRules.get('dmca').specificRules = dmcaRules;
    }

    async initializeCopyrightDirectiveCompliance() {
        // EU Copyright Directive compliance
        const directiveRules = {
            uploadFilters: {
                required: true,
                effectiveness_threshold: 0.95,
                false_positive_rate: 0.05
            },
            staydown: {
                required: true,
                monitoring_period: 30 * 24 * 60 * 60 * 1000 // 30 days
            },
            transparency: {
                reports_required: true,
                frequency: 'annual',
                metrics: [
                    'content_recognized',
                    'content_blocked',
                    'complaints_received',
                    'complaints_resolved'
                ]
            }
        };

        this.complianceRules.get('copyrightDirective').specificRules = directiveRules;
    }

    setupComplianceMonitoring() {
        // Set up periodic compliance checks
        this.complianceMonitor = setInterval(() => {
            this.performComplianceCheck();
        }, 60 * 60 * 1000); // Every hour

        // Set up audit log rotation
        this.auditRotation = setInterval(() => {
            this.rotateAuditLogs();
        }, 24 * 60 * 60 * 1000); // Daily
    }

    async initializeAuditLog() {
        try {
            if (window.electronAPI) {
                const existingLog = await window.electronAPI.invoke('store-get', 'legal-audit-log');
                if (existingLog) {
                    this.auditLog = existingLog;
                }
            }
        } catch (error) {
            console.warn('Failed to load audit log:', error);
        }
    }

    async loadLicenseRegistry() {
        try {
            if (window.electronAPI) {
                const registry = await window.electronAPI.invoke('store-get', 'license-registry');
                if (registry) {
                    this.licenseRegistry = new Map(Object.entries(registry));
                }
            }
        } catch (error) {
            console.warn('Failed to load license registry:', error);
        }
    }

    async loadConsentRecords() {
        try {
            if (window.electronAPI) {
                const consents = await window.electronAPI.invoke('store-get', 'consent-records');
                if (consents) {
                    this.consentRecords = new Map(Object.entries(consents));
                }
            }
        } catch (error) {
            console.warn('Failed to load consent records:', error);
        }
    }

    async recordConsent(userId, consentType, details = {}) {
        const consentId = this.generateConsentId();
        const consent = {
            id: consentId,
            userId,
            type: consentType,
            granted: true,
            timestamp: Date.now(),
            ipAddress: details.ipAddress,
            userAgent: details.userAgent,
            method: details.method || 'explicit',
            purposes: details.purposes || [],
            dataCategories: details.dataCategories || [],
            withdrawable: true,
            withdrawn: false,
            expiryDate: details.expiryDate,
            legalBasis: details.legalBasis || 'consent'
        };

        this.consentRecords.set(consentId, consent);
        await this.saveConsentRecords();

        // Log audit event
        await this.logAuditEvent('consent_granted', {
            consentId,
            userId,
            type: consentType,
            purposes: consent.purposes
        });

        console.log(`✅ Recorded consent: ${consentId} for user ${userId}`);
        return consentId;
    }

    async withdrawConsent(consentId, userId, reason = 'user_request') {
        const consent = this.consentRecords.get(consentId);
        if (!consent) {
            throw new Error(`Consent record ${consentId} not found`);
        }

        if (consent.userId !== userId) {
            throw new Error('Unauthorized consent withdrawal attempt');
        }

        consent.withdrawn = true;
        consent.withdrawnAt = Date.now();
        consent.withdrawalReason = reason;

        await this.saveConsentRecords();

        // Log audit event
        await this.logAuditEvent('consent_withdrawn', {
            consentId,
            userId,
            reason,
            originalPurposes: consent.purposes
        });

        console.log(`🚫 Withdrawn consent: ${consentId} for user ${userId}`);
        return true;
    }

    async registerLicense(contentId, licenseInfo) {
        const licenseId = this.generateLicenseId();
        const license = {
            id: licenseId,
            contentId,
            type: licenseInfo.type,
            owner: licenseInfo.owner,
            grantedTo: licenseInfo.grantedTo || 'public',
            permissions: licenseInfo.permissions || [],
            restrictions: licenseInfo.restrictions || [],
            obligations: licenseInfo.obligations || [],
            validFrom: licenseInfo.validFrom || Date.now(),
            validUntil: licenseInfo.validUntil,
            territory: licenseInfo.territory || 'worldwide',
            exclusive: licenseInfo.exclusive || false,
            transferable: licenseInfo.transferable || false,
            sublicensable: licenseInfo.sublicensable || false,
            registered: Date.now(),
            status: 'active'
        };

        this.licenseRegistry.set(licenseId, license);
        await this.saveLicenseRegistry();

        // Log audit event
        await this.logAuditEvent('license_registered', {
            licenseId,
            contentId,
            type: license.type,
            owner: license.owner
        });

        console.log(`📜 Registered license: ${licenseId} for content ${contentId}`);
        return licenseId;
    }

    async validateLicenseUsage(contentId, usage) {
        const licenses = Array.from(this.licenseRegistry.values())
            .filter(license => license.contentId === contentId && license.status === 'active');

        if (licenses.length === 0) {
            return {
                valid: false,
                reason: 'No valid license found',
                compliance: 'violation'
            };
        }

        for (const license of licenses) {
            const validation = await this.validateLicense(license, usage);
            if (validation.valid) {
                return validation;
            }
        }

        return {
            valid: false,
            reason: 'Usage not permitted under any license',
            compliance: 'violation',
            licenses: licenses.map(l => l.id)
        };
    }

    async validateLicense(license, usage) {
        const now = Date.now();
        
        // Check validity period
        if (license.validUntil && now > license.validUntil) {
            return {
                valid: false,
                reason: 'License expired',
                licenseId: license.id
            };
        }

        // Check permissions
        const requiredPermissions = usage.permissions || [];
        for (const permission of requiredPermissions) {
            if (!license.permissions.includes(permission)) {
                return {
                    valid: false,
                    reason: `Permission '${permission}' not granted`,
                    licenseId: license.id
                };
            }
        }

        // Check restrictions
        for (const restriction of license.restrictions) {
            if (this.violatesRestriction(usage, restriction)) {
                return {
                    valid: false,
                    reason: `Usage violates restriction: ${restriction}`,
                    licenseId: license.id
                };
            }
        }

        // Check obligations
        const unmetObligations = license.obligations.filter(obligation => 
            !this.meetsObligation(usage, obligation)
        );

        if (unmetObligations.length > 0) {
            return {
                valid: false,
                reason: `Unmet obligations: ${unmetObligations.join(', ')}`,
                licenseId: license.id
            };
        }

        return {
            valid: true,
            licenseId: license.id,
            compliance: 'compliant',
            obligations: license.obligations
        };
    }

    violatesRestriction(usage, restriction) {
        // Check if usage violates a specific restriction
        switch (restriction) {
            case 'no_commercial_use':
                return usage.commercial === true;
            case 'no_modifications':
                return usage.modified === true;
            case 'no_redistribution':
                return usage.redistribute === true;
            case 'attribution_required':
                return !usage.attribution;
            default:
                return false;
        }
    }

    meetsObligation(usage, obligation) {
        // Check if usage meets a specific obligation
        switch (obligation) {
            case 'attribution':
                return usage.attribution === true;
            case 'share_alike':
                return usage.shareAlike === true;
            case 'source_disclosure':
                return usage.sourceDisclosed === true;
            case 'notice_preservation':
                return usage.noticePreserved === true;
            default:
                return true;
        }
    }

    async performComplianceCheck() {
        console.log('🔍 Performing compliance check...');

        const issues = [];

        // Check each framework
        for (const [framework, rules] of this.complianceRules) {
            const frameworkIssues = await this.checkFrameworkCompliance(framework, rules);
            issues.push(...frameworkIssues);
        }

        // Check license compliance
        const licenseIssues = await this.checkLicenseCompliance();
        issues.push(...licenseIssues);

        // Check consent validity
        const consentIssues = await this.checkConsentCompliance();
        issues.push(...consentIssues);

        if (issues.length > 0) {
            console.warn(`⚠️ Found ${issues.length} compliance issues`);
            await this.handleComplianceIssues(issues);
        } else {
            console.log('✅ No compliance issues found');
        }

        // Log compliance check
        await this.logAuditEvent('compliance_check', {
            timestamp: Date.now(),
            issuesFound: issues.length,
            frameworks: Array.from(this.complianceRules.keys()),
            status: issues.length === 0 ? 'compliant' : 'issues_found'
        });
    }

    async checkFrameworkCompliance(framework, rules) {
        const issues = [];

        switch (framework) {
            case 'gdpr':
                const gdprIssues = await this.checkGDPRCompliance(rules);
                issues.push(...gdprIssues);
                break;
            case 'ccpa':
                const ccpaIssues = await this.checkCCPACompliance(rules);
                issues.push(...ccpaIssues);
                break;
            case 'dmca':
                const dmcaIssues = await this.checkDMCACompliance(rules);
                issues.push(...dmcaIssues);
                break;
        }

        return issues;
    }

    async checkGDPRCompliance(rules) {
        const issues = [];

        // Check expired consents
        const expiredConsents = Array.from(this.consentRecords.values())
            .filter(consent => consent.expiryDate && Date.now() > consent.expiryDate);

        for (const consent of expiredConsents) {
            issues.push({
                type: 'expired_consent',
                severity: 'high',
                description: `Consent ${consent.id} has expired`,
                framework: 'gdpr',
                requirement: 'valid_consent'
            });
        }

        // Check data breach notification requirements
        // (This would integrate with actual breach detection)

        return issues;
    }

    async checkCCPACompliance(rules) {
        const issues = [];

        // Check consumer rights implementation
        // (This would verify that all required rights are implemented)

        return issues;
    }

    async checkDMCACompliance(rules) {
        const issues = [];

        // Check takedown notice response times
        // (This would integrate with takedown notice processing)

        return issues;
    }

    async checkLicenseCompliance() {
        const issues = [];

        // Check for expired licenses
        const now = Date.now();
        for (const license of this.licenseRegistry.values()) {
            if (license.validUntil && now > license.validUntil && license.status === 'active') {
                issues.push({
                    type: 'expired_license',
                    severity: 'medium',
                    description: `License ${license.id} has expired`,
                    licenseId: license.id,
                    contentId: license.contentId
                });
            }
        }

        return issues;
    }

    async checkConsentCompliance() {
        const issues = [];

        // Check for consents that need renewal
        const renewalThreshold = 365 * 24 * 60 * 60 * 1000; // 1 year
        const now = Date.now();

        for (const consent of this.consentRecords.values()) {
            if (!consent.withdrawn && (now - consent.timestamp) > renewalThreshold) {
                issues.push({
                    type: 'consent_renewal_required',
                    severity: 'medium',
                    description: `Consent ${consent.id} requires renewal`,
                    consentId: consent.id,
                    userId: consent.userId
                });
            }
        }

        return issues;
    }

    async handleComplianceIssues(issues) {
        for (const issue of issues) {
            // Log the issue
            await this.logAuditEvent('compliance_issue', issue);

            // Take automatic action if enabled
            if (this.config.autoEnforcement) {
                await this.takeComplianceAction(issue);
            }
        }

        // Send notification
        const notification = {
            title: 'Compliance Issues Detected',
            message: `Found ${issues.length} compliance issues requiring attention`,
            type: 'warning',
            action: 'view-compliance'
        };

        window.dispatchEvent(new CustomEvent('show-notification', { detail: notification }));
    }

    async takeComplianceAction(issue) {
        switch (issue.type) {
            case 'expired_consent':
                await this.handleExpiredConsent(issue);
                break;
            case 'expired_license':
                await this.handleExpiredLicense(issue);
                break;
            case 'consent_renewal_required':
                await this.handleConsentRenewal(issue);
                break;
        }
    }

    async logAuditEvent(eventType, details) {
        const auditEntry = {
            id: this.generateAuditId(),
            timestamp: Date.now(),
            type: eventType,
            details,
            source: 'legal_compliance_tools',
            userId: await this.getCurrentUserId(),
            sessionId: await this.getCurrentSessionId()
        };

        this.auditLog.push(auditEntry);
        await this.saveAuditLog();

        console.debug(`📋 Audit logged: ${eventType}`, details);
    }

    async rotateAuditLogs() {
        const retentionTime = this.config.auditRetentionDays * 24 * 60 * 60 * 1000;
        const cutoffTime = Date.now() - retentionTime;

        const originalLength = this.auditLog.length;
        this.auditLog = this.auditLog.filter(entry => entry.timestamp >= cutoffTime);

        if (this.auditLog.length < originalLength) {
            await this.saveAuditLog();
            console.log(`🗂️ Rotated audit log: removed ${originalLength - this.auditLog.length} old entries`);
        }
    }

    // Helper methods
    generateConsentId() {
        return `consent_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    generateLicenseId() {
        return `license_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    generateAuditId() {
        return `audit_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    async getCurrentUserId() {
        try {
            if (window.electronAPI) {
                return await window.electronAPI.invoke('store-get', 'current-user-id');
            }
        } catch (error) {
            return 'unknown';
        }
    }

    async getCurrentSessionId() {
        try {
            if (window.electronAPI) {
                return await window.electronAPI.invoke('store-get', 'current-session-id');
            }
        } catch (error) {
            return 'unknown';
        }
    }

    async saveConsentRecords() {
        try {
            if (window.electronAPI) {
                const consents = Object.fromEntries(this.consentRecords);
                await window.electronAPI.invoke('store-set', 'consent-records', consents);
            }
        } catch (error) {
            console.error('Failed to save consent records:', error);
        }
    }

    async saveLicenseRegistry() {
        try {
            if (window.electronAPI) {
                const registry = Object.fromEntries(this.licenseRegistry);
                await window.electronAPI.invoke('store-set', 'license-registry', registry);
            }
        } catch (error) {
            console.error('Failed to save license registry:', error);
        }
    }

    async saveAuditLog() {
        try {
            if (window.electronAPI) {
                await window.electronAPI.invoke('store-set', 'legal-audit-log', this.auditLog);
            }
        } catch (error) {
            console.error('Failed to save audit log:', error);
        }
    }

    // Public API methods
    getComplianceStatus() {
        const status = {
            frameworks: {},
            licenses: {
                total: this.licenseRegistry.size,
                active: 0,
                expired: 0
            },
            consents: {
                total: this.consentRecords.size,
                active: 0,
                withdrawn: 0,
                expired: 0
            },
            audit: {
                entries: this.auditLog.length,
                oldestEntry: this.auditLog.length > 0 ? Math.min(...this.auditLog.map(e => e.timestamp)) : null
            }
        };

        // Framework status
        for (const [framework, rules] of this.complianceRules) {
            status.frameworks[framework] = {
                enabled: rules.enabled !== false,
                requirements: rules.requirements.length,
                violations: rules.violations.length,
                lastAudit: rules.lastAudit
            };
        }

        // License statistics
        const now = Date.now();
        for (const license of this.licenseRegistry.values()) {
            if (license.status === 'active') {
                if (!license.validUntil || license.validUntil > now) {
                    status.licenses.active++;
                } else {
                    status.licenses.expired++;
                }
            }
        }

        // Consent statistics
        for (const consent of this.consentRecords.values()) {
            if (consent.withdrawn) {
                status.consents.withdrawn++;
            } else if (consent.expiryDate && consent.expiryDate < now) {
                status.consents.expired++;
            } else {
                status.consents.active++;
            }
        }

        return status;
    }

    getAuditLog(filter = {}) {
        let log = [...this.auditLog];

        if (filter.type) {
            log = log.filter(entry => entry.type === filter.type);
        }
        if (filter.since) {
            log = log.filter(entry => entry.timestamp >= filter.since);
        }
        if (filter.userId) {
            log = log.filter(entry => entry.userId === filter.userId);
        }

        return log.sort((a, b) => b.timestamp - a.timestamp);
    }

    getLicenses(filter = {}) {
        let licenses = Array.from(this.licenseRegistry.values());

        if (filter.contentId) {
            licenses = licenses.filter(license => license.contentId === filter.contentId);
        }
        if (filter.type) {
            licenses = licenses.filter(license => license.type === filter.type);
        }
        if (filter.status) {
            licenses = licenses.filter(license => license.status === filter.status);
        }

        return licenses.sort((a, b) => b.registered - a.registered);
    }

    getConsents(filter = {}) {
        let consents = Array.from(this.consentRecords.values());

        if (filter.userId) {
            consents = consents.filter(consent => consent.userId === filter.userId);
        }
        if (filter.type) {
            consents = consents.filter(consent => consent.type === filter.type);
        }
        if (filter.withdrawn !== undefined) {
            consents = consents.filter(consent => consent.withdrawn === filter.withdrawn);
        }

        return consents.sort((a, b) => b.timestamp - a.timestamp);
    }

    isHealthy() {
        return this.complianceRules.size > 0 && this.auditLog.length < 10000;
    }
}

export default LegalComplianceTools;