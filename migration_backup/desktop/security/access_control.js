/**
 * Ainflue Desktop - Access Control System
 * 
 * Role-based access control and permission management for desktop application
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * @license Proprietary - Unauthorized use prohibited
 */

const crypto = require('crypto');
const fs = require('fs').promises;
const path = require('path');

class AccessControlManager {
    constructor(options = {}) {
        this.sessionTimeout = options.sessionTimeout || 24 * 60 * 60 * 1000; // 24 hours
        this.maxFailedAttempts = options.maxFailedAttempts || 3;
        this.lockoutDuration = options.lockoutDuration || 15 * 60 * 1000; // 15 minutes
        
        this.sessions = new Map();
        this.failedAttempts = new Map();
        this.permissions = new Map();
        this.roles = new Map();
        this.users = new Map();
        
        this.initializeDefaultRoles();
        this.initializeDefaultPermissions();
    }

    /**
     * Initialize default roles and permissions
     */
    initializeDefaultRoles() {
        // Define role hierarchy
        this.roles.set('admin', {
            name: 'Administrator',
            level: 100,
            permissions: ['*'], // All permissions
            description: 'Full system access'
        });

        this.roles.set('creator', {
            name: 'Content Creator',
            level: 80,
            permissions: [
                'content.create', 'content.edit', 'content.delete', 'content.publish',
                'project.create', 'project.edit', 'project.delete',
                'ai.process', 'ai.analyze',
                'export.all', 'collaboration.manage'
            ],
            description: 'Content creation and management'
        });

        this.roles.set('editor', {
            name: 'Content Editor',
            level: 60,
            permissions: [
                'content.edit', 'content.view',
                'project.edit', 'project.view',
                'ai.process', 'export.basic'
            ],
            description: 'Content editing capabilities'
        });

        this.roles.set('viewer', {
            name: 'Content Viewer',
            level: 40,
            permissions: [
                'content.view', 'project.view', 'export.basic'
            ],
            description: 'Read-only access'
        });

        this.roles.set('guest', {
            name: 'Guest User',
            level: 20,
            permissions: ['content.view'],
            description: 'Limited viewing access'
        });
    }

    /**
     * Initialize permission system
     */
    initializeDefaultPermissions() {
        const permissionCategories = {
            content: [
                'create', 'edit', 'delete', 'view', 'publish', 'archive'
            ],
            project: [
                'create', 'edit', 'delete', 'view', 'share', 'export'
            ],
            ai: [
                'process', 'analyze', 'optimize', 'enhance', 'train'
            ],
            collaboration: [
                'invite', 'manage', 'moderate', 'share'
            ],
            export: [
                'basic', 'advanced', 'all', 'distribute'
            ],
            security: [
                'encrypt', 'decrypt', 'sign', 'verify', 'audit'
            ],
            admin: [
                'users', 'roles', 'permissions', 'system', 'settings'
            ]
        };

        for (const [category, actions] of Object.entries(permissionCategories)) {
            for (const action of actions) {
                const permission = `${category}.${action}`;
                this.permissions.set(permission, {
                    category,
                    action,
                    description: `${action} access for ${category}`
                });
            }
        }
    }

    /**
     * Create user session with authentication
     */
    async createSession(userId, credentials = {}) {
        try {
            // Check if user is locked out
            if (this.isUserLockedOut(userId)) {
                throw new Error('User account is temporarily locked due to failed login attempts');
            }

            // Validate credentials (simplified for desktop app)
            const user = await this.validateUserCredentials(userId, credentials);
            if (!user) {
                this.recordFailedAttempt(userId);
                throw new Error('Invalid credentials');
            }

            // Clear failed attempts on successful login
            this.failedAttempts.delete(userId);

            // Create session
            const sessionId = this.generateSessionId();
            const session = {
                id: sessionId,
                userId: user.id,
                role: user.role,
                permissions: this.getUserPermissions(user.role),
                createdAt: Date.now(),
                lastActivity: Date.now(),
                expiresAt: Date.now() + this.sessionTimeout,
                ipAddress: credentials.ipAddress || 'desktop',
                userAgent: credentials.userAgent || 'Ainflue Desktop'
            };

            this.sessions.set(sessionId, session);
            
            // Log successful login
            this.logSecurityEvent('LOGIN_SUCCESS', {
                userId: user.id,
                sessionId,
                timestamp: new Date().toISOString()
            });

            return {
                sessionId,
                expiresAt: session.expiresAt,
                permissions: session.permissions,
                role: session.role
            };
        } catch (error) {
            this.logSecurityEvent('LOGIN_FAILED', {
                userId,
                reason: error.message,
                timestamp: new Date().toISOString()
            });
            throw error;
        }
    }

    /**
     * Validate user session
     */
    validateSession(sessionId) {
        const session = this.sessions.get(sessionId);
        
        if (!session) {
            return { valid: false, reason: 'Session not found' };
        }

        if (Date.now() > session.expiresAt) {
            this.sessions.delete(sessionId);
            return { valid: false, reason: 'Session expired' };
        }

        // Update last activity
        session.lastActivity = Date.now();
        this.sessions.set(sessionId, session);

        return {
            valid: true,
            session: {
                userId: session.userId,
                role: session.role,
                permissions: session.permissions,
                lastActivity: session.lastActivity
            }
        };
    }

    /**
     * Check if user has specific permission
     */
    hasPermission(sessionId, permission) {
        const sessionValidation = this.validateSession(sessionId);
        
        if (!sessionValidation.valid) {
            return false;
        }

        const session = sessionValidation.session;
        
        // Admin role has all permissions
        if (session.permissions.includes('*')) {
            return true;
        }

        // Check specific permission
        return session.permissions.includes(permission);
    }

    /**
     * Check if user has role level access
     */
    hasRoleLevel(sessionId, requiredLevel) {
        const sessionValidation = this.validateSession(sessionId);
        
        if (!sessionValidation.valid) {
            return false;
        }

        const userRole = this.roles.get(sessionValidation.session.role);
        return userRole && userRole.level >= requiredLevel;
    }

    /**
     * Require permission for operation
     */
    requirePermission(sessionId, permission) {
        if (!this.hasPermission(sessionId, permission)) {
            const session = this.sessions.get(sessionId);
            this.logSecurityEvent('PERMISSION_DENIED', {
                sessionId,
                userId: session?.userId,
                permission,
                timestamp: new Date().toISOString()
            });
            throw new Error(`Permission denied: ${permission}`);
        }
        return true;
    }

    /**
     * Create secure resource access token
     */
    createResourceToken(sessionId, resourceType, resourceId, permissions = []) {
        this.requirePermission(sessionId, `${resourceType}.access`);
        
        const token = {
            resourceType,
            resourceId,
            permissions,
            sessionId,
            createdAt: Date.now(),
            expiresAt: Date.now() + (60 * 60 * 1000), // 1 hour
            nonce: crypto.randomBytes(16).toString('hex')
        };

        const tokenString = JSON.stringify(token);
        const signature = crypto.createHmac('sha256', this.getTokenSecret())
            .update(tokenString)
            .digest('hex');

        return {
            token: Buffer.from(tokenString).toString('base64'),
            signature,
            expiresAt: token.expiresAt
        };
    }

    /**
     * Validate resource access token
     */
    validateResourceToken(tokenData, requiredPermission) {
        try {
            const tokenString = Buffer.from(tokenData.token, 'base64').toString('utf8');
            const token = JSON.parse(tokenString);

            // Verify signature
            const expectedSignature = crypto.createHmac('sha256', this.getTokenSecret())
                .update(tokenString)
                .digest('hex');

            if (tokenData.signature !== expectedSignature) {
                return { valid: false, reason: 'Invalid token signature' };
            }

            // Check expiration
            if (Date.now() > token.expiresAt) {
                return { valid: false, reason: 'Token expired' };
            }

            // Validate session
            const sessionValidation = this.validateSession(token.sessionId);
            if (!sessionValidation.valid) {
                return { valid: false, reason: 'Invalid session' };
            }

            // Check permission
            if (requiredPermission && !token.permissions.includes(requiredPermission)) {
                return { valid: false, reason: 'Insufficient token permissions' };
            }

            return {
                valid: true,
                token: {
                    resourceType: token.resourceType,
                    resourceId: token.resourceId,
                    permissions: token.permissions,
                    session: sessionValidation.session
                }
            };
        } catch (error) {
            return { valid: false, reason: 'Token parsing failed' };
        }
    }

    /**
     * Terminate user session
     */
    terminateSession(sessionId) {
        const session = this.sessions.get(sessionId);
        if (session) {
            this.sessions.delete(sessionId);
            this.logSecurityEvent('LOGOUT', {
                sessionId,
                userId: session.userId,
                timestamp: new Date().toISOString()
            });
            return true;
        }
        return false;
    }

    /**
     * Get user permissions based on role
     */
    getUserPermissions(roleName) {
        const role = this.roles.get(roleName);
        return role ? role.permissions : [];
    }

    /**
     * Validate user credentials (simplified for desktop)
     */
    async validateUserCredentials(userId, credentials) {
        // For desktop app, we'll use a simplified validation
        // In a real app, this would integrate with proper authentication
        
        // Default admin user for desktop
        const defaultUser = {
            id: 'desktop_admin',
            username: 'admin',
            role: 'admin',
            isActive: true
        };

        if (userId === 'desktop_admin' || userId === 'admin') {
            return defaultUser;
        }

        // Creator user
        if (userId === 'creator' || userId === 'desktop_creator') {
            return {
                id: userId,
                username: userId,
                role: 'creator',
                isActive: true
            };
        }

        return null;
    }

    /**
     * Record failed login attempt
     */
    recordFailedAttempt(userId) {
        const attempts = this.failedAttempts.get(userId) || { count: 0, lastAttempt: 0 };
        attempts.count++;
        attempts.lastAttempt = Date.now();
        this.failedAttempts.set(userId, attempts);
    }

    /**
     * Check if user is locked out
     */
    isUserLockedOut(userId) {
        const attempts = this.failedAttempts.get(userId);
        if (!attempts || attempts.count < this.maxFailedAttempts) {
            return false;
        }

        const lockoutExpiry = attempts.lastAttempt + this.lockoutDuration;
        return Date.now() < lockoutExpiry;
    }

    /**
     * Generate secure session ID
     */
    generateSessionId() {
        return crypto.randomBytes(32).toString('hex');
    }

    /**
     * Get token signing secret
     */
    getTokenSecret() {
        // In production, this should be stored securely
        return 'ainflue_desktop_token_secret_' + process.env.NODE_ENV || 'development';
    }

    /**
     * Log security events
     */
    logSecurityEvent(eventType, details) {
        const logEntry = {
            timestamp: new Date().toISOString(),
            type: eventType,
            details,
            source: 'AccessControlManager'
        };

        // In production, integrate with proper logging system
        console.log('[SECURITY]', logEntry);
    }

    /**
     * Get access control statistics
     */
    getAccessStats() {
        const activeSessions = Array.from(this.sessions.values())
            .filter(session => Date.now() < session.expiresAt);

        return {
            activeSessions: activeSessions.length,
            totalRoles: this.roles.size,
            totalPermissions: this.permissions.size,
            lockedUsers: Array.from(this.failedAttempts.entries())
                .filter(([userId, attempts]) => this.isUserLockedOut(userId)).length,
            sessionStats: {
                oldest: activeSessions.length > 0 ? 
                    Math.min(...activeSessions.map(s => s.createdAt)) : null,
                newest: activeSessions.length > 0 ?
                    Math.max(...activeSessions.map(s => s.createdAt)) : null
            }
        };
    }

    /**
     * Cleanup expired sessions and reset lockouts
     */
    cleanup() {
        const now = Date.now();
        let expiredSessions = 0;
        let clearedLockouts = 0;

        // Remove expired sessions
        for (const [sessionId, session] of this.sessions.entries()) {
            if (now > session.expiresAt) {
                this.sessions.delete(sessionId);
                expiredSessions++;
            }
        }

        // Clear expired lockouts
        for (const [userId, attempts] of this.failedAttempts.entries()) {
            if (now > (attempts.lastAttempt + this.lockoutDuration)) {
                this.failedAttempts.delete(userId);
                clearedLockouts++;
            }
        }

        return {
            expiredSessions,
            clearedLockouts,
            activeSessions: this.sessions.size
        };
    }
}

module.exports = AccessControlManager;

/**
 * Copyright Notice:
 * This code is the exclusive property of Fahed Mlaiel.
 * Unauthorized use, copying, or distribution is strictly prohibited.
 * Contact: mlaiel@live.de
 */